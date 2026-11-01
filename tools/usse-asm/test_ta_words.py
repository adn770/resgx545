# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Tests of ta_words.py: the VDM stream and TA object by glossary name, the 11.8 tables, the
region test and the script readers."""
from __future__ import annotations

import os
import pathlib
import struct
import tomllib

import pytest

import pbdump
import ta_words

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(os.environ.get("RESGX545_DATA", pathlib.Path.home() / "src" / "resgx545-data"))

# The library's triangle stream (userspace/libsgxfive render.c sgxfive_tri_vdm) with its PDS
# and index addresses at 0x10000 and 0x20000.
TRI = [0x40001004, 0x0a022405, 0x80c00003, 0x00020200, 0xf0000000, 0x003fffff,
       0xf0001000, 0x01c00081, 0x60001008, 0x0a022401, 0xc0000000]


def test_the_triangle_stream_splits_into_state_index_state_terminate():
    blocks = ta_words.vdm_blocks(TRI)
    assert [b["kind"] for b in blocks] == ["state", "index", "state", "terminate"]
    assert [b["at"] for b in blocks] == [0, 2, 8, 10]
    assert len(blocks[1]["words"]) == 6


def test_state_word_1_by_its_glossary_fields():
    f = ta_words.vdm_blocks(TRI)[0]["fields"]
    assert f["VDM_STATE1.BITS11_9"] == 2
    assert f["VDM_STATE1.BITS15_13"] == 1
    assert f["VDM_STATE1.BIT8"] == 0
    assert f["VDM_STATE1.BIT12"] == 0
    assert f["VDM_STATE1.BIT25"] == 1
    assert f["VDM_STATE1.BIT18"] == 0


def test_index_list_by_its_glossary_fields():
    f = ta_words.vdm_blocks(TRI)[1]["fields"]
    assert f["VDM_INDEX0.PRIMITIVE_TOPOLOGY"] == 0
    assert f["VDM_INDEX0.WORDS_PRESENT"] == 3
    assert f["VDM_INDEX2.WORD"] == 0xf0000000
    assert f["VDM_INDEX3.INDEX_WRAP"] == 0x003fffff
    assert f["VDM_TASK0.MAX_VERTICES"] == 15
    assert f["VDM_TASK1.OUTPUT_SIZE"] == 1


def test_an_index_list_without_trailing_words_is_four_words():
    blocks = ta_words.vdm_blocks([0x80000003, 0x2000, 0xf0001000, 0x01c00081, 0xc0000000])
    assert [b["kind"] for b in blocks] == ["index", "terminate"]
    assert "VDM_INDEX2.WORD" not in blocks[0]["fields"]
    assert len(blocks[0]["words"]) == 4


def test_a_stream_line_names_fields_and_marks_unknown_blocks():
    text = ta_words.vdm_text([0xc0000000, 0x00000000])
    assert "unknown" in text and "terminate" in text
    assert "VDM_STATE1.BITS11_9 2" in ta_words.vdm_text(TRI)


def _object(n_vertices=3, per_vertex=1, prims=1):
    """A TA object of the dumps' shape: three PDS words, the vertices, ISP words, the
    primitive list, line widths, format word, four set masks, packed vertices."""
    ws = [0x04000004, 0x00030001, 0x04000000]
    ws += [0x3f800000 + v for v in range(n_vertices * per_vertex)]
    ws += [0x01d00200, 0x10f0]
    ws += [0x4a30 | 0x4a30 << 16] * ((prims + 1) // 2)
    ws += [0x1010, 0x00040000 | per_vertex << 8 | per_vertex, 0, 0, 0, 0]
    ws += [0x11111111] * 8
    return ws


def test_the_object_by_pb_obj_fields_from_its_object_word():
    ws = _object()
    o = pbdump.object_fields(ws, isp_at=6, vertices=3, prims=1)
    assert o["PB_OBJ.PDS_WORDS"] == [0x04000004, 0x00030001, 0x04000000]
    assert o["PB_OBJ.ISP_WORDS"] == [0x01d00200, 0x10f0]
    assert o["PB_OBJ.PRIM_LIST"] == [(16, 17, 18)]
    assert o["PB_OBJ.LINE_WIDTHS"] == 0x1010
    assert o["format"] == 0x00040101
    assert o["PB_OBJ.SET_MASKS"] == [0, 0, 0, 0]
    assert o["vertex dwords"] == 1
    assert len(o["packed"]) == 8


def test_the_object_reads_three_dwords_a_vertex():
    ws = _object(per_vertex=3)
    o = pbdump.object_fields(ws, isp_at=12, vertices=3, prims=1)
    assert o["vertex dwords"] == 3
    assert o["PB_OBJ.RHW"] == [0x3f800000, 0x3f800003, 0x3f800006]


def test_the_report_prints_the_object_by_field(tmp_path):
    param = bytearray(0x2000)
    obj = _object()
    param[0:4 * len(obj)] = struct.pack(f"<{len(obj)}I", *obj)
    param[0x80:0x88] = struct.pack("<2I", 0x4490ffff, 0x04000406)
    param[0x88:0x8c] = struct.pack("<I", pbdump.FILLER)
    td = bytearray(0x1000)
    td[0:12] = struct.pack("<3I", 0x00000000, 0x1080, 0)
    (tmp_path / "t__0.param.bin").write_bytes(bytes(param))
    (tmp_path / "t__0.tadata.bin").write_bytes(bytes(td))
    text = pbdump.report(tmp_path, "t__0")
    assert "PB_OBJ.ISP_WORDS 01d00200 000010f0" in text
    assert "PB_OBJ.PRIM_LIST (16, 17, 18)" in text


def test_random_triangles_are_reproducible_and_on_the_target():
    a = ta_words.random_triangles(1108, 24, 128)
    assert a == ta_words.random_triangles(1108, 24, 128)
    assert len(a) == 24
    for t in a:
        assert all(-16 * 16 <= c <= 144 * 16 for p in t for c in p)


def test_region_test_predicts_the_streamed_regions_of_a_triangle():
    t = ((8 * 16, 8 * 16), (56 * 16, 20 * 16), (20 * 16, 56 * 16))
    want = ta_words.predicted_regions(t, 64, 64)
    assert (0, 0) in want and want[(0, 0)] == (True, True)
    assert all(k[0] < 2 and k[1] < 4 for k in want)


def test_region_check_scores_agreement():
    t = ((8 * 16, 8 * 16), (56 * 16, 20 * 16), (20 * 16, 56 * 16))
    want = ta_words.predicted_regions(t, 64, 64)
    seen = {k: (0x90 if v == (True, True) else 0x80 if v[0] else 0x98) for k, v in want.items()}
    r = ta_words.region_check(want, seen)
    assert r == {"regions": len(want), "missing": [], "extra": [], "form": []}
    seen.pop(next(iter(seen)))
    assert len(ta_words.region_check(want, seen)["missing"]) == 1


def test_tables_load_and_name_their_probes():
    tabs = ta_words.tables()
    assert set(tabs) == {"vdm/state1-split", "vdm/index2", "render/bg-pds-word",
                         "render/reg-0148", "render/frag-flags", "render/rtds-words",
                         "ta/te-psg", "ta/object-words"}
    for path, text in tabs.items():
        t = tomllib.loads(text)
        unit, feature = path.split("/")
        assert t.get("name", f"{unit}-{feature}") == f"{unit}-{feature}"
        for p in t.get("probe", []):
            assert p["name"].startswith(f"{unit}-{feature}")
            assert len(p["cases"]) == len(p.get("labels", p["cases"]))


def test_index2_probes_cover_the_question_values_twice():
    t = tomllib.loads(ta_words.tables()["vdm/index2"])
    values = [[c["vdm"]["4"] for c in p["case_set"]] for p in t["probe"]]
    assert len(values) == 2 and values[0] == values[1]
    assert {1, 2, 3, 5, 0xff, 0x0f000000, 0xf0000000, 0} <= set(values[0])


def test_tables_name_scripts_and_sources_their_templates_hold():
    probes = HERE.parents[1] / "probes"
    for path, text in ta_words.tables().items():
        t = tomllib.loads(text)
        templates = probes / path.split("/")[0] / "templates"
        if "script" in t:
            assert (templates / t["script"]).is_file(), path
        for p in t.get("probe", []):
            for src in [p["source"], *p.get("slots", {}).values()]:
                assert (templates / src).is_file(), (path, src)


def test_written_tables_are_the_generated_ones():
    probes = HERE.parents[1] / "probes"
    for path, text in ta_words.tables().items():
        assert (probes / f"{path}.toml").read_text() == text, path


def test_pixels_reader_counts_the_surviving_pixels():
    out = "\n".join(["== a: tri --pixels", "job: faulted",
                     "row 0: deadbeef ff00ff00", "row 1: ff203040 deadbeef",
                     "== b: tri --pixels", "job: ok", "row 0: ff00ff00 ff00ff00",
                     "row 1: ff203040 ff203040"])
    cases = ta_words.case_pixels(out)
    assert cases["a"] == [[0xdeadbeef, 0xff00ff00], [0xff203040, 0xdeadbeef]]
    cut = ta_words.case_pixels("== c: x\nrow 0: 0xdeadbeef sgxfive-test: render: job faulted, "
                               "context lost (Input/output error) 0xff00ff00")
    assert cut["c"] == [[0xdeadbeef, 0xff00ff00]]
    agree = ta_words.agreeing(cases["a"], cases["b"])
    assert agree == [(1, 0), (0, 1)]


def test_ta3dctl_reader_takes_each_case_block():
    out = "\n".join(["== x: tri -n 1", "tri: 1 renders ok",
                     "ta3dctl: " + " ".join(f"{i:08x}" for i in range(59)),
                     "cleanup: rtds 0x1 ctx 0x2 pbdesc 0x3 flags 0x0 ret 0"])
    s = ta_words.case_states(out)
    assert s["x"]["ta3dctl"][24] == 24
    named = ta_words.case_states("== one-rd:54-0x8: tri -n 1 --kpoke-render 1:rd:54^=0x8\n"
                                 "job: ok\n== one-rd:54-0xc: tri\njob: failed")
    assert named["one-rd:54-0x8"]["lines"] == ["job: ok"]
    assert named["one-rd:54-0xc"]["lines"] == ["job: failed"]
    assert s["x"]["cleanup"][0].startswith("rtds")
    assert s["x"]["lines"] == ["tri: 1 renders ok"]


@pytest.mark.skipif(not (DATA / "render" / "kick-objects").is_dir(),
                    reason="no resgx545-data render/kick-objects")
def test_the_kick_objects_dumps_decode_as_objects():
    d = DATA / "render" / "kick-objects" / "render-kick-objects-tris2" / "dumps"
    name = "render-kick-objects-tris2__0"
    param = (d / f"{name}.param.bin").read_bytes()
    td = (d / f"{name}.tadata.bin").read_bytes()
    o = ta_words.first_object(param, td)
    assert o["PB_OBJ.PDS_WORDS"][1] == 0x00030001
    assert len(o["PB_OBJ.PRIM_LIST"]) == 2


# ---- the records' numbers on the data (skipped when resgx545-data is absent) ----

RANDOM = DATA / "ta" / "object-words" / "ta-object-words-random" / "dumps"
IDX2 = DATA / "vdm" / "index2"


def _first(stem: pathlib.Path) -> dict | None:
    return ta_words.first_object(pathlib.Path(f"{stem}.param.bin").read_bytes(),
                                 pathlib.Path(f"{stem}.tadata.bin").read_bytes())


def _seen(k: int) -> dict:
    stem = RANDOM / f"ta-object-words-random__{k}"
    return ta_words.seen_regions(pathlib.Path(f"{stem}.param.bin").read_bytes(),
                                 pathlib.Path(f"{stem}.tadata.bin").read_bytes())


@pytest.mark.skipif(not RANDOM.is_dir(), reason="no resgx545-data ta/object-words")
def test_e307_every_region_of_the_random_triangles_is_predicted():
    total = ta_words.random_report(RANDOM, "ta-object-words-random").splitlines()[-1]
    assert total == ("total: predicted 265, streamed 265, missing 0, extra 0, wrong form 0")
    forms: dict[int, int] = {}
    for k in range(ta_words.RANDOM_COUNT):
        for f in _seen(k).values():
            forms[f] = forms.get(f, 0) + 1
    assert forms == {0x80: 61, 0x90: 154, 0x98: 50}     # never 0x8a or 0x8c


def _overlap(t, x0, y0, x1, y1, closed: bool) -> bool:
    """A plain separating-axis test of triangle t against a box, edges closed or open."""
    box = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    axes = [(1, 0), (0, 1)] + [(t[i - 1][1] - t[i][1], t[i][0] - t[i - 1][0]) for i in range(3)]
    for ax, ay in axes:
        a = [ax * x + ay * y for x, y in t]
        b = [ax * x + ay * y for x, y in box]
        if (max(a) < min(b) or max(b) < min(a)) if closed else \
                (max(a) <= min(b) or max(b) <= min(a)):
            return False
    return True


@pytest.mark.skipif(not RANDOM.is_dir(), reason="no resgx545-data ta/object-words")
def test_e307_the_random_triangles_do_not_reach_the_fitted_boundary_rules():
    # a plain overlap test, all closed or all open, gives the fitted test's tiles in every
    # region: no random vertex or edge lies on a tile boundary
    n = ta_words.RANDOM_SIZE
    regions = 0
    for t16 in ta_words.random_triangles(ta_words.SEED, ta_words.RANDOM_COUNT, n):
        t = [(x / 16, y / 16) for x, y in t16]
        want = ta_words.predicted_regions(t16, n, n)
        for row in range(n // 16):
            for col in range(n // 32):
                x0, y0 = col * 32, row * 16
                fitted = want.get((col, row), (False, False))
                for closed in (True, False):
                    plain = (_overlap(t, x0, y0, x0 + 16, y0 + 16, closed),
                             _overlap(t, x0 + 16, y0, x0 + 32, y0 + 16, closed))
                    assert plain == fitted
                regions += 1
    assert regions == 768


@pytest.mark.skipif(not RANDOM.is_dir(), reason="no resgx545-data ta/object-words")
def test_prim_list_bit_15_follows_the_random_triangles_winding():
    flagged = []
    for k, t in enumerate(ta_words.random_triangles(ta_words.SEED, ta_words.RANDOM_COUNT,
                                                    ta_words.RANDOM_SIZE)):
        (ax, ay), (bx, by), (cx, cy) = t
        o = _first(RANDOM / f"ta-object-words-random__{k}")
        assert o["PB_OBJ.PRIM_LIST"] == [(16, 17, 18)]
        bit = o["PB_OBJ.PRIM_LIST bit 15"][0]
        assert bit == ((bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0)
        flagged.append(bit)
    assert sum(flagged) == 11


def _decoded(d: pathlib.Path) -> list[dict | None]:
    return [_first(pathlib.Path(str(f)[:-len(".param.bin")]))
            for f in sorted(d.glob("*/dumps/*.param.bin"))]


@pytest.mark.skipif(not (DATA / "ta" / "objects").is_dir() or not IDX2.is_dir()
                    or not RANDOM.is_dir(), reason="no resgx545-data object dumps")
def test_e308_the_layout_decodes_28_fit_and_45_new_objects():
    fit = _decoded(DATA / "ta" / "objects")
    new = [o for d in (IDX2, DATA / "ta" / "object-words") for o in _decoded(d)]
    assert len(fit) == 28 and None not in fit
    formats = sorted({o["format"] for o in fit})
    assert formats == [0x00040101, 0x00040303, 0x00040503, 0x00040505, 0x000c0202]
    # no object: 0xff in both runs, the first run's hung control, the faulting PDS case
    assert len(new) == 49 and new.count(None) == 4
    new = [o for o in new if o]
    assert len(new) == 45
    assert {o["format"] for o in new} == {0x00040101}   # one format: one dword a vertex
    assert all(o["format"] & 0xff == o["vertex dwords"] for o in fit + new)


@pytest.mark.skipif(not IDX2.is_dir(), reason="no resgx545-data vdm/index2")
def test_e300_index2_objects_by_value():
    values = [0xf0000000, 0, 1, 2, 3, 5, 0xff, 0x0f000000, 0x80000000]
    want = {0xf0000000: 15, 0: 15, 1: 15, 2: 12, 3: 12, 5: 9, 0x0f000000: 9, 0x80000000: 15}
    for probe in ("vdm-index2-copies", "vdm-index2-copies-r2"):
        for i, v in enumerate(values):
            o = _first(IDX2 / probe / "dumps" / f"{probe}__{i}")
            if v == 0xff or (v == 0xf0000000 and probe == "vdm-index2-copies"):
                assert o is None            # no object, and the first run's hung control
                continue
            assert len(o["PB_OBJ.RHW"]) == want[v]
            assert len(o["PB_OBJ.PRIM_LIST"]) == want[v] // 3
            assert o["PB_OBJ.RHW"][-1] == (0x47c35000 if v == 1 else 0x3f800000)
            assert o["PB_OBJ.PRIM_LIST bit 15"][:2] == ([1, 1] if v == 0x0f000000 else [0, 0])
