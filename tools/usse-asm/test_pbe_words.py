# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The PBE word tools (pbe_words.py): the words by glossary name, the tables that vary them on
the laptop, and the readers of the stored images (byte-field correlator, word effects)."""
from __future__ import annotations

import os
import pathlib
import tomllib

import pytest

import pbe_words as P
import probe

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
PACK = DATA / "pbe" / "pack-colours"


def test_the_words_of_a_64x64_target_follow_the_library():
    w = P.words(64, 64, 0x10000)
    assert w == [0x00000000, 0x003f003f, 0x001f8000, 0x00010000, 0x200]


def test_decode_names_every_field_and_keeps_the_bits_outside_them():
    d = P.decode("EMIT2", 0xf01f8001)
    assert d["EMIT2.BITS15_8"] == 0x80
    assert d["EMIT2.LINE_STRIDE"] == 0x01f
    assert d["EMIT2.rest"] == 0x80000001          # bit 31 and bit 0: no field
    d = P.decode("SIDEBAND", 0x2203)
    assert (d["SIDEBAND.PACKMODE"], d["SIDEBAND.BIT9"], d["SIDEBAND.MEMLAYOUT"]) == (3, 1, 1)
    assert d["SIDEBAND.BITS8_6"] == 0 and d["SIDEBAND.rest"] == 0
    assert P.decode("SIDEBAND", 0x603)["SIDEBAND.DITHER"] == 1
    d = P.decode("EMIT2", 0x701f8000)
    assert (d["EMIT2.BIT28"], d["EMIT2.BIT29"], d["EMIT2.BIT30"]) == (1, 1, 1)
    assert d["EMIT2.rest"] == 0
    with pytest.raises(P.PbeError):
        P.decode("EMIT9", 0)


def test_the_fields_of_each_word_do_not_overlap():
    for word, fields in P.FIELDS.items():
        seen = 0
        for _name, hi, lo in fields:
            mask = (1 << (hi + 1)) - (1 << lo)
            assert not seen & mask, word
            seen |= mask


def test_a_word_case_masks_then_sets_one_register():
    case = P.word_case(2, 0xffff00ff, 0x8100)
    assert case == ["r2", "0xFFFF00FF", "0x00008100"]
    with pytest.raises(P.PbeError):
        P.word_case(4, 0, 0)


def test_the_fields_follow_the_glossary_rows_of_the_words():
    # the glossary's terms for the PBE words, as 11.5 leaves them
    names = {f"{w}.{n}" for w, fs in P.FIELDS.items() for n, _hi, _lo in fs}
    assert {"EMIT2.BIT28", "EMIT2.BIT29", "EMIT2.BIT30", "SIDEBAND.DITHER"} <= names


def test_the_word_probe_flips_the_bits_free_when_it_ran():
    # the probe ran before bits 28-30 of EMIT2 had names: their flips stay in the table
    labels = P.word_probe()["labels"]
    for b in (28, 29, 30, 31):
        assert f"EMIT2 bit {b}" in labels


def test_the_word_probe_covers_each_field_and_each_free_bit():
    p = P.word_probe()
    labels = p["labels"]
    assert labels[0] == "base" and len(labels) == len(set(labels)) == len(p["cases"])
    # the free bits of EMIT0/EMIT1 (15:13, 31:29), EMIT2 (7:0, 31:28) and EMIT3 (1:0)
    for b in (13, 14, 15, 29, 30, 31):
        assert f"EMIT0 bit {b}" in labels and f"EMIT1 bit {b}" in labels
    for b in list(range(8)) + [28, 29, 30, 31]:
        assert f"EMIT2 bit {b}" in labels
    assert "EMIT3 bit 0" in labels and "EMIT3 bit 1" in labels
    for v in (0x00, 0x01, 0x81, 0xff):
        assert f"EMIT2.BITS15_8 = 0x{v:02x}" in labels
    assert p["slot"] == "eot" and p["host"] == "tri" and p["pixels"]


def test_the_count_probe_sets_every_value_of_bits_15_8():
    p = P.count_probe()
    assert len(p["cases"]) == 256
    assert p["cases"][0x81] == ["r2", "0xFFFF00FF", "0x00008100"]


def test_the_followup_table_repeats_a_subset():
    text = P.tables()["emit-words-followup"]
    assert 'name = "pbe-emit-words-followup"' in text
    assert "pbe-emit-words-followup-fields" in text and "pbe-emit-words-followup-pixev-tri" in text
    assert len(P.count_probe(P.FOLLOWUP_COUNTS)["cases"]) == len(P.FOLLOWUP_COUNTS)


def test_the_tables_are_the_committed_probe_tables():
    for name, text in P.tables().items():
        assert (ROOT / "probes" / "pbe" / f"{name}.toml").read_text() == text, name


def test_tables_parse_as_probe_tables(tmp_path):
    for name, text in P.tables().items():
        f = tmp_path / "probes" / "pbe" / f"{name}.toml"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
        d = tomllib.loads(text)
        assert d["needs"] == ["render"]
        ps = probe.load(f)
        assert ps, name
        assert len({p.name for p in ps}) == len(ps)


def test_the_reg_0400_table_runs_each_bit_in_each_pack_mode():
    ps = P.reg0400_probes()
    assert [p["sideband"] for p in ps] == [0x200, 0x201, 0x202, 0x203]
    for p in ps:
        vals = [c["cmd"][11] for c in p["case_set"]]
        assert vals[0] == P.REG_0400 and P.REG_0400 ^ 1 << 25 in vals
        assert all(P.REG_0400 ^ 1 << b in vals for b in range(12))
        assert 0 in vals and 0xffffffff in vals


def test_the_sideband_table_runs_bits_8_6_in_each_setting():
    ps = P.sideband_probes()
    sbs = {(p["sideband"], tuple(p.get("size", (64, 64))), p.get("cmd", {}).get(13))
           for p in ps}
    for k in range(8):
        assert (0x200 | k << 6, (64, 64), 0x80000001) in sbs
        assert (0x200 | k << 6, (64, 64), 0x80000002) in sbs
        assert (0x200 | k << 6, (128, 128), None) in sbs
        for mode in P.PARTIAL_MODES:
            assert (0x200 | k << 6 | mode, (64, 64), None) in sbs
    for bit in (10, 11, 12):
        assert (0x200 | 1 << bit, (64, 64), None) in sbs


def test_the_dither_table_pairs_each_mode_with_and_without_bit_10():
    sbs = sorted(p["sideband"] for p in P.dither_probes())
    assert sbs == [0x203, 0x204, 0x205, 0x603, 0x604, 0x605]


def test_the_float_table_runs_modes_22_and_34_over_singles():
    ps = P.float_probes()
    assert [p["sideband"] for p in ps] == [0x200, 0x216, 0x222]
    assert all(len(p["cases"]) == len(P.FLOATS) == 10 for p in ps)


def test_correlate_finds_copied_bits_and_constants():
    colours = P.COLOURS
    # R >> 3 in 4:0, G >> 3 in 9:5 and a constant 0x10 in 14:10
    outs = [((c >> 19) & 0x1f) | ((c >> 11) & 0x1f) << 5 | 0x10 << 10 for c in colours]
    fit = P.correlate(colours, outs, width=16)
    assert fit[0] == ("bit", 19) and fit[4] == ("bit", 23)
    assert fit[5] == ("bit", 11) and fit[9] == ("bit", 15)
    assert fit[14] == ("const", 1) and fit[10] == ("const", 0) and fit[15] == ("const", 0)
    fit = P.correlate(colours, [~c & 0xff for c in colours], width=8)
    assert fit[0] == ("not", 0)
    fit = P.correlate(colours, [0, 1, 0, 1, 1, 0, 0, 1, 1, 0], width=1)
    assert fit[0] == ("none", None)
    fit = P.correlate([0, 3, 0, 3], [0, 1, 0, 1], width=1)
    assert fit[0] == ("some", [0, 1])


def test_the_coded_colours_tell_every_bit_apart():
    sig = {b: tuple(c >> b & 1 for c in P.COLOURS) for b in range(32)}
    assert len(set(sig.values())) == 32
    for b, s in sig.items():
        assert len(set(s)) == 2
        assert tuple(1 - x for x in s) not in sig.values()


def test_correlate_text_groups_runs_of_bits():
    fit = {0: ("bit", 19), 1: ("bit", 20), 2: ("bit", 21), 3: ("const", 1), 4: ("none", None)}
    assert P.fit_text(fit) == "2:0 = in 21:19; 3 = 1; 4 = ?"


def _raw(case: str, rows: list[list[int]]) -> str:
    return "".join(f"probe {case}: row {y}: " + " ".join(f"0x{v:08x}" for v in r) + "\n"
                   for y, r in enumerate(rows))


def test_effect_names_a_shift_a_clip_and_a_change():
    base = [[0x10 * y + x for x in range(4)] for y in range(4)]
    s = 0xdeadbeef
    shifted = [[s] + r[:3] for r in base]
    clipped = [r if y < 2 else [s] * 4 for y, r in enumerate(base)]
    raw = _raw("p__0", base) + _raw("p__1", shifted) + _raw("p__2", clipped) + \
        _raw("p__3", base) + "probe p__4: failed: job hung\n"
    out = P.effects(raw, "p", ["base", "a", "b", "c", "d"])
    assert out["a"] == "moved (1, 0)"
    assert out["b"] == "written box x 0-3 y 0-1 (8 of 16), rest unwritten"
    assert out["c"] == "same"
    assert out["d"] == "failed: job hung"


def test_the_triangle_is_where_the_plain_image_is_not_the_background():
    bg = P.pixels.BG
    assert P.triangle([bg, 7, bg, 7, 7]) == [1, 3, 4]


def test_at_splits_the_dwords_of_16_and_8_bit_modes():
    img = [0x22221111, 0x44443333, 0xdeadbeef, 0xdeadbeef]
    assert P.at(img, [0, 1, 3], 32) == [0x22221111, 0x44443333, 0xdeadbeef]
    assert P.at(img, [0, 1, 2, 3], 16) == [0x1111, 0x2222, 0x3333, 0x4444]
    assert P.at(img, [0, 1, 5], 8) == [0x11, 0x11, 0x33]
    with pytest.raises(P.PbeError):
        P.pixel_bits(9)


def test_correlate_reads_the_stored_pixels_at_the_triangle(tmp_path):
    # a 4x4 target, 16-bit pack mode 26: the triangle is pixels 5 and 6 of the plain image;
    # each case stores R >> 3 there and the background pair elsewhere
    bg = P.pixels.BG
    plain = [bg] * 16
    plain[5] = plain[6] = 0x80ff8040
    (tmp_path / "base.txt").write_text(_raw("p0__0", [plain[i:i + 4] for i in (0, 4, 8, 12)]))
    raw = ""
    for i, c in enumerate(P.CODED):
        px = [0x40c4] * 16
        px[5] = px[6] = c >> 19 & 0x1f
        dw = [px[2 * j] | px[2 * j + 1] << 16 for j in range(8)] + [P.SENTINEL] * 8
        raw += _raw(f"p__{i}", [dw[k:k + 4] for k in (0, 4, 8, 12)])
    (tmp_path / "raw.txt").write_text(raw)
    table = tmp_path / "t.toml"
    table.write_text("[[probe]]\nname = \"p\"\nsideband = 0x21a\ncases = [" + ", ".join(
        f'["mov.skipinv.end o0, #0x{c:08X}"]' for c in P.CODED) + "]\n")
    out = P.correlate_run((tmp_path / "raw.txt").read_text(), "p", table,
                          (tmp_path / "base.txt").read_text())
    assert out["cases"][0] == (P.CODED[0], P.CODED[0] >> 19 & 0x1f, 2, 2)
    assert P.fit_text(out["fit"]) == "4:0 = in 23:19; 15:5 = 0"


@pytest.mark.skipif(not PACK.is_dir(), reason="resgx545-data not present")
def test_correlate_on_the_pack_colours_run(capsys):
    """E270: by position, mode 26 stores R >> 3, G >> 3 and B >> 2 at the triangle; no stored
    bit of modes 22 and 34 copies a bit of o0."""
    base = str(PACK / "pbe-pack-colours-mode0" / "raw.txt")

    def run(mode):
        P.main(["correlate", str(PACK / f"pbe-pack-colours-mode{mode}" / "raw.txt"),
                f"pbe-pack-colours-mode{mode}", str(ROOT / "probes" / "pbe" / "pack-colours.toml"),
                base])
        return capsys.readouterr().out
    out = run(26)
    assert "o0 0x80ff8040: commonest at the triangle 0x0000421f (1062 of 1062)" in out
    assert out.splitlines()[-1] == "fit: 4:0 = in 23:19; 9:5 = in 15:11; 15:10 = in 7:2"
    out = run(22)
    assert "o0 0x55555555: commonest at the triangle 0xfff00088 (727 of 1062)" in out
    assert "in " not in out.splitlines()[-1]
    out = run(34)
    assert "o0 0x7f807f80: commonest at the triangle 0x608007f9 (727 of 1062)" in out
    assert "in " not in out.splitlines()[-1]


# ---- 11.14: the pixel-naming shader and the batch-2 tables (Q012, Q040, Q044, Q046, Q074) ----

PBE_TEMPLATES = ROOT / "probes" / "pbe" / "templates"


def test_xy_word_names_each_pixel_and_xy_of_reads_it_back():
    words = {P.xy_word(x, y) for x in range(64) for y in range(64)}
    assert len(words) == 4096
    assert P.xy_word(0, 0) == 0x3f003f00                 # 0.5 and 0.5
    assert P.xy_of(P.xy_word(37, 5)) == (37, 5)
    assert P.xy_of(0xff203040) is None                   # the background names no pixel


def test_place_map_finds_a_mirror_and_an_offset():
    w, h = 8, 4
    plain = [P.xy_word(x, y) for y in range(h) for x in range(w)]
    mirror = [P.xy_word(w - 1 - x, y) for y in range(h) for x in range(w)]
    assert P.place_fit(mirror, w, h) == "x' = 7 - x, y' = y (32 of 32 pixels)"
    shifted = [P.xy_word(min(x + 2, w - 1), y) for y in range(h) for x in range(w)]
    assert P.place_fit(shifted, w, h).startswith("x' = x - 2, y' = y")
    assert P.place_fit(plain, w, h) == "x' = x, y' = y (32 of 32 pixels)"


def test_the_1114_tables_parse_and_every_case_assembles(tmp_path):
    ts = P.tables_1114()
    assert set(ts) == {"emit-transforms", "pack-floats-channels", "pack-floats-ramps",
                       "sideband-channels",
                       "reg-0400-alpha", "emit-twice"}
    for feature, text in ts.items():
        assert all(line.rstrip() == line for line in text.splitlines())
        path = tmp_path / f"{feature}.toml"
        path.write_text(text)
        for p in probe.load(path):
            assert p.name.startswith(f"pbe-{feature}-"), p.name
            assert len(p.cases) == len(p.labels)
            probe.build(p, tmp_path / "bins", PBE_TEMPLATES)


def test_the_transform_table_runs_bits_31_28_and_6_0_twice_with_the_xy_shader():
    p = P.transform_probe()
    assert p["slots"]["pixel"] == "pix_xy.s" and p["slots"]["pixpds"] == "pds_iter_xy.s"
    labels = p["labels"]
    assert sum(lab.endswith("EMIT2 bits 31:28 = 0x5") for lab in labels) == 2
    counts = [int(lab.rsplit("0x", 1)[1], 16) for lab in labels if "bits 15:8" in lab]
    assert counts and all(c % 2 == 0 and c > 0x80 for c in counts)   # odd counts hang (E266)
