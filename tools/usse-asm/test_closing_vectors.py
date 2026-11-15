# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""closing_vectors.py: the converter of the closing sessions' kept jobs (round 4, sim item 4).
Synthetic jobs first (the layout of render/closing-*/out/<attempt>/<stage>), then the published
R3-pixel session when the data repository is present."""
import gzip
import json
import os
import pathlib
import struct

import pytest

import closing_vectors as cv

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
SESSION = DATA / "render" / "closing-r3-pixel"

IDLE, TICK, TA, G3D = 0x20, 0xccfa0, 0xccff8, 0xfffa7


def tl(rows):
    """regtimeline rows (t ns, 0x0008, 0x0118, 0x012c) as the runner printed them."""
    return "".join(f"tl {t} {a:08x} {s:08x} 20000000\n" for t, a, s in rows)


def job_text(label, o0, rows, tri=None):
    lines = ["programs asm", f"probe {label}: scratch at 0x3e003000 (64 KiB)"]
    if tri:
        lines.append(f"probe {label}: tri {tri}, pixel replaced")
    lines += [f"probe {label}: o0 {o0}",
              f"timeline: regs 0x0008 0x0118 0x012c samples {len(rows)} seconds 0 start 0 end 1 rc 0"]
    return "\n".join(lines) + "\n" + tl(rows)


def us(n):
    return int(n * 1000)


def write_stage(tmp, stage, jobs, bins):
    """jobs: [(name, args, status2 after, text)]; bins: {name: [words]}."""
    d = tmp / "out" / stage
    d.mkdir(parents=True)
    head = "name\tstage\tset\trisk\tknobs\trt\targs\trc\tclass\tmode\tfault_req\treset_rc\theld_msg\n"
    body = ""
    for name, args, after, text in jobs:
        body += f"{name}\t{stage}\tcontrol\tsafe\tstophang s2\t0x0008,0x0118,0x012c\t{args}\t0\tok\t" \
                f"status2 1024 -> {after}\n"
        with gzip.open(d / f"{name}.txt.gz", "wt") as f:
            f.write(text)
    (d / "cases.tsv").write_text(head + body)
    b = tmp / "bins"
    b.mkdir(exist_ok=True)
    for name, words in bins.items():
        (b / f"{name}.bin").write_bytes(struct.pack(f"<{len(words)}Q", *words))
    return d


# a burst of 100 us: idle, 3D clocks at 10 us, TA clocks 20 to 150 us, tick, idle
ROWS = [(0, IDLE, 0x400), (us(10), G3D, 0x400), (us(20), TA, 0x400), (us(150), TICK, 0x400),
        (us(160), IDLE, 0x400)]
ROWS_SET = [(0, IDLE, 0x400), (us(10), G3D, 0x400), (us(20), TA, 0x400), (us(146), TA, 0x480),
            (us(150), TICK, 0x4c0), (us(160), IDLE, 0x4c0)]


def test_parse_reads_the_proof_the_timeline_and_the_regs():
    j = cv.parse_job(job_text("loop-rel-b8-i53", "0xc0de0035 (2048 of 2048)", ROWS))
    assert j.label == "loop-rel-b8-i53"
    assert j.proof == (0xc0de0035, 2048, 2048)
    assert j.regs == ["0x0008", "0x0118", "0x012c"]
    assert j.rows[2] == (us(20), [TA, 0x400, 0x20000000])
    assert j.tri is None


def test_parse_reads_a_triangle_size_and_a_mixed_readback():
    t = job_text("loop-rel-b8-i56", "mixed 0xff203040 x3034 0xc0de0038 x1062", ROWS, tri="64x64")
    j = cv.parse_job(t)
    assert j.tri == (64, 64)
    assert j.proof == (0xc0de0038, 1062, 4096)


def test_parse_refuses_a_job_without_a_loop_proof():
    j = cv.parse_job(job_text("pix_green", "0xff00ff00 (64 of 64)", ROWS, tri="8x8"))
    assert j.proof == (0xff00ff00, 64, 64)       # read as is; the caller decides it is no loop


def test_timing_of_a_clear_and_a_set_job():
    a = cv.timing(cv.parse_job(job_text("x", "0x1 (1 of 1)", ROWS)), 0x400)
    assert a["burst_us"] == 150.0 and a["ta_run_us"] == 130.0 and a["a_us"] == 0.0
    assert a["tile_time_us"] == pytest.approx((150 - 60.2) / 4, abs=0.06)
    assert a["bit6"] is False and a["bit7"] is False and a["t6_us"] is None and a["t7_us"] is None
    b = cv.timing(cv.parse_job(job_text("x", "0x1 (1 of 1)", ROWS_SET)), 0x4c0)
    assert b["bit6"] and b["bit7"]
    assert b["t7_us"] == 136.0 and b["d7_us"] == 126.0      # t from the burst's start (10 us)
    assert b["t6_us"] == 140.0 and b["d6_us"] == 140.0      # d6 from the 3D clocks' first sample


def test_timing_without_a_burst_is_empty_not_zero():
    t = cv.timing(cv.parse_job(job_text("x", "0x1 (1 of 1)", [(0, IDLE, 0x400), (us(5), IDLE, 0x400)])),
                  0x400)
    assert t["burst_us"] is None and t["ta_run_us"] == 0.0 and t["tile_time_us"] is None


def test_loop_vector_of_a_fill_and_a_triangle(tmp_path):
    words = [0x1111, 0x2222, 0x3333]
    d = write_stage(tmp_path, "q-x", [
        ("f-1", 'probe "$S/loop-rel-b8-i53.bin"', 0x400,
         job_text("loop-rel-b8-i53", "0xc0de0035 (2048 of 2048)", ROWS)),
        ("t-1", 'probe --tri pixel --temps 32 --width 8 --height 8 --tri-full "$S/loop-rel-b8-i53.bin"',
         0x440, job_text("loop-rel-b8-i53", "0xc0de0035 (64 of 64)", ROWS_SET, tri="8x8")),
        ("g-1", 'probe --tri pixel --temps 32 --width 8 --height 8 --tri-full "$S/pix_green.bin"',
         0x400, job_text("pix_green", "0xff00ff00 (64 of 64)", ROWS, tri="8x8")),
    ], {"loop-rel-b8-i53": words, "pix_green": [9]})
    vs, skipped = cv.loop_vectors(d, tmp_path / "bins")
    assert [v["id"] for v in vs] == ["f-1", "t-1"]
    assert skipped == {"g-1": "not a loop program"}
    f, t = vs
    assert f["program"] == {"isa": "usse", "entry": 0, "source": "recorded",
                            "words": ["0x0000000000001111", "0x0000000000002222",
                                      "0x0000000000003333"]}
    assert f["init"]["task"] == "loop-proof" and f["init"]["host"] == "fill"
    assert f["init"]["instances"] == 2048 and f["init"]["temps"] is None
    assert f["readback"]["o0"] is None            # the generic replay leaves these out
    assert f["readback"]["proof"] == {"o0": "0xc0de0035", "count": 2048, "of": 2048}
    assert t["init"]["host"] == "tri" and t["init"]["temps"] == 32
    assert t["init"]["instances"] == 64 and t["init"]["code_index"] == 0x20
    assert f["init"]["code_index"] == 0
    cv.validate_loops(vs)


def test_the_proof_of_a_loop_must_equal_its_counter(tmp_path):
    d = write_stage(tmp_path, "q-x", [
        ("f-1", 'probe "$S/loop-rel-b8-i53.bin"', 0x400,
         job_text("loop-rel-b8-i53", "0xc0de0036 (2048 of 2048)", ROWS))], {"loop-rel-b8-i53": [1]})
    with pytest.raises(ValueError, match="counter"):
        cv.loop_vectors(d, tmp_path / "bins")


def test_the_abs_loop_proves_with_zero(tmp_path):
    d = write_stage(tmp_path, "q-x", [
        ("a-1", 'probe "$S/loop-abs-b8-i53.bin"', 0x400,
         job_text("loop-abs-b8-i53", "0x00000000 (2048 of 2048)", ROWS))], {"loop-abs-b8-i53": [1]})
    vs, _ = cv.loop_vectors(d, tmp_path / "bins")
    assert vs[0]["readback"]["proof"]["o0"] == "0x00000000"


def test_timings_file_has_a_row_a_job_and_says_what_it_is(tmp_path):
    d = write_stage(tmp_path, "q-x", [
        ("f-1", 'probe "$S/p.bin"', 0x400, job_text("p", "0x1 (1 of 1)", ROWS)),
        ("f-2", 'probe "$S/p.bin"', 0x4c0, job_text("p", "0x1 (1 of 1)", ROWS_SET))], {})
    doc = cv.timings(d, session="render/closing-r3-pixel")
    assert doc["format"] == "sgx545-timings" and doc["version"] == 1
    assert [r["id"] for r in doc["jobs"]] == ["f-1", "f-2"]
    assert doc["jobs"][1]["bit7"] is True and doc["jobs"][0]["status2_after"] == "0x00000400"
    assert "not a simulator prediction" in doc["note"]
    (d / "cases.tsv").write_text((d / "cases.tsv").read_text() + "f-3\tq-x\tcontrol\tsafe\tk\trt\tprobe\t0\n")
    assert cv.timings(d, session="s")["not_run"] == ["f-3"]


def test_no_trailing_whitespace_in_the_json(tmp_path):
    d = write_stage(tmp_path, "q-x", [
        ("f-1", 'probe "$S/loop-rel-b8-i53.bin"', 0x400,
         job_text("loop-rel-b8-i53", "0xc0de0035 (2048 of 2048)", ROWS))], {"loop-rel-b8-i53": [1]})
    out = tmp_path / "o"
    cv.convert(d, tmp_path / "bins", out, session="render/closing-r3-pixel")
    for f in out.rglob("*.json"):
        assert not any(ln != ln.rstrip() for ln in f.read_text().splitlines())
        json.loads(f.read_text())


needs_data = pytest.mark.skipif(not SESSION.is_dir(), reason="no resgx545-data render/closing-r3-pixel")


@needs_data
def test_published_session_counts():
    att = next((SESSION / "out").glob("2026*"))
    n = {}
    for stage in ("q-f0", "q-f1a", "q-f1b", "q-t"):
        vs, sk = cv.loop_vectors(att / stage, SESSION / "bins")
        n[stage] = (len(vs), len(sk))
    assert n == {"q-f0": (10, 0), "q-f1a": (54, 0), "q-f1b": (54, 0), "q-t": (86, 7)}


@needs_data
def test_published_timings_agree_with_the_scorers_lines():
    """E805/E806: the clear fill at 16 and the set one at 136; the bit from the job's own read."""
    att = next((SESSION / "out").glob("2026*"))
    doc = cv.timings(att / "q-f0", session="render/closing-r3-pixel")
    by = {r["id"]: r for r in doc["jobs"]}
    assert by["f0-rel-b8-16"]["bit6"] is False and by["f0-rel-b8-136"]["bit6"] is True
    assert by["f0-rel-b8-136"]["t6_us"] is not None


def test_vertex_vector_carries_the_depth_words_and_the_loop_count(tmp_path):
    (tmp_path / "bins").mkdir()
    (tmp_path / "bins" / "vloop-b8v-i1045.bin").write_bytes(struct.pack("<2Q", 5, 6))
    case = {"name": "v-up-n1045", "args": 'probe --temps 16 --pixels --tri vtxuse "$S/vloop-b8v-i1045.bin"'}
    v = cv.vertex_vector(case, "vloop-b8v-i1045", [0x3f200000 + 1045] * 3, tmp_path / "bins", "rel")
    assert v["id"] == "v-up-n1045"
    assert v["program"]["words"] == ["0x0000000000000005", "0x0000000000000006"]
    assert v["init"] == {"task": "vertex", "instances": 3, "per": 3, "temps": 16, "outputs": ["o2"],
                         "skip": [], "draw_vertices": 3}
    assert v["readback"]["o0"] is None and v["readback"]["vertices"] is None
    assert v["readback"]["depth_words"] == ["0x3f200415"] * 3
    assert v["provenance"]["inputs"] == {"N": 1045}


def test_vertex_vector_refuses_a_job_whose_words_disagree_with_its_counter(tmp_path):
    (tmp_path / "bins").mkdir()
    (tmp_path / "bins" / "vloop-b8v-i7.bin").write_bytes(struct.pack("<Q", 5))
    case = {"name": "v-x", "args": 'probe --temps 16 "$S/vloop-b8v-i7.bin"'}
    with pytest.raises(ValueError, match="depth"):
        cv.vertex_vector(case, "vloop-b8v-i7", [0x3f200007, 0x3f200008, 0x3f200007], tmp_path / "bins", "r")


@needs_data
def test_published_vertex_jobs_decode_to_the_loop_count():
    att = next((SESSION / "out").glob("2026*"))
    vs, skipped = cv.vertex_vectors(att / "q-v", SESSION / "bins", "r")
    assert len(vs) + len(skipped) == 74
    by = {v["id"]: v for v in vs}
    assert by["v-i1760"]["readback"]["depth_words"] == [f"0x{0x3f200000 + 1760:08x}"] * 3
    assert len(by["v-v48-n329"]["readback"]["depth_words"]) == 15      # as the scorer decoded
    assert by["v-v48-n329"]["init"]["draw_vertices"] == 48 and by["v-i1760"]["init"]["draw_vertices"] == 3


def word_at(x, y, w, h, tag=15):
    """The premise control's word of a pixel: pa0 and pa1 as the float in each half (pa-x: x in the high half)."""
    def hi(v):
        return struct.unpack("<I", struct.pack("<f", v))[0] & 0xffff0000
    return hi((x + .5 - w / 2) * 2 / w) | tag, hi((y + .5 - h / 2) * 2 / h) | tag


def grid_text(label, rows):
    return "\n".join(f"probe {label}: row {i}: " + " ".join(f"{v:08x}" for v in r) for i, r in enumerate(rows))


def test_source_of_decodes_the_float_pair_to_the_pixel():
    for (x, y) in [(0, 0), (3, 5), (63, 63), (20, 33)]:
        vx, vy = word_at(x, y, 64, 64)
        assert cv.source_of(vx, vy, 64, 64) == (x, y)
    vx, vy = word_at(5, 100, 128, 128)
    assert cv.source_of(vx, vy, 128, 128) == (5, 100)


def test_decoded_mask_marks_the_pixels_the_premise_control_confirms():
    w = h = 4
    gx = [[word_at(x, y, w, h)[0] for x in range(w)] for y in range(h)]
    gy = [[word_at(x, y, w, h)[1] for x in range(w)] for y in range(h)]
    gx[1][2] = cv.BG                        # not written
    gy[3][0] = gy[2][0]                     # decodes to another pixel's row
    mask = cv.decoded(gx, gy, w, h)
    assert len(mask) == 16 and mask[1 * 4 + 2] is False and mask[3 * 4 + 0] is False
    assert sum(mask) == 14


def test_direct_vector_carries_the_image_and_its_premise_mask(tmp_path):
    w = h = 4
    gx = [[word_at(x, y, w, h)[0] for x in range(w)] for y in range(h)]
    gy = [[word_at(x, y, w, h)[1] for x in range(w)] for y in range(h)]
    img = [[x % 2 for x in range(w)] for y in range(h)]
    jobs = []
    for name, rows in (("c-rdf-pa-x", gx), ("c-rdf-pa-y", gy), ("c-rdf-g25", img)):
        args = f'probe --tri pixel --temps 32 --pixels --width 4 --height 4 --tri-full "$S/r3c-{name[2:]}-x.bin"'
        jobs.append((name, args, 0x400, job_text(f"r3c-{name[2:]}-x", "mixed 0x0 x1", ROWS, tri="4x4")
                     + grid_text(f"r3c-{name[2:]}-x", rows) + "\n"))
    d = write_stage(tmp_path, "p-c3", jobs, {"r3c-rdf-g25-x": [7, 8]})
    vs, skipped = cv.direct_vectors(d, tmp_path / "bins", "r")
    assert [v["id"] for v in vs] == ["c-rdf-g25"] and skipped == {}
    v = vs[0]
    assert v["init"] == {"task": "direct-read", "host": "tri", "width": 4, "height": 4, "temps": 32,
                         "code_index": 0x20, "reads": "g25", "background": "0xff203040"}
    assert v["readback"]["image"] == [f"0x{x % 2:08x}" for _ in range(h) for x in range(w)]
    assert v["readback"]["undecoded"] == []
    assert v["program"]["words"] == ["0x0000000000000007", "0x0000000000000008"]


@needs_data
def test_published_direct_reads_have_the_premise_fractions_of_e808():
    att = next((SESSION / "out").glob("2026*"))
    vs, skipped = cv.direct_vectors(att / "p-c3", SESSION / "bins", "r")
    assert sorted(v["id"] for v in vs) == sorted(
        ["c-rd-g23", "c-rd-g24", "c-rd-g25", "c-rdf-g23", "c-rdf-g24", "c-rdf-g25", "c-rdf128-g23",
         "c-rdf128-g25"])
    frac = {}
    for v in vs:
        w = v["init"]["width"]
        img, und = v["readback"]["image"], set(v["readback"]["undecoded"])
        written = [i for i, p in enumerate(img) if p != "0xff203040"]
        frac[v["id"]] = round(sum(i not in und for i in written) / len(written), 3)
        assert len(img) == w * v["init"]["height"]
    assert frac["c-rd-g23"] == 1.0 and frac["c-rdf-g23"] == 0.995 and frac["c-rdf128-g25"] == 0.996


@needs_data
def test_published_timings_give_round_4_readings_of_bits_6_and_7():
    """Data statements, not rules of the simulator (closing4/pixel/rule_ta.txt and rule_px.txt): bit 7 of the
    74 q-v jobs is set iff the TA clocks' run is 125 us or more, and bit 6 of the 106 fills without a load iff
    the tile time is 125 us or more, with no job on the wrong side outside the edge bands (120 to 131 and
    118 to 132)."""
    att = next((SESSION / "out").glob("2026*"))
    v = cv.timings(att / "q-v", session="s")["jobs"]
    assert len(v) == 74
    assert [r["id"] for r in v if not 120 <= r["ta_run_us"] <= 131 and (r["ta_run_us"] >= 125) != r["bit7"]] == []
    fills = [r for s in ("q-f0", "q-f1a", "q-f1b") for r in cv.timings(att / s, session="s")["jobs"]
             if "ld8" not in r["program"]]
    assert len(fills) == 106
    assert [r["id"] for r in fills
            if not 118 <= r["tile_time_us"] <= 132 and (r["tile_time_us"] >= 125) != r["bit6"]] == []


# ---- probe jobs of a session (round 26 P1): PDS secondaries (E1104) and fills in a batch whose
# colour-space set is machine state from job to job (E1097, E1103)

BT601 = ["0x00950095", "0x00000095", "0x010203ce", "0x039800cc", "0x00000000"]
ZEROS = ["0x00000000"] * 5
CSC_POKES = "--poke xfer:17^=0x1 " + " ".join(f"--poke xfer:{18 + i}={w}" for i, w in enumerate(BT601))


def probe_stage(tmp, stage, jobs, bins):
    """jobs: [(name, args, text)] in run order; bins: {file: bytes}."""
    d = tmp / "out" / "20261115-000000" / stage
    d.mkdir(parents=True)
    head = "name\tstage\tset\trisk\tknobs\ttool\targs\trc\tclass\tfault_int\tfault_word\tfree_kb\n"
    body = ""
    for name, args, text in jobs:
        body += f"{name}\t{stage}\tfit\tsafe\t-\tt24\t{args}\t0\tok\t-\t-\t1\n"
        if text is not None:
            with gzip.open(d / f"{name}.txt.gz", "wt") as f:
                f.write(text)
    (d / "cases.tsv").write_text(head + body)
    b = tmp / "bins"
    b.mkdir(exist_ok=True)
    for name, blob in bins.items():
        (b / name).write_bytes(blob)
    return d


def probe_text(name, lines):
    return "programs asm\n" + "".join(f"probe {name}: {x}\n" for x in
                                      ["scratch at 0x3e003000 (64 KiB)"] + lines)


def test_a_pds_job_becomes_a_pds_secondary_vector_with_its_attrs(tmp_path):
    """A `probe --pds N --use U --scratch-show 64` job: the PDS words (32-bit) and data size, the
    USE program as sent, attrs 64 (vectors.pds_attrs), its pokes as init.job, and sa_kept: the
    attributes this job's PDS does not write hold what earlier jobs left (E1104)."""
    pds = struct.pack("<4I", 1, 2, 3, 4)
    use = struct.pack("<2Q", 0xfa44070000000000, 0xfca1705003af0000)
    args = 'probe --temps 32 --pds 36 --use "$S/bins/sa64_dump.bin" --scratch-show 64 ' \
           '--poke bg:1=0x30000 "$S/bins/j-a32.bin"'
    text = probe_text("j-a32", ["pokes bg:1=0x30000", "poked bg:1 0x00130000 -> 0x00030000",
                                "o0 0x0da7a000 (2048 of 2048)", "scratch +0x080 0xa1000020"])
    d = probe_stage(tmp_path, "q019", [("j-a32", args, text)],
                    {"j-a32.bin": pds, "sa64_dump.bin": use})
    vs, skipped = cv.probe_vectors(d, tmp_path / "bins", "s/out/a/q019")
    assert skipped == {}
    (v,) = vs
    assert v["id"] == "j-a32" and v["program"]["isa"] == "pds" and v["program"]["data"] == 36
    assert v["program"]["words"] == ["0x00000001", "0x00000002", "0x00000003", "0x00000004"]
    init = v["init"]
    assert init["task"] == "pds-secondary" and init["attrs"] == 64 and init["sa_kept"] is True
    assert init["use"]["words"] == ["0xfa44070000000000", "0xfca1705003af0000"]
    assert init["job"]["pokes"] == ["bg:1=0x30000"] and "csc" not in init["job"]
    assert v["readback"]["scratch"] == {"0x080": "0xa1000020"}
    assert v["readback"]["o0"] == "0x0da7a000"


def test_the_colour_space_set_is_kept_from_job_to_job(tmp_path):
    """E1103: a job whose transfer command sets xfer:17 bit 0 loads set 0 from xfer:18-22 (a copy
    or a fill), a fill without it reads the last loaded set; before any load the set is not
    known (no init.job.csc). A fill whose load poke was not echoed leaves the set not known
    (E568's dangling pokes before t22). Copies are skipped (the transfer path)."""
    prog = struct.pack("<Q", 0xfa44070000000000)
    fill = 'probe --temps 32 --coords --pixels'
    pixel = ["o0 0xff000000 (2048 of 2048)"] + [f"row {y}: " + " ".join(["ff000000"] * 64)
                                                 for y in range(32)]
    zc = "copy --every-value --pixels --poke tex:1=0x7d03f01f --poke xfer:17^=0x1 " + \
        " ".join(f"--poke xfer:{18 + i}=0" for i in range(5))
    echo = ["pokes xfer:17^=0x1 " + " ".join(f"xfer:{18 + i}={w}" for i, w in enumerate(BT601)),
            "poked xfer:17 0x00000000 -> 0x00000001"]
    jobs = [("f0", f'{fill} "$S/bins/f0.bin"', probe_text("f0", pixel)),
            ("zc", zc, "programs asm\njob: ok\n"),
            ("fa", f'{fill} "$S/bins/fa.bin"', probe_text("fa", pixel)),
            ("fb", f'{fill} {CSC_POKES} "$S/bins/fb.bin"', probe_text("fb", echo + pixel)),
            ("fc", f'{fill} "$S/bins/fc.bin"', probe_text("fc", pixel)),
            ("fx", f'{fill} {CSC_POKES} "$S/bins/fx.bin"', probe_text("fx", pixel)),
            ("fy", f'{fill} "$S/bins/fy.bin"', probe_text("fy", pixel))]
    d = probe_stage(tmp_path, "csc", jobs, {f"{n}.bin": prog for n in ("f0", "fa", "fb", "fc", "fx", "fy")})
    vs, skipped = cv.probe_vectors(d, tmp_path / "bins", "s/out/a/csc")
    assert list(skipped) == ["zc"] and "copy" in skipped["zc"]
    by = {v["id"]: v for v in vs}
    assert list(by) == ["f0", "fa", "fb", "fc", "fx", "fy"]
    csc = {k: v["init"]["job"].get("csc") for k, v in by.items()}
    assert csc["f0"] is None and csc["fx"] is None and csc["fy"] is None
    assert csc["fa"] == {"set": 0, "words": ZEROS, "loaded_by": "zc"}
    assert csc["fb"] == {"set": 0, "words": BT601, "loaded_by": "fb"}
    assert csc["fc"] == {"set": 0, "words": BT601, "loaded_by": "fb"}
    v = by["fa"]
    assert v["init"]["task"] == "pixel" and v["init"]["pa0"] == "coords" and v["init"]["temps"] == 32
    assert v["program"]["words"] == ["0xfa44070000000000"] and len(v["readback"]["pixels"]) == 2048
    assert "sa_kept" not in v["init"]


def test_probe_vectors_cli_writes_one_file_a_stage(tmp_path):
    prog = struct.pack("<Q", 0xfa44070000000000)
    text = probe_text("f0", ["o0 0x00000001 (2048 of 2048)"])
    probe_stage(tmp_path, "s1", [("f0", 'probe --temps 32 "$S/bins/f0.bin"', text)], {"f0.bin": prog})
    out = tmp_path / "vec"
    assert cv.main(["--session", str(tmp_path), "--out", str(out), "--probes", "s1"]) == 0
    doc = json.loads((out / "s1.vec.json").read_text())
    assert doc["format"] == "sgx545-vectors" and [v["id"] for v in doc["vectors"]] == ["f0"]
    assert doc["run"]["raw"] == [f"{tmp_path.parent.name}/{tmp_path.name}/out/20261115-000000/s1/f0.txt.gz"]


SA64 = DATA / "render" / "closing-r25-sa64"
CSC = DATA / "render" / "closing-r25-csc"


@pytest.mark.skipif(not SA64.is_dir(), reason="no resgx545-data render/closing-r25-sa64")
def test_published_r25_sa64_jobs_convert_with_64_attributes():
    """E1104: 2 pk64 and 56 q019 jobs, each a PDS secondary with attrs 64, none skipped."""
    att = next((SA64 / "out").glob("2026*"))
    n = {}
    for stage in ("pk64", "q019"):
        vs, sk = cv.probe_vectors(att / stage, SA64 / "bins", f"render/closing-r25-sa64/out/{att.name}/{stage}")
        assert all(v["init"]["attrs"] == 64 and v["init"]["sa_kept"] for v in vs)
        n[stage] = (len(vs), len(sk))
    assert n == {"pk64": (2, 0), "q019": (56, 0)}


@pytest.mark.skipif(not CSC.is_dir(), reason="no resgx545-data render/closing-r25-csc")
def test_published_r25_csc_fills_carry_the_set_the_batch_left():
    """E1103's table: per format, a after zc (zeros), b and c after b's own load (BT.601), d after
    bc (BT.601), e and f after e's load (zeros); the four copies skipped."""
    att = next((CSC / "out").glob("2026*"))
    vs, sk = cv.probe_vectors(att / "csc", CSC / "bins", "c")
    assert sorted(sk) == ["y28-bc", "y28-zc", "y29-bc", "y29-zc"]
    got = {v["id"]: (v["init"]["job"]["csc"]["words"] == BT601, v["init"]["job"]["csc"]["loaded_by"])
           for v in vs}
    for f in ("y28", "y29"):
        assert got[f"{f}-a"] == (False, f"{f}-zc") and got[f"{f}-b"] == (True, f"{f}-b")
        assert got[f"{f}-c"] == (True, f"{f}-b") and got[f"{f}-d"] == (True, f"{f}-bc")
        assert got[f"{f}-e"] == (False, f"{f}-e") and got[f"{f}-f"] == (False, f"{f}-e")
    assert all(len(v["readback"]["pixels"]) == 2048 for v in vs)
