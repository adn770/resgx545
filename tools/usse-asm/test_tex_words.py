# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The texture word tools (tex_words.py): T0-T3 by glossary name, the mip-field and fetch-size
tables, the copy's source and colour-space models, and the luma-key cut-point fitter."""
from __future__ import annotations

import os
import pathlib

import pytest

import probe
import tex_words as T

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
CUTS = DATA / "texture" / "luma-cuts" / "output.txt"
LUMA = (0x02020106, 0x00210064, 0xff008000)


def test_decode_names_the_fields_of_each_word():
    d = T.decode("T1", 0xcc03f01f)
    assert d["T1.TEXTYPE"] == 6 and d["T1.TEXFORMAT"] == 12
    assert d["T1.WIDTH"] == 63 and d["T1.HEIGHT"] == 31 and d["T1.rest"] == 0
    d = T.decode("T0", 0x07fa0000)
    assert d["T0.BITS26_21"] == 0x3f and d["T0.MAX_LEVEL"] == 0xd and d["T0.rest"] == 0
    assert T.decode("T0", 1 << 27)["T0.BIT27"] == 1
    d = T.decode("T0", 0x080e0e00, strided=True)
    assert d["T0.STRIDE"] == 63 and d["T0.BIT27"] == 1 and d["T0.rest"] == 0
    assert "T0.MINFILTER" not in d and "T0.MAX_LEVEL" not in d
    d = T.decode("T3", 0xa0800000)
    assert d["T3.CMP_MODE"] == 5 and d["T3.DATA_SIZE"] == 1 and d["T3.rest"] == 0
    d = T.decode("T3", 0x180c44f3)
    assert (d["T3.BITS28_27"], d["T3.BITS19_18"], d["T3.BIT14"], d["T3.BIT10"],
            d["T3.BITS7_0"]) == (3, 3, 1, 1, 0xf3)
    assert d["T3.rest"] == 0
    with pytest.raises(T.TexError):
        T.decode("T4", 0)


def test_the_fields_follow_the_glossary_rows_of_the_words():
    # the glossary's terms for T0 and T3 as 11.5 leaves them; T0.MAX_LEVEL holds the older
    # rows T0.BITS20_19 and T0.NO_MIPMAPS, which decode() does not split out
    names = {f"{w}.{n}" for w, fs in T.FIELDS.items() for n, _hi, _lo in fs}
    assert {"T0.MAX_LEVEL", "T0.BIT27", "T3.BITS7_0", "T3.BIT10", "T3.BIT14",
            "T3.BITS19_18", "T3.BITS28_27"} <= names
    assert not {"T0.BITS20_19", "T0.NO_MIPMAPS"} & names
    for word, fields in list(T.FIELDS.items()) + [("T0", T.STRIDED_T0)]:
        seen = 0
        for _name, hi, lo in fields:
            assert not seen & T._mask(hi, lo), word
            seen |= T._mask(hi, lo)


def test_the_tables_are_the_committed_probe_tables():
    for name, text in T.tables().items():
        assert (ROOT / "probes" / "texture" / f"{name}.toml").read_text() == text, name
    assert (ROOT / "probes" / "texture" / "templates" / T.MIP_TEMPLATE).read_text() == \
        T.mip_template()
    assert (ROOT / "probes" / "texture" / "templates" / T.MIP8_TEMPLATE).read_text() == \
        T.mip8_template()


def test_the_copy_words_follow_the_library():
    assert T.copy_words(64, 32, 0x2000, 256) == [0x000e0e00, 0xcc03f01f, 0x2000, 0xa0800000]
    assert T.decode("T0", T.copy_words(64, 32, 0, 256)[0], strided=True)["T0.STRIDE"] == 63


def test_the_sources_follow_sgxfive_test():
    assert T.source(0, 0, 64) == 0xa5000000
    assert T.source(3, 2, 64) == 0xa5020301
    assert T.source(0, 0, 64, every=True) == 0x000d6539
    assert T.source(1, 0, 64, every=True) >> 24 == 1


def test_csc_matches_e037_bt601():
    # Y 16, U = V = 128: black; Y 235: white
    assert T.csc(16, 128, 128, T.BT601) == (0, 0, 0)
    assert T.csc(235, 128, 128, T.BT601) == (254, 254, 254)
    assert T.csc(81, 90, 255, T.BT601)[0] == 255


def test_yuyv_image_reads_two_byte_texels_at_a_stride():
    src = bytes(range(256)) * 4
    img = T.yuv_image(src, 2, 1, 128, "YUYV", T.BT601)
    y0, u, y1, v = src[0], src[1], src[2], src[3]
    assert img[0] == 0xff000000 | T.pack(T.csc(y0, u, v, T.BT601))
    assert img[1] == 0xff000000 | T.pack(T.csc(y1, u, v, T.BT601))
    img = T.yuv_image(src, 2, 2, 128, "UYVY", T.BT601)
    assert img[2] == 0xff000000 | T.pack(T.csc(src[129], src[128], src[130], T.BT601))


def test_luma_sums_the_weighted_channels():
    words = (0x02020106, 0x00210064, 0xff008000)
    k = T.Band.of(words)
    assert (k.wr, k.wg, k.wb, k.offset, k.threshold, k.below, k.above) == \
        (262, 514, 100, 0x21, 0x80, 0, 0xff)
    assert k.low == 0
    assert k.luma(0, 0, 0) == (512 * 0x21) >> 10
    assert k.alpha(255, 255, 255) == 0xff and k.alpha(0, 0, 0) == 0


def test_the_band_takes_alpha_below_from_the_low_byte_to_the_threshold():
    k = T.Band.of((0x02020106, 0x00210064, 0xff008040))       # low 64, threshold 128
    assert k.low == 64
    # grey v: S = 876 v + 512 x 33; luma 63 for v = 55, 64 for v = 56, 129 for v = 132
    assert k.sum(55, 55, 55) == 876 * 55 + 512 * 33
    assert k.luma(55, 55, 55) == 63 and k.alpha(55, 55, 55) == 0xff
    assert k.luma(56, 56, 56) == 64 and k.alpha(56, 56, 56) == 0
    assert k.luma(132, 132, 132) == 129 and k.alpha(132, 132, 132) == 0xff
    # the low cut read as (S + r) >> 10: black (S = 16896, luma 16) reaches 17 at r = 1024
    lo = T.Band.of((0x02020106, 0x00210064, 0xff008011))      # low 17
    assert lo.alpha(0, 0, 0) == 0xff and lo.alpha(0, 0, 0, round_low=1024) == 0


def test_band_misfits_counts_the_pixels_the_band_does_not_give():
    text = ("#### low 64 threshold 128\nrow 0: 0xff363636 0x00383838 0xff848484\n"
            "#### low 64 threshold 0\nrow 0: 0xff363636 0xff383838\n"
            "#### low 64 threshold 128 (a misfit)\nrow 0: 0x00363636\n")
    out = T.band_misfits(text, LUMA, 0)
    assert out == {"low 64 threshold 128": 0, "low 64 threshold 0": 0,
                   "low 64 threshold 128 (a misfit)": 1}


@pytest.mark.skipif(not CUTS.is_file(), reason="resgx545-data not present")
def test_the_band_fits_the_luma_cuts_run():
    """E275: with the low cut read as (S + r) >> 10, r from 12 to 35, every pixel of 272 of
    the 274 copies; at low 119 and 122, 8 pixels each, S = low x 1024 + 4."""
    text = CUTS.read_text()
    for r in (12, 20, 35):
        bad = {k: n for k, n in T.band_misfits(text, LUMA, r).items() if n}
        assert bad == {"low 119 threshold 128": 8, "low 122 threshold 128": 8}, r
    assert len(T.band_misfits(text, LUMA, 20)) == 274
    assert "low 33 threshold 128" in {k for k, n in T.band_misfits(text, LUMA, 11).items() if n}
    assert "low 76 threshold 128" in {k for k, n in T.band_misfits(text, LUMA, 36).items() if n}


def test_cuts_finds_the_threshold_of_a_monotone_image():
    k = T.Band.of((0x02020106, 0x00210064, 0xff008000))
    pix = []
    for v in range(0, 256, 3):
        a = k.alpha(v, v, v)
        pix.append(a << 24 | v << 16 | v << 8 | v)
    cut = T.cuts(pix, k)
    assert cut["monotone"] and cut["below"] == 0 and cut["above"] == 0xff
    assert cut["last_below"] < cut["first_above"]
    assert cut["first_above"] - 1 <= k.threshold + 1


def test_cuts_reports_alphas_by_luma_interval_when_not_monotone():
    k = T.Band.of((0x02020106, 0x00210064, 0xff008000))
    pix = [(0xff if 40 <= v < 80 else 0) << 24 | v << 16 | v << 8 | v for v in range(256)]
    cut = T.cuts(pix, k)
    assert not cut["monotone"]
    assert [a for a, _lo, _hi in cut["runs"] if a is not None] == [0, 0xff, 0]


def test_sections_split_a_script_output():
    text = ("#### one\nrow 0: 0x00000001 0x00000002\nrow 1: 0x00000003 0x00000004\n## exit 0\n"
            "#### two\njob: failed: job hung\n## exit 1\n")
    s = T.sections(text)
    assert s["one"] == [1, 2, 3, 4] and s["two"] == []


def test_the_mip_probes_vary_t0_and_lod(tmp_path):
    ps = T.mip_probes()
    by = {p["name"]: p for p in ps}
    p = by["texture-mip-fields-bits20-17"]
    assert len(p["cases"]) == 16 * len(T.LODS)
    assert [0x07e00000, 0x40000000] in p["cases"]              # 20:17 = 0, LOD 2.0
    assert p["source"] == T.MIP_TEMPLATE and p["inputs"] == ["T0", "LOD"]
    p = by["texture-mip-fields-bits26-21"]
    assert len(p["cases"]) == 64 * 2
    f = tmp_path / "probes" / "texture" / "mip-fields.toml"
    f.parent.mkdir(parents=True)
    f.write_text(T.table_text("mip fields", "x", ps))
    assert len(probe.load(f)) == 2
    text = T.mip_template()
    assert "mov r20, #{T0}" in text and "mov r26, #{LOD}" in text and "{OP}" not in text
    assert text.count("smp2dreplace r10") == 1 and "stad [r30,+#84], r31" in text


def test_the_fetch_probes_put_the_field_at_8_and_15(tmp_path):
    ps = T.fetch_probes()
    for p in ps:
        assert p["source"] == "pds_tex2.s"
    fields = {(c[2] >> 23) & 0xf for p in ps for c in p["cases"]}
    assert {1, 8, 15} <= fields
    f = tmp_path / "probes" / "texture" / "fetch-size.toml"
    f.parent.mkdir(parents=True)
    f.write_text(T.table_text("fetch size", "x", ps))
    assert len(probe.load(f)) == len(ps)


def test_the_eight_level_chain_names_each_texel_by_its_scratch_dword():
    # a 128x128 twiddled chain in the scratch buffer from its start: the host fills dword i with
    # 0xD0000000 | i, so a texel read names the level and the place it came from (x in the even
    # bits of the twiddle, y in the odd)
    offs = T.mip_offsets(128)
    assert offs == [0, 16384, 20480, 21504, 21760, 21824, 21840, 21844] and T.mip_dwords(128) == 21845
    assert T.mip_offsets(16) == [0, 256, 320, 336, 340] and T.mip_offsets(1) == [0]
    assert T.twiddle(0, 0) == 0 and T.twiddle(1, 0) == 1 and T.twiddle(0, 1) == 2
    assert T.twiddle(2, 0) == 4 and T.twiddle(0, 2) == 8 and T.twiddle(127, 127) == 16383
    assert T.mip_texel(128, 0, 0, 0) == 0xd0000000
    assert T.mip_texel(128, 1, 1, 1) == 0xd0000000 | 16384 + 3
    assert T.mip_texel(128, 7, 0, 0) == 0xd0000000 | 21844
    for lv in range(8):
        for x, y in ((0, 0), (max(0, (128 >> lv) - 1),) * 2, (28 >> lv, 84 >> lv)):
            assert T.mip_of(128, T.mip_texel(128, lv, x, y)) == (lv, x, y)
    assert T.mip_of(128, 0xd0000000 | 21845) is None and T.mip_of(128, 0xa0000000) is None
    with pytest.raises(T.TexError):
        T.mip_offsets(100)


def test_the_sampled_texel_follows_the_coordinates_and_the_level():
    # the template's coordinates r24 = 0.21875 (the y) and r25 = 0.65625 (the x) at level l of a
    # 128-wide chain
    assert T.mip_sample(128, 0) == (84, 28) and T.mip_sample(128, 3) == (10, 3)
    assert T.mip_sample(128, 4) == (5, 1) and T.mip_sample(128, 7) == (0, 0)
    assert T.mip_read(128, 2) == T.mip_texel(128, 2, 21, 7)


def test_the_linear_level_blend_is_a_channel_wise_lerp():
    a, b = 0xd0102030, 0xd0305070
    assert T.mip_blend(a, b, 0.0) == a and T.mip_blend(a, b, 1.0) == b
    assert T.mip_blend(a, b, 0.5) == 0xd0203850
    assert T.mip_blend(a, b, 0.25) == 0xd0182c40


def test_the_eight_level_probes_read_the_chain(tmp_path):
    ps = {p["name"]: p for p in T.mip8_probes()}
    assert set(ps) == {"texture-mip8-fields-max-level", "texture-mip8-fields-bias", "texture-mip8-fields-mipfilter"}
    p = ps["texture-mip8-fields-max-level"]
    # all 16 values of bits 20:17 at LODs inside the chain (1, 3, 5, 7) and beyond it (8, 9)
    assert len(p["cases"]) == 16 * 6 and [0x07e00000 | 15 << 17, _f(7.0)] in p["cases"]
    assert [0x07e00000, _f(9.0)] in p["cases"]
    p = ps["texture-mip8-fields-bias"]
    assert len(p["cases"]) == 64 * 2 and p["scratch_pages"] == 24
    assert [0 << 21 | 0xe << 17, _f(7.0)] in p["cases"] and [63 << 21 | 0xe << 17, _f(5.0)] in p["cases"]
    p = ps["texture-mip8-fields-mipfilter"]
    assert all(c[0] & 0x200 for c in p["cases"]) and len(p["cases"]) == 3 * 5 * 3
    assert all(q["source"] == T.MIP8_TEMPLATE and q["scratch_pages"] == 24 for q in ps.values())
    text = T.mip8_template()
    assert "mov r20, #{T0}" in text and "mov r26, #{LOD}" in text and "stad [r30" not in text
    assert "mov r21, #0x0C07F07F" in text and text.count("smp2dreplace r10") == 1
    f = tmp_path / "probes" / "texture" / "mip8-fields.toml"
    f.parent.mkdir(parents=True)
    f.write_text(T.table_text("mip8 fields", "x", list(ps.values())))
    assert len(probe.load(f)) == 3


def _f(v):
    return T._f32(v)
