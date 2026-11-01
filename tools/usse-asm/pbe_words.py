#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The PBE words of the end-of-tile emit: their fields by glossary name, the probe tables that
vary them on the laptop, and readers of what the runs stored.

The end-of-tile program hands the pixel back end four words and a sideband (asm/transfer/
use_eot.s): EMIT0 and EMIT1 (emitpix1's sources) and EMIT2 and EMIT3 (emitpix2's), then the
sideband immediate. FIELDS names each word's fields as the glossary does; decode() splits a
word into them and keeps the bits outside every field as `<WORD>.rest`.

The tables (probes/pbe/, all on the triangle job, every pixel read back):

  emit-words       eot_words.s in the end-of-tile slot: after the four movs that load the
                   words into r0-r3, `REG = REG & AND | OR` on one register per case; each
                   field set to other values and each bit outside a field flipped; and every
                   value of EMIT2 bits 15:8 (a probe of its own). With them, the fill's, the
                   copy's and the triangle's pixel-event data dword 8 (sweeps): the dword E046's
                   EMIT2 table varied.
  emit-words-followup  emit-words again: the fields, twelve values of bits 15:8, dword 8.
  reg-0400-modes   the render command's word 11 (it loads CR_REG_0400) with bit 25 and each of
                   bits 11:0 flipped, 0 and 0xffffffff, under pack modes 0 to 3.
  sideband-fields  SIDEBAND bits 8:6 at 0 to 7 under CR_ISP_MSAA modes 1 and 2, in the pack
                   modes that store part of a colour, on a 128x128 target; bits 10 to 12.
  sideband-dither  SIDEBAND bit 10 clear and set in pack modes 3, 4 and 5, three colours.
  pack-colours     pack modes 0, 22, 26 and 34 over a set of shader colours, for the
                   byte-field correlator.
  pack-floats      pack modes 0, 22 and 34 over ten IEEE singles.

The 11.14 tables (tables_1114, `table --phase 11.14`), with the pixel-naming shader pix_xy.s
(pds_iter_xy.s iterates each pixel's x + 0.5 and y + 0.5 into pa0 and pa1; o0 = xy_word):

  emit-transforms      EMIT2 bits 31:28 at each of their 16 values, bits 6:0 at nine values
                       and even counts above 0x80 in bits 15:8, twice each (Q040).
  pack-floats-channels pack modes 22 and 34 (and 0) with o0-o3 four singles, each alone, and
                       the pixel's x and y in o0 and o1 (Q012).
  sideband-channels    SIDEBAND bits 8:6 at 0-7 in pack modes 7, 8, 15, 18, 24, 25 and 28, two
                       colours whose bytes all differ; bits 11 and 12 in pack modes 0-8 (Q046).
  reg-0400-alpha       CR_REG_0400's word (render command word 11) with an alpha that varies
                       over x, in pack modes 0 and 4, and bit 25 in modes 4, 5 and 8 (Q044).
  emit-twice           two end-of-tile emits per tile, bit 9 on one of them, each followed by
                       jobs that store nothing (EMIT2 count 0) (Q074).

place_fit reads where each stored word of a pix_xy.s image came from, as x' and y' of x, y.

The correlator reads each case's pixels where the plain image (a pack mode 0 run of the same
triangle, BASE) holds the triangle (E031's 1062 pixels), splitting the dwords of the 16- and
8-bit modes into their pixels, and fits each bit of the commonest value there against o0.

    pbe_words.py decode WORD VALUE        the fields of one word (EMIT0-3, SIDEBAND)
    pbe_words.py table DIR [--phase 11.14] write the tables into DIR (probes/pbe/)
    pbe_words.py place RAW PROBE TABLE    each case of a pix_xy.s run: where its pixels came from
    pbe_words.py effects RAW PROBE TABLE  each case of a saved run against case 0
    pbe_words.py correlate RAW PROBE TABLE BASE  per pack mode, each bit stored at the
                                          triangle against o0's bits
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import struct
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pixels  # noqa: E402

FIELDS = {
    "EMIT0": [("MINCLIP_X", 12, 0), ("MINCLIP_Y", 28, 16)],
    "EMIT1": [("MAXCLIP_X", 12, 0), ("MAXCLIP_Y", 28, 16)],
    "EMIT2": [("BITS15_8", 15, 8), ("LINE_STRIDE", 27, 16), ("BIT28", 28, 28),
              ("BIT29", 29, 29), ("BIT30", 30, 30)],
    "EMIT3": [("ADDRESS", 31, 2)],
    "SIDEBAND": [("PACKMODE", 5, 0), ("BITS8_6", 8, 6), ("BIT9", 9, 9), ("DITHER", 10, 10),
                 ("MEMLAYOUT", 13, 13)],
}
# The fields as the emit-words table was written (before its runs named EMIT2 bits 28-30):
# the word probe flips every bit outside them, so the table stays the one that ran.
PROBED_FIELDS = {**FIELDS, "EMIT2": [("BITS15_8", 15, 8), ("LINE_STRIDE", 27, 16)]}
WORDS = ("EMIT0", "EMIT1", "EMIT2", "EMIT3")
SENTINEL = 0xdeadbeef
REG_0400 = 0x80                # the render command's word 11 (pixelbe) as the library writes it
COLOUR = 0x80ff8040            # the shader colour of the pack-mode probes (E031)
# The pack modes that store part of a colour or a whole colour into part of the target (E031)
PARTIAL_MODES = (4, 5, 8, 9, 26)
MSAA = {10: 0xeaa26e26, 16: 0xeaa26e26}     # the sample positions of E210
# Seven coded colours give each bit of o0 its own pattern over the cases (bit b: the bits of
# b + 1), never constant nor another bit's inverse, so a stored bit names the o0 bit it copies;
# then E031's colour and the two constants.
CODED = [sum(((b + 1) >> j & 1) << b for b in range(32)) for j in range(7)]
COLOURS = CODED + [COLOUR, 0x00000000, 0xffffffff]


class PbeError(Exception):
    pass


def words(width: int, height: int, fb: int) -> list[int]:
    """EMIT0-EMIT3 and the sideband of an ARGB8888 target (sgxfive_pbe, fw_format.md §9.6)."""
    return [0, (width - 1) | (height - 1) << 16, 0x80 << 8 | (4 * width // 8 - 1) << 16,
            fb & ~3, 0x200]


def _mask(hi: int, lo: int) -> int:
    return (1 << (hi + 1)) - (1 << lo)


def decode(word: str, value: int) -> dict:
    """{glossary name: field value} of one word, and `<word>.rest` the bits outside them."""
    if word not in FIELDS:
        raise PbeError(f"no word {word}: one of {', '.join(FIELDS)}")
    out, rest = {}, value
    for name, hi, lo in FIELDS[word]:
        out[f"{word}.{name}"] = (value & _mask(hi, lo)) >> lo
        rest &= ~_mask(hi, lo)
    out[f"{word}.rest"] = rest
    return out


def free_bits(word: str, fields: dict = FIELDS) -> list[int]:
    """The bits of a word no field covers."""
    used = 0
    for _n, hi, lo in fields[word]:
        used |= _mask(hi, lo)
    return [b for b in range(32) if not used >> b & 1]


def word_case(reg: int, and_: int, or_: int) -> list[str]:
    """A case of eot_words.s: register r<reg> becomes r & AND | OR after its mov."""
    if not 0 <= reg < 4:
        raise PbeError(f"r{reg}: the PBE words are r0-r3")
    return [f"r{reg}", f"0x{and_ & 0xffffffff:08X}", f"0x{or_ & 0xffffffff:08X}"]


def _field_set(reg: int, hi: int, lo: int, v: int) -> list[str]:
    return word_case(reg, ~_mask(hi, lo), v << lo)


def _flip(reg: int, base: int, bit: int) -> list[str]:
    """A flip as a mask and a set (the base word is known): clear it if set, set it if clear."""
    if base >> bit & 1:
        return word_case(reg, ~(1 << bit), 0)
    return word_case(reg, 0xffffffff, 1 << bit)


def _probe(name: str, question: str, cases: list, labels: list, **kw) -> dict:
    p = {"name": name, "question": question, "source": "eot_words.s", "host": "tri",
         "slot": "eot", "slots": {"pixel": "pix_colour.s"}, "size": [64, 64], "pixels": True,
         "inputs": ["R", "AND", "OR"]}
    p.update(kw)
    p["labels"], p["cases"] = labels, cases
    return p


def word_probe() -> dict:
    """Each field of EMIT0-EMIT3 at other values, each bit outside a field flipped, on the
    64x64 triangle; case 0 leaves the words as the host wrote them."""
    base = words(64, 64, 0)
    cases, labels = [word_case(0, 0xffffffff, 0)], ["base"]

    def add(label, case):
        labels.append(label)
        cases.append(case)
    for x, y in ((8, 0), (0, 8), (8, 8), (32, 16), (40, 24)):
        add(f"EMIT0 clip min ({x}, {y})", word_case(0, 0, x | y << 16))
    for x, y in ((31, 63), (63, 31), (40, 40), (15, 15)):
        add(f"EMIT1 clip max ({x}, {y})", word_case(1, 0, x | y << 16))
    for v in (0x00, 0x01, 0x40, 0x7f, 0x81, 0x83, 0xc1, 0xff):
        add(f"EMIT2.BITS15_8 = 0x{v:02x}", _field_set(2, 15, 8, v))
    for v in (15, 0, 63):
        add(f"EMIT2.LINE_STRIDE = {v}", _field_set(2, 27, 16, v))
    for off in (4, 0x40, 0x100):
        add(f"EMIT3 + 0x{off:x}", word_case(3, 0xffffffff, off))
    for i, word in enumerate(WORDS):
        for b in free_bits(word, PROBED_FIELDS):
            add(f"{word} bit {b}", _flip(i, base[i], b))
    return _probe("pbe-emit-words-fields",
                  "what each field of EMIT0-EMIT3 does at other values, and whether the end-of-"
                  "tile emit reads the bits outside the fields", cases, labels)


# The values of EMIT2 bits 15:8 the follow-up run repeats: the ends, two odd values (which
# hang), and the even values around the 0x80 the library writes.
FOLLOWUP_COUNTS = (0x00, 0x01, 0x02, 0x04, 0x10, 0x40, 0x7e, 0x80, 0x81, 0x82, 0xc0, 0xfe)


def count_probe(values=range(256), name: str = "pbe-emit-words-bits15-8") -> dict:
    """Every value of EMIT2 bits 15:8 (the field E046's table was taken to vary), or some."""
    values = list(values)
    return _probe(name, "whether any value of EMIT2 bits 15:8 changes what the end-of-tile "
                  "emit stores", [_field_set(2, 15, 8, v) for v in values],
                  [f"EMIT2.BITS15_8 = 0x{v:02x}" for v in values])


def _pix(colour: int) -> list[str]:
    return [f"mov.skipinv.end o0, #0x{colour:08X}"]


def _sb_probe(name: str, question: str, sideband: int, cases: list, labels: list,
              **kw) -> dict:
    p = {"name": name, "question": question, "source": "pix_op.s", "host": "tri",
         "slot": "pixel", "slots": {"eot": "eot_plain.s"}, "sideband": sideband,
         "size": [64, 64], "pixels": True, "inputs": ["OP"]}
    p.update(kw)
    p["cases"], p["labels"] = cases, labels
    return p


def reg0400_probes() -> list[dict]:
    """The word that loads CR_REG_0400 varied under pack modes 0-3: one probe per mode."""
    vals = [REG_0400, REG_0400 ^ 1 << 25] + [REG_0400 ^ 1 << b for b in range(12)] + \
        [0, 0xffffffff]
    labels = ["0x80 (as built)", "bit 25 flipped"] + [f"bit {b} flipped" for b in range(12)] + \
        ["0", "0xffffffff"]
    out = []
    for mode in range(4):
        out.append(_sb_probe(
            f"pbe-reg-0400-modes-{mode}",
            f"what the word that loads CR_REG_0400 does to a triangle stored in pack mode {mode}",
            0x200 | mode, [_pix(COLOUR) for _ in vals], labels,
            case_set=[{"cmd": {11: v}} for v in vals]))
    return out


def sideband_probes() -> list[dict]:
    """SIDEBAND bits 8:6 at 0-7 in each setting, and bits 10-12 flipped."""
    out = []
    for k in range(8):
        sb = 0x200 | k << 6
        for n in (1, 2):
            out.append(_sb_probe(
                f"pbe-sideband-fields-msaa{n}-{sb:04x}",
                f"what sideband 0x{sb:x} stores under CR_ISP_MSAA mode {n}", sb, [_pix(COLOUR)],
                [f"bits 8:6 = {k}, MSAA mode {n}"], cmd={**MSAA, 13: 0x80000000 | n}))
        out.append(_sb_probe(
            f"pbe-sideband-fields-128-{sb:04x}",
            f"what sideband 0x{sb:x} stores on a 128x128 target", sb, [_pix(COLOUR)],
            [f"bits 8:6 = {k}, 128x128"], size=[128, 128]))
        for mode in PARTIAL_MODES:
            out.append(_sb_probe(
                f"pbe-sideband-fields-mode{mode}-{sb | mode:04x}",
                f"what sideband 0x{sb | mode:x} stores (pack mode {mode}, bits 8:6 = {k})",
                sb | mode, [_pix(COLOUR)], [f"bits 8:6 = {k}, pack mode {mode}"]))
    for bit in (10, 11, 12):
        sb = 0x200 | 1 << bit
        out.append(_sb_probe(
            f"pbe-sideband-fields-bit{bit}", f"what sideband 0x{sb:x} stores (bit {bit})", sb,
            [_pix(COLOUR)], [f"bit {bit}"]))
    return out


def dither_probes() -> list[dict]:
    """SIDEBAND bit 10 (the Rogue name is a dither enable) in the modes that drop colour bits:
    RGB565, ARGB1555 and ARGB4444, each with and without the bit; colours whose low bits the
    modes drop."""
    cols = [COLOUR, 0x80818283, 0xff7f7f7f]
    return [_sb_probe(f"pbe-sideband-dither-{sb:04x}",
                      f"what sideband 0x{sb:x} stores (pack mode {sb & 0x3f}, bit 10 "
                      f"{'set' if sb & 0x400 else 'clear'})", sb, [_pix(c) for c in cols],
                      [f"o0 0x{c:08x}" for c in cols])
            for mode in (3, 4, 5) for sb in (0x200 | mode, 0x600 | mode)]


def pack_probes() -> list[dict]:
    """Pack modes 0, 22, 26 and 34 over COLOURS, one case a colour."""
    return [_sb_probe(f"pbe-pack-colours-mode{m}",
                      f"what pack mode {m} stores for each of {len(COLOURS)} shader colours",
                      0x200 | m, [_pix(c) for c in COLOURS],
                      [f"o0 0x{c:08x}" for c in COLOURS]) for m in (0, 22, 26, 34)]


# IEEE singles for the modes whose stored values follow o0 read as a float (pack-floats)
FLOATS = [0x00000000, 0x3e800000, 0x3f000000, 0x3f400000, 0x3f800000, 0x40000000, 0xbf000000,
          0x3dcccccd, 0x3f7f0000, 0x3c000000]


def float_probes() -> list[dict]:
    """Pack modes 22 and 34 (and 0, the control) over FLOATS: 0, 0.25, 0.5, 0.75, 1, 2, -0.5,
    0.1, 0.99609375, 1/128."""
    return [_sb_probe(f"pbe-pack-floats-mode{m}",
                      f"what pack mode {m} stores for o0 at ten IEEE singles", 0x200 | m,
                      [_pix(c) for c in FLOATS], [f"o0 0x{c:08x}" for c in FLOATS])
            for m in (0, 22, 34)]


def pixev_sweeps() -> list[dict]:
    """The pixel-event program's data dword 8 (0x100) in the fill, the copy and the triangle:
    the values E046's EMIT2 table gave it, and masks of single event bits."""
    values = ["^=0x100", "^=0x8100", "^=0x300", "^=0x4100", "^=0x8000", "=0", "=0x2",
              "=0x4", "=0x8", "=0x200"]
    return [{"name": f"pbe-emit-words-pixev-{host}",
             "about": f"the {host}'s pixel-event data dword 8, E046's values and single bits",
             "host": host, "bits": [], "values": values, "repeat": 2,
             "range": [{"space": "pds:pixev", "indices": [8, 8]}]} for host in
            ("fill", "copy", "tri")]


def _toml(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, int):
        return f"0x{v:x}" if v > 9 else str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_toml(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml(x)}" for k, x in v.items()) + " }"
    raise PbeError(f"no TOML for {v!r}")


def table_text(title: str, about: str, ps: list[dict], sweeps: list[dict] = ()) -> str:
    head = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
            f"# pbe {title}: {len(sweeps)} sweeps, {len(ps)} probes (written by "
            "tools/usse-asm/pbe_words.py).", f"# {about}", 'needs = ["render"]']
    if sweeps:
        head.append(f'name = "pbe-{title.replace(" ", "-")}"')
    body = []
    for s in sweeps:
        body.append("\n[[sweep]]")
        body += [f"{k} = {_toml(v)}" for k, v in s.items() if k != "range"]
        for r in s["range"]:
            body.append("\n[[sweep.range]]")
            body += [f"{k} = {_toml(v)}" for k, v in r.items()]
    for p in ps:
        body.append("\n[[probe]]")
        body += [f"{k} = {_toml(v)}" for k, v in p.items()]
    return "\n".join(head + body) + "\n"


def tables() -> dict[str, str]:
    """{feature: table text} of the 11.5 PBE tables."""
    return {
        "emit-words": table_text(
            "emit words", "EMIT0-EMIT3 fields and free bits; the pixel-event dword 8 of E046.",
            [word_probe(), count_probe()], pixev_sweeps()),
        "emit-words-followup": table_text(
            "emit words followup", "emit-words again: the fields, 12 values of bits 15:8, dword 8.",
            [dict(word_probe(), name="pbe-emit-words-followup-fields"),
             count_probe(FOLLOWUP_COUNTS, "pbe-emit-words-followup-bits15-8")],
            [dict(s, name=s["name"].replace("words-", "words-followup-"), repeat=1)
             for s in pixev_sweeps()]),
        "reg-0400-modes": table_text(
            "reg 0400 modes", "CR_REG_0400's word under pack modes 0-3 (Q044).",
            reg0400_probes()),
        "sideband-fields": table_text(
            "sideband fields", "SIDEBAND bits 8:6 under MSAA, partial modes, 128x128 (Q046).",
            sideband_probes()),
        "sideband-dither": table_text(
            "sideband dither", "SIDEBAND bit 10 in pack modes 3, 4 and 5.", dither_probes()),
        "pack-floats": table_text(
            "pack floats", "pack modes 22 and 34 over ten floats (Q012).", float_probes()),
        "pack-colours": table_text(
            "pack colours", "pack modes 0, 22, 26 and 34 over ten colours (Q012).",
            pack_probes()),
    }


# ---- 11.14 (batch 2 of the 11.12 triage) ------------------------------------------------

def _single(v: float) -> int:
    return struct.unpack("<I", struct.pack("<f", v))[0]


def xy_word(x: int, y: int) -> int:
    """What pix_xy.s stores at (x, y): x + 0.5's bits 31:16, then y + 0.5's."""
    return _single(x + 0.5) & 0xffff0000 | _single(y + 0.5) >> 16


_XY = {xy_word(x, y): (x, y) for x in range(256) for y in range(256)}


def xy_of(word: int) -> tuple[int, int] | None:
    """The pixel an xy_word names, or None."""
    return _XY.get(word)


_XY_SLOTS = {"pixel": "pix_xy.s", "pixpds": "pds_iter_xy.s", "vtxuse": "vtx_coords.s"}


def _term(a: int, b: int, c: int) -> str:
    v = {(1, 0): "x", (-1, 0): "-x", (0, 1): "y", (0, -1): "-y"}[(a, b)]
    if v.startswith("-"):
        return f"{c} - {v[1:]}"
    return v if c == 0 else f"{v} + {c}" if c > 0 else f"{v} - {-c}"


def place_fit(img: list[int], width: int, height: int) -> str:
    """Where the stored words of a pix_xy.s image came from: x' and y' (the place stored) as
    +-x or +-y plus a constant, each the commonest fit, and the pixels both fit."""
    pairs = [(i % width, i // width, *xy_of(v)) for i, v in enumerate(img[:width * height])
             if xy_of(v) is not None]
    if not pairs:
        return "no pixel names its source"
    fits = []
    for coord in (0, 1):
        best = None
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c, n = collections.Counter(q[coord] - (a * q[2] + b * q[3]) for q in pairs
                                       ).most_common(1)[0]
            if best is None or n > best[0]:
                best = (n, a, b, c)
        fits.append(best[1:])
    both = sum(1 for q in pairs if all(q[k] == a * q[2] + b * q[3] + c
                                        for k, (a, b, c) in enumerate(fits)))
    return (f"x' = {_term(*fits[0])}, y' = {_term(*fits[1])} "
            f"({both} of {len(pairs)} pixels)")


def place_run(raw: str, probe: str, labels: list[str], size: tuple) -> dict[str, str]:
    """{label: place_fit} of each case of a pix_xy.s probe."""
    img, fail = _img(raw, probe)
    out = {}
    for i, label in enumerate(labels):
        out[label] = f"failed: {fail[i]}" if i in fail else "not run" if i not in img else \
            place_fit(img[i], *size)
    return out


TRANSFORM_RUNS = 2
EMIT2_HIGH = range(16)                                   # bits 31:28
EMIT2_LOW = (1, 2, 3, 4, 8, 16, 32, 64, 127)            # bits 6:0
EMIT2_COUNTS = (0x82, 0x84, 0x90, 0xc0, 0xfe)            # bits 15:8 above 0x80, even (E266)


def transform_probe() -> dict:
    """EMIT2 bits 31:28 at each value, bits 6:0 at EMIT2_LOW and counts above 0x80, the
    shader naming each pixel, TRANSFORM_RUNS times each (Q040)."""
    cases, labels = [], []
    for run in range(1, TRANSFORM_RUNS + 1):
        for v in EMIT2_HIGH:
            cases.append(_field_set(2, 31, 28, v))
            labels.append(f"run {run}: EMIT2 bits 31:28 = 0x{v:x}")
        for v in EMIT2_LOW:
            cases.append(_field_set(2, 6, 0, v))
            labels.append(f"run {run}: EMIT2 bits 6:0 = 0x{v:02x}")
        for v in EMIT2_COUNTS:
            cases.append(_field_set(2, 15, 8, v))
            labels.append(f"run {run}: EMIT2 bits 15:8 = 0x{v:02x}")
    return _probe("pbe-emit-transforms-xy", "where the end-of-tile emit stores each pixel under "
                  "EMIT2 bits 31:28, 6:0 and counts above 0x80, the shader naming its pixel",
                  cases, labels, slots=dict(_XY_SLOTS), vtx_coords=2)


ONE, TWO, HALF, QUARTER = 0x3f800000, 0x40000000, 0x3f000000, 0x3e800000


def _outs(o: list) -> list[str]:
    """Writes of o0-o3 (None: left unwritten), the last ending the task."""
    lines = [f"mov.skipinv o{i}, {v if isinstance(v, str) else f'#0x{v:08X}'}"
             for i, v in enumerate(o) if v is not None]
    return ["\n".join(lines[:-1] + [lines[-1].replace("mov.skipinv ", "mov.skipinv.end ")])]


def float_channel_probes() -> list[dict]:
    """Pack modes 22 and 34 (0 the control) with o0-o3 four singles, each alone, and the
    pixel's place in o0 and o1 (pa0, pa1) (Q012); every case twice."""
    sets = [("o0-o3 = 1.0, 2.0, 0.5, 0.25", [ONE, TWO, HALF, QUARTER]),
            ("o0 = 1.0, o1-o3 = 0", [ONE, 0, 0, 0]), ("o1 = 2.0, o0, o2, o3 = 0", [0, TWO, 0, 0]),
            ("o2 = 0.5, o0, o1, o3 = 0", [0, 0, HALF, 0]),
            ("o3 = 0.25, o0-o2 = 0", [0, 0, 0, QUARTER]),
            ("o0 = x + 0.5, o1 = y + 0.5, o2 = 1.0, o3 = 0.5", ["pa0", "pa1", ONE, HALF]),
            ("o0 = x + 0.5, o1-o3 = 0", ["pa0", 0, 0, 0]),
            ("o1 = y + 0.5, o0, o2, o3 = 0", [0, "pa1", 0, 0])]
    out = []
    for m in (0, 22, 34):
        cases, labels = [], []
        for run in (1, 2):
            for lab, o in sets:
                cases.append(_outs(o))
                labels.append(f"run {run}: {lab}")
        out.append(_sb_probe(f"pbe-pack-floats-channels-mode{m}",
                             f"what pack mode {m} stores for o0-o3 four singles, each alone, "
                             "and the pixel's x and y", 0x200 | m, cases, labels,
                             source="pix_xy_op.s",
                             slots={"eot": "eot_plain.s", "pixpds": "pds_iter_xy.s",
                                    "vtxuse": "vtx_coords.s"}, vtx_coords=2))
    return out


# o0 = x / 128 (0 to 0.5), o1 = 0.5 + y / 128 (0.5 to 1), o2 = 0.3, o3 = 0.9: a stored field's
# value names the register and the pixel it came from (pix_xy_op.s, pa0 = x + 0.5, pa1 = y + 0.5)
_RAMP_SETUP = ["mov.skipinv r1, #0x3C000000", "mov.skipinv r2, #0x00000000",
               "mov.skipinv r3, #0x3F000000"]
RAMPS = (
    ("o0 = x/128, o1 = 0.5 + y/128, o2 = 0.3, o3 = 0.9",
     ["fmad.skipinv o0, pa0, r1, r2", "fmad.skipinv o1, pa1, r1, r3",
      "mov.skipinv o2, #0x3E99999A", "mov.skipinv.end o3, #0x3F666666"]),
    ("o0 = x/128, o1-o3 = 0",
     ["mov.skipinv o1, #0", "mov.skipinv o2, #0", "mov.skipinv o3, #0",
      "fmad.skipinv.end o0, pa0, r1, r2"]),
    ("o1 = 0.5 + y/128, o0, o2, o3 = 0",
     ["mov.skipinv o0, #0", "mov.skipinv o2, #0", "mov.skipinv o3, #0",
      "fmad.skipinv.end o1, pa1, r1, r3"]),
)


def ramp_probes() -> list[dict]:
    """Pack modes 0, 22 and 34 with o0 and o1 ramps over x and y and o2, o3 constants (RAMPS),
    twice each (Q012): each stored field names its register and pixel."""
    return [_sb_probe(f"pbe-pack-floats-ramps-mode{m}",
                      f"what pack mode {m} stores for o0 = x/128, o1 = 0.5 + y/128, o2 = 0.3, "
                      "o3 = 0.9 and each ramp alone", 0x200 | m,
                      [["\n".join(_RAMP_SETUP + ops)] for _ in (1, 2) for _, ops in RAMPS],
                      [f"run {r}: {lab}" for r in (1, 2) for lab, _ in RAMPS],
                      source="pix_xy_op.s",
                      slots={"eot": "eot_plain.s", "pixpds": "pds_iter_xy.s",
                             "vtxuse": "vtx_coords.s"}, vtx_coords=2)
            for m in (0, 22, 34)]


CHANNEL_COLOURS = (0xc0804020, 0x13579bdf)          # every byte differs
CHANNEL_MODES = (7, 8, 15, 18, 24, 25, 28)


def channel_probes() -> list[dict]:
    """SIDEBAND bits 8:6 at 0-7 in CHANNEL_MODES with two colours, and bits 11 and 12 in pack
    modes 0-8 (bit 12 twice; bit 11 faults the job, once) (Q046)."""
    out = []
    for mode in CHANNEL_MODES:
        for k in range(8):
            sb = 0x200 | k << 6 | mode
            out.append(_sb_probe(f"pbe-sideband-channels-{sb:04x}",
                                 f"what sideband 0x{sb:x} stores (pack mode {mode}, bits 8:6 = "
                                 f"{k}) for two colours", sb, [_pix(c) for c in CHANNEL_COLOURS],
                                 [f"o0 0x{c:08x}" for c in CHANNEL_COLOURS]))
    for bit, runs in ((12, 2), (11, 1)):
        for mode in range(9):
            sb = 0x200 | 1 << bit | mode
            out.append(_sb_probe(f"pbe-sideband-channels-bit{bit}-{sb:04x}",
                                 f"what sideband 0x{sb:x} stores (bit {bit}, pack mode {mode})",
                                 sb, [_pix(CHANNEL_COLOURS[0])] * runs,
                                 [f"run {r}: o0 0x{CHANNEL_COLOURS[0]:08x}"
                                  for r in range(1, runs + 1)]))
    return out


# o0 = the colour 0x00ff8040 with alpha = bits 23:16 of x + 0.5 as a single (pix_xy_op.s):
# from 0 at x = 0 up through 64 values over the 64 columns
ALPHA_RAMP = ("shl.skipinv r0, pa0, #8\nand.skipinv r0, r0, #0xFF000000\n"
              "mov.skipinv r1, #0x00FF8040\nor.skipinv r0, r0, r1\nmov.skipinv.end o0, r0")
REG_0400_VALUES = (("0x80 (as built)", 0x80), ("low byte 0", 0x00), ("low byte 0x40", 0x40),
                   ("low byte 0xc0", 0xc0), ("low byte 0xff", 0xff),
                   ("bit 8 set", 0x180), ("bit 9 set", 0x280), ("bit 10 set", 0x480),
                   ("bit 11 set", 0x880))


def alpha_ramp(x: int) -> int:
    """The alpha ALPHA_RAMP gives column x."""
    return _single(x + 0.5) >> 16 & 0xff


def alpha_probes() -> list[dict]:
    """CR_REG_0400's word under an alpha that varies over x: REG_0400_VALUES in pack modes 0
    and 4, and bit 25 against 0x80 in modes 4, 5 and 8; every case twice (Q044)."""
    out = []
    for mode, vals in ((0, REG_0400_VALUES), (4, REG_0400_VALUES)) + tuple(
            (m, (("0x80 (as built)", 0x80), ("bit 25 set", 0x80 | 1 << 25))) for m in (4, 5, 8)):
        if mode == 4 and len(vals) == 2:
            name = "pbe-reg-0400-alpha-bit25-mode4"
        elif len(vals) == 2:
            name = f"pbe-reg-0400-alpha-bit25-mode{mode}"
        else:
            name = f"pbe-reg-0400-alpha-mode{mode}"
        labels = [f"run {r}: {lab}" for r in (1, 2) for lab, _ in vals]
        out.append(_sb_probe(name, f"what the word that loads CR_REG_0400 does to an alpha "
                             f"ramp over x in pack mode {mode}", 0x200 | mode,
                             [[ALPHA_RAMP]] * len(labels), labels, source="pix_xy_op.s",
                             slots={"eot": "eot_plain.s", "pixpds": "pds_iter_xy.s",
                                    "vtxuse": "vtx_coords.s"}, vtx_coords=2,
                             case_set=[{"cmd": {11: v}} for _ in (1, 2) for _, v in vals]))
    return out


_EMIT1 = "emitpix1{f} #0 /* incp */, r0, r1"
_EMIT2 = "emitpix2{f} #0 /* incp */, r2, r3, r0, #0x{sb:04X}"
_BLANK = ("mov.skipinv r4, #0xFFFF00FF\nand.skipinv r2, r2, r4\n" +
          _EMIT1.format(f=".freep") + "\n" + _EMIT2.format(f=".end.freep", sb=0x200))


def _emits(first: int, second: int) -> str:
    return "\n".join([_EMIT1.format(f=""), _EMIT2.format(f="", sb=first),
                      _EMIT1.format(f=".freep"), _EMIT2.format(f=".end.freep", sb=second)])


EMIT_TWICE = (
    ("one emit (eot_plain.s)", _EMIT1.format(f=".freep") + "\n" +
     _EMIT2.format(f=".end.freep", sb=0x200)),
    ("a blank job (EMIT2 count 0)", _BLANK),
    ("two emits, sideband 0x200 and 0x200", _emits(0x200, 0x200)),
    ("a blank job after it", _BLANK), ("a second blank job", _BLANK),
    ("two emits, bit 9 on the second only (0x000, 0x200)", _emits(0x000, 0x200)),
    ("a blank job after it", _BLANK),
    ("two emits, bit 9 on the first only (0x200, 0x000)", _emits(0x200, 0x000)),
    ("a blank job after it", _BLANK),
)


_ONE = EMIT_TWICE[0][1]
# On a one-tile target (E239's): each double emit, then a job of one emit, then a blank one.
EMIT_TWICE_TILE = (
    ("two emits, sideband 0x200 and 0x200", _emits(0x200, 0x200)),
    ("one emit after it", _ONE), ("a blank job after that", _BLANK),
    ("two emits, bit 9 on the second only (0x000, 0x200)", _emits(0x000, 0x200)),
    ("one emit after it", _ONE), ("a blank job after that", _BLANK),
    ("two emits, bit 9 on the first only (0x200, 0x000)", _emits(0x200, 0x000)),
    ("one emit after it", _ONE), ("a blank job after that", _BLANK),
)


def emit_twice_probes() -> list[dict]:
    """Two end-of-tile emits per tile, each followed by other jobs, bit 9 on one emit only;
    each sequence twice, on 64x64 and on one tile (E239's 32x16) (Q074)."""
    out = []
    for name, seq, size in (("sequence", EMIT_TWICE, [64, 64]),
                            ("one-tile", EMIT_TWICE_TILE, [32, 16])):
        cases = [[e] for _ in (1, 2) for _, e in seq]
        labels = [f"run {r}: {lab}" for r in (1, 2) for lab, _ in seq]
        out.append(_probe(f"pbe-emit-twice-{name}", "what a second end-of-tile emit does to "
                          f"its job and the next ones on {size[0]}x{size[1]}, and SIDEBAND bit "
                          "9 on one of two emits; may hang", cases, labels, source="eot_emits.s",
                          inputs=["EMITS"], size=size))
    return out


def tables_1114() -> dict[str, str]:
    """{feature: table text} of the 11.14 PBE tables."""
    return {
        "emit-transforms": table_text(
            "emit transforms", "EMIT2 bits 31:28, 6:0 and counts above 0x80, pix_xy.s (Q040).",
            [transform_probe()]),
        "pack-floats-channels": table_text(
            "pack floats channels", "pack modes 22 and 34 with o0-o3 and x, y (Q012).",
            float_channel_probes()),
        "pack-floats-ramps": table_text(
            "pack floats ramps", "pack modes 22 and 34 with x and y ramps in o0, o1 (Q012).",
            ramp_probes()),
        "sideband-channels": table_text(
            "sideband channels", "SIDEBAND bits 8:6 in seven pack modes; bits 11, 12 (Q046).",
            channel_probes()),
        "reg-0400-alpha": table_text(
            "reg 0400 alpha", "CR_REG_0400's word under an alpha ramp (Q044).", alpha_probes()),
        "emit-twice": table_text(
            "emit twice", "two end-of-tile emits, then blank jobs; bit 9 on one (Q074).",
            emit_twice_probes()),
    }


# ---- readers ------------------------------------------------------------------------------

def _img(raw: str, probe: str) -> tuple[dict, dict]:
    img, fail = pixels.parse(raw)
    pre = f"{probe}__"
    return ({int(k[len(pre):]): v for k, v in img.items() if k.startswith(pre)},
            {int(k[len(pre):]): v for k, v in fail.items() if k.startswith(pre)})


def _side(n: int) -> int:
    w = int(n ** 0.5)
    if w * w != n:
        raise PbeError(f"{n} pixels: not a square target")
    return w


def effect(base: list[int], got: list[int]) -> str:
    """What a case's image is against the base image: same, moved (dx, dy), a written box (its
    pixels as the base's) with the rest unwritten, or the count of changed pixels."""
    if got == base:
        return "same"
    w = _side(len(base))
    h = len(base) // w
    for dy in range(-4, 5):
        for dx in range(-64, 65):
            if (dx, dy) == (0, 0):
                continue
            ok = n = 0
            for y in range(h):
                for x in range(w):
                    sx, sy = x - dx, y - dy
                    if 0 <= sx < w and 0 <= sy < h:
                        n += 1
                        ok += got[y * w + x] == base[sy * w + sx]
            if n and ok == n and n >= len(base) // 2:
                return f"moved ({dx}, {dy})"
    written = [i for i, v in enumerate(got) if v != SENTINEL]
    if written and all(got[i] == base[i] for i in written):
        xs = [i % w for i in written]
        ys = [i // w for i in written]
        return (f"written box x {min(xs)}-{max(xs)} y {min(ys)}-{max(ys)} "
                f"({len(written)} of {len(base)}), rest unwritten")
    diff = sum(a != b for a, b in zip(base, got))
    top = collections.Counter(v for a, v in zip(base, got) if a != v).most_common(3)
    return f"{diff} of {len(base)} differ: " + ", ".join(f"0x{v:08x} x{n}" for v, n in top)


def effects(raw: str, probe: str, labels: list[str]) -> dict[str, str]:
    """{label: effect} of each case of a probe against its case 0."""
    img, fail = _img(raw, probe)
    if 0 not in img:
        raise PbeError(f"{probe}: no base image ({fail.get(0, 'not run')})")
    out = {}
    for i, label in enumerate(labels[1:], 1):
        if i in fail:
            out[label] = f"failed: {fail[i]}"
        elif i not in img:
            out[label] = "not run"
        else:
            out[label] = effect(img[0], img[i])
    return out


def correlate(colours: list[int], outs: list[int], width: int = 32) -> dict[int, tuple]:
    """For each stored bit (0..width-1): ("bit", b) when it equals bit b of the colour in every
    case and no other bit does, ("not", b) its inverse, ("some", [b...]) when several bits fit
    (the colours do not tell them apart), ("const", v), or ("none", None)."""
    fit = {}
    for o in range(width):
        col = [v >> o & 1 for v in outs]
        if len(set(col)) == 1:
            fit[o] = ("const", col[0])
            continue
        same = [b for b in range(32) if [c >> b & 1 for c in colours] == col]
        inv = [b for b in range(32) if [1 - (c >> b & 1) for c in colours] == col]
        if len(same) == 1 and not inv:
            fit[o] = ("bit", same[0])
        elif len(inv) == 1 and not same:
            fit[o] = ("not", inv[0])
        elif same or inv:
            fit[o] = ("some", same + [f"not {b}" for b in inv])
        else:
            fit[o] = ("none", None)
    return fit


def fit_text(fit: dict[int, tuple]) -> str:
    """Runs of stored bits that copy a run of input bits, constants, and the rest (?)."""
    parts, o = [], 0
    top = max(fit) + 1
    while o < top:
        kind, b = fit[o]
        n = 1
        while o + n < top and fit[o + n][0] == kind and (
                (kind in ("bit", "not") and fit[o + n][1] == b + n) or
                (kind == "const" and fit[o + n][1] == b) or
                (kind == "none" and fit[o + n][1] is None)):
            n += 1
        hi = o + n - 1
        rng = f"{hi}:{o}" if n > 1 else f"{o}"
        if kind in ("bit", "not"):
            src = f"{b + n - 1}:{b}" if n > 1 else f"{b}"
            parts.append(f"{rng} = {'not ' if kind == 'not' else ''}in {src}")
        elif kind == "const":
            parts.append(f"{rng} = {b if n == 1 else (2 ** n - 1) * b}")
        elif kind == "some":
            parts.append(f"{rng} = one of {b}")
        else:
            parts.append(f"{rng} = ?")
        o += n
    return "; ".join(parts)


# Bits a pixel of each pack mode takes in the target, as E031 and E269 read the images: the
# 16-bit modes hold two pixels a dword (the first in bits 15:0), mode 8 four (the first in
# bits 7:0); the rows follow each other without a gap.
PIXEL_BITS = {0: 32, 1: 32, 2: 32, 3: 16, 4: 16, 5: 16, 8: 8, 22: 32, 26: 16, 34: 32}


def pixel_bits(mode: int) -> int:
    if mode not in PIXEL_BITS:
        raise PbeError(f"pack mode {mode}: its pixel size is not known")
    return PIXEL_BITS[mode]


def triangle(base: list[int], bg: int = pixels.BG) -> list[int]:
    """The pixels where the plain image (a pack mode 0 run) holds the triangle (E031)."""
    return [i for i, v in enumerate(base) if v not in (bg, SENTINEL)]


def at(img: list[int], where: list[int], bits: int) -> list[int]:
    """The values of pixels `where` (row by row) of an image read back as dwords."""
    per = 32 // bits
    return [img[p // per] >> bits * (p % per) & ((1 << bits) - 1) for p in where]


def stored(img: list[int], base: list[int], bits: int = 32,
           bg: int = pixels.BG) -> collections.Counter:
    """The values a pack-mode image holds where the plain image (base) holds the triangle."""
    return collections.Counter(at(img, triangle(base, bg), bits))


def correlate_run(raw: str, probe: str, table: pathlib.Path, base_raw: str) -> dict:
    """Each case of a pack-mode probe read at the triangle of a plain run (base_raw, its case
    0): {"cases": [(o0, commonest value, its count, triangle pixels) or (o0, why failed)],
    "fit": correlate() of the commonest values against o0}."""
    p = _probe_meta(table, probe)
    bits = pixel_bits(p["sideband"] & 0x3f)
    plain, _fail = pixels.parse(base_raw)
    first = [k for k in plain if k.endswith("__0")]
    if not first:
        raise PbeError("the base run has no case 0")
    where = triangle(plain[first[0]])
    img, fail = _img(raw, probe)
    cols = [int(re.search(r"#0x([0-9A-Fa-f]+)", c[0]).group(1), 16) for c in p["cases"]]
    cases, ok = [], []
    for i, c in enumerate(cols):
        if i in fail or i not in img:
            cases.append((c, fail.get(i, "not run")))
            continue
        top, n = collections.Counter(at(img[i], where, bits)).most_common(1)[0]
        cases.append((c, top, n, len(where)))
        ok.append((c, top))
    return {"cases": cases, "fit": correlate([c for c, _ in ok], [v for _, v in ok], bits)}


def _probe_meta(table: pathlib.Path, name: str) -> dict:
    for p in tomllib.loads(table.read_text()).get("probe", []):
        if p["name"] == name:
            return p
    raise PbeError(f"{name}: not in {table}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decode")
    d.add_argument("word")
    d.add_argument("value")
    t = sub.add_parser("table")
    t.add_argument("out")
    t.add_argument("--phase", default="11.5", choices=("11.5", "11.14"))
    pl = sub.add_parser("place")
    pl.add_argument("raw")
    pl.add_argument("probe")
    pl.add_argument("table")
    for name in ("effects", "correlate"):
        e = sub.add_parser(name)
        e.add_argument("raw")
        e.add_argument("probe")
        e.add_argument("table")
        if name == "correlate":
            e.add_argument("base", help="raw.txt of a pack mode 0 run of the same triangle")
    a = ap.parse_args(argv)
    if a.cmd == "decode":
        for k, v in decode(a.word, int(a.value, 0)).items():
            print(f"{k} = 0x{v:x}")
    elif a.cmd == "place":
        p = _probe_meta(pathlib.Path(a.table), a.probe)
        for label, e in place_run(pathlib.Path(a.raw).read_text(), a.probe, p["labels"],
                                  tuple(p.get("size", (64, 64)))).items():
            print(f"{label}: {e}")
    elif a.cmd == "table":
        for name, text in (tables_1114() if a.phase == "11.14" else tables()).items():
            (pathlib.Path(a.out) / f"{name}.toml").write_text(text)
    elif a.cmd == "effects":
        p = _probe_meta(pathlib.Path(a.table), a.probe)
        for label, e in effects(pathlib.Path(a.raw).read_text(), a.probe,
                                p["labels"]).items():
            print(f"{label}: {e}")
    else:
        out = correlate_run(pathlib.Path(a.raw).read_text(), a.probe, pathlib.Path(a.table),
                            pathlib.Path(a.base).read_text())
        for case in out["cases"]:
            if len(case) == 2:
                print(f"o0 0x{case[0]:08x}: {case[1]}")
            else:
                c, top, n, total = case
                print(f"o0 0x{c:08x}: commonest at the triangle 0x{top:08x} ({n} of {total})")
        print("fit: " + fit_text(out["fit"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
