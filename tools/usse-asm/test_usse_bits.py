# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""usse_bits.py: the USSE encoding-bit and encoding-gap tables and their reading."""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import probe  # noqa: E402
import usse_bits  # noqa: E402


def fake(monkeypatch):
    """One form (7) with bits 1 and 3 unmapped; flipping bit 3 decodes to form 9."""
    fs = [{"index": 7, "pat": "x{0}", "mask": 0xF0, "val": 0x10, "unmapped": 0b1010},
          {"index": 9, "pat": "y", "mask": 0xF0, "val": 0x20, "unmapped": 0}]
    monkeypatch.setattr(usse_bits, "BASES", (usse_bits.Base("x", "x r10"),))
    enc = lambda t: {"word": "0000000000000100", "form": 7}  # noqa: E731
    dec = lambda w: 9 if w & 8 else 7  # noqa: E731
    return fs, enc, dec


def test_a_probe_flips_each_unmapped_bit_that_keeps_the_form(monkeypatch):
    fs, enc, dec = fake(monkeypatch)
    (p,) = usse_bits.probes("data", fs, dec, enc)
    assert p["name"] == "usse-encoding-bits-x"
    assert p["labels"] == ["base", "bit 1"]          # bit 3 decodes to form 9: left out
    assert p["cases"][0][0] == ".long 0x0000000000000100 ; base: x r10"
    assert p["cases"][1][0] == ".long 0x0000000000000102 ; bit 1"
    assert p["cases"][1][1:] == [f"0x{usse_bits.INPUTS[k]:08X}" for k in "ABCDEFGH"]
    assert p["source"] == "dump.s" and p["params"] == {"OUT": "r10"}
    assert usse_bits.probes("state", fs, dec, enc) == []


def test_the_lines_around_a_base_stay(monkeypatch):
    fs, enc, dec = fake(monkeypatch)
    monkeypatch.setattr(usse_bits, "BASES",
                        (usse_bits.Base("x", "x r10", setup=("mov r1, #0",), after=("wdf drc0",)),))
    (p,) = usse_bits.probes(None, fs, dec, enc)
    assert p["cases"][1][0] == "mov r1, #0\n.long 0x0000000000000102 ; bit 1\nwdf drc0"


def test_the_tables_load_as_campaign_tables(tmp_path, monkeypatch):
    fs, enc, dec = fake(monkeypatch)
    text = usse_bits.table_text(usse_bits.probes(None, fs, dec, enc))
    (tmp_path / "encoding-bits.toml").write_text(text)
    (p,) = probe.load(tmp_path / "encoding-bits.toml")
    assert p.name == "usse-encoding-bits-x" and len(p.cases) == 2 and p.temps == 32
    assert text.startswith("# SPDX-License-Identifier: MIT\n")


def test_every_base_reaches_a_form_with_unmapped_bits():
    """The real tables (formdump): each base decodes to a form that has bits to flip, the
    names are unique, and no base of a group flips bits of a form another base of it covers
    (a follow-up group runs a form again)."""
    fs = {f["index"]: f for f in usse_bits.forms()}
    names, reached = set(), {}
    for b in usse_bits.BASES:
        e = usse_bits._encode(b.test)
        assert fs[e["form"]]["unmapped"], b
        assert b.name not in names
        key = (b.group, e["form"])
        assert key not in reached, (b, reached.get(key))
        names.add(b.name)
        reached[key] = b.name
        assert b.group in usse_bits.GROUPS and b.group != "gaps"


def test_gap_words_match_no_form_s_mask():
    fs = usse_bits.forms()
    words = usse_bits.gap_words(fs, per=2)
    assert sorted(words) == list(usse_bits.GAP_CLASSES)
    for cls, ws in words.items():
        assert len(ws) == 2
        for w in ws:
            assert w >> 59 == cls and usse_bits.no_form(w, fs) and usse_bits.decode(w) is None
    # seeded: the same words every time
    assert usse_bits.gap_words(fs, per=2) == words


def test_a_reserved_field_value_is_not_a_gap():
    # bilin's mask and value with format 3 (enc[41:40]): the decoder rejects it, but it is
    # bilin's word, and flipping bit 40 or 41 decodes it as bilin (E297)
    w = 0xB7ECF778F9B27E62
    fs = usse_bits.forms()
    assert usse_bits.decode(w) is None and not usse_bits.no_form(w, fs)
    assert usse_bits.decode(w ^ 1 << 40) == usse_bits.decode(w ^ 1 << 41) == 216
    # the 11.7 run's table took the decoder's rule, and so this word first in class 22
    assert usse_bits.gap_words(by_decoder=True)[22][0] == w
    assert w not in usse_bits.gap_words(fs)[22]
    # the rules differ only where a form's mask matches
    fake = [{"mask": 0xF0, "val": 0x10}]
    assert usse_bits.no_form(0x20, fake) and not usse_bits.no_form(0x13, fake)


def test_a_gap_probe_starts_with_a_nop():
    (p,) = usse_bits.gap_probes({2: [0x1000000000000005]})
    assert p["name"] == "usse-encoding-gaps-class2"
    assert p["cases"][0][0] == "nop"
    assert p["cases"][1][0] == ".long 0x1000000000000005 ; class 2 word"


def test_classify_against_the_base():
    raw = """probe t__0: o0 0x00000001 (2048 of 2048)
probe t__0: scratch +0x000 0x00000001
probe t__1: o0 0x00000001 (2048 of 2048)
probe t__1: scratch +0x000 0x00000001
probe t__2: o0 0x00000002 (2048 of 2048)
probe t__2: scratch +0x000 0x00000002
probe t__3: failed: job hung
"""
    got = usse_bits.classify("t", ["base", "bit 1", "bit 2", "bit 3", "bit 4"], probe.parse(raw))
    assert got[0] == ("bit 1", "same")
    assert got[1][1].startswith("differs: o0 1 -> 2; +0x000 0x00000001 -> 0x00000002")
    assert got[2] == ("bit 3", "failed: job hung")
    assert got[3] == ("bit 4", "not run")


def test_the_committed_tables_are_what_the_generator_writes():
    """probes/usse/encoding-*.toml as run: the generator writes them again byte for byte (the
    gaps table by the decoder's rule, as the 11.7 run took it)."""
    tables = HERE.parents[1] / "probes" / "usse"
    for group, name in usse_bits.GROUPS.items():
        path = tables / f"{name}.toml"
        ps = usse_bits.gap_probes(usse_bits.gap_words(by_decoder=True)) if group == "gaps" else \
            usse_bits.probes(group)
        what = "encoding gaps" if group == "gaps" else "encoding bits"
        assert usse_bits.table_text(ps, what) == path.read_text(), name
