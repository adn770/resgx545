#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The PDS encoding-bit probes: does the hardware read the bits no form of isa/pds/ maps?

A form's unmapped bits are those neither in its mask (the identifying bits) nor in one of its
fields. For each form (BASES) a base instruction with a visible effect runs in the template
`pds_bits.s` (pds_dump.s with a POST slot after the sixteen douta writes and an END slot for
the halt) as a fill's PDS secondary program; case 0 is the base word and every other case the
same word with one unmapped bit flipped, as a raw `.word`. A bit the hardware ignores leaves
the readback (o0, the scratch dwords) as case 0 left it; one it reads changes it, or hangs or
faults the job. mov32's and alum's unused bits are left out: their own probes
(pds-moves-mov32-spare, pds-alu-alum-spare) measured them. A form with no unmapped bit left has
no probe. probes/pds/encoding-bits.toml, -flow.toml and -memory.toml were written before the
runs gave bra and call 24-bit targets, abs's ds1[n] bits 15:10 and mov128's bit 15 (the field
lastpair since 11.14), with the forms as they were then (BEFORE, BEFORE_PAT); `table --before`
writes them again, byte for byte (test_pds_bits.py).

    pds_bits.py table DIR [--before]   write the three tables into DIR (probes/pds/): GROUPS;
                                       --before with the fields of BEFORE, as committed
    pds_bits.py table DIR --mov128     write mov128-bit15.toml (11.14, Q077) into DIR
    pds_bits.py eval TABLE RAW         each probe's cases against its base, from a saved run

The mov128 follow-up (11.14, Q077) gives every input dword its own marker (MOV128_MARKS: ds0[n]
0xA00000nn, ds1[n] 0xB00000nn), so that `locate` names the dword each value read back came from,
and sets mov128's bit 15 with each of its other unmapped bits in turn (MOV128_CASES), every case
MOV128_RUNS times; a second probe repeats a few cases with another set of markers.
"""
from __future__ import annotations

import argparse
import dataclasses
import pathlib
import re
import sys
import tempfile
import tomllib

import probe

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ISA = ROOT / "isa" / "pds"
TEMPLATES = ROOT / "probes" / "pds" / "templates"
TEMPLATE = "pds_bits.s"
# The inputs: ds0[48..55] = A..H, ds1[48..55] = I..P, with zeros and negatives for the tests.
INPUTS = {"A": 0x11111111, "B": 0x22222222, "C": 0x80000003, "D": 0x00000000,
          "E": 0x55555555, "F": 0x66666666, "G": 0x77777777, "H": 0x0000FF01,
          "I": 0x99999999, "J": 0xAAAAAAAA, "K": 0x00000000, "L": 0x8000000B,
          "M": 0xCCCCCCCC, "N": 0xDDDDDDDD, "O": 0xEEEEEEEE, "P": 0x00010203}
LOW = 0x10000                  # the scratch mapped in the first MiB (the memory probes' address)
NAMED = {"PRED": "26:24", "DST7": "6:0"}
SLOTS = ("OP", "POST", "END")
# The tables, so that each runs as a batch of its own: the data operations, the flow control
# (whose flipped bits may send the program anywhere and hang the job), and load, store and the
# fences (with the scratch mapped low, the kernel's vm_low switch).
GROUPS = {"data": "encoding-bits", "flow": "encoding-bits-flow",
          "memory": "encoding-bits-memory"}
FLOW = {"bra", "call", "rtn", "halt", "nop"}
# The bits the forms left unmapped when the committed tables were written, which the runs then
# mapped (E259, E260, E261, E379): bra's and call's target bits 23:19, abs ds1[n]'s bit 15 and
# mov128's bit 15, whose pattern then ended with the swap flag only.
BEFORE = {2380: 0x00f80000, 2390: 0x00f80000, 2290: 0x00008000, 2240: 0x00008000}
BEFORE_PAT = {2240: "{0}mov128 ds[{1}], ds[{2}]{3}"}


class BitsError(Exception):
    pass


# The mov128 follow-up (Q077): ds0[n] and ds1[n] of the inputs (n 2-9) each hold their own marker.
_PARAM_DWORDS = {"A": (0, 2), "B": (0, 3), "C": (0, 4), "D": (0, 5), "E": (0, 6), "F": (0, 7),
                 "G": (0, 8), "H": (0, 9), "I": (1, 2), "J": (1, 3), "K": (1, 4), "L": (1, 5),
                 "M": (1, 6), "N": (1, 7), "O": (1, 8), "P": (1, 9)}
MOV128_MARKS = {k: f"0x{(0xA0000000, 0xB0000000)[b] | n:08X}" for k, (b, n) in _PARAM_DWORDS.items()}
MOV128_MARKS2 = {k: f"0x{(0xC0000000, 0xE0000000)[b] | n << 8 | n:08X}"
                 for k, (b, n) in _PARAM_DWORDS.items()}
MOV128_RUNS = 3
_COMPLEMENT = "\n".join(f"not ds{b}[{n}], ds{b}[{n}]" for b in (0, 1) for n in range(48, 56))
_MR_FIRST = "movs mr, ds0[2], ds0[3], ds1[2], ds1[3]"
# (label, destination, source row, extra bits, a line before the mov128)
MOV128_CASES = (
    ("ds[52], row 2, control without bit 15", 52, 2, 0, ""),
    ("ds[52], row 2 + bit 15", 52, 2, 1 << 15, ""),
    *((f"ds[52], row 2 + bit 15 + bit {b}", 52, 2, 1 << 15 | 1 << b, "")
      for b in (16, 17, 18, 19, 20, 21, 22, 23, 9, 7, 1, 0)),
    ("ds[52], row 2 + bit 15 + bits 23:16", 52, 2, 1 << 15 | 0xff << 16, ""),
    ("ds[52], row 2 + bit 15 + bits 1:0", 52, 2, 1 << 15 | 3, ""),
    ("ds[52], row 0 + bit 15", 52, 0, 1 << 15, ""),
    ("ds[52], row 4 + bit 15", 52, 4, 1 << 15, ""),
    ("ds[52], row 24 + bit 15", 52, 24, 1 << 15, ""),
    ("ds[48], row 2 + bit 15", 48, 2, 1 << 15, ""),
    ("ds[52], row 2 + bit 15, mr written first", 52, 2, 1 << 15, _MR_FIRST),
)
# The mr follow-up: (label, the lines before mov128 ds[52], ds[4] with bit 15).
MOV128_MR = (
    ("movs mr from ds0[6-7], ds1[6-7]", "movs mr, ds0[6], ds0[7], ds1[6], ds1[7]"),
    ("movs mr from ds0[6-7], ds1[6-7], then ds0[6] complemented",
     "movs mr, ds0[6], ds0[7], ds1[6], ds1[7]\nnot ds0[6], ds0[6]"),
    ("movs mr from ds0[2-3], ds1[6-7]", "movs mr, ds0[2], ds0[3], ds1[6], ds1[7]"),
    ("movs douta from ds0[6] before, no mr write", "movs douta, ds0[6], ds1[10], ds0[6], ds0[6]"),
    ("movs mr from ds0[2-3], then movs douta from ds0[6]",
     "movs mr, ds0[2], ds0[3], ds1[2], ds1[3]\nmovs douta, ds0[6], ds1[10], ds0[6], ds0[6]"),
    ("movs mr from ds0[2-3], mov64 ds0[48], mr01 read, then the mov128",
     "movs mr, ds0[2], ds0[3], ds1[2], ds1[3]\nmov64 ds0[48], mr01"),
    ("movs mr from ds0[50-51] (temporaries), then ds0[50] complemented again",
     "movs mr, ds0[50], ds0[51], ds1[50], ds1[51]\nnot ds0[50], ds0[50]"),
    ("movs mr from ds0[50-51] (temporaries), then mov32 ds0[50], ds0[2]",
     "movs mr, ds0[50], ds0[51], ds1[50], ds1[51]\nmov32 ds0[50], ds0[2]"),
    ("movs mr from ds0[2-3], mov128 without bit 15 (control)",
     "movs mr, ds0[2], ds0[3], ds1[2], ds1[3]"),
)
MOV128_CASES2 = tuple(c for c in MOV128_CASES if c[0].endswith(("control without bit 15",
                                                                "row 2 + bit 15", "bit 16",
                                                                "row 24 + bit 15")))


def mov128_word(dst: int, row: int) -> int:
    """mov128 ds[dst], ds[2 row] (isa/pds/forms/mov128.toml: dst/2 in 6:2, row in 14:10),
    always executed (predicate 7)."""
    return 0x04 << 27 | 7 << 24 | row << 10 | dst // 2 << 2


def _mov128_probe(name: str, question: str, marks: dict, cases: tuple) -> dict:
    out, labels = [], []
    for run in range(1, MOV128_RUNS + 1):
        for label, dst, row, extra, before in cases:
            word = mov128_word(dst, row) | extra
            op = "\n".join(x for x in (_COMPLEMENT, before,
                                       f".word /* {label} */ 0x{word:08X}") if x)
            out.append([op, "nop", "halt"])
            labels.append(f"run {run}: {label}")
    return {"name": name, "question": question, "isa": "pds", "source": TEMPLATE,
            "params": dict(marks), "inputs": list(SLOTS), "labels": labels, "cases": out}


def _mr_probe() -> dict:
    out, labels, word = [], [], mov128_word(52, 2)
    for run in range(1, MOV128_RUNS + 1):
        for label, before in MOV128_MR:
            w = word if "without bit 15" in label else word | 1 << 15
            out.append(["\n".join((_COMPLEMENT, before, f".word /* {label} */ 0x{w:08X}")),
                        "nop", "halt"])
            labels.append(f"run {run}: {label}")
    return {"name": "pds-mov128-bit15-mr",
            "question": "mov128 ds[52], ds[4] with bit 15 after movs writes to mr and to douta: "
                        "whether it reads mr's value or the registers mr names, and mr only; "
                        "recorded", "isa": "pds", "source": TEMPLATE, "params": dict(MOV128_MARKS),
            "inputs": list(SLOTS), "labels": labels, "cases": out}


def mov128_probes() -> list[dict]:
    """The mov128 bit 15 follow-up (Q077): its three probes."""
    return [
        _mov128_probe("pds-mov128-bit15-companions",
                      "mov128 with bit 15 and each other unmapped bit, every input dword its own "
                      "marker, the temporaries complemented first: which dwords it reads; "
                      "recorded", MOV128_MARKS, MOV128_CASES),
        _mov128_probe("pds-mov128-bit15-markers2",
                      "the same with another set of markers, a few cases: the dwords read follow "
                      "the data; recorded", MOV128_MARKS2, MOV128_CASES2),
        _mr_probe(),
    ]


def locate(value: int, params: dict) -> str | None:
    """The input dword (ds0[n] or ds1[n]) whose marker value is, ~ for a complemented one."""
    for k, v in params.items():
        b, n = _PARAM_DWORDS[k]
        if int(v, 16) == value:
            return f"ds{b}[{n}]"
        if int(v, 16) ^ 0xFFFFFFFF == value:
            return f"~ds{b}[{n}]"
    return None


@dataclasses.dataclass(frozen=True)
class Base:
    """A form's base instruction (`test`), the lines around it, and its slot."""
    order: int                 # the form's order in isa/pds/forms
    name: str                  # the probe.s name, after pds-<table>-
    test: str
    setup: tuple = ()
    after: tuple = ()
    slot: str = "OP"           # OP, POST or END
    low: bool = False          # the probe maps the scratch at LOW (load, store, the fences)

    @property
    def group(self) -> str:
        return "memory" if self.low else "flow" if self.name in FLOW else "data"


# Every form but mov32 and alum. The tests set p0-p2 false first, then the one under test
# sets p0 true; a predicate it writes instead shows in ds0[52]-ds0[54].
_TST_SETUP = ("tstz p0, ds1[48]", "tstz p1, ds1[48]", "tstz p2, ds1[48]")
_TST_AFTER = ("(p0) mov32 ds0[52], ds1[48]", "(p1) mov32 ds0[53], ds1[49]",
              "(p2) mov32 ds0[54], ds1[51]")
BASES = (
    Base(2190, "movs", "movs douta, ds0[50], ds1[10], ds0[50], ds0[50]", slot="POST"),
    Base(2200, "movsa", "movsa douta, ds0[50], ds1[10], ds0[50], ds0[50]", slot="POST"),
    Base(2210, "mov16", "mov16 ds0[105], ds1[49].h"),
    Base(2230, "mov64", "mov64 ds0[52], ds1[48]"),
    Base(2240, "mov128", "mov128 ds[52], ds[4]"),
    Base(2250, "load", f"load 0x{LOW + 0x100:08x}, ds0[52-53]", after=("rfence",), low=True),
    Base(2260, "store", f"store 0x{LOW + 0x100:08x}, ds1[48-55]", low=True),
    Base(2270, "alu", "add ds0[52], ds0[49], ds1[49]"),
    Base(2280, "mul", "mul ds0[52], ds0[49].l, ds1[49].l"),
    Base(2290, "abs-ds1", "abs ds0[52], ds1[3]", setup=("alum signed",)),
    Base(2300, "abs", "abs ds0[52], ds0[50]", setup=("alum signed",)),
    Base(2310, "not-ds1", "not ds0[52], ds1[3]"),
    Base(2320, "not", "not ds0[52], ds0[50]"),
    Base(2330, "fence", "rfence", setup=(f"load 0x{LOW + 0x100:08x}, ds0[52-53]",), low=True),
    Base(2340, "tstz-ds1", "tstz p0, ds1[50]", _TST_SETUP, _TST_AFTER),
    Base(2350, "tstz", "tstz p0, ds0[51]", _TST_SETUP, _TST_AFTER),
    Base(2360, "tstn-ds1", "tstn p0, ds1[51]", _TST_SETUP, _TST_AFTER),
    Base(2370, "tstn", "tstn p0, ds0[50]", _TST_SETUP, _TST_AFTER),
    Base(2380, "bra", "bra skip", after=("mov32 ds0[52], ds1[48]", "skip: mov32 ds0[53], ds1[49]")),
    Base(2390, "call", "call sub", after=("mov32 ds0[52], ds1[48]", "bra out",
                                         "sub: mov32 ds0[53], ds1[49]", "rtn", "out: nop")),
    Base(2400, "rtn", "rtn", setup=("call sub", "mov32 ds0[52], ds1[48]", "bra out",
                                    "sub: mov32 ds0[53], ds1[49]"), after=("out: nop",)),
    Base(2410, "halt", "halt", slot="END"),
    Base(2420, "nop", "nop", after=("mov32 ds0[52], pc.0",)),
    Base(2440, "shl", "shl ds0[52], ds0[49], 4"),
    Base(2450, "shr", "shr ds0[52], ds0[49], 4"),
)


def _mask(expr: str) -> int:
    expr = expr.replace("OPM", "m(31, 27)")
    return eval(expr, {"__builtins__": {}},  # noqa: S307 - the table's own expressions
                {"m": lambda h, lo: ((1 << (h - lo + 1)) - 1) << lo, "b": lambda n: 1 << n})


def _bits_of(spec: str) -> int:
    m = 0
    for c in spec.split():
        hi, lo = (int(x) for x in c.split(":")) if ":" in c else (int(c), int(c))
        m |= ((1 << (hi - lo + 1)) - 1) << lo
    return m


def forms(isa: pathlib.Path = ISA, before: bool = False) -> list[dict]:
    """Every form of isa/pds/forms: order, op, pattern, mask, val and its unmapped bits;
    `before`: with the bits of BEFORE unmapped again."""
    out = []
    for f in sorted((isa / "forms").glob("*.toml")):
        for fm in tomllib.loads(f.read_text())["form"]:
            mask, cov = _mask(fm["mask"]), _mask(fm["mask"])
            for fd in fm.get("fields", []):
                spec = fd.split("=", 1)[1].split(None, 1)
                cov |= _bits_of(spec[1] if len(spec) > 1 else NAMED[spec[0]])
            if before:
                cov &= ~BEFORE.get(fm["order"], 0)
            pat = BEFORE_PAT.get(fm["order"], fm["pat"]) if before else fm["pat"]
            out.append({"order": fm["order"], "op": fm["op"], "pat": pat, "mask": mask,
                        "val": _mask(fm["val"]), "unmapped": ~cov & 0xFFFFFFFF})
    return out


def bits(mask: int) -> list[int]:
    return [b for b in range(32) if mask >> b & 1]


def _slots(base: Base, test: str) -> list[str]:
    lines = {"OP": "\n".join([*base.setup, test, *base.after]) if base.slot == "OP" else "nop",
             "POST": test if base.slot == "POST" else "nop", "END": "halt"}
    if base.slot == "END":
        lines["END"] = test
    return [lines[s] for s in SLOTS]


def _listing(base: Base, test: str) -> list[int]:
    p = probe.Probe(name="x", question="", source=TEMPLATE,
                    params={k: f"0x{v:08X}" for k, v in INPUTS.items()},
                    inputs=list(SLOTS), cases=[], hypotheses={}, isa="pds")
    text = probe.render(p, _slots(base, test), (TEMPLATES / TEMPLATE).read_text())
    with tempfile.TemporaryDirectory() as d:
        out = probe._assemble(text, pathlib.Path(d) / "x.bin", "pds")
    return [int(m.group(1), 16) for m in re.finditer(r"^\d+: 0x([0-9A-F]{8})\t", out, re.M)]


def base_word(base: Base) -> int:
    """The word the base instruction assembles to, in place (its labels resolved)."""
    a, b = _listing(base, base.test), _listing(base, "nop" if base.test != "nop" else "halt")
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(a) != len(b) or len(diff) != 1:
        raise BitsError(f"{base.name}: the base is not one word in place")
    return a[diff[0]]


def probes(group: str | None = None, isa: pathlib.Path = ISA, before: bool = False) -> list[dict]:
    """The [[probe]] entries of one group's table (every group's: None), in BASES order;
    `before`: as the committed tables (BEFORE)."""
    fs = {f["order"]: f for f in forms(isa, before)}
    out = []
    for base in BASES:
        if group and base.group != group or not fs[base.order]["unmapped"]:
            continue
        f, word = fs[base.order], base_word(base)
        flips = bits(f["unmapped"])
        cases = [_slots(base, f".word /* base */ 0x{word:08X}")]
        cases += [_slots(base, f".word /* bit {b} */ 0x{word ^ 1 << b:08X}") for b in flips]
        # the campaign runner wants pds-<table>-<case>
        p = {"name": f"pds-{GROUPS[base.group]}-{base.name}",
             "question": f"which unmapped bits of {f['pat']!r} the hardware reads "
                         f"(0x{f['unmapped']:08x}), base {base.test!r}, recorded; may hang",
             "isa": "pds", "source": TEMPLATE,
             "params": {k: f"0x{v:08X}" for k, v in INPUTS.items()}}
        if base.low:
            p["low"] = LOW
        p.update({"inputs": list(SLOTS), "labels": ["base"] + [f"bit {b}" for b in flips],
                  "cases": cases})
        out.append(p)
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


def table_text(ps: list[dict], about: str = "") -> str:
    """A table of the probes ps; it needs the vm_low switch if one of them maps low."""
    needs = ["render", "vm_low"] if any("low" in p for p in ps) else ["render"]
    head = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
            f"# pds {about or 'encoding bits'}: 0 sweeps, {len(ps)} probes (written by "
            "tools/usse-asm/pds_bits.py).",
            "# Each probe flips one unmapped bit of a form per case; case 0 is the base word."
            if not about else "# Every case runs MOV128_RUNS times (run k: in its label).",
            f"needs = {_toml(needs)}"]
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
        elif o.o0 == base.o0 and dict(o.scratch) == want:
            out.append((label, "same"))
        else:
            got = dict(o.scratch)
            d = [f"+0x{k:03x} 0x{want.get(k, probe.SCRATCH_FILL | k // 4):08x} -> "
                 f"0x{got.get(k, probe.SCRATCH_FILL | k // 4):08x}"
                 for k in sorted(set(want) | set(got)) if want.get(k) != got.get(k)]
            if o.o0 != base.o0:
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
        lines.append(f"{p.name}: {len(same)} of {len(got)} bits same as the base")
        lines += [f"  {lab}: {s}" for lab, s in got if s != "same"]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("table")
    t.add_argument("out")
    t.add_argument("--before", action="store_true", help="the fields of BEFORE, as committed")
    t.add_argument("--mov128", action="store_true", help="the mov128 bit 15 follow-up (Q077)")
    e = sub.add_parser("eval")
    e.add_argument("table")
    e.add_argument("raw")
    a = ap.parse_args(argv)
    if a.cmd == "table" and a.mov128:
        (pathlib.Path(a.out) / "mov128-bit15.toml").write_text(
            table_text(mov128_probes(), about="mov128 bit 15 (Q077)"))
    elif a.cmd == "table":
        for group, name in GROUPS.items():
            (pathlib.Path(a.out) / f"{name}.toml").write_text(
                table_text(probes(group, before=a.before)))
    else:
        sys.stdout.write(evaluate(pathlib.Path(a.table), pathlib.Path(a.raw).read_text()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
