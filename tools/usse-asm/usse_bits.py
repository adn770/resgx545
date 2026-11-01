#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The USSE encoding-bit probes: does the hardware read the bits no form of isa/usse/ maps?

A form's unmapped bits are those neither in its mask (the identifying bits) nor in one of its
fields (formdump's `bits_read`, doc/isa/formdump.c, from the tables the tools use). For each
form with a base (BASES) the base instruction runs in the template `dump.s` (the inputs A-H in
r1-r8, r10-r17 preset, both stored to the scratch and OUT as the pixel) as a fill's pixel
program; case 0 is the base word and every other case the same word with one unmapped bit
flipped, as a raw `.long`. A bit the hardware ignores leaves the readback (o0, the scratch
dwords) as case 0 left it; one it reads changes it, or hangs or faults the job. A flip that makes
the word decode to another form is left out (it tests that form, not this one's bits).

The no-form encodings (classes 2, 22, 26 and 31 have words that match no form's mask and value,
`gaps`) run the same way, one raw word per case after a base `nop` case, in their own table. The
11.7 run's table took the words the decoder rejects instead (`--gaps-by-decoder`); that rule also
takes words that match a form's mask but hold a reserved value in a field (one of them, of class
22, is bilin's with format 3), and the decoder rejects about a quarter of all words that way.

    usse_bits.py table DIR [--group G...] [--gaps-by-decoder]
                                            write the tables (GROUPS) into DIR (probes/usse/)
    usse_bits.py eval TABLE RAW             each probe's cases against its base, from a run
    usse_bits.py count                      unmapped bits per form, and those BASES reach
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import pathlib
import random
import sys

import probe

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "doc" / "isa"))
TEMPLATE = "dump.s"
ALL = (1 << 64) - 1
# r1-r8: integers, floats and halves with distinct bytes, none zero, so that a flip that moves a
# source, a modifier or a format shows in the result.
INPUTS = {"A": 0x3FC01234, "B": 0x40105678, "C": 0x8001C003, "D": 0x00FF7F80,
          "E": 0x3F800001, "F": 0xC0400002, "G": 0x12345678, "H": 0x7F7F0101}
# Each group runs as a batch (its own table): ALU and data forms; the forms whose effect a fill
# does not show (state, visibility, MOE immediates); the loads; the dual-issue pairs; the
# follow-ups of the first run (rlp with p0 set first: its first run read an unset p0, which
# differs from instance to instance); the no-form encodings.
GROUPS = {"data": "encoding-bits", "state": "encoding-bits-state", "load": "encoding-bits-load",
          "dual": "encoding-bits-dual", "followup": "encoding-bits-followup",
          "gaps": "encoding-gaps"}
GAP_CLASSES = (2, 22, 26, 31)
GAPS_PER_CLASS = 3


class BitsError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class Base:
    """A form's base instruction (`test`), the lines around it, and its batch."""
    name: str                  # the probe's name, after usse-<table>-
    test: str
    group: str = "data"
    setup: tuple = ()
    after: tuple = ()
    out: str = "r10"


# Set-up lines: p0 set (a test of a constant), and i0-i2 loaded and stored to r15-r17 after the
# instruction (the dual-issue secondary's results show there).
_P0 = ("and.skipinv.testtanz.chan0 !r0, p0, #0x00000001, #1",)
_I = ("mov i0, r5", "mov i1, r6", "mov i2, r7")
_IO = ("mov r15, i0", "mov r16, i1", "mov r17, i2")

# The forms with a base, by group. Each base decodes to the form named by its pattern in the
# probe's question; forms the table reaches only through another form's word (an earlier form
# with the same mask and value decodes first) have none.
BASES = (
    Base("mov-imm", "mov r10, #0x12345678"),
    Base("mov", "mov r10, r1"),
    Base("and", "and r10, r1, r2"),
    Base("and-repeat", "and.repeat2 r10, r1, r3"),
    Base("shl", "shl r10, r1, r4"),
    Base("shr-repeat", "shr.repeat2 r10, r1, r3"),
    Base("imae", "imae.u r10, r1.low, r2.low, r3, u32"),
    Base("ima16", "ima16.u r10, r1, r2, r3, u16, u16"),
    Base("ima16-8bit", "ima16.u r10, r1, r2.low, r3, u8, u16"),
    Base("ima16-s8", "ima16.u r10, r1, r2, r3.high, u16, s8"),
    Base("ima16-u8u8", "ima16.u r10, r1, r2.low, r3.low, u8, u8"),
    Base("ima32", "ima32.u r10, r1, r2, r3"),
    Base("fsubflr", "fsubflr r10, r1, r2"),
    Base("fsubflr-f16", "fsubflr r10, r1.flt16, r2.flt16.2"),
    Base("frcp", "frcp r10, r1"),
    Base("frcp-repeat", "frcp.repeat2 r10, r1"),
    Base("fdp", "fdp r10, r1, r5"),
    Base("fdp-f16", "fdp r10, r1.flt16.0, r2.flt16.2"),
    Base("fdpc", "fdpc r10, cp0, r1, r2"),
    Base("fdpc-f16", "fdpc r10, cp0, r1.flt16, r2.flt16.2"),
    Base("fddpc", "fddpc r10, i0, cp0, cp0, r1, r2, r3"),
    Base("fdsx", "fdsx r10, r1, r2"),
    Base("fdsx-f16", "fdsx r10, r1.flt16.0, r2.flt16.2"),
    Base("sop2wm", "sop2wm r10.e0.e1.e2.e3, r1, r2, zero.comp, zero.comp, add, sub"),
    Base("u8dot4", "u8dot4 r10, Cx1, Ax1, r1, r2"),
    Base("u8dot3", "u8dot3 r10, Cx1, Ax1, r1, r2"),
    Base("u16dot3", "u16dot3 r10, Cx1, r1, r2"),
    Base("u8dot3-aadd", "u8dot3 r10, Cx1, r1, r2+aadd Ax1, zero, s1a, zero, s2a"),
    Base("rlp", "rlp r10, r1, p0"),
    Base("rlp-repeat", "rlp.repeat2 r10, r1, p0"),
    Base("movc", "movc.i32.tz r10, r1, r2, r3"),
    Base("movc-repeat", "movc.i32.repeat2.tz r10, r1, r3, r5"),
    Base("movc-i8", "movc.repeat2.i8.tz r10, r1, r3, r5"),
    Base("movmsk", "movmsk.mask r10, r1, r2"),
    Base("movmsk-repeat", "movmsk.mask.repeat2 r10, r3, r1"),
    Base("movmsk-smsk", "movmsk.mask.smsk r10, r1, r2, r3"),
    Base("movmsk-u8", "movmsk.u8 r10, r1, r2"),
    Base("movmsk-smsk-u8", "movmsk.smsk.u8 r10, r1, r2, r3"),
    Base("test-mask-xor", "xor.testtanz.bmsk r10, r1, r2"),
    Base("test-mask-fadd", "fadd.testpat.bmsk r10, r1, r2"),
    Base("test-mask-frcp", "frcp.testpat.wmsk r10, r1"),
    Base("test-mask-iadd8", "iadd8.sat.testtanz.bmsk r10, r1, r2"),
    Base("adif", "adif r10, r1, r2"),
    Base("adifsum", "adifsum r10, r3.low, r1, r2"),
    Base("bilin", "bilin r10, r3, r1, r2, u8, planar, src01, dst01"),
    Base("firv", "firv r10, r1, r2, r3, u8"),
    Base("firh", "firh r10, r1, r2, r3, u8, rep, fcs3, #4, #0"),
    Base("idiv", "idiv r10, r1, r2, drc0", after=("wdf drc0",)),
    # forms whose effect a fill does not show: a flip that does change something shows
    Base("nop", "nop", "state"),
    Base("setfc", "setfc #0, #0", "state"),
    Base("moest", "moest r17, #0", "state", out="r17"),
    Base("setm", "setm #0", "state"),
    Base("imo", "imo #0, #0, #0, #0", "state"),
    Base("smoa-imm", "smoa #0, #0, #0, #0, none, none, none, none", "state"),
    Base("smr-imm", "smr #0, #0, #0, #0", "state"),
    Base("smbo-imm", "smbo #0, #0, #0, #0", "state"),
    Base("smlsi-imm", "smlsi #0, #0, #0, #0, incrementmode, incrementmode, incrementmode, "
         "incrementmode, #0, #0, #0", "state"),
    Base("pcoeff", "pcoeff r1, r2, r3", "state"),
    Base("depthf", "depthf r1, r2, r3, nfb", "state"),
    Base("atst8", "atst8 r10, p0, r1, r2, r3, nfb", "state",
         setup=("and.skipinv.testtanz.chan0 !r0, p0, #0x00000001, #1",)),
    # dual issue: a primary on r1-r3 and a secondary on i0-i2 (set first)
    Base("dual-fmad-frcp", "fmad r10, r1, r2, r3+frcp i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-fmad-mov", "fmad r10, r1, r2, r3+mov i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-mov-fmad", "mov r10, r1+fmad i0, i0, i1, i2", "dual", setup=_I, after=_IO),
    Base("dual-mov-fadd", "mov r10, r1+fadd i0, i1, i2", "dual", setup=_I, after=_IO),
    Base("dual-mov-frcp", "mov r10, r1+frcp i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-mov-mov", "mov r10, r1+mov i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-fddp-frcp", "fddp r10, i0, r1, r2, r3+frcp i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-fddp-mov", "fddp r10, i0, r1, r2, r3+mov i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-fssq-fadd", "fssq r10, r2, r3+fadd i0, i1, i2", "dual", setup=_I, after=_IO),
    Base("dual-fssq-frcp", "fssq r10, r2, r3+frcp i0, i1", "dual", setup=_I, after=_IO),
    Base("dual-fssq-mov", "fssq r10, r2, r3+mov i0, i1", "dual", setup=_I, after=_IO),
    # rlp again with p0 set first (case 0 of the first run read an unset p0)
    Base("rlp-p0", "rlp r10, r1, p0", "followup", setup=_P0),
    Base("rlp-repeat-p0", "rlp.repeat2 r10, r1, p0", "followup", setup=_P0),
    # loads of the global registers: ldr's unmapped bits
    Base("ldr-imm", "ldr r10, #0, drc0", "load", after=("wdf drc0",)),
    Base("ldr", "ldr r10, r1, drc0", "load", setup=("mov r1, #0",), after=("wdf drc0",)),
)


def _tables() -> dict:
    import build  # doc/isa/build.py: formdump, compiled from the tools' tables
    return json.loads(build.formdump("tables"))["usse"]


def _encode(text: str) -> dict:
    import build
    return json.loads(build.formdump("encode", "usse", text))


def decode(word: int) -> int | None:
    """The form a word decodes to, None if none."""
    import build
    try:
        return json.loads(build.formdump("decode", "usse", f"{word:016X}"))["form"]
    except build.BuildError:
        return None


def forms(tables: dict | None = None) -> list[dict]:
    """Every USSE form: index, pattern, mask, value and its unmapped bits."""
    out = []
    for f in (tables or _tables())["forms"]:
        out.append({"index": f["index"], "pat": f["pat"], "mask": int(f["mask"], 16),
                    "val": int(f["val"], 16), "unmapped": ~int(f["bits_read"], 16) & ALL})
    return out


def bits(mask: int) -> list[int]:
    return [b for b in range(64) if mask >> b & 1]


def _op(base: Base, line: str) -> str:
    return "\n".join([*base.setup, line, *base.after])


def _case(base: Base, word: int, label: str) -> list:
    return [_op(base, f".long 0x{word:016X} ; {label}")] + [f"0x{INPUTS[k]:08X}" for k in "ABCDEFGH"]


def probes(group: str | None = None, fs: list | None = None, decoder=decode,
           encoder=_encode) -> list[dict]:
    """The [[probe]] entries of one group's table (every group's: None), in BASES order. A flip
    whose word decodes to another form is left out; so is a base whose form has no unmapped
    bit."""
    fs = fs or forms()
    by = {f["index"]: f for f in fs}
    out = []
    for base in BASES:
        if group and base.group != group:
            continue
        e = encoder(base.test)
        word, f = int(e["word"], 16), by[e["form"]]
        flips = [b for b in bits(f["unmapped"]) if decoder(word ^ 1 << b) == f["index"]]
        if not flips:
            continue
        cases = [_case(base, word, f"base: {base.test}")]
        cases += [_case(base, word ^ 1 << b, f"bit {b}") for b in flips]
        out.append({"name": f"usse-{GROUPS[base.group]}-{base.name}",
                    "question": f"which unmapped bits of form {f['index']} {f['pat']!r} the "
                                f"hardware reads (0x{f['unmapped']:016x}), base {base.test!r}; "
                                f"may hang",
                    "source": TEMPLATE, "params": {"OUT": base.out},
                    "inputs": ["OP", *"ABCDEFGH"],
                    "labels": ["base"] + [f"bit {b}" for b in flips], "cases": cases})
    return out


def no_form(word: int, fs: list) -> bool:
    """Whether no form's mask and value match the word (forms())."""
    return not any(word & f["mask"] == f["val"] for f in fs)


def gap_words(fs: list | None = None, decoder=decode, per: int = GAPS_PER_CLASS,
              seed: int = 117, by_decoder: bool = False) -> dict[int, list[int]]:
    """Words of each class in GAP_CLASSES that no form's mask and value match: random words
    (seeded) of the class, the first `per` of them. by_decoder takes the words the decoder
    rejects instead, as the 11.7 run's table did (a reserved field value counts there too)."""
    fs = fs if fs is not None or by_decoder else forms()
    rng = random.Random(seed)
    out: dict[int, list[int]] = {}
    for cls in GAP_CLASSES:
        got: list[int] = []
        for _ in range(4000):
            w = rng.getrandbits(64) & ~(0x1F << 59) | cls << 59
            gap = decoder(w) is None if by_decoder else no_form(w, fs)
            if gap and w not in got:
                got.append(w)
            if len(got) == per:
                break
        out[cls] = got
    return out


def gap_probes(words: dict[int, list[int]]) -> list[dict]:
    """One probe per class: case 0 a nop, then each no-form word in its place."""
    nop = Base("nop", "nop")
    out = []
    for cls, ws in words.items():
        cases = [["nop"] + [f"0x{INPUTS[k]:08X}" for k in "ABCDEFGH"]]
        cases += [_case(nop, w, f"class {cls} word") for w in ws]
        out.append({"name": f"usse-{GROUPS['gaps']}-class{cls}",
                    "question": f"what a word of class {cls} that no form decodes does in a "
                                "fill: nothing, a change, or a hang or fault",
                    "source": TEMPLATE, "params": {"OUT": "r10"},
                    "inputs": ["OP", *"ABCDEFGH"],
                    "labels": ["base"] + [f"0x{w:016X}" for w in ws], "cases": cases})
    return out


def _toml(v) -> str:
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, int):
        return f"0x{v:x}"
    if isinstance(v, list):
        return "[" + ", ".join(_toml(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_toml(x)}" for k, x in v.items()) + " }"
    raise BitsError(f"no TOML for {v!r}")


def table_text(ps: list[dict], what: str = "encoding bits") -> str:
    head = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
            f"# usse {what}: 0 sweeps, {len(ps)} probes (written by "
            "tools/usse-asm/usse_bits.py).",
            "# Each probe flips one unmapped bit of a form per case; case 0 is the base word."
            if what == "encoding bits" else
            "# Each probe runs one word no form decodes per case; case 0 is a nop.",
            'needs = ["render"]']
    body = []
    for p in ps:
        body.append("\n[[probe]]")
        body += [f"{k} = {_toml(v)}" for k, v in p.items()]
    return "\n".join(head + body) + "\n"


def classify(name: str, labels: list[str], obs: dict) -> list[tuple[str, str]]:
    """Each case of probe `name` against case 0: same, differs (the dwords) or failed."""
    base = obs.get(f"{name}__0")
    if base is None or base.failed:
        raise BitsError(f"{name}: no base reading ({base.failed if base else 'not run'})")
    want = dict(base.scratch)
    out = []
    for i, label in enumerate(labels[1:], 1):
        o = obs.get(f"{name}__{i}")
        if o is None:
            out.append((label, "not run"))
        elif o.failed:
            out.append((label, f"failed: {o.failed}"))
        elif o.o0 == base.o0 and o.mixed == base.mixed and dict(o.scratch) == want:
            out.append((label, "same"))
        else:
            got = dict(o.scratch)
            d = [f"+0x{k:03x} 0x{want.get(k, probe.SCRATCH_FILL | k // 4):08x} -> "
                 f"0x{got.get(k, probe.SCRATCH_FILL | k // 4):08x}"
                 for k in sorted(set(want) | set(got)) if want.get(k) != got.get(k)]
            if o.o0 != base.o0 or o.mixed != base.mixed:
                d.insert(0, f"o0 {base.o0} -> {o.o0}")
            out.append((label, "differs: " + "; ".join(d)))
    return out


def evaluate(table: pathlib.Path, raw: str) -> str:
    obs = probe.parse(raw)
    lines = []
    for p in probe.load(table):
        try:
            got = classify(p.name, p.labels, obs)
        except BitsError as e:
            lines.append(f"{p.name}: {e}")
            continue
        same = [lab for lab, s in got if s == "same"]
        lines.append(f"{p.name}: {len(same)} of {len(got)} cases same as the base")
        lines += [f"  {lab}: {s}" for lab, s in got if s != "same"]
    return "\n".join(lines) + "\n"


def count(fs: list | None = None, encoder=_encode) -> str:
    """The unmapped bits: in all, per form, and how many BASES reach."""
    fs = fs or forms()
    total = sum(len(bits(f["unmapped"])) for f in fs)
    with_bits = [f for f in fs if f["unmapped"]]
    reached = {encoder(b.test)["form"] for b in BASES}
    covered = sum(len(bits(f["unmapped"])) for f in with_bits if f["index"] in reached)
    return (f"{total} unmapped bits in {len(with_bits)} of {len(fs)} forms; the bases reach "
            f"{covered} bits in {len(reached & {f['index'] for f in with_bits})} forms\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("table")
    t.add_argument("out")
    t.add_argument("--group", action="append", choices=sorted(GROUPS))
    t.add_argument("--gaps-by-decoder", action="store_true",
                   help="the gap words the decoder rejects (the 11.7 run's table)")
    e = sub.add_parser("eval")
    e.add_argument("table")
    e.add_argument("raw")
    sub.add_parser("count")
    a = ap.parse_args(argv)
    if a.cmd == "table":
        for group in a.group or GROUPS:
            ps = gap_probes(gap_words(by_decoder=a.gaps_by_decoder)) if group == "gaps" \
                else probes(group)
            what = "encoding gaps" if group == "gaps" else "encoding bits"
            (pathlib.Path(a.out) / f"{GROUPS[group]}.toml").write_text(table_text(ps, what))
    elif a.cmd == "eval":
        sys.stdout.write(evaluate(pathlib.Path(a.table), pathlib.Path(a.raw).read_text()))
    else:
        sys.stdout.write(count())
    return 0


if __name__ == "__main__":
    sys.exit(main())
