#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The model behind the hypotheses of probes/pds/*.toml, and the check of the tables against it.

Every PDS fill probe runs `pds_dump.s`: inputs A-H in ds0[2]-ds0[9], I-P in ds1[2]-ds1[9],
then OP, then all sixteen back through douta. A hypothesis of such a probe is a literal
prediction of the sixteen readbacks of each case. `run` computes them: a small model of the
operations the probes use, configured per hypothesis (AS_NAMED, the readings the names
suggest; SETTLED, the readings the hardware has settled, the base of the later probes, each of
which leaves one open). `model()` lists the probes the model covers, with the cases of each
and what each hypothesis predicts.

`check_table` recomputes the hypotheses of a resgx545 table and returns the differences. A
table probe is matched to the model's by its OP parameter and its cases, not by its name:
the same inputs run the same program. Probes the model does not cover (hosts other than the
fill, recorded sweeps without hypotheses) are left alone; `--check` lists the PDS fill probes
with hypotheses that it does not cover, and fails when a probe of the model matches no table
probe (its cases or OP were edited).

The check keeps the tables and the model consistent (it regenerates the hypotheses from the
model that wrote them, so it detects a hand edit, not a wrong claim); what tests the model
itself are the hardware results.

    python3 tools/usse-asm/pds_tables.py --check     # every probes/pds table; non-zero on a diff
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import tomllib

M = 0xFFFFFFFF

# The readings that are open. AS_NAMED is the one the names suggest.
AS_NAMED = {
    "nor_nand": "named",      # or "swapped"
    "addsub": "wrap",         # "wrap" modular, "sat" unsigned saturating, "rev" sub = ds1 - src
    "flag_ops": {"add", "sub", "adc", "sbc", "and", "or", "xor", "nor", "nand", "not", "abs",
                 "shl", "shr"},   # the ops that set aluz/alun; None: the flags never test true
    "tstn": "sign",           # "sign": bit 31; "le0": signed <= 0
    "test_pred": True,        # a predicated tstz/tstn obeys its predicate
    "shift": "logical",       # "logical", "arith" (shr keeps the sign), "mod32" (amount & 31),
                              # "u7": logical, the amount unsigned 0-127 (32 and up give 0)
    "call": "stack",          # "stack": a return stack; "link": one return register
    "mul": "alum",            # 16-bit halves signed under alum signed; "unsigned", "signed"
    "alum_shr": False,        # alum signed also makes shr arithmetic
    "carry": "borrow",        # add/sub set c (carry out / borrow); adc adds it, sbc
                              # subtracts it; "notborrow": sub sets c = no borrow and sbc
                              # subtracts !c; "none": adc/sbc are add/sub; "high": add/sub
                              # leave the high dword of the exact result (+1 carry, -1
                              # borrow), which adc and sbc both add
    "abs": "wrap",            # abs(0x80000000): "wrap" itself, "sat" 0x7fffffff; "alum": the
                              # identity unless alum signed (then "wrap"); "id": always
    "consts": "rw",           # a write to ds0/ds1[0..47] other than the inputs: "rw" lands,
                              # "ro" is dropped, "alias16" lands in ds[48 + (n & 15)],
                              # "alias48" in ds[(n + 48) % 64] if that is 48 or more
    "alun": "always",         # "signed": alun is set (by a negative result) only under alum
                              # signed; "never": not even then
    "mov16": "low",           # the half into dst's low half, high kept; "zext"; "same" half;
                              # "halves": dsB[n] names half n & 1 (1 high) of dsB[n >> 1], the
                              # other half kept; "halves_zext": the other half cleared;
                              # "halves_swapped": n & 1 = 1 is the low half
    "mov64": "named",         # "reversed": the pair lands swapped
    "mov128": "rows",         # ds[2k] = ds0[2k], ds0[2k+1], ds1[2k], ds1[2k+1]; "ds0": ds0[2k..]
    "swap": "pairs",          # mov128 swap exchanges the two pairs; "words": within each pair
    "carry_clear": set(),     # the ops (besides add/sub/adc/sbc) that leave the carry 0
    "mov16_ro": "temp",       # a mov16 into dsB[0..47] (which lands in a temporary, "consts"):
                              # its other half from the temporary ("temp"), from the constant
                              # row ("row"), or cleared ("zero")
    "flag_clear": set(),      # ops that leave aluz and alun false
    "carry_adc": "high",      # after adc/sbc: "high" the high dword of their exact result,
                              # "keep" the carry they used, "clear" 0
    "carry_signed": "unsigned",   # add/sub's carry under alum signed: "unsigned" the high
                              # dword of the unsigned result, "signed" of the signed one,
                              # "none" 0, "overflow" what makes exact = signed(r) + c * 2^32
    "adc_signed": "unsigned",  # adc/sbc's carry under alum signed: "unsigned" as unsigned,
                              # "overflow" as add/sub's signed overflow, "keep" the old one
    "ashr_big": "sign",       # an arithmetic shr by 32-127: "sign" fills with the sign,
                              # "zero" gives 0, "mod32" shifts by the amount & 31
}

# The readings the hardware settled: the base of the later probes, each of which leaves one
# of them open.
SETTLED = dict(AS_NAMED, flag_ops={"add", "sub"}, alun="signed", shift="u7", alum_shr=True,
               call="link", carry="high", abs="alum", consts="alias16", mov16="halves")

_LINE = re.compile(r"^(?:(\w+):\s*)?(?:\((p[0-2]|aluz|alun)\)\s*)?(\w+)\s*(.*)$")
_REG = re.compile(r"^ds([01])\[(\d+)\](?:\.([lh]))?$")
_QUAD = re.compile(r"^ds\[(\d+)\]$")


class Fail(Exception):
    """The program would not finish (the job fails)."""


def _sext32(n: int) -> int:
    """A 32-bit value as a signed integer."""
    n &= M
    return n - (1 << 32) if n >> 31 else n


def run(op: str, ds0: list, ds1: list, cfg: dict) -> list | str:
    """Run OP from the probe's start; the readback (ds0[2..9], ds1[2..9]) or "fail"."""
    banks = [list(ds0), list(ds1)]
    lines = [ln.split(";")[0].strip() for ln in op.split("\n")]
    prog, labels = [], {}
    for ln in lines:
        if not ln:
            continue
        m = _LINE.match(ln)
        if not m:
            raise ValueError(f"cannot model {ln!r}")
        label, pred, mn, rest = m.groups()
        if label:
            labels[label] = len(prog)
        if mn:
            prog.append((pred, mn, [a.strip() for a in rest.split(",")] if rest else []))
    p = [None, None, None]
    flags = None                # (z, n) once set
    carry = None
    alum_signed = None
    stack: list = []
    link = None

    def get(r):
        m = _REG.match(r)
        if not m:
            raise ValueError(f"cannot model the source {r}")
        return banks[int(m.group(1))][int(m.group(2))]

    def put(r, v):
        m = _REG.match(r)
        n = int(m.group(2))
        if cfg["consts"] != "rw" and n < 48 and not 2 <= n <= 9:
            # a constant row (2..9 stand for the temporaries 48..55)
            t = {"ro": None, "alias16": 48 + (n & 15),
                 "alias48": (n + 48) % 64 if (n + 48) % 64 >= 48 else None}[cfg["consts"]]
            if t is None:
                return
            n = t - TEMPS if 48 <= t <= 55 else t
        banks[int(m.group(1))][n] = v & M

    def half(r):
        """A .l/.h operand: the half, and whether it is the high one."""
        m = _REG.match(r)
        v = banks[int(m.group(1))][int(m.group(2))]
        return ((v >> 16) if m.group(3) == "h" else v) & 0xFFFF, m.group(3) == "h"

    def quad(r):
        """The four dwords mov128 names ds[n] (the mov128 reading)."""
        n = int(_QUAD.match(r).group(1))
        if cfg["mov128"] == "rows":
            return [(0, n), (0, n + 1), (1, n), (1, n + 1)]
        return [(0, n), (0, n + 1), (0, n + 2), (0, n + 3)]

    def test(pred):
        if pred is None:
            return True
        if pred in ("aluz", "alun"):
            if cfg["flag_ops"] is None:
                return False
            if flags is None:
                raise ValueError("a flag read before any op set it")
            return flags[0] if pred == "aluz" else flags[1]
        v = p[int(pred[1])]
        if v is None:
            raise ValueError(f"{pred} read before a test set it")
        return v

    def signed_carry(x, y, unsigned, sign):
        """add/sub's high dword: as measured unsigned, or by carry_signed under alum signed."""
        if not alum_signed or cfg["carry_signed"] == "unsigned":
            return unsigned
        if cfg["carry_signed"] == "none":
            return 0
        sx = lambda v: v - (1 << 32) if v >> 31 else v                     # noqa: E731
        exact = sx(x) + sign * sx(y)
        if cfg["carry_signed"] == "overflow":
            return (exact - sx(exact & M)) >> 32
        return exact >> 32

    def setflags(r):
        nonlocal flags
        flags = (r & M == 0, bool(r & 0x80000000)
                 and (cfg["alun"] == "always" or cfg["alun"] == "signed" and bool(alum_signed)))

    pc, steps, last = 0, 0, None
    while pc < len(prog):
        steps += 1
        if steps > 1000:
            raise Fail()
        if last in cfg["carry_clear"] and carry is not None:
            carry = 0
        if last in cfg["flag_clear"]:
            flags = (False, False)
        pred, mn, a = prog[pc]
        last = mn
        pc += 1
        if mn in ("tstz", "tstn"):
            if cfg["test_pred"] and not test(pred):
                continue
            x = get(a[1])
            if mn == "tstz":
                p[int(a[0][1])] = x == 0
            elif cfg["tstn"] == "sign":
                p[int(a[0][1])] = bool(x >> 31)
            else:
                p[int(a[0][1])] = x == 0 or bool(x >> 31)
            if cfg["flag_ops"] is not None and mn in cfg["flag_ops"]:
                setflags(x)
            continue
        if not test(pred):
            continue
        if mn in ("nop", "movs", "movsa"):       # a port write changes no register
            continue
        if mn == "bra":
            pc = labels[a[0]]
            continue
        if mn == "call":
            if cfg["call"] == "stack":
                stack.append(pc)
            else:
                link = pc
            pc = labels[a[0]]
            continue
        if mn == "rtn":
            if cfg["call"] == "stack":
                pc = stack.pop()
            else:
                pc = link
            continue
        if mn == "mov32":
            put(a[0], get(a[1]))
            continue
        if mn == "alum":
            alum_signed = a[0] == "signed"
            continue
        if mn == "mov16":
            h, high = half(a[1])
            if cfg["mov16"].startswith("halves"):
                m = _REG.match(a[0])
                b, n = int(m.group(1)), int(m.group(2))
                hi = bool(n & 1) != (cfg["mov16"] == "halves_swapped")
                d = n >> 1
                old = 0 if cfg["mov16"] == "halves_zext" else banks[b][d]
                if cfg["consts"] == "alias16" and d < 48 and not 2 <= d <= 9:
                    # a constant row: the half lands in its temporary
                    t = 48 + (d & 15)
                    t = t - TEMPS if t <= 55 else t
                    old = {"temp": banks[b][t], "row": banks[b][d], "zero": 0}[cfg["mov16_ro"]]
                    d = t
                banks[b][d] = (old & 0xFFFF) | h << 16 if hi else (old & 0xFFFF0000) | h
                if cfg["flag_ops"] is not None and mn in cfg["flag_ops"]:
                    setflags(banks[b][d])
                continue
            old = get(a[0])
            if cfg["mov16"] == "zext":
                put(a[0], h)
            elif cfg["mov16"] == "same" and high:
                put(a[0], (old & 0xFFFF) | h << 16)
            else:
                put(a[0], (old & 0xFFFF0000) | h)
            continue
        if mn == "mov64":
            d, s_ = _REG.match(a[0]), _REG.match(a[1])
            src = [banks[int(s_.group(1))][int(s_.group(2)) + k] for k in (0, 1)]
            if cfg["mov64"] == "reversed":
                src.reverse()
            for k in (0, 1):
                banks[int(d.group(1))][int(d.group(2)) + k] = src[k]
            continue
        if mn == "mov128":
            src = [banks[b][n] for b, n in quad(a[1])]
            if len(a) > 2 and a[2] == "swap":
                src = src[2:] + src[:2] if cfg["swap"] == "pairs" else \
                    [src[1], src[0], src[3], src[2]]
            for (b, n), v in zip(quad(a[0]), src):
                banks[b][n] = v
            continue
        if mn == "mul":
            (x, _), (y, _) = half(a[1]), half(a[2])
            signed = cfg["mul"] == "signed" or (cfg["mul"] == "alum" and alum_signed)
            if cfg["mul"] == "alum" and alum_signed is None:
                raise ValueError("mul before an alum")
            if signed:
                x, y = (x ^ 0x8000) - 0x8000, (y ^ 0x8000) - 0x8000
            put(a[0], x * y)
            if cfg["flag_ops"] is not None and "mul" in cfg["flag_ops"]:
                setflags(x * y)
            continue
        if mn in ("shl", "shr"):
            x, n = get(a[1]), _sext32(int(a[2], 0))
            if cfg["shift"] == "u7":
                left, n = mn == "shl", n & 0x7F
            elif cfg["shift"] == "mod32":
                left, n = mn == "shl", n & 31
            else:
                left = (mn == "shl") == (n >= 0)
                n = abs(n)
            if left:
                r = (x << n) & M if n < 32 else 0
            elif cfg["alum_shr"] and alum_signed and n >= 32 and cfg["ashr_big"] != "sign":
                ext = (x | ~M) if x >> 31 else x
                r = 0 if cfg["ashr_big"] == "zero" else (ext >> (n & 31)) & M
            elif (cfg["shift"] == "arith" or (cfg["alum_shr"] and alum_signed)) and x >> 31:
                r = ((x | ~M) >> n) & M if n < 32 else M
            else:
                r = x >> n if n < 32 else 0
        elif mn in ("not", "abs"):
            x = get(a[1])
            r = ~x & M if mn == "not" else (-x & M if x >> 31 else x)
            if mn == "abs" and x == 0x80000000 and cfg["abs"] == "sat":
                r = 0x7FFFFFFF
            if mn == "abs" and (cfg["abs"] == "id" or cfg["abs"] == "alum" and not alum_signed):
                r = x
        else:
            x, y = get(a[1]), get(a[2])
            name = mn
            if cfg["nor_nand"] == "swapped" and mn in ("nor", "nand"):
                name = "nand" if mn == "nor" else "nor"
            cin = 0
            if name in ("adc", "sbc") and cfg["carry"] == "high":
                if carry is None:
                    raise ValueError(f"{name} before any op set the carry")
                exact = x + y + carry if name == "adc" else x - y + carry
                r = exact & M
                if cfg["carry_adc"] == "high" and alum_signed and cfg["adc_signed"] != "unsigned":
                    if cfg["adc_signed"] == "overflow":
                        sx = lambda v: v - (1 << 32) if v >> 31 else v             # noqa: E731
                        e = sx(x) + (sx(y) if name == "adc" else -sx(y)) + carry
                        carry = (e - sx(r)) >> 32
                elif cfg["carry_adc"] == "high":
                    carry = (exact >> 32) if exact > M else (-1 if exact < 0 else 0)
                elif cfg["carry_adc"] == "clear":
                    carry = 0
                put(a[0], r)
                if cfg["flag_ops"] is not None and mn in cfg["flag_ops"]:
                    setflags(r)
                continue
            if name in ("adc", "sbc") and cfg["carry"] != "none":
                if carry is None:
                    raise ValueError(f"{name} before any op set the carry")
                cin = int(carry) if cfg["carry"] == "borrow" or name == "adc" else int(not carry)
            if name in ("adc", "sbc"):
                name = name.replace("adc", "add").replace("sbc", "sub")
            if name == "add":
                r = min(x + y + cin, M) if cfg["addsub"] == "sat" else (x + y + cin) & M
                carry = x + y + cin > M
                if cfg["carry"] == "high":
                    carry = signed_carry(x, y, int(carry), 1)
            elif name == "sub":
                if cfg["addsub"] == "sat":
                    r = max(x - y - cin, 0)
                elif cfg["addsub"] == "rev":
                    r = (y - x - cin) & M
                else:
                    r = (x - y - cin) & M
                borrow = x < y + cin
                carry = borrow if cfg["carry"] != "notborrow" else not borrow
                if cfg["carry"] == "high":
                    carry = signed_carry(x, y, -int(borrow), -1)
            else:
                r = {"and": x & y, "or": x | y, "xor": x ^ y, "nor": ~(x | y) & M,
                     "nand": ~(x & y) & M}[name]
        put(a[0], r)
        if cfg["flag_ops"] is not None and mn in cfg["flag_ops"]:
            setflags(r)
    return banks[0][2:10] + banks[1][2:10]


def predict(op: str, inputs: list, cfg: dict) -> list | str:
    ds0, ds1 = [0] * 64, [0] * 64
    ds0[2:10], ds1[2:10] = inputs[:8], inputs[8:16]
    # pds_dump.s rows 5-8: the douta control words (attribute 8 + k in ds0, k in ds1)
    ds0[10:18], ds1[10:18] = [0x800 + 0x100 * k for k in range(8)], [0x100 * k for k in range(8)]
    try:
        return run(op, ds0, ds1, cfg)
    except Fail:
        return "fail"


LETTERS = "ABCDEFGHIJKLMNOP"
TEMPS = 46      # pds_dump.s copies ds0/ds1[2..9] to [48..55]: the constants are read-only

_INPUT = re.compile(r"\bds([01]?)\[([2-9])\]")
_HALF = re.compile(r"ds([01])\[(\d+)\]")
READ_ONLY = {"movs", "movsa", "tstz", "tstn", "bra", "call", "rtn", "halt", "nop", "alum",
             "store", "rwfence"}      # mnemonics whose first operand is not a data register
# Sources (by bank) that encode only as constant rows: mov128 ds[0..30], abs ds1[0..31].
CONST_SRC = {"mov128": "", "abs": "1"}


def in_temps(op: str) -> str:
    """OP as it runs: its inputs ds0/ds1[2..9] moved to the temporaries pds_dump.s copies
    them to. A source with a constants-only encoding (CONST_SRC) stays on its row, which
    still holds the input if OP did not write it."""
    def move(m):
        return f"ds{m.group(1)}[{int(m.group(2)) + TEMPS}]"

    out, written = [], set()
    for ln in op.split("\n"):
        m = _LINE.match(ln.split(";")[0].strip())
        mn, regs = (m.group(3), _INPUT.findall(m.group(4))) if m else (None, [])
        if mn == "mov16":
            # the destination is a half index: halves 4..19 are ds0/ds1[2..9]
            d = _HALF.match(m.group(4))
            if d and 4 <= int(d.group(2)) <= 19:
                dst = f"ds{d.group(1)}[{int(d.group(2)) + 2 * TEMPS}]"
                rest = _INPUT.sub(move, m.group(4)[d.end():])
                ln = ln.replace(m.group(4), dst + rest)
                written.add(int(d.group(2)) >> 1)
                out.append(ln)
                continue
        if mn in CONST_SRC and regs[1:] and regs[1][0] == CONST_SRC[mn]:
            src = int(regs[1][1])
            if written & ({src, src + 1} if mn == "mov128" else {src}):
                raise ValueError(f"{mn} reads ds{regs[1][0]}[{src}] after OP wrote it: {ln!r}")
            ln = _INPUT.sub(move, ln, count=1)
        else:
            ln = _INPUT.sub(move, ln)
        if mn and mn not in READ_ONLY and regs:
            n = int(regs[0][1])
            written.update({n, n + 1} if mn in ("mov64", "mov128") else {n})
        out.append(ln)
    return "\n".join(out)


class Model:
    """The probes the model covers: for each, its cases (as a table writes them) and what
    each hypothesis predicts (None: nothing is predicted, the probe only records)."""

    def __init__(self):
        self.probes = []

    def probe(self, name, question, cases, hypotheses, *, labels=None, op=None, use=None,
              pixels=False):
        """cases: (op, 16 inputs) pairs (or 16 inputs with a fixed op); hypotheses: name ->
        a cfg override (on AS_NAMED, or on SETTLED when it has a "base" key) or the literal
        readbacks of a program the model cannot run; None for a probe that is only recorded.
        question, labels, use and pixels describe the probe in its table; the model keeps
        them out."""
        rows = [(c if isinstance(c, tuple) else (op, c)) for c in cases]
        fixed = op is not None
        preds = None
        if hypotheses:
            preds = {}
            for h, override in hypotheses.items():
                if isinstance(override, list):
                    preds[h] = override
                else:
                    over = dict(override)
                    cfg = dict(SETTLED if over.pop("base", None) else AS_NAMED, **over)
                    preds[h] = [predict(c_op, ins, cfg) for c_op, ins in rows]
        self.probes.append(ModelProbe(
            name, in_temps(op) if fixed else None,
            [([] if fixed else [in_temps(c_op)]) + list(ins) for c_op, ins in rows], preds))


class ModelProbe:
    def __init__(self, name, op, cases, hypotheses):
        self.name, self.op, self.cases, self.hypotheses = name, op, cases, hypotheses


def two(a8: list) -> list:
    """The same eight inputs in both banks."""
    return a8 + a8


DISTINCT = [0x11111111 * (i + 1) & M for i in range(8)]
EDGES = [0, M, 0x80000000, 0x7FFFFFFF, 1, 0xFFFFFFFE, 0x0000FFFF, 0xFFFF0000]
MARK = 0x000000AA            # H: the marker the predicated ops write (positive, nonzero)


def model() -> list:
    t = Model()

    # A0: the readback path itself
    t.probe("pds-readback",
            "PDS probes: do douta -> sa -> stad return the data words (the readback path itself)?",
            [two(DISTINCT), two(EDGES)],
            {"each data word reaches its attribute": {}},
            labels=["distinct words", "edge values"], op="nop")

    # A1b: writes to ds0/ds1[0..47]. ds1[1] (the unused word of row 0, 0) is copied back;
    # past the segment the rows hold what earlier tasks left, so ds0[36] and ds1[19] are
    # only written, to see where the writes land
    t.probe("pds-constants", "where does a write to ds0/ds1[0..47] go? writes ds1[1] (0), "
            "ds0[36] and ds1[19], copies ds1[1] back",
            [two(DISTINCT)], {"to the temporary ds[48 + (n & 15)]": {"consts": "alias16"},
                              "to ds[(n + 48) mod 64], dropped below 48": {"consts": "alias48"},
                              "dropped": {"consts": "ro"}, "writable": {}},
            labels=["distinct"],
            op="mov32 ds1[1], ds1[2]\nmov32 ds0[36], ds0[3]\nmov32 ds1[19], ds0[4]\n"
               "mov32 ds0[2], ds1[1]")

    # A1: the data rows, with different words in the two banks
    rows = [[0xA0000000 | i for i in range(16)], [0x0B000000 | (i << 8) | i for i in range(16)]]
    t.probe("pds-banks",
            "data segment rows: ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1]",
            rows, {"rows: the ds0 pair, then the ds1 pair": {}},
            labels=["A0-AF", "0B..."], op="nop")

    # A2: bitwise ops
    bit_op = "\n".join(["xor ds0[2], ds0[2], ds1[2]", "nor ds0[3], ds0[3], ds1[3]",
                        "nand ds0[4], ds0[4], ds1[4]", "and ds0[5], ds0[5], ds1[5]",
                        "or ds0[6], ds0[6], ds1[6]", "xor ds1[7], ds0[7], ds1[7]"])
    pats = [[0xF0F0F0F0] * 8 + [0xFF00FF00] * 8, [0, M] * 4 + [M, 0] * 4,
            [0x12345678] * 8 + [0x0F0F0F0F] * 8]
    t.probe("pds-bitwise", "xor, nor, nand, and, or: dst = src op ds1[n] on 32 bits",
            pats, {"as named": {}, "nor and nand swapped": {"nor_nand": "swapped"}},
            labels=["F0/FF00", "0/1s", "12345678/0F0F"], op=bit_op)

    # A3: add and sub
    as_op = "\n".join(["add ds0[2], ds0[2], ds1[2]", "sub ds0[3], ds0[3], ds1[3]",
                       "sub ds0[4], ds0[4], ds1[4]", "add ds0[5], ds0[5], ds1[5]"])
    as_cases = [[5, 9, 2, 7, 0, 0, 0, 0, 3, 4, 3, M, 0, 0, 0, 0],
                [M, 0, 0, 0x80000000, 0, 0, 0, 0, 1, 1, 1, 0x80000000, 0, 0, 0, 0],
                [0x7FFFFFFF, 0x80000000, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]]
    t.probe("pds-add-sub", "add and sub: 32-bit modular, and the operand order of sub",
            as_cases, {"modular, dst = src - ds1": {}, "unsigned saturating": {"addsub": "sat"},
                       "sub is ds1 - src": {"addsub": "rev"}},
            labels=["small", "wrap", "signed edges"], op=as_op)

    # A4: which ops set aluz/alun. A known add first, then op X into ds0[2], then marks.
    # marks with mov32, which no hypothesis lets set the flags
    marks = "\n".join(["(aluz) mov32 ds0[3], ds0[9]", "(alun) mov32 ds0[4], ds0[9]"])
    pre = "add ds0[8], ds0[8], ds1[8]"       # G + O = 2: z = 0, n = 0 if add sets them
    base = [0, 0, 0, 0, 0, 0, 1, MARK, 0, 0, 0, 0, 0, 0, 1, MARK]
    fl_cases, fl_labels = [], []
    xs = [("add ds0[2], ds0[2], ds1[2]", "add"), ("sub ds0[2], ds0[2], ds1[2]", "sub"),
          ("and ds0[2], ds0[2], ds1[2]", "and"), ("xor ds0[2], ds0[2], ds1[2]", "xor"),
          ("shl ds0[2], ds0[2], 1", "shl"), ("not ds0[2], ds0[2]", "not"),
          ("mov32 ds0[2], ds1[2]", "mov32"), ("tstz p0, ds0[2]", "tstz")]
    # (A, I) giving a zero, a negative and a positive result for each op
    vals = {"add": [(0, 0), (0x80000000, 1), (1, 1)], "sub": [(5, 5), (0, 1), (5, 1)],
            "and": [(0xF0, 0x0F), (M, 0x80000000), (3, 1)],
            "xor": [(7, 7), (0x80000000, 0), (1, 0)],
            "shl": [(0x80000000, 0), (0x40000000, 0), (1, 0)],
            "not": [(M, 0), (0, 0), (0x80000000, 0)],
            "mov32": [(0, 0), (0, 0x80000000), (0, 5)], "tstz": [(0, 0), (0x80000000, 0), (5, 0)]}
    for x, mn in xs:
        for (a, i), what in zip(vals[mn], ("zero", "negative", "positive")):
            ins = list(base)
            ins[0], ins[8] = a, i
            fl_cases.append(("\n".join([pre, x, marks]), ins))
            fl_labels.append(f"{mn} {what}")
    alu = AS_NAMED["flag_ops"]
    t.probe("pds-flags",
            "which ops set aluz/alun, and (aluz)/(alun) as predicates; "
            "ds0[3] = H if aluz, ds0[4] = H if alun after the op",
            fl_cases,
            {"every ALU op, shift and not/abs sets them from its result; mov32 and tests do not":
             {}, "only add and sub set them": {"flag_ops": {"add", "sub", "adc", "sbc"}},
             "the logic ops too, not the shifts": {"flag_ops": alu - {"shl", "shr"}},
             "they never test true": {"flag_ops": None},
             "every op sets aluz; alun only under alum signed": {"alun": "signed"},
             "add and sub set aluz; alun only under alum signed":
             {"flag_ops": {"add", "sub", "adc", "sbc"}, "alun": "signed"}},
            labels=fl_labels)
    # the same under alum signed (where alun may be set): the ops that settle it
    sg = [(f"alum signed\n{c_op}", ins) for (c_op, ins), lbl in zip(fl_cases, fl_labels)
          if lbl.split()[0] in ("add", "sub", "and", "xor", "shl", "not")]
    sg_labels = [lbl for lbl in fl_labels if lbl.split()[0] in ("add", "sub", "and", "xor", "shl",
                                                                  "not")]
    addsub = {"add", "sub", "adc", "sbc"}
    t.probe("pds-flags-signed",
            "aluz/alun under alum signed: which ops set alun; ds0[4] = H if alun",
            sg, {"add and sub set both; alun by a negative result":
                 {"flag_ops": addsub, "alun": "signed"},
                 "every ALU op sets them": {"alun": "signed"},
                 "alun never tests true": {"flag_ops": addsub, "alun": "never"}},
            labels=sg_labels)

    # A5: tstn, the ds1 source form, and a predicated test
    tst_op = "\n".join(["tstn p0, ds0[2]", "(p0) or ds0[3], ds0[9], ds1[9]",
                        "tstz p1, ds1[2]", "(p1) or ds0[4], ds0[9], ds1[9]",
                        "tstz p2, ds0[9]", "tstz p0, ds0[9]", "(p0) tstz p2, ds0[6]",
                        "(p2) or ds0[7], ds0[9], ds1[9]"])
    tst_cases = []
    for x in (0, 1, 0x7FFFFFFF, 0x80000000, M):
        ins = [x, 0, 0, 0, 0, 0, 0, MARK, x, 0, 0, 0, 0, 0, 0, MARK]
        tst_cases.append(ins)
    t.probe("pds-tst",
            "tstn: the sign bit? tstz on a ds1 source; does a predicated test obey its predicate",
            tst_cases, {"tstn = bit 31, tests obey their predicate": {},
                        "tstn = bit 31, a test ignores its predicate": {"test_pred": False},
                        "tstn = signed <= 0": {"tstn": "le0"}},
            labels=["0", "1", "0x7fffffff", "0x80000000", "0xffffffff"], op=tst_op)

    # A6: shift amounts, the shr fill and negative amounts
    sh_cases, sh_labels = [], []
    for n in (0, 1, 4, 31, 32, 33, 63, -1, -4, -31, -32, -64):
        amount = n & M
        op = "\n".join([f"shr ds0[2], ds0[2], {amount}", f"shl ds0[3], ds0[3], {amount}",
                        f"shr ds0[4], ds1[4], {amount}"])
        ins = [0x80000001, 0x80000001, 0, 0, 0, 0, 0, 0, 0, 0, 0xC0000003, 0, 0, 0, 0, 0]
        sh_cases.append((op, ins))
        sh_labels.append(str(n))
    t.probe("pds-shifts",
            "shr: logical or arithmetic; amounts past 31; a negative amount",
            sh_cases, {"logical; 32 and up give 0; negative shifts the other way": {},
                       "arithmetic shr; negative shifts the other way": {"shift": "arith"},
                       "the amount modulo 32": {"shift": "mod32"},
                       "logical; the amount unsigned 0-127, 32 and up give 0": {"shift": "u7"}},
            labels=sh_labels)

    # A7: a counted loop (bra back and forward), then call/rtn nesting
    loop_op = "\n".join(["loop: sub ds0[2], ds0[2], ds1[9]", "add ds0[3], ds0[3], ds1[8]",
                         "tstz p0, ds0[2]", "(p0) bra out", "bra loop", "out: nop"])
    loop_cases = [[n, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x10, 1] for n in (1, 3, 7)]
    t.probe("pds-loop", "bra forwards and backwards: a counted loop",
            loop_cases, {"bra to the label's instruction index": {}},
            labels=["1", "3", "7"], op=loop_op)

    call_cases, call_labels = [], []
    for d in range(1, 8):
        body = ["call f1", "or ds1[2], ds0[9], ds1[9]", "bra end"]
        for i in range(1, d + 1):
            body.append(f"f{i}: or ds0[{1 + i}], ds0[9], ds1[9]")
            if i < d:
                body += [f"call f{i + 1}", f"or ds1[{2 + i}], ds0[9], ds1[9]"]
            body.append("rtn")
        body.append("end: nop")
        ins = [0x100 + k for k in range(7)] + [MARK] + [0x200 + k for k in range(7)] + [MARK]
        call_cases.append(("\n".join(body), ins))
        call_labels.append(f"depth {d}")
    t.probe("pds-call",
            "call/rtn: a return stack, and how deep; level i marks ds0[1+i] on entry "
            "and ds1[1+i] after its call returns",
            call_cases, {"a return stack at least 7 deep": {},
                         "one return register: a nested return loops (the job fails)":
                         {"call": "link"}},
            labels=call_labels)

    # A8: the input registers, the timer and pc as sources (recorded: no prediction)
    in_op = "\n".join(["mov32 ds0[2], ir0.0", "mov32 ds0[3], ir0.1", "mov32 ds0[4], pc.0",
                       "mov32 ds0[5], ir1.1", "mov32 ds0[6], ir1.1", "mov32 ds0[7], ir1.0",
                       "mov32 ds0[8], ir1.0"])
    t.probe("pds-inputs",
            "ir0, ir1, ir2, tim (twice) and pc as mov32 sources, recorded",
            [[0] * 16], None, labels=["fill"], op=in_op)

    _units(t)
    _flags_and_carry(t)
    _carry_chains(t)
    _signed_carries(t)
    _timer_and_sweeps(t)
    _flagged_moves(t)
    return t.probes


def _units(t: Model) -> None:
    # B1: mul's halves and signedness, with alum both ways
    mul_op = "\n".join(["alum unsigned", "mul ds0[2], ds0[2].l, ds1[2].l",
                         "mul ds0[3], ds0[3].h, ds1[3].l", "mul ds0[4], ds0[4].l, ds1[4].h",
                         "alum signed", "mul ds0[5], ds0[5].l, ds1[5].l",
                         "mul ds0[6], ds0[6].h, ds1[6].h"])
    mk = lambda a, b: [a] * 8 + [b] * 8                                     # noqa: E731
    t.probe("pds-mul", "mul: 16 x 16 halves, signed or not, and alum",
            [mk(0xFFFF0002, 0x0002FFFF), mk(0x80008000, 0x80008000), mk(0x12345678, 0x9ABC0003)],
            {"unsigned unless alum signed": {}, "always unsigned": {"mul": "unsigned"},
             "always signed": {"mul": "signed"}},
            labels=["ffff x 2", "8000 x 8000", "mixed"], op=mul_op)

    # B2: the carry of adc and sbc, each after the other kind (an add's carry into sbc, a
    # sub's borrow into adc), so that "borrow" and "no borrow" readings differ
    c_op = "\n".join(["add ds0[8], ds0[8], ds1[8]", "sbc ds0[3], ds0[3], ds1[3]",
                       "sub ds0[9], ds0[9], ds1[9]", "adc ds0[2], ds0[2], ds1[2]"])
    c_cases = []
    for g, o_ in ((1, 1), (M, 1)):           # G + O: no carry, carry
        for h, p_ in ((5, 1), (1, 5)):       # H - P: no borrow, borrow
            c_cases.append([10, 10, 0, 0, 0, 0, g, h, 3, 3, 0, 0, 0, 0, o_, p_])
    t.probe("pds-adc-sbc", "adc/sbc: where their carry comes from",
            c_cases, {"add/sub leave a carry / a borrow, adc adds it, sbc subtracts it": {},
                      "sub leaves no-borrow, sbc subtracts its complement": {"carry": "notborrow"},
                      "no carry: adc and sbc are add and sub": {"carry": "none"},
                      "add/sub leave the high dword (+1 carry, -1 borrow); adc and sbc add it":
                      {"carry": "high"}},
            labels=["no carry, no borrow", "no carry, borrow", "carry, no borrow",
                    "carry, borrow"],
            op=c_op)

    # B3: does alum signed make shr arithmetic?
    a_op = "\n".join(["alum signed", "shr ds0[2], ds0[2], 4", "alum unsigned",
                       "shr ds0[3], ds0[3], 4"])
    t.probe("pds-alum-shr", "alum signed and shr",
            [[0x80000010, 0x80000010] + [0] * 14, [0x40000010, 0x40000010] + [0] * 14],
            {"shr ignores alum": {}, "alum signed makes shr arithmetic": {"alum_shr": True}},
            labels=["negative", "positive"], op=a_op)

    # B4: abs and not, both source forms
    an_op = "\n".join(["abs ds0[2], ds0[2]", "abs ds0[3], ds1[3]", "not ds0[4], ds0[4]",
                        "not ds0[5], ds1[5]"])
    an_cases = [[5, 0, 0x0F0F0F0F, 0, 0, 0, 0, 0] + [0, (-5) & M, 0, 0xF0F0F0F0, 0, 0, 0, 0],
                [0x80000000, 0, 0, 0, 0, 0, 0, 0] + [0, 0x80000000, 0, M, 0, 0, 0, 0],
                [(-5) & M, 0, 0, 0, 0, 0, 0, 0] + [0, 5, 0, 0, 0, 0, 0, 0]]
    t.probe("pds-abs-not", "abs (two's complement? abs of the most negative) and not",
            [[5, 0, 0x0F0F0F0F, 0, 0, 0, 0, 0] + [0, (-5) & M, 0, 0xF0F0F0F0, 0, 0, 0, 0],
             [0x80000000, 0, 0, 0, 0, 0, 0, 0] + [0, 0x80000000, 0, M, 0, 0, 0, 0]],
            {"two's complement; abs of the most negative is itself": {},
             "abs saturates": {"abs": "sat"},
             "abs is the identity unless alum signed": {"abs": "alum"}},
            labels=["5, -5", "most negative"], op=an_op)
    t.probe("pds-abs-signed", "abs under alum signed: two's complement, and the most negative",
            an_cases, {"two's complement; abs of the most negative is itself": {"abs": "alum"},
                       "abs saturates": {"abs": "sat"},
                       "still the identity": {"abs": "id"}},
            labels=["5, -5", "most negative", "-5 from ds0"], op="alum signed\n" + an_op)

    # B5: mov16 halves, mov64 pairs, mov128 and swap
    # mov16's destination index names a 16-bit half (measured): ds0[4] is ds0[2]'s low half,
    # ds0[9] ds0[4]'s high half, ds1[4] ds1[2]'s low, ds1[7] ds1[3]'s high
    m16_op = "\n".join(["mov16 ds0[4], ds0[3].h", "mov16 ds0[9], ds1[5].l",
                         "mov16 ds1[4], ds0[6].h", "mov16 ds1[7], ds1[8].l"])
    seq = [0x10101010 * (k + 1) & M for k in range(8)] + \
        [0x0A0B0C00 + k for k in range(8)]
    t.probe("pds-mov16", "mov16: which half of the destination it writes",
            [seq], {"the index names a half (n & 1 = 1 high); the other half kept":
                    {"mov16": "halves"},
                    "the index names a half; the other half cleared": {"mov16": "halves_zext"},
                    "the index names a half (n & 1 = 1 low)": {"mov16": "halves_swapped"}},
            labels=["distinct"], op=m16_op)
    wide = [("mov64 ds0[2], ds1[4]", "mov64 ds1 to ds0"),
            ("mov64 ds1[2], ds0[6]", "mov64 ds0 to ds1"),
            ("mov128 ds[2], ds[4]", "mov128"), ("mov128 ds[2], ds[4], swap", "mov128 swap"),
            ("mov128 ds[6], ds[2], swap", "mov128 swap back")]
    t.probe("pds-mov-wide", "mov64 pairs, mov128 across the banks and its swap",
            [(o_, seq) for o_, _ in wide],
            {"mov128 = rows (ds0 pair, ds1 pair); swap exchanges the pairs": {},
             "swap exchanges the words of each pair": {"swap": "words"},
             "mov128 = four ds0 dwords": {"mov128": "ds0"},
             "mov64 lands its pair reversed": {"mov64": "reversed"}},
            labels=[lbl for _, lbl in wide])

    # B6: if0/if1 in the secondary program (recorded: each pixel shows the sa0 it got)
    t.probe("pds-if", "if0/if1: which secondary PDS runs see them, per pixel: sa0 = A | 1 if if0, "
            "| 2 if if1 (recorded)",
            [[0x1F000000] + [0] * 13 + [1, 2]], None, labels=["64x32 fill"],
            op="(if0) or ds0[2], ds0[2], ds1[8]\n(if1) or ds0[2], ds0[2], ds1[9]",
            use="sa_pixel.s", pixels=True)

    # B7: the banks past the data segment between runs (recorded)
    t.probe("pds-uninit", "are ds0/ds1 past the data segment cleared between PDS runs? "
            "reads ds0[60], ds1[60], then writes P there (recorded)",
            [[0] * 15 + [0x5EED0001]], None, labels=["fill"],
            op="\n".join(["mov32 ds0[2], ds0[60]", "mov32 ds0[3], ds1[60]",
                           "mov32 ds0[60], ds1[9]", "mov32 ds1[60], ds1[9]"]))


def _flags_and_carry(t: Model) -> None:
    """The specials as movs sources, the flags and the carry after more ops, and a mov16 into
    a constant row, on the settled readings (SETTLED)."""
    # D1: the specials as movs sources, recorded: their values vary from
    # run to run. Each program copies ir0, ir1, pc, tim, ir2 with mov32 to ds1[48..52] (sa8-
    # sa12), and passes movs specials to sa0-sa7 with their own douta; then kicks and halts.
    def douta(srcs):
        return [f"movs douta, {v}, ds1[{10 + k}], {rest}" for k, (v, rest) in enumerate(srcs)]

    kick = [f"movs douta, ds1[{48 + k}], ds0[{10 + k}], ds1[{48 + k}], ds1[{48 + k}]"
            for k in range(8)] + ["movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]", "halt"]
    copies = ["mov32 ds1[48], ir0.0", "mov32 ds1[49], ir0.1", "mov32 ds1[50], ir1.0",
              "mov32 ds1[51], ir1.1", "mov32 ds1[52], pc.0"]
    same = lambda r: (r, f"{r}, {r}")                                       # noqa: E731
    halves = [same(r) for r in ("ir0.l", "ir0.h", "ir1.l", "ir1.h", "tim.l", "tim.h", "ir2.l",
                                "ir2.h")]
    mixed = [("ir0.l", "ir0.h, ir0.h"), ("ir0.h", "ir0.l, ir0.l"), ("ir0.l", "ir0.l, ir0.h"),
             ("ir0.l", "ir0.h, ir0.l"), ("tim.l", "tim.h, tim.h"), ("tim.h", "tim.l, tim.l"),
             ("ir1.l", "ir1.h, ir1.h"), ("ir2.l", "ir2.h, ir2.h")]
    again = [same(r) for r in ("ir0.l", "ir0.l", "tim.l", "tim.l", "ir1.l", "ir1.h", "ir2.l",
                               "ir2.h")]
    sp_cases = [(copies + douta(halves), "copies, then each special .l/.h"),
                (douta(halves) + copies, "each special .l/.h, then copies"),
                (copies + douta(mixed), "the unused slots varied"),
                (copies + douta(again), "repeated reads")]
    tim = [f"movs douta, tim.l, ds1[{10 + k}], tim.l, tim.l" for k in range(8)]
    gaps = [ln for k, n in enumerate([0, 1, 2, 4, 8, 16, 32, 64]) for ln in ["nop"] * n + [tim[k]]]
    sp_cases += [(copies + tim, "tim.l 8 times back to back"),
                 (copies + gaps, "tim.l after 0, 1, 2, 4, ..., 64 nops")]
    t.probe("pds-specials",
            "the specials as movs sources, recorded: sa0-sa7 the movs reads, "
            "sa8-sa12 mov32 copies of ir0, ir1, pc, tim, ir2",
            [("\n".join(c + kick), [0] * 16) for c, _ in sp_cases], None,
            labels=[lbl for _, lbl in sp_cases])

    # The flags and the carry after the ops the first probes did not try. Flag cases: a known
    # add (or sub) first, the op into ds0[2], then ds0[3] = H if
    # aluz, ds0[4] = H if alun; the alun cases under alum signed. Carry cases: an add that
    # carries (+1) or a sub that borrows (-1), the op, then adc ds0[5] = 0 + 0 + carry.
    fmarks = "(aluz) mov32 ds0[3], ds0[9]\n(alun) mov32 ds0[4], ds0[9]"
    pre_add, pre_sub = "add ds0[8], ds0[8], ds1[8]", "sub ds0[8], ds0[8], ds1[8]"
    adc = "adc ds0[5], ds0[5], ds1[5]"
    # op -> (code, flag inputs (A, I) for: nonzero, zero, positive, negative), None: carry only
    ops = {
        "or": ("or ds0[2], ds0[2], ds1[2]", [(1, 0), (0, 0), (1, 0), (0x80000000, 0)]),
        "nor": ("nor ds0[2], ds0[2], ds1[2]", [(0x80000000, 0), (M, 0), (0x80000000, 0), (1, 0)]),
        "nand": ("nand ds0[2], ds0[2], ds1[2]",
                 [(0x80000000, M), (M, M), (0x80000000, M), (0, 0)]),
        "shr": ("shr ds0[2], ds0[2], 1", [(4, 0), (1, 0), (4, 0), (0x80000000, 0)]),
        "abs": ("abs ds0[2], ds0[2]", [(5, 0), (0, 0), (0xFFFFFFFB, 0), (0x80000000, 0)]),
        "mul": ("mul ds0[2], ds0[2].l, ds1[2].l", [(2, 3), (0, 5), (0xFFFF, 0xFFFF), (0xFFFF, 2)]),
        "mov16": ("mov16 ds0[4], ds1[2].l", [(0, 5), (0, 0), (0, 5), (0x80000000, 5)]),
        "tstn": ("tstn p0, ds0[2]", [(1, 0), (0, 0), (1, 0), (0x80000000, 0)]),
        "adc": ("adc ds0[2], ds0[2], ds1[2]", [(1, 0), (0, 0), (1, 0), (0x80000000, 0)]),
        "sbc": ("sbc ds0[2], ds0[2], ds1[2]", [(1, 0), (0, 0), (1, 0), (0, 1)]),
        "and": ("and ds0[2], ds0[2], ds1[2]", None),
        "xor": ("xor ds0[2], ds0[2], ds1[2]", None),
        "shl": ("shl ds0[2], ds0[2], 1", None),
        "not": ("not ds0[2], ds0[2]", None),
        "mov32": ("mov32 ds0[2], ds1[2]", None),
        "mov64": ("mov64 ds0[6], ds1[6]", None),
        "mov128": ("mov128 ds[6], ds[2]", None),
        "tstz": ("tstz p0, ds0[2]", None),
        "alum": ("alum signed", None),
        "nop": ("nop", None),
    }
    # the pre-op's (G, O) for: zero, nonzero, negative (signed), positive (signed)
    pres = [(0, 0), (1, 1), (0x80000000, 1), (1, 1)]
    flabels = ["aluz kept?", "aluz set?", "alun kept? (signed)", "alun set? (signed)"]
    for mn, (code, fl) in ops.items():
        cases, labels = [], []
        for k, ((a, i), (g, o)) in enumerate(zip(fl or [], pres)):
            ins = [a, 0, 0, 0, 0, 0, g, MARK, i, 0, 0, 0, 0, 0, o, MARK]
            mode = "alum signed" if k >= 2 else "alum unsigned"
            cases.append(("\n".join([mode, pre_add, code, fmarks]), ins))
            labels.append(flabels[k])
        if mn not in ("adc", "sbc"):
            for pre, (g, o), what in ((pre_add, (M, 1), "carry +1 kept?"),
                                      (pre_sub, (0, 1), "borrow -1 kept?")):
                ins = [1, 0, 0, 0, 0, 0, g, MARK, 0, 0, 0, 0, 0, 0, o, MARK]
                cases.append(("\n".join(["alum unsigned", pre, code, adc]), ins))
                labels.append(what)
        keep_f, set_f = {"base": True}, {"base": True, "flag_ops": SETTLED["flag_ops"] | {mn}}
        if mn in ("adc", "sbc"):
            hyps = {f"{mn} keeps the flags": keep_f, f"{mn} sets them from its result": set_f}
        elif fl is None:
            hyps = {f"{mn} keeps the carry": keep_f,
                    f"{mn} clears the carry": dict(keep_f, carry_clear={mn})}
        else:
            hyps = {f"{mn} keeps the flags and the carry": keep_f,
                    f"{mn} sets the flags from its result, keeps the carry": set_f,
                    f"{mn} keeps the flags, clears the carry": dict(keep_f, carry_clear={mn}),
                    f"{mn} sets the flags, clears the carry": dict(set_f, carry_clear={mn})}
        t.probe(f"pds-after-{mn}",
                f"the flags and the carry after {mn}", cases, hyps,
                labels=labels)

    # D3: a mov16 into a constant row: the half lands in the temporary
    # ds[48 + (n & 15)] (measured); its other half from the temporary, the constant row or cleared
    m_cases = [("mov16 ds0[33], ds1[2].l", "high half of ds0[16] (0xE00)"),
               ("mov16 ds0[34], ds1[3].l", "low half of ds0[17] (0xF00)"),
               ("mov16 ds1[35], ds0[4].l", "high half of ds1[17] (0x700)"),
               ("mov16 ds0[41], ds1[5].l", "high half of ds0[20] (past the segment)")]
    seq = [0x11112222 * (k + 1) & M for k in range(8)] + [0x0A0B0C00 + k for k in range(8)]
    t.probe("pds-mov16-constants",
            "mov16 into ds0/ds1[0..47]: the other half of the temporary it lands in "
            "",
            [(c, seq) for c, _ in m_cases],
            {"the temporary's other half kept": {"base": True, "mov16_ro": "temp"},
             "the constant row's other half": {"base": True, "mov16_ro": "row"},
             "the other half cleared": {"base": True, "mov16_ro": "zero"}},
            labels=[lbl for _, lbl in m_cases])


def _carry_chains(t: Model) -> None:
    """The flags after mov64, mov128, alum and a port write, the carry after adc and sbc, and
    shr by 32 or more, on the settled readings."""
    fmarks = "(aluz) mov32 ds0[3], ds0[9]\n(alun) mov32 ds0[4], ds0[9]"
    pre_add = "add ds0[8], ds0[8], ds1[8]"
    # E1: the flags after mov64, mov128, alum and a port write: kept, or cleared
    ops = {"mov64": ("mov64 ds0[6], ds1[6]", "mov64 ds0[6], ds1[6]"),
           "mov128": ("mov128 ds[6], ds[2]", "mov128 ds[6], ds[2]"),
           "alum": ("alum unsigned", "alum signed"),
           "movs": ("movs douta, ds0[10], ds1[10], ds0[10], ds0[10]",) * 2}
    for mn, (unsigned_op, signed_op) in ops.items():
        cases = [("\n".join(["alum unsigned", pre_add, unsigned_op, fmarks]),
                  [0] * 6 + [0, MARK] + [0] * 6 + [0, MARK]),
                 ("\n".join(["alum signed", pre_add, signed_op, fmarks]),
                  [0] * 6 + [0x80000000, MARK] + [0] * 6 + [1, MARK])]
        t.probe(f"pds-flags-{mn}", f"the flags after {mn}: kept or cleared",
                cases, {f"{mn} keeps the flags": {"base": True},
                        f"{mn} clears them": {"base": True, "flag_clear": {mn}}},
                labels=["aluz (zero) kept?", "alun (negative, signed) kept?"])

    # E2: the carry after adc and sbc; a second adc 0 + 0 into ds0[5] shows it
    adc2 = "adc ds0[5], ds0[5], ds1[5]"
    ca = [("add ds0[8], ds0[8], ds1[8]\nadc ds0[2], ds0[2], ds1[2]", (1, 1), (M, 1), "adc 1+1+1"),
          ("add ds0[8], ds0[8], ds1[8]\nadc ds0[2], ds0[2], ds1[2]", (M, 1), (0, 0), "adc ~0+1+0"),
          ("sub ds0[8], ds0[8], ds1[8]\nsbc ds0[2], ds0[2], ds1[2]", (5, 1), (0, 1), "sbc 5-1-1"),
          ("add ds0[8], ds0[8], ds1[8]\nsbc ds0[2], ds0[2], ds1[2]", (0, 1), (0, 0), "sbc 0-1+0")]
    cases, labels = [], []
    for code, (a, i), (g, o), lbl in ca:
        cases.append(("\n".join(["alum unsigned", code, adc2]),
                      [a, 0, 0, 0, 0, 0, g, 0, i, 0, 0, 0, 0, 0, o, 0]))
        labels.append(lbl)
    t.probe("pds-adc-carry", "the carry adc and sbc leave; adc 0 + 0 shows it",
            cases, {"the high dword of their exact result, as add/sub": {"base": True},
                    "the carry they used, kept": {"base": True, "carry_adc": "keep"},
                    "cleared": {"base": True, "carry_adc": "clear"}}, labels=labels)

    # E3: the carry of add/sub under alum signed; alum unsigned (which keeps it) before the adc
    sc = [("add", (M, 1), "add -1 + 1"), ("add", (0x7FFFFFFF, 1), "add 0x7fffffff + 1"),
          ("sub", (0, 1), "sub 0 - 1"), ("sub", (0x80000000, 1), "sub 0x80000000 - 1"),
          # the last three confirm the overflow reading
          ("add", (0x7FFFFFFF, 0x7FFFFFFF), "add 0x7fffffff + 0x7fffffff"),
          ("sub", (0x7FFFFFFF, M), "sub 0x7fffffff - -1"),
          ("add", (0x80000000, 0x80000000), "add 0x80000000 + 0x80000000")]
    cases = [("\n".join(["alum signed", f"{mn} ds0[8], ds0[8], ds1[8]", "alum unsigned", adc2]),
              [0] * 6 + [g, 0] + [0] * 6 + [o, 0]) for mn, (g, o), _ in sc]
    t.probe("pds-signed-carry", "add/sub's carry under alum signed",
            cases, {"the unsigned result's high dword, as unsigned": {"base": True},
                    "the signed result's high dword": {"base": True, "carry_signed": "signed"},
                    "no carry": {"base": True, "carry_signed": "none"},
                    "the signed overflow: exact = signed(r) + c * 2^32":
                    {"base": True, "carry_signed": "overflow"}},
            labels=[lbl for _, _, lbl in sc])

    # E4: an arithmetic shr by 32 or more (sgx-sim stops there)
    sh = []
    for n in (32, 33, 63, 64, 127):
        amt = n if n < 64 else (n - 128) & M        # the assembler writes 64-127 as -64..-1
        sh.append(("\n".join(["alum signed", f"shr ds0[2], ds0[2], {amt}",
                               f"shr ds0[3], ds0[3], {amt}", f"shr ds0[4], ds0[4], {n & 31}"]),
                   [0x80000001, 0x40000001, 0x80000001] + [0] * 13))
    t.probe("pds-ashr-big", "shr under alum signed by 32-127: ds0[2] = 0x80000001, ds0[3] = "
            "0x40000001 by n, ds0[4] = 0x80000001 by n & 31 (a reference)",
            sh, {"filled with the sign": {"base": True},
                 "0": {"base": True, "ashr_big": "zero"},
                 "by the amount mod 32": {"base": True, "ashr_big": "mod32"}},
            labels=[str(n) for n in (32, 33, 63, 64, 127)])

    # E5: the specials through each datapath, recorded: mov32, the ALU's first source, mul's
    # halves and mov16, once as found and once after a movs to tim (I = 1: mul's multiplier)
    paths = ["mov32 ds0[2], ir1.1", "or ds0[3], tim, ds1[1]", "mul ds0[4], tim.l, ds1[2].l",
             "mul ds0[5], tim.h, ds1[2].l", "mov16 ds0[12], ir1.1.l", "mov16 ds0[15], ir1.1.h",
             "or ds0[8], ir1, ds1[1]", "mov32 ds0[9], ir1.0", "mov32 ds1[3], ir0.1",
             "mov32 ds1[4], pc.0", "mov16 ds1[10], ir1.0.l", "or ds1[6], ir0, ds1[1]",
             "mov32 ds1[7], ir0.0", "mov32 ds1[8], ir1.1", "or ds1[9], tim, ds1[1]",
             "mul ds1[2], ir1.l, ds1[2].l"]
    ins = [0x00ABCDEF] + [0] * 7 + [1] + [0] * 7
    t.probe("pds-specials-paths",
            "the specials through each datapath (recorded): ds0[2..9] = mov32 tim, or tim, "
            "mul tim.l, mul tim.h, mov16 tim.l (low), mov16 tim.h (high), or ir1, mov32 pc; "
            "ds1[2..9] = mul ir1.l, mov32 ir1, mov32 ir2, mov16 pc.l, or ir0, mov32 ir0, "
            "mov32 tim, or tim",
            [("\n".join(paths), ins),
             ("\n".join(["movs tim, ds0[2], ds0[2], ds0[2], ds0[2]"] + paths), ins)], None,
            labels=["as found", "after movs tim, 0x00abcdef"])


def _signed_carries(t: Model) -> None:
    """The carry after a port write and under alum signed, the counter, and the specials on
    the remaining datapaths."""
    sig = {"base": True, "carry_signed": "overflow"}
    adc2 = "adc ds0[5], ds0[5], ds1[5]"
    # F1: the carry after a port write
    port = "movs douta, ds0[10], ds1[10], ds0[10], ds0[10]"
    cases = [("\n".join(["alum unsigned", pre, port, adc2]),
              [0] * 6 + [g, 0] + [0] * 6 + [o, 0])
             for pre, (g, o) in (("add ds0[8], ds0[8], ds1[8]", (M, 1)),
                                 ("sub ds0[8], ds0[8], ds1[8]", (0, 1)))]
    t.probe("pds-carry-movs", "the carry after a port write", cases,
            {"movs keeps the carry": dict(sig), "movs clears it": dict(sig, carry_clear={"movs"})},
            labels=["carry +1 kept?", "borrow -1 kept?"])

    # F2: adc/sbc's carry under alum signed; alum unsigned (which keeps it) before adc 0 + 0
    sa = [("add", "adc", (M, 1), (0x7FFFFFFF, 1), "-1+1; adc 0x7fffffff + 1"),
          ("add", "adc", (0x7FFFFFFF, 1), (0, 0), "0x7fffffff+1; adc 0 + 0"),
          ("add", "adc", (0x7FFFFFFF, 1), (0x7FFFFFFF, 0), "0x7fffffff+1; adc 0x7fffffff + 0"),
          ("sub", "sbc", (0, 1), (0x80000000, 1), "0-1; sbc 0x80000000 - 1"),
          ("sub", "sbc", (0x80000000, 1), (0, 0), "0x80000000-1; sbc 0 - 0")]
    cases = []
    for pre, op, (g, o), (a, i), _ in sa:
        cases.append(("\n".join(["alum signed", f"{pre} ds0[8], ds0[8], ds1[8]",
                                  f"{op} ds0[2], ds0[2], ds1[2]", "alum unsigned", adc2]),
                      [a, 0, 0, 0, 0, 0, g, 0, i, 0, 0, 0, 0, 0, o, 0]))
    t.probe("pds-signed-adc", "adc/sbc's carry under alum signed", cases,
            {"the signed overflow, as add/sub": dict(sig, adc_signed="overflow"),
             "the unsigned high dword": dict(sig, adc_signed="unsigned"),
             "the carry kept": dict(sig, adc_signed="keep")},
            labels=[lbl for *_, lbl in sa])

    # F3: the counter, recorded: loaded by movs tim (or not), read through the ALU after
    # 0, 1, 2, 4, 8, 16, 32 and 64 nops into ds0[2..9]
    reads = []
    for k, n in enumerate([0, 1, 2, 4, 8, 16, 32, 64]):
        reads += ["nop"] * n + [f"or ds0[{2 + k}], tim, ds1[1]"]
    load = "movs tim, ds1[2], ds1[2], ds1[2], ds1[2]"
    t.probe("pds-tim-count",
            "the counter after a movs tim (recorded): ds0[2..9] = tim (ALU) after 0, 1, 2, 4, "
            "8, 16, 32, 64 nops; loaded with I (0x1000, 40), or not loaded",
            [("\n".join([load] + reads), [0] * 8 + [0x1000] + [0] * 7),
             ("\n".join([load] + reads), [0] * 8 + [40] + [0] * 7),
             ("\n".join(reads), [0] * 16)], None,
            labels=["loaded 0x1000", "loaded 40", "not loaded"])

    # F4: the specials on the remaining datapaths, recorded (I = 1, P = MARK)
    paths = ["shl ds0[2], ir0, 0", "shl ds0[3], ir1, 0", "abs ds0[4], ir0", "abs ds0[5], ir1",
             "not ds0[6], tim", "mul ds0[7], ir0.l, ds1[2].l", "mul ds0[8], ir0.h, ds1[2].l",
             "tstz p0, ir1", "(p0) mov32 ds0[9], ds1[9]", "tstz p1, ir0",
             "(p1) mov32 ds1[3], ds1[9]", "mov16 ds1[8], ir0.0.l", "mov16 ds1[10], ir0.0.h",
             "mov16 ds1[12], ir0.1.l", "mov16 ds1[14], pc.0.l", "or ds1[8], ir0, ds1[1]",
             "mul ds1[2], ir1.l, ds1[2].l"]
    t.probe("pds-specials-paths2",
            "the specials on the other datapaths (recorded): ds0[2..9] = shl ir0, shl ir1, abs "
            "ir0, abs ir1, not tim, mul ir0.l, mul ir0.h, P if tstz ir1; ds1[2..8] = mul ir1.l, P "
            "if tstz ir0, mov16 ir0.l, mov16 ir0.h, mov16 ir1.l, mov16 ir2.l (low halves), or ir0",
            [("\n".join(paths), [0] * 8 + [1] + [0] * 6 + [MARK])], None, labels=["fill"])


def raw(word: int, bank: int, reg: int) -> str:
    """A hand-encoded word in OP. The C comment (which pds-asm blanks) names the register
    the word writes, where test_probe's check of the destinations reads it."""
    return f".word /*ds{bank}[{reg}]*/ 0x{word:08x}"


# The special source fields swept by _timer_and_sweeps, always (w[26:24] = 7), the
# rest of each word fixed: name -> (the encoding of (index, bank, register), the special
# values, results per program, the instructions before the words). mov16 writes two
# results per temporary, .l (even index) to its low half, .h to its high one.
ALWAYS = 7 << 24
SWEEP = {
    "mov32": (lambda i, b, r: 0x02 << 27 | ALWAYS | i << 9 | b << 7 | r << 1,
              range(128, 256), 16, []),
    # or dst, <special>, ds1[1] (0)
    "alu": (lambda i, b, r: 0x18 << 27 | ALWAYS | i << 17 | 1 << 10 | b << 6 | r,
            range(64, 128), 16, []),
    "mov16": (lambda i, b, r: 0x01 << 27 | ALWAYS | i << 8 | b << 7 | (2 * r + (i & 1)),
              range(256, 512), 32, []),
    # mul dst, <special half>, ds1[9].l (P = 1), unsigned
    "mul": (lambda i, b, r: 0x0C << 27 | ALWAYS | i << 16 | 18 << 9 | b << 6 | r,
            range(128, 256), 16, ["alum unsigned"]),
    # shl dst, <special>, 0
    "shl": (lambda i, b, r: 0x1E << 27 | ALWAYS | i << 16 | b << 6 | r,
            range(128, 256), 16, []),
}


def mov32_field(sel: int, flag: int) -> int:
    """mov32's special source field as the sweeps fit it: selector (ir0, ir1, pc, tim) and flag."""
    return 128 + 2 * sel + flag


def mov16_field(sel: int, flag: int, *, hi: bool) -> int:
    """mov16's: the same, in 16-bit halves (the half in bit 0)."""
    return 256 + 4 * sel + 2 * flag + hi


def mov32_raw(i: int, b: int, r: int) -> int:
    return SWEEP["mov32"][0](i, b, r)


def mov16_raw(i: int, b: int, r: int, *, hi: bool) -> int:
    """mov16 from source field i into the low (high) half of dsB[r]."""
    return 0x01 << 27 | ALWAYS | i << 8 | b << 7 | (2 * r + hi)


def mov64_raw(i: int, b: int, r: int) -> int:
    """mov64 from source field i into the pair dsB[r], dsB[r + 1] (r even)."""
    return 0x03 << 27 | ALWAYS | i << 10 | b << 7 | (r >> 1) << 2


def _timer_and_sweeps(t: Model) -> None:
    """Which word of movs tim loads the counter, and every special index of the mov32, ALU,
    mov16, mul and shl source fields."""
    # G1: movs tim with four distinct words, each case's own (the counter keeps the last
    # load across jobs, so a case that does not load shows the previous case's value), read
    # through the ALU after 0, 1, 2, 4, 8, 16, 32 and 64 nops into ds0[4..7], ds1[4..7].
    # A word k of the printed order (movs tim, a, b, c, d: slots 3 down to 0) loads it.
    reads = []
    for k, n in enumerate([0, 1, 2, 4, 8, 16, 32, 64]):
        reads += ["nop"] * n + [f"or ds{k >> 2}[{4 + (k & 3)}], tim, ds1[1]"]
    orders = [("ds0[2]", "ds0[3]", "ds1[2]", "ds1[3]"), ("ds1[3]", "ds1[2]", "ds0[3]", "ds0[2]"),
              ("ds0[2]", "ds1[2]", "ds0[3]", "ds1[3]")]
    slot = {"ds0[2]": 0, "ds0[3]": 1, "ds1[2]": 8, "ds1[3]": 9}     # the inputs A, B, I, J
    # word s (a-d) of case c: 0xA0c0A0c0, 0xB0c0B0c0, ...: halves distinct per word and case
    word = lambda c, s: (0xA + s) * 0x10001000 + c * 0x00100010             # noqa: E731
    specs = [(o, None, "a-d = " + ", ".join(LETTERS[slot[r]] for r in o)) for o in orders]
    specs += [(orders[0], z, f"word {'abcd'[z]} zero") for z in range(4)]
    specs += [(orders[0], "small", "small words (bit 31 clear)")]
    # word a's top bits dropped: bits 31-25 set,
    # bit 24 (which, set, keeps the counter running) clear
    specs += [(orders[0], "high", "word a 0xfe..., bit 24 clear")]
    cases, labels = [], []
    for c, (order, mod, lbl) in enumerate(specs, start=1):
        ins = [0] * 16
        for s, reg in enumerate(order):
            ins[slot[reg]] = word(c, s)
            if mod == "small":
                ins[slot[reg]] = c << 16 | (s + 1) << 12 | s + 1
            elif mod == "high":
                ins[slot[reg]] = 0xFE000000 | word(c, s) & 0x00FFFFFF
            elif mod == s:
                ins[slot[reg]] = 0
        cases.append(("\n".join([f"movs tim, {', '.join(order)}"] + reads), ins, order))
        labels.append(lbl)
    hyps = {}
    for k in range(4):
        preds = []
        for _, ins, order in cases:
            v = ins[slot[order[k]]]
            preds.append(ins[:2] + [v] * 4 + ins[6:10] + [v] * 4 + ins[14:])
        hyps[f"word {'abcd'[k]} (slot {3 - k}) loads it, stopped; the others do nothing"] = preds
    # word a's bits 24-0 (bit 24 clear in every case: the counter stays stopped)
    preds = []
    for _, ins, order in cases:
        v = ins[slot[order[0]]] & 0x01FFFFFF
        preds.append(ins[:2] + [v] * 4 + ins[6:10] + [v] * 4 + ins[14:])
    hyps["word a loads its bits 24-0 (the counter is 25 bits), stopped; the others do "
         "nothing"] = preds
    t.probe("pds-tim-words",
            "which of movs tim's four words loads the counter: movs tim, a, "
            "b, c, d from A, B, I, J in the order labelled, then tim (ALU) into ds0[4..7], "
            "ds1[4..7] after 0, 1, 2, 4, 8, 16, 32, 64 nops",
            [(op, ins) for op, ins, _ in cases], hyps, labels=labels)

    # G2: the sweeps, recorded: each program reads 16 (mov16: 32) consecutive special
    # indices into ds0[48..55], ds1[48..55] (mov16: their halves). The inputs mark the
    # temporaries, so a word that writes nothing leaves its mark. Each sweep is its own
    # probe: an index that hangs the job loses only that probe.
    marks = [0x5EED0000 | k for k in range(16)]
    for name, (enc, values, per, pre) in SWEEP.items():
        cases, labels = [], []
        for lo in range(values.start, values.stop, per):
            words = []
            for j in range(per):
                k = j >> 1 if per == 32 else j
                b, r = k >> 3, 48 + (k & 7)
                words.append(raw(enc(lo + j, b, r), b, r))
            ins = list(marks)
            if name == "mul":
                ins[15] = 1                                 # ds1[9]: the multiplier
            cases.append(("\n".join(pre + words), ins))
            labels.append(f"{lo}-{lo + per - 1}")
        t.probe(f"pds-x-index-{name}",
                f"every special source index of {name} ({values.start}-{values.stop - 1}), "
                f"recorded: hand-encoded words into ds0[48..55], ds1[48..55]"
                + (" (.l to the low half, .h to the high)" if per == 32 else "")
                + "; the inputs mark the temporaries; may hang",
                cases, None, labels=labels)


def _flagged_moves(t: Model) -> None:
    """The low bit of the mov16/mov32 special index. The index sweeps fit special k
    as selector k >> 1 (ir0, ir1, pc, tim: the reference's order at every other index) and a
    flag k & 1, which mov32 ignores and with which mov16 reads 0. What the flag is (a 64-bit
    entry's high word, an extension, a flags update), what the count at selector 2 is, and
    how mov64 sees the specials."""
    marks = [0x5EED0000 | k for k in range(16)]

    # H1: one result per temporary, each marked with distinct halves: a 16-bit write keeps
    # the other half's 0x5eed, a whole-dword (extending) one replaces it. ds0: the ALU's tim
    # (into ds0[55]) just before mov16 tim.l, tim.h, flagged tim.l, flagged tim.h, flagged
    # ir0.l, pc.l, flagged pc.l; ds1: mov32 ir0, ir0 flagged, tim, tim flagged, pc, pc
    # flagged, ir1, ir1 flagged
    m16 = [mov16_field(3, 0, hi=False), mov16_field(3, 0, hi=True), mov16_field(3, 1, hi=False),
           mov16_field(3, 1, hi=True), mov16_field(0, 1, hi=False), mov16_field(2, 0, hi=False),
           mov16_field(2, 1, hi=False)]
    m32 = [mov32_field(s, f) for s in (0, 3, 2, 1) for f in (0, 1)]
    words = ["or ds0[55], tim, ds1[1]"]
    words += [raw(mov16_raw(f, 0, 48 + k, hi=bool(f & 1)), 0, 48 + k) for k, f in enumerate(m16)]
    words += [raw(mov32_raw(f, 1, 48 + k), 1, 48 + k) for k, f in enumerate(m32)]
    t.probe("pds-mov-flag-write",
            "what a flagged mov16/mov32 writes (recorded): ds0[48..54] = mov16 tim.l, tim.h, "
            "flagged tim.l, flagged tim.h, flagged ir0.l, pc.l, flagged pc.l into one half of "
            "a marked temporary (the other half's 0x5eed kept: a 16-bit write; replaced: an "
            "extending one), ds0[55] = tim (ALU) just before; ds1[48..55] = mov32 ir0, "
            "ir0 flagged, tim, tim flagged, pc, pc flagged, ir1, ir1 flagged",
            [("\n".join(words), marks)], None, labels=["fill"])

    # H2: the flags and the carry after a flagged move. A setup sets them, the move writes
    # ds0[48], then ds0[49] = H if aluz, ds0[50] = H if alun, ds0[51] = D + L + the carry
    # (adc), and ds0[48] is cleared (ir0 varies from run to run)
    zmarks = "(aluz) mov32 ds0[3], ds0[9]\n(alun) mov32 ds0[4], ds0[9]"
    setups = {"sub": (["sub ds0[2], ds0[2], ds1[2]"], False),
              "add": (["add ds0[2], ds0[2], ds1[2]"], False),
              "signed sub": (["alum signed", "sub ds0[2], ds0[2], ds1[2]"], True)}
    # label, setup, (A, I), the setup's (aluz, alun, carry), the move, the moved value zero?
    specs = [("sub 5 - 5: aluz; mov32 ir0 flagged", "sub", (5, 5), (1, 0, 0), ("mov32", 129),
              False),
             ("sub 5 - 3; mov32 ir1 flagged (0)", "sub", (5, 3), (0, 0, 0), ("mov32", 131), True),
             ("sub 5 - 3; mov16 ir0.l flagged (0)", "sub", (5, 3), (0, 0, 0), ("mov16", 258),
              True),
             ("sub 5 - 5: aluz; mov32 ir0 (unflagged)", "sub", (5, 5), (1, 0, 0), ("mov32", 128),
              False),
             ("add -1 + 1: aluz, carry; mov32 ir0 flagged", "add", (M, 1), (1, 0, 1),
              ("mov32", 129), False),
             ("signed sub 3 - 5: alun; mov32 ir1 flagged (0)", "signed sub", (3, 5), (0, 1, 0),
              ("mov32", 131), True)]
    cases, labels = [], []
    hyps = {"the flag leaves aluz, alun and the carry, as a plain move does": [],
            "a flagged move sets aluz/alun from the value moved; the carry kept": [],
            "a flagged move sets aluz/alun from the value moved and clears the carry": []}
    for lbl, setup, (a, i), (z, n, c), (mn, fld), zero in specs:
        lines, signed = setups[setup]
        word = (mov32_raw(fld, 0, 48) if mn == "mov32"
                else mov16_raw(fld, 0, 48, hi=False))
        adc = not signed                # (under alum signed adc's carry is another question)
        op = lines + [raw(word, 0, 48), zmarks] + (["adc ds0[5], ds0[5], ds1[5]"] if adc else [])
        op.append("mov32 ds0[2], ds1[1]")
        ins = list(marks)
        ins[0], ins[8], ins[3], ins[11], ins[7] = a, i, 0, 0, MARK
        cases.append(("\n".join(op), ins))
        labels.append(lbl)
        flagged = fld & 1 if mn == "mov32" else fld >> 1 & 1
        for k, h in enumerate(hyps):
            fz, fn, fc = z, n, c
            if k and flagged:
                fz, fn = int(zero), 0
                fc = 0 if k == 2 else c
            pred = list(ins)
            pred[0] = 0
            pred[1] = MARK if fz else ins[1]
            pred[2] = MARK if fn else ins[2]
            pred[3] = (ins[3] + ins[11] + fc) & M if adc else ins[3]
            hyps[h].append(pred)
    t.probe("pds-mov-flag-flags",
            "do flagged mov32/mov16 specials set the flags or the carry? a setup, the move into "
            "ds0[48], then ds0[49] = H if aluz, ds0[50] = H if alun, ds0[51] = D + L + carry "
            "(adc; not after the signed setup)", cases, hyps, labels=labels)

    # H3: the count at selector 2 (pc, flagged or not, alternating) against where it is read:
    # back to back, after 0-7 nops, after muls (a read once gave index + 1
    # there), and twice inside a loop (a pc reads the same, a cycle count grows)
    reads = [raw(mov32_raw(132 + (j & 1), j >> 3, 48 + (j & 7)), j >> 3, 48 + (j & 7))
             for j in range(16)]
    gaps = []
    for k in range(8):
        gaps += ["nop"] * k + [raw(mov32_raw(132 + (k & 1), 0, 48 + k), 0, 48 + k)]
    muls = [f"mul ds1[{2 + k}], ds0[{2 + k}].l, ds1[{2 + k}].l" for k in range(4)] + reads[:8]
    loop = ["loop: mov32 ds0[4], ds0[3]", raw(mov32_raw(132, 0, 49), 0, 49),
            "sub ds0[2], ds0[2], ds1[9]", "tstz p0, ds0[2]", "(p0) bra out", "bra loop",
            "out: nop"]
    zeros_hi = marks[:8] + [0] * 8
    cases = [(reads, marks), (gaps, marks), (muls, zeros_hi),
             (loop, [2] + marks[1:15] + [1])]
    preds = []
    for op, ins in cases:
        pred = list(ins)
        for li, ln in enumerate(op):
            m = re.match(r"^\.word /\*ds([01])\[(\d+)\]\*/", ln)
            if m:
                pred[8 * int(m.group(1)) + int(m.group(2)) - 48] = 16 + li + 3
        if op is loop:
            pred[0], pred[2] = 0, pred[1]
        preds.append(pred)
    t.probe("pds-mov-pc",
            "the count mov32 reads at selector 2 (it reads as pc; an earlier fit called it ir2) "
            "against "
            "where it is read: 16 back to back, after 0-7 nops, after 4 muls, and twice in a "
            "loop (ds0[50] the first pass, ds0[49] the second)",
            [("\n".join(op), ins) for op, ins in cases],
            {"the reading instruction's own index + 3, whatever ran before": preds},
            labels=["back to back", "after 0-7 nops", "after 4 muls", "in a loop"])

    # H3b: a side effect of the flag on the register read (an auto-decrement, say), recorded:
    # each of ir0, ir1 and tim read plain, flagged twice and plain again, back to back, into
    # ds0[48..55], ds1[48..51]; ds1[52..55] four plain tim reads, the counter's own pace.
    # Once with flagged mov32s, once with flagged mov16s (into the low halves)
    cases = []
    for mn in ("mov32", "mov16"):
        ws = []
        for sel in (0, 1, 3):
            for flag in (0, 1, 1, 0):
                k = len(ws)
                b, r = k >> 3, 48 + (k & 7)
                if flag and mn == "mov16":
                    w = mov16_raw(mov16_field(sel, 1, hi=False), b, r, hi=False)
                else:
                    w = mov32_raw(mov32_field(sel, flag), b, r)
                ws.append(raw(w, b, r))
        ws += [raw(mov32_raw(mov32_field(3, 0), 1, 52 + j), 1, 52 + j) for j in range(4)]
        cases.append(("\n".join(ws), marks))
    t.probe("pds-mov-flag-side",
            "does a flagged move change the register it reads (an auto-decrement)? ir0, ir1, "
            "tim each read plain, flagged, flagged, plain into ds0[48..55], ds1[48..51], then "
            "tim plain x4 into ds1[52..55] (recorded)", cases, None,
            labels=["flagged mov32", "flagged mov16 (low halves)"])

    # H3c: the flag as a condition on the state before the move (a select: the value if the
    # condition holds, else 0), recorded. Every flagged mov16 seen so far ran in the state the
    # program starts in; here a setup sets aluz, the carry, a borrow, alun (signed) or p0-p2
    # first, then: ds0[49..54] = mov16 ir0.l flagged, ir0.l plain, tim.l flagged, tim.h
    # flagged (high half), pc.l flagged, pc.l plain into marked halves; ds0[55], ds1[49] =
    # mov32 ir0, tim flagged; ds1[50..54] = P if aluz, alun, p0, p1, p2 after the moves (moves
    # keep the flags), the state they saw
    moves = [(0, 49, mov16_field(0, 1, hi=False)), (0, 50, mov16_field(0, 0, hi=False)),
             (0, 51, mov16_field(3, 1, hi=False)), (0, 52, mov16_field(3, 1, hi=True)),
             (0, 53, mov16_field(2, 1, hi=False)), (0, 54, mov16_field(2, 0, hi=False))]
    words = [raw(mov16_raw(f, b, r, hi=bool(f & 1)), b, r) for b, r, f in moves]
    words += [raw(mov32_raw(mov32_field(0, 1), 0, 55), 0, 55),
              raw(mov32_raw(mov32_field(3, 1), 1, 49), 1, 49)]
    state = [f"({c}) mov32 ds1[{4 + k}], ds1[9]"
             for k, c in enumerate(("aluz", "alun", "p0", "p1", "p2"))]
    sub, add = "sub ds0[2], ds0[2], ds1[2]", "add ds0[2], ds0[2], ds1[2]"
    tsts = [f"tstz p{k}, ds0[2]" for k in range(3)]
    specs = [("as found", [], (0, 0)), ("aluz (sub 5 - 5)", [sub], (5, 5)),
             ("carry +1, aluz (add -1 + 1)", [add], (M, 1)),
             ("borrow -1 (sub 0 - 1)", [sub], (0, 1)),
             ("alun (signed sub 3 - 5)", ["alum signed", sub], (3, 5)),
             ("p0-p2 true (tstz 0)", tsts, (0, 0)), ("p0-p2 false (tstz 5)", tsts, (5, 0))]
    cases = []
    for _, setup, (a, i) in specs:
        ins = list(marks)
        ins[0], ins[8], ins[15] = a, i, MARK
        cases.append(("\n".join(setup + words + state), ins))
    t.probe("pds-mov-flag-cond",
            "is the flag a condition on the state before the move (the value if it holds, else "
            "0)? a setup (labelled), then ds0[49..54] = mov16 ir0.l flagged, ir0.l, tim.l "
            "flagged, tim.h flagged (high half), pc.l flagged, pc.l; ds0[55], ds1[49] = mov32 "
            "ir0, tim flagged; ds1[50..54] = P if aluz, alun, p0, p1, p2 after (recorded)",
            cases, None, labels=[lbl for lbl, *_ in specs])

    # H3d: the flag as the other PDS pipe's register (SGX545 has two PDS pipes),
    # recorded: in every
    # tile of the fill the secondary ORs 200 samples of a move into ds0[48], which sa_pixel.s
    # paints, so a sample taken while the other pipe runs shows as a nonzero pixel. Cases:
    # flagged pc.l, ir0.l, tim.l; plain ir0 (which tiles read 0x402, which 0x403); plain pc.l
    # (the control: never 0)
    def sampler(fld):
        return "\n".join(["loop: mov32 ds1[4], ds1[1]",
                          raw(mov16_raw(fld, 1, 50, hi=False), 1, 50),
                          "or ds0[2], ds0[2], ds1[4]", "sub ds0[3], ds0[3], ds1[9]",
                          "tstz p0, ds0[3]", "(p0) bra out", "bra loop", "out: nop"])
    loop_ins = [0, 200] + [0] * 13 + [1]
    specs = [("flagged pc.l", mov16_field(2, 1, hi=False)),
             ("flagged ir0.l", mov16_field(0, 1, hi=False)),
             ("flagged tim.l", mov16_field(3, 1, hi=False)), ("plain ir0", None),
             ("control: plain pc.l", mov16_field(2, 0, hi=False))]
    cases = [(sampler(f), loop_ins) if f is not None else ("mov32 ds0[2], ir0.0", [0] * 16)
             for _, f in specs]
    t.probe("pds-mov-flag-pipes",
            "is the flag the other PDS pipe's register? per tile, the pixel = the OR of 200 "
            "samples of the move labelled (flagged pc.l, ir0.l, tim.l; the control plain pc.l), "
            "or ir0 itself (recorded)",
            cases, None, labels=[lbl for lbl, _ in specs], use="sa_pixel.s", pixels=True)

    # H3e: where mov32 keeps its pipe select, if the flag is one (bit 9, the flag, is the
    # same bit in mov16 and mov32, and mov32 ignores it). Recorded. (1) mov32's unused bits,
    # 0, 8 (mov16's half bit) and 23:17, one per case: ds0[48..53] = ir0, pc, tim plain and
    # with the bit; ds0[54] = mov16 ir0.l with the bit (plain for 0 and 8, which mov16
    # uses); ds0[55] = flagged mov16 ir0.l, the known 0. (2) alum's unused bits 23:1 as a
    # mode: alum with one set, then plain reads into ds0[48..54] (mov32 ir0, pc, tim; mov16
    # ir0.l, pc.l; the ALU's ir0; G + O), then alum unsigned again
    cases, labels = [], []
    for bit in [0, 8, *range(17, 24)]:
        ws = []
        for k, fld in enumerate((128, 132, 134)):
            ws.append(raw(mov32_raw(fld, 0, 48 + 2 * k), 0, 48 + 2 * k))
            ws.append(raw(mov32_raw(fld, 0, 49 + 2 * k) | 1 << bit, 0, 49 + 2 * k))
        m16 = mov16_raw(256, 0, 54, hi=False)
        ws.append(raw(m16 | 1 << bit if bit >= 17 else m16, 0, 54))
        ws.append(raw(mov16_raw(258, 0, 55, hi=False), 0, 55))
        cases.append(("\n".join(ws), marks))
        labels.append(f"bit {bit}")
    t.probe("pds-x-mov32-spare",
            "mov32's unused bits (0, 8, 23:17) as its pipe select, one per case (recorded): "
            "ds0[48..53] = mov32 ir0, pc, tim plain and with the bit; ds0[54] = mov16 ir0.l "
            "with the bit (17-23); ds0[55] = flagged mov16 ir0.l (0); may hang",
            cases, None, labels=labels)
    reads = [raw(mov32_raw(128, 0, 48), 0, 48), raw(mov32_raw(132, 0, 49), 0, 49),
             raw(mov32_raw(134, 0, 50), 0, 50), raw(mov16_raw(256, 0, 51, hi=False), 0, 51),
             raw(mov16_raw(264, 0, 52, hi=False), 0, 52),
             "or ds0[7], ir0, ds1[1]", "add ds0[8], ds0[8], ds1[8]", "alum unsigned"]
    cases = [("\n".join(["alum unsigned"] + reads), marks)]
    cases += [("\n".join([f".word 0x{0xBF000000 | 1 << b:08x}"] + reads), marks)
              for b in range(1, 24)]
    t.probe("pds-x-alum-spare",
            "alum's unused bits (23:1) as a mode for the specials, one per case (recorded): "
            "ds0[48..54] = mov32 ir0, pc, tim, mov16 ir0.l, pc.l, the ALU's ir0, G + O after "
            "it, then alum unsigned; may hang",
            cases, None,
            labels=["alum unsigned (control)"] + [f"alum bit {b}" for b in range(1, 24)])

    # H4: every special source of mov64 (64-127, past the ds pairs; the decoder names 64 and
    # 65 mr01 and mr23), recorded: 8 pairs per program into ds0/ds1[48, 50, 52, 54]. If the
    # specials are 64-bit entries, a pair shows an entry's high word whole
    cases, labels = [], []
    for lo in range(64, 128, 8):
        ws = [raw(mov64_raw(lo + j, j >> 2, 48 + 2 * (j & 3)), j >> 2, 48 + 2 * (j & 3))
              for j in range(8)]
        cases.append(("\n".join(ws), marks))
        labels.append(f"{lo}-{lo + 7}")
    t.probe("pds-x-index-mov64",
            "every special source index of mov64 (64-127), recorded: hand-encoded words into "
            "the pairs ds0/ds1[48, 50, 52, 54]; the inputs mark the temporaries; may hang",
            cases, None, labels=labels)




ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
PDS_TABLES = ROOT / "probes" / "pds"


def _key(op, cases) -> str:
    """A probe's identity: its fixed OP (or None) and its cases."""
    return json.dumps([op, cases])


def _index() -> dict:
    index = {}
    for m in model():
        k = _key(m.op, m.cases)
        if k in index:
            raise ValueError(f"{m.name} and {index[k].name} have the same OP and cases")
        index[k] = m
    return index


def match(probe: dict, index: dict | None = None) -> ModelProbe | None:
    """The model's probe for a table probe (a dict of the TOML), by its OP parameter and its
    cases; None if the model has none, or the probe is not a fill probe of the PDS."""
    if probe.get("isa") != "pds" or probe.get("host", "fill") != "fill":
        return None
    index = _index() if index is None else index
    return index.get(_key(probe.get("params", {}).get("OP"), probe["cases"]))


def check_probe(probe: dict, index: dict | None = None) -> list:
    """The differences between a table probe's hypotheses and the model's: [] if it agrees,
    or the model has nothing to say about it."""
    m = match(probe, index)
    if m is None or m.hypotheses is None:
        return []
    got = probe.get("hypotheses", {})
    name = probe["name"]
    out = []
    if list(got) != list(m.hypotheses):
        out.append(f"{name}: hypotheses {list(got)} where the model has {list(m.hypotheses)}")
    for h, want in m.hypotheses.items():
        if h in got and got[h] != want:
            bad = [i for i, (g, w) in enumerate(zip(got[h], want)) if g != w]
            out.append(f"{name}: {h!r}: cases {bad or 'count'} differ from the model")
    return out


def check_table(path: pathlib.Path, index: dict | None = None) -> list:
    """Recompute the hypotheses of every probe of a table the model covers; the differences."""
    index = _index() if index is None else index
    out = []
    for p in tomllib.loads(pathlib.Path(path).read_text()).get("probe", []):
        out += check_probe(p, index)
    return out


def covered(paths=None, index: dict | None = None) -> list:
    """(table probe name, ModelProbe) for each probe of the tables the model has hypotheses for."""
    index = _index() if index is None else index
    out = []
    for path in paths or sorted(PDS_TABLES.glob("*.toml")):
        for p in tomllib.loads(pathlib.Path(path).read_text()).get("probe", []):
            m = match(p, index)
            if m is not None and m.hypotheses is not None:
                out.append((p["name"], m))
    return out


def unmatched(cov: list, index: dict | None = None) -> list:
    """The names of the model's probes with hypotheses that no table probe matches: a table
    probe whose cases or OP were edited has dropped out of the check."""
    index = _index() if index is None else index
    seen = {id(m) for _, m in cov}
    return [m.name for m in index.values() if m.hypotheses is not None and id(m) not in seen]


def unchecked(paths=None, index: dict | None = None) -> list:
    """The names of the PDS fill probes of the tables with hypotheses the model does not
    cover (their hypotheses are hand-written, nothing recomputes them)."""
    index = _index() if index is None else index
    out = []
    for path in paths or sorted(PDS_TABLES.glob("*.toml")):
        for p in tomllib.loads(pathlib.Path(path).read_text()).get("probe", []):
            if (p.get("isa") == "pds" and p.get("host", "fill") == "fill"
                    and p.get("hypotheses") and match(p, index) is None):
                out.append(p["name"])
    return out


def main(argv: list) -> int:
    if argv != ["--check"]:
        sys.stderr.write(__doc__)
        return 2
    index, bad = _index(), []
    for path in sorted(PDS_TABLES.glob("*.toml")):
        bad += check_table(path, index)
    cov = covered(index=index)
    print(f"{len(cov)} probes, {sum(len(m.hypotheses) for _, m in cov)} hypotheses checked")
    lost = unmatched(cov, index)
    for line in bad:
        print(line)
    for name in lost:
        print(f"unmatched: the model's {name} matches no table probe (cases or OP edited?)")
    for name in unchecked(index=index):
        print(f"unchecked (no model): {name}")
    return 1 if bad or lost else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
