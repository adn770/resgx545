# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""closing_tables.py: the data statements of the closing pass that no simulator replays (round 4,
sim item 4 of R3-P11): depth words (E795-E798), dword 36 (E803), parameter buffer pages (E824),
count tables (r3-geo, r3-geo-c). Synthetic stages first, then the published sessions when the data
repository is present."""
import gzip
import json
import os
import pathlib
import struct

import pytest

import closing_tables as ct

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
GEO = DATA / "render" / "closing-r3-geo"
K = DATA / "render" / "closing-r3k-pixel"
GEOC = pathlib.Path(os.environ.get("RESGX545_GEOC") or DATA / "render" / "closing-r3-geo-c")
R6M = DATA / "render" / "closing-r6-misc"

HEAD = "name\tstage\tset\trisk\tP\tknobs\trt\targs\trc\tclass\tnote\n"


def put(d, name, data):
    p = d / name
    if isinstance(data, str):
        data = data.encode()
    with gzip.open(p, "wb") as f:
        f.write(data)


def tline(t, s58, s24, s2c, knob=0x60):
    return f"tl {t} {knob:08x} {s58:08x} {s24:08x} {s2c:08x}\n"


def timeline(rows, start=0):
    """regtimeline rows (t, 0x0658, 0x0724, 0x072c) and the header the runner prints."""
    return (f"timeline: regs 0x0624 0x0658 0x0724 0x072c samples {len(rows)} seconds 0 start {start} end 9 rc 0\n"
            + "".join(tline(*r) for r in rows))


def stage(tmp, name, jobs):
    """jobs: [(name, set, P, args, class, text, buf09 dwords or None)]."""
    d = tmp / "out" / name
    d.mkdir(parents=True)
    body = ""
    for n, st, P, args, cls, text, b9 in jobs:
        body += f"{n}\t{name}\t{st}\tsafe\t{P}\tstophang\t-\t{args}\t0\t{cls}\t-\n"
        if text is not None:
            put(d, f"{n}.txt.gz", text)
        if b9 is not None:
            ws = [0] * 59
            for i, v in b9.items():
                ws[i] = v
            put(d, f"{n}.after.buf09.bin.gz", struct.pack("<59I", *ws))
    (d / "cases.tsv").write_text(HEAD + body)
    return d


# two aborts: 0x072c = 7 before the first rising edge of bit 0 of 0x0658, 9 before the second
ROWS = [(0, 0, 0x10, 5), (100, 0, 0x30, 7), (200, 1, 0x30, 7), (300, 0, 0x20, 4), (400, 0, 0x30, 9),
        (500, 1, 0x30, 9), (600, 0, 0, 0)]


def test_find_stage_takes_the_plain_or_the_attempt_layout(tmp_path):
    (tmp_path / "out" / "g-x").mkdir(parents=True)
    assert ct.find_stage(tmp_path, "g-x") == tmp_path / "out" / "g-x"
    (tmp_path / "out" / "20261110-1" / "k-y").mkdir(parents=True)
    (tmp_path / "out" / "20261110-2" / "k-y").mkdir(parents=True)
    assert ct.find_stage(tmp_path, "k-y") == tmp_path / "out" / "20261110-2" / "k-y"
    with pytest.raises(FileNotFoundError):
        ct.find_stage(tmp_path, "nope")


def test_reading_of_a_dpm_job(tmp_path):
    d = stage(tmp_path, "g-c4", [("c4-a", "fit", "0x82", "probe --tri pixel --width 2048 --height 2048 --vertices 1500",
                                  "ok", "job: ok\n" + timeline(ROWS), {36: 5, 37: 0x2c0, 38: 0x20})])
    r = ct.counts_table(d, "s/geo")["rows"][0]
    assert (r["id"], r["P"], r["knob0624"]) == ("c4-a", 0x82, 0x60)
    assert r["partial_renders"] == 2 and r["thr0"] == 0x30 and r["peaks"] == [0x30, 0x30, 0]
    assert r["counts_before_aborts"] == [7, 9] and r["need"] == 0x30
    assert (r["dw36"], r["dw37"], r["dw38"]) == (5, 0x2c0, 0x20)
    assert (r["width"], r["height"], r["vertices"]) == (2048, 2048, 1500)


def test_a_job_whose_knob_did_not_land_or_failed_is_skipped_with_a_reason(tmp_path):
    d = stage(tmp_path, "g-c4", [
        ("bad-knob", "fit", "0x99", "tri --width 64 --height 64", "ok", timeline(ROWS) + "job: ok\n", None),
        ("hung", "fit", "0x82", "tri --width 64 --height 64", "hang", timeline(ROWS), None),
        ("none", "fit", "0x82", "tri --width 64 --height 64", "ok", None, None),
        ("early", "fit", "0x82", "tri --width 64 --height 64 -n 2", "ok",
         "tri 64x64 #1: overflowed\n" + timeline(ROWS), None)])
    t = ct.counts_table(d, "s/geo")
    assert t["rows"] == []
    assert "did not land" in t["skipped"]["bad-knob"] and "hang" in t["skipped"]["hung"]
    assert "no output" in t["skipped"]["none"] and "before the last" in t["skipped"]["early"]


def test_a_stage_without_the_count_register_has_counts_without_it(tmp_path):
    txt = ("timeline: regs 0x0624 0x0658 0x0724 samples 3 seconds 0 start 0 end 9 rc 0\n"
           "tl 0 00000002 00000000 00000010\ntl 100 00000002 00000001 00000030\n"
           "tl 200 00000002 00000000 00000030\n")
    d = stage(tmp_path, "g-qf", [("qf-0x24", "fit", "0x24", "tri --width 4096 --height 4096", "ok", txt, None)])
    r = ct.counts_table(d, "s")["rows"][0]
    assert r["partial_renders"] == 1 and r["counts_before_aborts"] is None


def test_dword36_rows_carry_the_last_count_and_say_what_they_are(tmp_path):
    d = stage(tmp_path, "g-d36", [("d36-a", "heldout", "0x82", "probe --width 2048 --height 2048", "ok",
                                   timeline(ROWS), {36: 7, 38: 0x20}),
                                  ("d36-b", "heldout", "0x82", "probe --width 2048 --height 2048", "ok",
                                   timeline(ROWS), {36: 2, 38: 0x20})])
    t = ct.dword36_table([("g-d36", d)], "s/geo")
    assert [(r["id"], r["last_count"], r["dw36"], r["agrees"]) for r in t["rows"]] == \
        [("d36-a", 9, 7, True), ("d36-b", 9, 2, False)]
    assert t["totals"] == {"jobs": 2, "agree": 1}
    assert t["replay"]["status"] == "refused" and t["replay"]["reason"]


def test_pb_pages_count_the_nonzero_pages_and_the_model(tmp_path):
    d = tmp_path / "k-f4"
    d.mkdir()
    page = bytes([1]) * 4096
    param = page * 2 + bytes(4096 * 3) + page + bytes(4096)
    put(d, "h1-288x144-k4.tri.param.bin.gz", param)
    put(d, "h1-288x144-k4.tri.tadata.bin.gz", bytes(64))
    put(d, "h1-288x144-k4.txt.gz", "diff: 0 of 41472 pixels\nprobe tri: render memory to x (20480, 32768 bytes)\n")
    args = "tri --tri-full --width 288 --height 144 --poke cmd:1=0xe0000000 --dump-render \"$W/dump\""
    (d / "cases.tsv").write_text(HEAD.replace("\tP\t", "\tP\t") + f"h1-288x144-k4\tk-f4\theldout\tsafe\t-\trgn:4 expectdiff\t-\t{args}\t0\tok\t-\n")
    t = ct.pb_pages_table(d, "s")
    r = t["rows"][0]
    assert (r["width"], r["height"], r["arrays"]) == (288, 144, 4)
    assert (r["pages"], r["nonzero"], r["runs"]) == (7, 3, [[0, 1], [5, 5]])
    assert r["ta_data_bytes"] == 32768 and r["wrong"] == 0
    assert r["tiles"] == 81 and r["model_nonzero"] == 15
    assert t["replay"]["status"] == "refused"


def test_pb_pages_skip_a_job_without_a_dump(tmp_path):
    d = tmp_path / "k-f4"
    d.mkdir()
    (d / "cases.tsv").write_text(HEAD + "c1-288x144-k1\tk-f4\tcontrol\tsafe\t-\theld rgn:1\t-\ttri --width 288 --height 144\t1\tfault\t-\n")
    t = ct.pb_pages_table(d, "s")
    assert t["rows"] == [] and "no dump" in t["skipped"]["c1-288x144-k1"]


def zdump(w, h, stored):
    """a depth dump (the layout of r3_geo: 512 dwords a 32 x 16 tile) with the pixels in `stored` not 1.0f."""
    g = max(1, (w + 31) // 32 - 1)
    tw, th = (w + 31) // 32, (h + 15) // 16
    n = 512 * ((th - 1) * (g + 1) + tw)
    ws = [0x3F800000] * n
    for x, y in stored:
        ws[ct.dword_index(x, y, w, h)] = 0x3F000000
    return struct.pack(f"<{n}I", *ws)


def test_zls_extent_is_the_stored_pixels_bounding_box(tmp_path):
    stored = [(x, y) for x in range(42) for y in range(22)]
    d = tmp_path / "g-z"
    d.mkdir()
    put(d, "z-a.txt.gz", "diff: 0 of 612 pixels\n")
    put(d, "z-a.depth.1.bin.gz", zdump(34, 18, stored))
    (d / "cases.tsv").write_text(HEAD + "z-a\tg-z\theldout\tsafe\t-\tx\t-\ttri --width 34 --height 18 --tri-full --depth\t0\tok\t-\n")
    t = ct.zls_table(d, "s")
    r = t["rows"][0]
    assert (r["width"], r["height"], r["stored"], r["extent"]) == (34, 18, 924, [42, 22])
    assert r["unwritten"] == 0 and r["full_screen"] is True


def test_dword_index_of_the_first_tiles():
    assert ct.dword_index(0, 0, 34, 18) == 0
    assert ct.dword_index(32, 0, 34, 18) == 512
    assert ct.dword_index(0, 16, 34, 18) == 512 * 2


def test_no_trailing_whitespace_and_tables_are_json(tmp_path):
    d = stage(tmp_path, "g-c4", [("c4-a", "fit", "0x82", "tri --width 64 --height 64", "ok", timeline(ROWS), None)])
    ct.write(tmp_path / "o" / "t.table.json", ct.counts_table(d, "s"))
    text = (tmp_path / "o" / "t.table.json").read_text()
    assert json.loads(text)["format"] == ct.TABLES
    assert all(line == line.rstrip() for line in text.splitlines())


# ------------------------------------------------------------------------------------------ published
needs_geo = pytest.mark.skipif(not GEO.is_dir(), reason="no render/closing-r3-geo")


def test_zls_table_names_the_test_that_replays_it_and_others_stay_refused(tmp_path):
    d = stage(tmp_path, "g-z", [])
    t = ct.zls_table(d, "s")
    assert t["replay"]["status"] == "replayed"
    assert t["replay"]["test"].endswith("zls_table.rs::the_band_replays_every_modelled_row_of_the_zls_tables")
    assert "E885" in t["replay"]["model"] and "odd widths" in t["replay"]["model"]
    assert "reason" not in t["replay"]
    assert ct.counts_table(d, "s")["replay"]["status"] == "refused"


@needs_geo
def test_published_depth_words_of_e795_to_e798():
    n = {s: ct.depth_table(ct.find_stage(GEO, s), "x") for s in ("g-da", "g-db", "g-dc", "g-dd")}
    assert {s: len(t["rows"]) for s, t in n.items()} == {"g-da": 27, "g-db": 16, "g-dc": 10, "g-dd": 4}
    by = {r["id"]: r for r in n["g-da"]["rows"]}
    assert by["da-ctl-z0-w3"]["depth_words"] == ["0x3f000000"] * 3     # E783's control, predictions file
    assert by["da-ctl-zm05-w1"]["depth_words"][0] == "0x3e800000"
    assert all(len(r["depth_words"]) == 4 for r in n["g-dd"]["rows"])   # E798: 4 vertices
    assert all(t["replay"]["status"] == "refused" for t in n.values())


@needs_geo
def test_published_dword36_is_e803s_table():
    stages = [(s, ct.find_stage(GEO, s)) for s in ("g-d36", "g-c4", "g-c5", "g-c6", "g-c7")]
    t = ct.dword36_table(stages, "x")
    by = {}
    for r in t["rows"]:
        by.setdefault(r["stage"], []).append(r)
    assert len(by["g-d36"]) == 6 and all(r["agrees"] for r in by["g-d36"])
    assert len(by["g-c4"]) == 10 and len(by["g-c5"]) == 33 and len(by["g-c6"]) == 4 and len(by["g-c7"]) == 7
    assert t["totals"] == {"jobs": 60, "agree": 60}                    # E803: 60 of 60


@needs_geo
def test_published_count_tables_have_a_row_a_usable_job():
    for s in ("g-c4", "g-c5", "g-c6", "g-c7", "g-d36"):
        t = ct.counts_table(ct.find_stage(GEO, s), "x")
        assert t["rows"] and all(r["partial_renders"] >= 0 and r["knob0624"] is not None for r in t["rows"])
        assert all(r["P"] == r["knob0624"] + 0x22 for r in t["rows"] if r["P"])


needs_k = pytest.mark.skipif(not K.is_dir(), reason="no render/closing-r3k-pixel")


@needs_k
def test_published_k_f4_page_counts_are_e824s_dumps():
    t = ct.pb_pages_table(ct.find_stage(K, "k-f4"), "x")
    got = {(r["width"], r["height"]): r["nonzero"] for r in t["rows"] if r["id"].startswith("h")}
    assert got == {(288, 144): 15, (256, 288): 22, (384, 384): 40, (320, 160): 17, (512, 384): 52,
                   (640, 480): 79, (320, 400): 36, (1024, 768): 196}
    assert all(r["nonzero"] == r["model_nonzero"] for r in t["rows"] if r["arrays"] == 4 and r["width"] > 64)
    assert {r["id"] for r in t["rows"] if r["arrays"] == 1} == {"c3-64x64-k1"}
    assert "no dump" in t["skipped"]["c1-288x144-k1"]
    assert [r["ta_data_bytes"] for r in t["rows"] if r["id"].startswith("h")] == \
        [0x8000, 0x8000, 0xb000, 0x8000, 0xb000, 0x13000, 0xc000, 0x1e000]     # E824's list


@pytest.mark.skipif(not GEOC.is_dir(), reason="no r3-geo-c session (RESGX545_GEOC)")
def test_r3_geo_c_tables():
    z = ct.zls_table(ct.find_stage(GEOC, "g-z"), "x")
    ext = {r["id"]: tuple(r["extent"]) for r in z["rows"]}
    assert ext["z-w32"] == (32, 22) and ext["z-w64"] == (64, 22) and ext["z-h32"] == (42, 32)
    assert ext["z-w20"] == (25, 22) and ext["z-ctl-66x34-x"] == (82, 42)
    assert {r["id"]: r["stored"] for r in z["rows"]}["z-tri-in"] == 96
    f = ct.counts_table(ct.find_stage(GEOC, "g-qf"), "x")
    assert {r["P"]: r["partial_renders"] for r in f["rows"]}[0x24] == 9
    assert len(f["rows"]) == 22
    h = ct.counts_table(ct.find_stage(GEOC, "g-qh"), "x")
    assert len(h["rows"]) == 8 and len(h["skipped"]) == 6


@pytest.mark.skipif(not R6M.is_dir(), reason="no render/closing-r6-misc")
def test_r6_misc_q287_table_is_e885s_odd_heights():
    # the latest attempt (freeze 2's rerun): every row of the 20 has its dump, W 34 throughout
    d = ct.find_stage(R6M, "q287")
    assert d.parent.name == "20261112-152213"
    z = ct.zls_table(d, "x")
    assert len(z["rows"]) == 20 and not z["skipped"]
    got = {(r["height"], tuple(r["extent"]), r["stored"]) for r in z["rows"]}
    assert got == {(17, (42, 21), 882), (18, (42, 22), 924), (19, (42, 24), 1008), (7, (42, 9), 378),
                   (11, (42, 14), 588), (23, (42, 29), 1218), (35, (42, 44), 1848), (21, (42, 26), 1092)}
    assert all(r["width"] == 34 and r["full_screen"] and r["diff_zero"] for r in z["rows"])
