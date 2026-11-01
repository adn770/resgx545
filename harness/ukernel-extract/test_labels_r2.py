# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Checks on sgx545_labels.r2, the hand-written radare2 labels and comments for the ukernel.

radare2 parses `;`, `|`, `>` and `~` in a script line as command separators, pipes,
redirections and filters, so an unquoted comment such as `CCu a -> b @ 0x10` writes a file
named `b @ 0x10`. Comments are therefore written as `"CCu text" @ 0xADDR`: the quotes keep
the text literal and the temporary seek stays outside them."""
import pathlib
import re

import pytest

HERE = pathlib.Path(__file__).resolve().parent
LABELS = HERE / "sgx545_labels.r2"

FLAG = re.compile(r'^f ([A-Za-z_][\w.]*) @ 0x([0-9a-f]+)$')
COMMENT = re.compile(r'^"CCu ([^"]+)" @ 0x([0-9a-f]+)$')


def lines():
    return [ln for ln in LABELS.read_text().splitlines() if ln.strip()]


def test_every_line_is_a_flag_or_a_quoted_comment():
    bad = [ln for ln in lines() if not (FLAG.match(ln) or COMMENT.match(ln))]
    assert bad == []


def test_addresses_are_instruction_aligned():
    for ln in lines():
        m = FLAG.match(ln) or COMMENT.match(ln)
        assert int(m.group(2), 16) % 8 == 0, ln


def test_flag_names_and_addresses_are_unique():
    flags = [FLAG.match(ln).groups() for ln in lines() if FLAG.match(ln)]
    names = [n for n, _ in flags]
    addrs = [a for _, a in flags]
    assert len(set(names)) == len(names)
    assert len(set(addrs)) == len(addrs)


# --- names ---------------------------------------------------------------------------------

def comments():
    return [(m.group(2), m.group(1)) for ln in lines() if (m := COMMENT.match(ln))]


# Names the comments once used that the records replaced: old structure and field names, the
# register block name that read the 3D patches as register writes (they are memory writes,
# E158), and any Hungarian or CamelCase client name, caught by its shape and not listed. Each
# old name matches as a whole name: "rd." is not the end of "word.".
STALE = re.compile(r"\b(?:CMDTA|hw_3d_registers|spec_object|regs_3d|PB desc)\b|\b(?:rd|ctx)\.")
HUNGARIAN = re.compile(r"\b(?:ui\d+|p?s[A-Z]|h[A-Z])\w*")
CAMEL = re.compile(r"\b\w*(?:[A-Z]{2}[a-z]|[a-z][A-Z])\w*")
HEX = re.compile(r"^0x[0-9A-Fa-f]+$")
SHAPE_OK = {"HWPerf"}         # the HWPerf buffer, as the records spell it


def stale_names(text: str) -> list[str]:
    """The replaced names a comment uses, each once."""
    out = [m.group(0) for m in STALE.finditer(text)]
    out += [m.group(0) for m in HUNGARIAN.finditer(text)]
    out += [w for m in CAMEL.finditer(text)
            if not HEX.match(w := m.group(0)) and w not in SHAPE_OK]
    return list(dict.fromkeys(out))


def test_stale_names_match_whole_names_and_shapes():
    assert stale_names("the third word. ctx. rd.state") == ["ctx.", "rd."]
    assert stale_names("CMDTA+0x10, CMDTA_SHARED") == ["CMDTA"]
    assert stale_names("TA3DCtl HostCtl TACount ui32Flags sPDDevPAddr hTA") == [
        "ui32Flags", "sPDDevPAddr", "hTA", "TA3DCtl", "HostCtl", "TACount"]
    assert stale_names("HWPerf buffer at 0xAD002600, sa15, pa1") == []


def test_no_comment_uses_a_replaced_name():
    bad = [(a, n) for a, t in comments() for n in stale_names(t)]
    assert bad == []


def test_the_3d_patches_are_memory_writes():
    (text,) = [t for a, t in comments() if a == "3d88"]
    assert "cmd_ta.patches_3d" in text and "memory writes" in text


FIELD = re.compile(r"\b([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)\b")
FLAGBIT = re.compile(r"\b([A-Z][A-Z0-9_]*)\.([A-Z][A-Z0-9_]*)\b")


def known_names():
    """The glossary's terms and kick3d.py's fields and flag bits."""
    import sys
    sys.path.insert(0, str(HERE.parent.parent / "tools" / "clean-room"))
    import glossary
    import kick3d
    names = {r["name"] for r in glossary.load(HERE.parent.parent / "glossary")}
    for layout, fields in kick3d.STRUCTS.items():
        names |= {f"{layout}.{p.split('.')[0]}" for p, *_ in kick3d._layout(fields)}
    for table, bits in kick3d.FLAGS.items():
        names |= {f"{table}.{b}" for b in bits.values()}
    return names


def unknown_names(text: str, known: set[str], labels: set[str]) -> list[str]:
    """The dotted names of a comment that are neither the glossary's or kick3d.py's names
    (known) nor a label or the start of one (edm.request, edm.ta)."""
    return [name for m in (*FIELD.finditer(text), *FLAGBIT.finditer(text))
            if (name := m.group(0)) not in known
            and not any(lb.startswith(name) for lb in labels)]


def test_a_made_up_or_unprefixed_head_is_unknown():
    known = {"CR_SOFT_RESET.TA_RESET", "cmd_ta.size", "GEOM_FLAGS.FIRST_KICK"}
    labels = {"edm.ta.pick", "edm.request"}
    assert unknown_names("CMD_TA_CTRL_FLAGS.READY, SOFT_RESET.TA_RESET, cmd_ta.sizes",
                         known, labels) == ["cmd_ta.sizes", "CMD_TA_CTRL_FLAGS.READY",
                                            "SOFT_RESET.TA_RESET"]
    assert unknown_names("CR_SOFT_RESET.TA_RESET; edm.ta.pick, edm.request(0x20000), "
                         "cmd_ta.size", known, labels) == []


@pytest.mark.skipif(not (HERE.parent.parent / "glossary").is_dir(), reason="needs the glossary")
def test_structure_and_flag_names_are_the_glossarys_or_kick3ds():
    """Every dotted name is the glossary's or kick3d.py's, or a label's (edm.ta.pick), so a
    made-up structure or flag table fails as well as a made-up field."""
    known = known_names()
    labels = {FLAG.match(ln).group(1) for ln in lines() if FLAG.match(ln)}
    bad = [(a, n) for a, t in comments() for n in unknown_names(t, known, labels)]
    assert bad == []
