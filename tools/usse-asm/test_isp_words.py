# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The ISP and MTE word tools (isp_words.py): the words by glossary name, the coverage model of
the triangle's samples, the line model, the rule and sample-layout fitters, the readers of the
stored images and the tables of sub-phase 11.6. The fitters and models are also scored against
the recorded images (resgx545-data), where the records' numbers come from."""
from __future__ import annotations

import os
import pathlib
import struct
import tomllib

import pytest

import isp_words as W
import probe

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
ISP = DATA / "isp"
data = pytest.mark.skipif(not (ISP / "line-sample").is_dir(), reason="resgx545-data not present")


def _f(v: float) -> int:
    return struct.unpack("<I", struct.pack("<f", v))[0]


def test_decode_names_every_field_and_keeps_the_bits_outside_them():
    d = W.decode("ISP0", 0x01d00355)
    assert d["ISP0.SREF"] == 0x55 and d["ISP0.ISP2_PRESENT"] == 1
    assert d["ISP0.BIT9"] == 1 and d["ISP0.DCMP_MODE"] == 7
    assert d["ISP0.DWRITE_DISABLE"] == 1 and d["ISP0.PASS_TYPE"] == 0
    assert d["ISP0.rest"] == 0
    d = W.decode("ISP2", 0x0e02ff0f)
    assert (d["ISP2.SCMP_MODE"], d["ISP2.SOP3"], d["ISP2.SCMP_MASK"], d["ISP2.SW_MASK"]) == \
        (7, 2, 0xff, 0x0f)
    d = W.decode("OUTSEL", 0x43000)
    assert d["OUTSEL.VTX_SIZE"] == 4 and d["OUTSEL.rest"] == 0x3000
    with pytest.raises(W.IspError):
        W.decode("ISP9", 0)


def test_the_fields_of_each_word_do_not_overlap():
    for word, fields in W.FIELDS.items():
        seen = 0
        for _name, hi, lo in fields:
            mask = (1 << (hi + 1)) - (1 << lo)
            assert not seen & mask, word
            seen |= mask


def test_a_position_word_gives_four_samples_in_sixteenths():
    assert W.samples(0xeaa26e26) == [(6, 2), (14, 6), (2, 10), (10, 14)]
    assert W.samples(0x88) == [(8, 8), (0, 0), (0, 0), (0, 0)]


def test_the_single_sample_triangle_draws_the_library_s_1062_pixels():
    tri = W.default_tri(64, 64)
    assert len(W.cover(tri, 64, 64, [(8, 8)])) == 1062


def test_the_eight_sample_rule_gives_the_counts_of_the_04c8_runs():
    # the counts of the three 0x04c8 values at 0x0520 = 0x0c0c0c0c (1122, 1134, 1098)
    tri = W.default_tri(64, 64)
    got = [len(W.rule_cover("eight", tri, 64, 64, m, 0x0c0c0c0c)) for m in (0x88, ~0 & 0xffffffff,
                                                                            0)]
    assert got == [1122, 1134, 1098]


def test_the_two_coverage_rules_part_where_every_sample_is_past_the_long_edge():
    tri = W.default_tri(64, 64)
    a = W.rule_cover("eight", tri, 64, 64, 0xcccccccc, 0xcccccccc)
    b = W.rule_cover("centre", tri, 64, 64, 0xcccccccc, 0xcccccccc)
    assert len(a) == 1086 and len(b) == 1122 and a < b


def test_fit_rules_scores_an_image_against_each_rule():
    tri = W.default_tri(64, 64)
    img = W.image_of(W.rule_cover("eight", tri, 64, 64, 0xcccccccc, 0), 64, 64)
    fit = W.fit_rules(img, 0xcccccccc, 0, 64, 64)
    assert fit["eight"] == 0 and fit["centre"] > 0
    img = W.image_of(W.rule_cover("single", tri, 64, 64, 0xcc, 0), 64, 64)
    assert len([v for v in img if v == W.GREEN]) == 1086
    assert W.fit_rules(img, 0xcc, 0, 64, 64)["single"] == 0


def test_the_layout_fitter_finds_a_side_by_side_layout_and_its_sample_positions():
    tri = W.affine_target(4, 4, 10, 0)
    pos = [(3, 5), (12, 9)]
    img = W.layout_image(tri, 64, 64, (2, 1), pos)
    best = W.fit_layout(img, tri, 64, 64)[0]
    assert best["layout"] == (2, 1) and best["mismatch"] == 0
    for got, want in zip(best["samples"], pos):
        assert W.covers_alike(tri, 64 // 2, 64, got, want)


def test_the_layout_fitter_prefers_the_2x2_layout_for_a_2x2_image():
    tri = W.affine_target(4, 4, 10, 0)
    pos = [(6, 2), (14, 6), (2, 10), (10, 14)]
    img = W.layout_image(tri, 64, 64, (2, 2), pos)
    fits = W.fit_layout(img, tri, 64, 64)
    assert fits[0]["layout"] == (2, 2) and fits[0]["mismatch"] == 0


def test_the_affine_vertex_shader_maps_the_library_triangle_onto_the_target():
    a, b, c, d, e, f = W.affine_params(W.affine_target(4, 4, 10, 8), 64, 64)
    for (cx, cy), (px, py) in zip(W.CLIP, [(4.5, 4.5), (14, 4.5), (4.5, 14)]):
        x, y = a * cx + b * cy + c, d * cx + e * cy + f
        assert abs((x + 1) * 32 - px) < 1e-6 and abs((y + 1) * 32 - py) < 1e-6


def test_the_line_reader_gives_the_columns_of_each_row():
    img = [W.BG] * (64 * 4)
    for x in range(8, 20):
        img[64 * 1 + x] = 0xff00ff00
    img[64 * 2 + 30] = 0xff00ff00
    spans = W.spans(img, 64, 0xff00ff00)
    assert spans == {1: (8, 19, 12), 2: (30, 30, 1)}


def test_a_copy_value_names_the_copy_whose_depth_it_carries():
    assert W.copy_of(0) == 0 and W.copy_of(_f(1 / 16)) == 1 and W.copy_of(_f(4 / 16)) == 4
    assert W.copy_of(W.BG) is None


def test_the_tables_load_as_probe_tables(tmp_path):
    for rel, text in W.tables().items():
        assert text.endswith("\n")
        assert all(len(l) <= 100 for l in text.splitlines() if l.startswith("#"))
        path = tmp_path / f"{rel}.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        spec = tomllib.loads(text)
        names = [p["name"] for p in spec.get("probe", [])]
        assert len(names) == len(set(names)), rel
        unit, feature = rel.split("/")
        assert all(n.startswith(f"{unit}-{feature}-") for n in names), rel
        if spec.get("probe"):
            ps = probe.load(path)
            assert ps and all(p.labels and len(p.labels) == len(p.cases) for p in ps)


def test_the_coverage_table_sets_isp0_bit_28_and_both_position_words():
    t = tomllib.loads(W.tables()["isp/coverage-samples"])
    p = t["probe"][0]
    assert p["blk"]["1"] == 0x11d00200
    sets = p["case_set"]
    assert {"cmd": {"16": 0xcccccccc}, "kpoke": ["rd:19=0xcccccccc"]} in sets


def test_the_stencil_word_tables_name_each_op_case():
    t = tomllib.loads(W.tables()["isp/stencil-word"])
    names = [p["name"] for p in t["probe"]]
    assert "isp-stencil-word-sop3-ref-55" in names
    p = next(p for p in t["probe"] if p["name"] == "isp-stencil-word-sop3-ref-55")
    assert p["obj2"]["blk"]["3"] == 0x0400ff00 and len(p["cases"]) == 8


def test_pb_unpack_reads_the_scene_script_s_base64_blocks(tmp_path):
    import base64
    import gzip
    raw = bytes(range(16)) * 4
    text = ("== 2 kick(s)\n#### param kicks2\n" +
            base64.b64encode(gzip.compress(raw)).decode() + "\n#### end\n")
    out = W.pb_unpack(text, tmp_path)
    assert out == [tmp_path / "kicks2.param.bin"]
    assert (tmp_path / "kicks2.param.bin").read_bytes() == raw


def test_the_joint_fitter_reads_a_cropped_2x2_image_inside_the_binned_tiles():
    pos = [(6, 2), (14, 6), (2, 10), (10, 14)]
    cases = []
    for k in range(0, 16, 2):
        tri = W.affine_target(4, 4, 10, k)
        img = W.layout_image(tri, 64, 64, (2, 2), pos)
        keep = W.tile_mask(W.binned_tiles(tri), 64, 64)
        cases.append(([v if (i % 64, i // 64) in keep else W.BG for i, v in enumerate(img)],
                      tri))
    best = W.fit_layout_joint(cases, 64, 64, layouts=((1, 1), (2, 1), (2, 2)))[0]
    assert best["layout"] == (2, 2) and best["mismatch"] == 0
    for (n, found), want in zip(best["slots"], pos):
        assert n == 0 and want in found


def test_the_binned_tiles_are_those_the_bounding_box_meets():
    assert W.binned_tiles(W.affine_target(4, 4, 10, 0)) == {(0, 0)}
    assert W.binned_tiles(W.default_tri(64, 64)) == {(x, y) for x in range(4) for y in range(4)}


def test_each_vertex_program_names_its_second_phase(tmp_path):
    """A vertex program's first phas instruction gives the index of its second: a wrong one
    hangs the job (the first depth-range run). Every table's vertex programs, as its first case
    renders them, are assembled and their listings checked."""
    import re
    import subprocess
    asm = pathlib.Path(probe.__file__).resolve().parent / "usse-asm"
    if not asm.exists():
        subprocess.run(["make", "-s", "-C", str(asm.parent)], check=True)
    root = pathlib.Path(__file__).resolve().parents[2] / "probes"
    texts = {}
    for rel, text in W.tables().items():
        path = tmp_path / f"{rel}.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        src = root / rel.split("/")[0] / "templates"
        for p in probe.load(path) if tomllib.loads(text).get("probe") else []:
            if p.slot == "vtxuse":
                texts[f"{rel}:{p.name}"] = probe.render(p, p.cases[0],
                                                        (src / p.source).read_text())
            for slot, f in p.slots.items():
                if slot == "vtxuse":
                    texts[f"{rel}:{f}"] = (src / f).read_text()
    for name, text in sorted(texts.items()):
        out = subprocess.run([str(asm), "-l", "-o", str(tmp_path / "x.bin"), "-"], input=text,
                             capture_output=True, text=True, check=True).stdout
        phas = [(int(m[1]), int(m[2])) for m in
                re.finditer(r"^\s*(\d+): \S+\s+phas #(\d+)", out, re.M)]
        assert len(phas) == 2 and phas[0][1] == phas[1][0], (name, phas)
    assert len(texts) >= 5


def test_the_line_model_moves_the_span_sample_and_keeps_the_rows_at_the_centre():
    ends = W.line_ends({})
    assert ends == ((8, 8), (56, 20))
    at1 = W.line_cover(ends, 1)
    assert len(at1) == 48 and min(at1) == (8, 8) and max(at1) == (55, 19)
    at0 = W.line_cover(ends, 0)
    assert min(at0) == (7, 7) and max(at0) == (54, 19)
    # a sixteenth on, bit 0 clear: column 8's span sample (9) is inside, its row is 8 at the centre
    moved = W.line_ends({6: W.f32(32 + 1 / 16)})
    assert (8, 8) in W.line_cover(moved, 0)
    assert (8, 7) in W.line_cover(moved, 0, row_at=W.Fraction(1))
    assert len(W.line_cover(ends, 1, 0x20)) == 96 and not W.line_cover(ends, 1, 0)


def _cases(table: str, probe_name: str):
    raw = (ISP / table / probe_name / "raw.txt").read_text()
    meta = W._meta(ROOT / "probes" / "isp" / f"{table}.toml", probe_name)
    img, fail = W.case_images(raw, probe_name)
    assert not fail
    return meta, img


def _line_miss(meta, img, i, **kw):
    blk, pos, lw = W.line_setting({"blk": {**meta.get("blk", {}),
                                           **meta["case_set"][i].get("blk", {})},
                                   "kpoke": meta["case_set"][i].get("kpoke", [])})
    got = {(j % 64, j // 64) for j, v in enumerate(img[i]) if v == W.GREEN}
    return len(got ^ W.line_cover(W.line_ends(blk), pos, lw, **kw))


@data
def test_the_line_model_fits_every_recorded_line_case():
    """E279: the 32 cases of both -x runs and the nine widths with no pixel missed, six of the
    eight -xy cases (the 3/4 ones miss 2 at either value); the far-corner rows miss 576 pixels a
    run, in the 16 cases at 0."""
    for name in ("isp-line-sample-x", "isp-line-sample-x-r2"):
        meta, img = _cases("line-sample", name)
        assert [_line_miss(meta, img, i) for i in range(32)] == [0] * 32
        far = [_line_miss(meta, img, i, row_at=W.Fraction(1)) for i in range(16, 32)]
        assert sum(far) == 576 and all(far)
    meta, img = _cases("line-sample", "isp-line-sample-xy")
    assert [_line_miss(meta, img, i) for i in range(8)] == [0, 0, 0, 2, 0, 0, 0, 2]
    meta, img = _cases("line-sample", "isp-line-sample-width")
    assert [_line_miss(meta, img, i) for i in range(9)] == [0] * 9
    assert [sum(1 for v in img[i] if v == W.GREEN) for i in range(9)] == \
        [0, 12, 24, 48, 72, 96, 192, 384, 768]


@data
def test_the_coverage_rules_score_the_recorded_images_as_e278_says():
    """E278: the eight-sample rule misses no pixel of the 56 bit-28 images; the centre reading
    misses 12, 24 or 36 pixels in 10 of the 28 settings, alike in both runs; with bit 28 clear
    byte 0 of 0x04c8 alone fits the four images."""
    fails = {}
    for table, names in (("coverage-samples", ("isp-coverage-samples-bit28",
                                               "isp-coverage-samples-bit28-r2")),
                         ("coverage-bytes", ("isp-coverage-bytes-bit28",
                                             "isp-coverage-bytes-bit28-r2"))):
        for name in names:
            meta, img = _cases(table, name)
            for i, s in enumerate(meta["case_set"]):
                m = s["cmd"]["16"]
                r = int(s["kpoke"][0].split("=")[1], 0)
                fit = W.fit_rules(img[i], m, r, 64, 64)
                assert fit["eight"] == 0, (name, i)
                if fit["centre"]:
                    fails.setdefault((m, r), []).append(fit["centre"])
    assert len(fails) == 10 and all(len(v) == 2 and v[0] == v[1] for v in fails.values())
    assert sorted(v[0] for v in fails.values()) == [12] * 6 + [24, 24, 36, 36]
    meta, img = _cases("coverage-samples", "isp-coverage-samples-single")
    for i, s in enumerate(meta["case_set"]):
        r = int(next(iter(s.get("kpoke", [])), "rd:19=0").split("=")[1], 0)
        assert W.fit_rules(img[i], s["cmd"]["16"], r, 64, 64)["single"] == 0


@data
def test_the_joint_layout_fit_of_the_recorded_modes():
    """E281: modes 0, 1 and 2 fit 1x1, 2x1 and 2x2 with no pixel missed, the next layout missing
    371, 423 and 406 pixels."""
    want = {0: ((1, 1), 371), 1: ((2, 1), 423), 2: ((2, 2), 406)}
    for mode, (layout, nxt) in want.items():
        name = f"isp-msaa-layout-m{mode}-te0"
        meta, img = _cases("msaa-layout", name)
        cases = [(img[i], W.affine_target(4, 4, 10, int(lab.split("=")[1])))
                 for i, lab in enumerate(meta["labels"])]
        fits = W.fit_layout_joint(cases, 64, 64)
        assert (fits[0]["layout"], fits[0]["mismatch"], fits[1]["mismatch"]) == (layout, 0, nxt)
