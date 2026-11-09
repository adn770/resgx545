#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The complete dataflow of the EDM firmware: every structure word and every register.

A forward dataflow analysis over the whole usse-dis listing of the microkernel, not aimed at any
field: every instruction of every routine (the ranges between the labels' addresses) is
analysed, from the entry points, through branches (values that disagree where paths join become
unknown) and calls (the callee sees what its callers agree on; the caller forgets what the
callee writes). Each value is a constant, a typed pointer into a structure, a value that came
from a structure word, an SGX register or a secondary attribute (with the transforms applied
since), or unknown. For every structure word (STRUCT+0xOFF) it records each read and where the
value goes: written to a register, stored to another word, tested (mask, the branch it steers
and what the skipped instructions do), used as a pointer or in arithmetic. For every register it
records each write with its source and each read with its uses. What the analysis cannot follow
(a base pointer or a predicate of unknown origin, a register-supplied register address) is
recorded as unresolved, never guessed.

Entry points: instruction 0, every label with no static predecessor (the PDS-entered tasks and
the kernel CCB handlers), then any code still unreached, each from its own start. Entry values:
sa0 = TA3D_CTL, sa1 = HOST_CTL, sa2 = CCB_CTL, sa22 = KCCB, sa43 = HWPERF_CB (the captured
TA3DCtl, doc/specs/hw_spec.md §11.1); a CCB handler receives the command's words in r4-r11,
ui32Data[1] (r7) typed where the kernel or the captures say what it holds (doc/specs/transfer.md
§5).
Pointer words are typed where a record establishes them (GLOSSARY_POINTERS), by the pointer
words of kick3d.py's kernel-side layouts and, iteratively, by what the firmware itself stores in
a slot: a slot that only ever receives pointers to one structure holds that structure. Every
pointer word of the client layouts (edmtrace.POINTS_AT) is a given one, so every word edmtrace.py
types, this tool types the same way (it types more: the given words no layout types and the
inferred slots); the table this tool reproduces is the one probes/firmware/edm-dataflow-11.toml
made.

The analysis names nothing from the glossary, so its TSV is the same whatever the glossary
says: subjects are offsets (0x0abc, CMDTA+0x0f8) and the details carry tokens, {R:0x012c} for a
register, {W:HOST_CTL+0x01c} for a structure word and {F:HWRENDERCONTEXT+0x000:4} for a flag bit
(the structure word and the bit number). render() resolves them with the glossary
(edmtrace.load_glossary): a term where it has one, else the offset; a flag bit with no term is
just the bit. A word of a kick3d layout is named as edmtrace names it: through the layouts nested
in it, an array's element as name[i] and a later word of a wide field as name+k. Addresses are
instruction indices (byte address / 8).

    usage: edm_dataflow.py [--ukernel <00_ukernel.bin>] [--tsv <out.tsv>] [--doc <out.md>]
           edm_dataflow.py --check     # the design document matches the TSV
           edm_dataflow.py --render    # rewrite the design document from the TSV
"""
from __future__ import annotations

import csv
import os
import pathlib
import re
import subprocess
import sys
import textwrap
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

import edmtrace
import kick3d

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UKERNEL = pathlib.Path(os.environ.get("RESGX545_UKERNEL", "/nonexistent"))
USSE_DIS = ROOT / "tools" / "usse-dis" / "usse-dis"
FW_MAGIC = b"SGX545FW"     # the .fw container's first word (tools/sgx_fw), not an image
LABELS = (HERE / "sgx545_labels.r2", HERE / "sgx545_ukernel.r2")
DATA = pathlib.Path(os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")
TSV = DATA / "firmware" / "edm-dataflow-11" / "edm_dataflow.tsv"
DOC = ROOT / "doc" / "specs" / "edm_dataflow.md"

IMM = edmtrace.IMM
REG = re.compile(r"^r(\d+)$")
SA = re.compile(r"^sa(\d+)$")
SA_INDEXED = re.compile(r"^sa\[il \+ #(\d+)\]$")
TAIL_ADD = re.compile(r" \+ 0x([0-9a-f]+)$")
PRED_REG = re.compile(r"^p\d$")
SKIP_MAX = 32            # a forward branch over at most this many instructions is a "skip"

# Entry values of the secondary attributes (captured TA3DCtl, hw_spec §11.1).
SA_SEEDS = {0: "TA3D_CTL", 1: "HOST_CTL", 2: "CCB_CTL", 22: "KCCB", 43: "HWPERF_CB"}

# Pointer words -> the structure they point at, where a record establishes the word: TA3DCtl's
# own address, kernel CCB and HWPerf buffer words (E002), the transfer context's client CCB and
# its control block (doc/specs/transfer.md §2.2: E018, E021) and its queue links (E015); the render
# context's client CCB and its control (E161), its PB descriptor (E159, E167), its pending and
# ready render lists (E156, E165) and its TA and 3D queue links (E157, E165); the RT data's
# render details (E159); the TA command's PB descriptor (E156), render details (E159),
# destination sync list (E161, E164) and RT data (E158, E161); the PB descriptor's first block
# (E200, E201); the render details' RT data (E163) and destination sync list (E164, E165); a PB
# block's next block (E200, E201); the TA/3D control block's job words: the RT data owning each
# DPM context slot (E158), the TA's command, RT data, render details and context (E158, E159),
# the 3D's RT data and render details (E163) and the PB descriptor loaded in each pipe (E200).
# Every other pointer word is typed by what the firmware stores in it (see analyze()).
GLOSSARY_POINTERS = {
    ("TA3D_CTL", 0x000): "TA3D_CTL", ("TA3D_CTL", 0x058): "KCCB",
    ("TA3D_CTL", 0x0ac): "HWPERF_CB",
    ("HWTRANSFERCONTEXT", 0x00c): "CCB_TQ", ("HWTRANSFERCONTEXT", 0x010): "CCB_CTL",
    ("HWTRANSFERCONTEXT", 0x0ac): "HWTRANSFERCONTEXT",
    ("HWTRANSFERCONTEXT", 0x0b0): "HWTRANSFERCONTEXT",
    ("HWRENDERCONTEXT", 0x00c): "CCB_TA", ("HWRENDERCONTEXT", 0x010): "CCB_CTL",
    ("HWRENDERCONTEXT", 0x018): "HWPBDESC",
    **{("HWRENDERCONTEXT", o): "HWRENDERDETAILS" for o in (0x020, 0x024, 0x028, 0x02c)},
    **{("HWRENDERCONTEXT", o): "HWRENDERCONTEXT" for o in (0x030, 0x034, 0x038, 0x03c)},
    ("HWRTDATA", 0x004): "HWRENDERDETAILS",
    # the closed client's own values (E325, captures; ours alike): the set and the context
    ("CMDTA", 0x040): "HWRTDATASET", ("HWRTDATA", 0x000): "HWRENDERCONTEXT",
    ("CMDTA", 0x024): "HWPBDESC", ("CMDTA", 0x038): "HWRENDERDETAILS",
    ("CMDTA", 0x03c): "HWDEVICE_SYNC_LIST", ("CMDTA", 0x044): "HWRTDATA",
    ("HWPBDESC", 0x038): "PB_BLOCK",
    ("HWRENDERDETAILS", 0x0dc): "HWRTDATA", ("HWRENDERDETAILS", 0x0e0): "HWDEVICE_SYNC_LIST",
    ("PB_BLOCK", 0x00c): "PB_BLOCK",
    **{("TA3D_CTL", o): "HWRTDATA" for o in (0x050, 0x054, 0x064, 0x070)},
    ("TA3D_CTL", 0x060): "CMDTA",
    **{("TA3D_CTL", o): "HWRENDERDETAILS" for o in (0x068, 0x074)},
    ("TA3D_CTL", 0x06c): "HWRENDERCONTEXT",
    **{("TA3D_CTL", o): "HWPBDESC" for o in (0x0b8, 0x0bc)},
}
# A base of an array plus a non-constant index is an element of it.
ARRAYS = {"KCCB": "COMMAND", "CCB_TA": "CMDTA", "CCB_TQ": "TRANSFERCMD"}

# Kernel CCB handlers (captured kick table, transfer §5): entry -> (command, r7's structure).
HANDLERS = {0x0D4: ("POWER", None), 0x0EB: ("CONTEXTSUSPEND", None),
            0x103: ("TRANSFER", "HWTRANSFERCONTEXT"), 0x11D: ("TA", "HWRENDERCONTEXT"),
            0x13A: ("CLEANUP", None), 0x156: ("PROCESS_QUEUES", None),
            0x157: ("SETHWPERFSTATUS", None), 0x173: ("GETMISCINFO", "MISC")}


# The layouts kick3d.py keeps from the kernel (sgx545-ce); the others are the client structures,
# named by us over the records' offsets.
KERNEL_SIDE = {"PVRSRV_BRIDGE_IN_DOKICK", "SGX_CCB_KICK", "SGXMKIF_CMDTA_SHARED",
               "SGXMKIF_HWDEVICE_SYNC_LIST"}


def _layout_pointers(layouts=KERNEL_SIDE) -> dict[tuple[str, int], str]:
    """Pointer words of kick3d's layouts (by default the kernel-side ones), by offset; their
    names stay internal."""
    out = {}
    for layout, fields in kick3d.STRUCTS.items():
        prefix = edmtrace.PREFIX.get(layout)
        if not prefix or layout not in layouts:
            continue
        for path, off, width, count, _a in kick3d._layout(fields):
            target = edmtrace._points_at(path) if width == 1 and count == 1 else None
            if target and target in edmtrace.PREFIX:
                out[canon(prefix, 4 * off)] = edmtrace.PREFIX[target]
    return out


def canon(prefix: str, off: int) -> tuple[str, int]:
    """The set's embedded render target data is a HWRTDATA (glossary HWRTDATASET+0x018)."""
    if prefix == "HWRTDATASET" and 0x18 <= off < 0x50:
        return "HWRTDATA", off - 0x18
    return prefix, off


# the evidence record of the dataflow (its id here; the retired rewrite kit used to put it in)
EVIDENCE = "E0" "13"


# --- neutral names -----------------------------------------------------------------------

def tok_reg(reg: int) -> str:
    return "{R:0x%04x}" % reg


def tok_word(prefix: str, off: int) -> str:
    return "{W:%s+%#05x}" % (prefix, off)


def tok_flag(prefix: str, off: int, bit: int) -> str:
    return "{F:%s+%#05x:%d}" % (prefix, off, bit)


# --- values ------------------------------------------------------------------------------

@dataclass(frozen=True)
class V:
    kind: str                  # "const", "ptr", "val", "idx" (unknown + value), "unknown"
    value: int = 0             # const
    struct: str = ""           # ptr: the structure it points into
    off: int = 0               # ptr: byte offset
    origin: tuple = ()         # ptr/val: ("S", prefix, off) | ("R", reg) | ("A", n)
    ops: str = ""              # val: transforms since the origin (" & 0xffff")


UNKNOWN = V("unknown")


def ptr(struct: str, off: int = 0) -> V:
    return V("ptr", struct=struct, off=off)


def const(x: int) -> V:
    return V("const", value=x & 0xFFFFFFFF)


def meet(a: V, b: V) -> V:
    """Where two paths join: the same value; a pointer of one type loses its provenance."""
    if a == b:
        return a
    if a.kind == b.kind == "ptr" and (a.struct, a.off) == (b.struct, b.off):
        return V("ptr", struct=a.struct, off=a.off)
    if {a.kind, b.kind} <= {"idx", "const"} and "idx" in (a.kind, b.kind):
        k = min(a.value, b.value)                  # an index: "k + something"
        hi = max(a.value, b.value)
        if a.kind == b.kind or hi == k or (a if a.kind == "idx" else b).value == k:
            return V("idx", value=k)
    return UNKNOWN


@dataclass(frozen=True)
class Pred:
    origin: tuple              # () when the tested value has no origin
    subject: str               # "bit 4 (FLAG)" or "" for comparisons
    t: str                     # when the predicate is true
    f: str                     # when it is false
    compound: bool = False

    def full(self, neg: bool) -> str:
        return " ".join(x for x in (self.subject, self.f if neg else self.t) if x)

    def other(self, neg: bool) -> str:
        return self.t if neg else self.f


@dataclass
class Row:
    kind: str                  # "word", "reg", "sa", "unresolved"
    subject: str
    use: str
    detail: str
    insn: int


@dataclass
class Result:
    rows: list[Row]
    subjects: dict[str, str]                   # subject -> "word", "reg" or "sa"
    inferred: dict[str, str]
    coverage: dict[str, int]
    ranges: list[tuple[int, int]]
    pointers: dict[tuple[str, int], str] = field(default_factory=dict)


# --- control flow ------------------------------------------------------------------------

def ranges(labels: list[int], n: int) -> list[tuple[int, int]]:
    starts = sorted({x for x in labels if 0 <= x < n} | {0})
    return [(s, (starts[k + 1] if k + 1 < len(starts) else n) - 1) for k, s in enumerate(starts)]


def _target(i: edmtrace.Insn) -> int | None:
    if i.args and (m := IMM.match(i.args[0])) and not m.group(1):
        t = int(m.group(2), 0)
        return i.index + t if i.op == "br" else t
    return None


def _ends(i: edmtrace.Insn) -> bool:
    return i.op == "lapc" or "end" in i.mods


def successors(i: edmtrace.Insn, n: int) -> list[int]:
    """Static successors in the same routine flow (a call returns to the next instruction)."""
    nxt = [i.index + 1] if i.index + 1 < n else []
    if _ends(i):
        return [] if not i.pred else nxt
    if i.op in ("ba", "br") and "savelink" not in i.mods:
        t = _target(i)
        if t is None:
            return []
        return [t] if not i.pred else [t] + [x for x in nxt if x != t]
    return nxt


def _call_target(i: edmtrace.Insn) -> int | None:
    return _target(i) if i.op == "ba" and "savelink" in i.mods else None


def _dests(i: edmtrace.Insn) -> list[str]:
    a = i.args
    if not a or i.op in edmtrace.NO_WRITE:
        return []
    if i.op == "ldad" or i.op == "ldaw":
        acc = edmtrace.mem_dwords(i.mods, a[1]) if len(a) > 1 else None
        n = len(acc[1]) if acc else 1
        out = [edmtrace._next_reg(a[0], k) for k in range(n)]
        if acc and acc[2]:
            out.append(acc[0])
        return out
    return [a[0]]


# --- the analysis ------------------------------------------------------------------------

class _Analysis:
    def __init__(self, insns, labels, handlers, pointers, sa_types):
        self.by = {i.index: i for i in insns}
        self.n = max(self.by) + 1 if self.by else 0
        self.handlers = handlers
        self.pointers = pointers
        self.sa_types = sa_types
        self.labels = labels
        self._clob: dict[int, frozenset] = {}

    # names
    def oname(self, o: tuple) -> str:
        if o[0] == "S":
            return tok_word(o[1], o[2])
        if o[0] == "R":
            return tok_reg(o[1])
        return f"sa{o[1]}"

    def describe(self, v: V) -> str:
        if v.kind == "const":
            return f"{v.value:#x}"
        if v.kind == "ptr":
            if v.origin:
                return self.oname(v.origin) + (f" + {v.off:#x}" if v.off else "")
            return f"&{v.struct}+{v.off:#05x}"
        if v.kind == "val":
            return self.oname(v.origin) + v.ops
        return "?"

    # values
    def sa_value(self, n: int) -> V:
        t = self.sa_types.get(n)
        return V("ptr", struct=t, origin=("A", n)) if t else V("val", origin=("A", n))

    def get(self, st, a: str) -> V:
        if a.endswith((".low", ".high")):
            a = a.rsplit(".", 1)[0]
        if (m := IMM.match(a)):
            x = int(m.group(2), 0)
            return const(~x if m.group(1) else x)
        if (m := SA.match(a)):
            return self.sa_value(int(m.group(1)))
        if (m := SA_INDEXED.match(a)):
            fam = self.family(st, int(m.group(1)))
            return UNKNOWN if fam is None else self.sa_value(fam)
        return st[0].get(a, UNKNOWN)

    def family(self, st, k: int) -> int | None:
        """The constant part of an indexed attribute sa[i.l + k]: a slot family."""
        v = st[0].get("i.l", UNKNOWN)
        if v.kind in ("const", "idx"):
            return v.value + k
        if v.kind == "val" and (m := TAIL_ADD.search(v.ops)):
            return int(m.group(1), 16) + k
        return None

    # control flow summaries
    def clobbers(self, t: int) -> frozenset:
        if t in self._clob:
            return self._clob[t]
        self._clob[t] = frozenset()
        out, seen, work = set(), set(), [t]
        while work:
            j = work.pop()
            if j in seen or j not in self.by:
                continue
            seen.add(j)
            i = self.by[j]
            out.update(_dests(i))
            if (c := _call_target(i)) is not None:
                out |= self.clobbers(c)
            work.extend(successors(i, self.n))
        self._clob[t] = frozenset(out)
        return self._clob[t]

    def static_preds(self) -> set[int]:
        out = set()
        for i in self.by.values():
            out.update(successors(i, self.n))
            if (c := _call_target(i)) is not None:
                out.add(c)
        return out

    # fixpoint
    def run(self):
        preds = self.static_preds()
        roots = sorted({0, *self.handlers} | {x for x in self.labels
                                             if x in self.by and x not in preds})
        self.state: dict[int, tuple] = {}
        self.frozen: set[int] = set()
        extra = 0
        for r in roots:
            self._seed(r)
        self._solve(deque(roots))
        self.frozen = set(self.state)     # code that unreached roots may not degrade
        while (todo := [j for j in sorted(self.by) if j not in self.state]):
            extra += 1
            self._seed(todo[0])
            self._solve(deque([todo[0]]))
        self.extra_roots = extra
        self.roots = roots

    def _seed(self, r: int):
        regs = dict(self.handlers.get(r, {}))
        self.state[r] = (regs, {})

    def _merge(self, j: int, st) -> bool:
        if j not in self.by or j in self.frozen:
            return False
        if j not in self.state:
            self.state[j] = st
            return True
        old = self.state[j]
        regs = {}
        for k, v in old[0].items():
            if (m := meet(v, st[0].get(k, UNKNOWN))).kind != "unknown":
                regs[k] = m
        prs = {k: v for k, v in old[1].items() if st[1].get(k) == v}
        if regs == old[0] and len(prs) == len(old[1]):
            return False
        self.state[j] = (regs, prs)
        return True

    def _solve(self, work: deque):
        while work:
            j = work.popleft()
            i = self.by[j]
            out = self.step(self.state[j], i, None)
            if (c := _call_target(i)) is not None:
                if self._merge(c, out):
                    work.append(c)
                clob = self.clobbers(c)
                after = ({k: v for k, v in out[0].items() if k not in clob}, {})
                for s in successors(i, self.n):
                    if self._merge(s, after):
                        work.append(s)
                continue
            for s in successors(i, self.n):
                if self._merge(s, out):
                    work.append(s)

    # one instruction: returns the new state; with rec, records rows
    def step(self, st, i: edmtrace.Insn, rec) -> tuple:
        regs, prs = dict(st[0]), dict(st[1])
        cur = (regs, prs)
        a = i.args
        pinfo = (prs.get(i.pred.lstrip("!")), i.pred.startswith("!")) if i.pred else None

        def emit(kind_subject, use, detail):
            if rec is not None:
                rec.add(kind_subject, use, detail, i.index)

        def guard(text):
            if rec is None or not pinfo:
                return
            p, neg = pinfo
            if p and p.origin:
                emit(p.origin, "guards", f"{p.full(neg)}: {text}")

        def flow(v: V, use: str, where: str):
            """A value with an origin reaches a sink."""
            if v.kind in ("val", "ptr") and v.origin:
                ops = v.ops if v.kind == "val" else (f" + {v.off:#x}" if v.off else "")
                emit(v.origin, use, where + (f" as{ops}" if ops else ""))

        def setreg(r: str, v: V):
            m = SA.match(r)
            mi = SA_INDEXED.match(r)
            fam = self.family(cur, int(mi.group(1))) if mi else None
            if mi and fam is None:
                rec and rec.unresolved("sa_indexed", "indexed secondary attribute", i.index)
                return
            if m or mi:
                n = int(m.group(1)) if m else fam
                emit(("A", n), "write", self.describe(v) + (" (indexed)" if mi else "")
                     + (f" (when {self._cond(pinfo)})" if pinfo else ""))
                flow(v, "to_sa", f"sa{n}")
                rec and rec.fx(i.index, f"sa{n} =")
                rec and rec.store(("A", n), v)
                return
            if not REG.match(r) and r != "i.l":
                return
            if pinfo:
                regs[r] = meet(regs.get(r, UNKNOWN), v)
            else:
                regs[r] = v

        # register accesses
        if i.op == "str" and len(a) >= 2:
            if (m := IMM.match(a[0])):
                reg = int(m.group(2), 0) * 4
                v = self.get(cur, a[1])
                rname = tok_reg(reg)
                c = f" (when {self._cond(pinfo)})" if pinfo else ""
                emit(("R", reg), "write", self.describe(v) + c)
                flow(v, "to_reg", rname + c)
                guard(f"W {rname} <- {self.describe(v)}")
                rec and rec.fx(i.index, f"W {rname}")
                if v.kind in ("unknown", "idx") and rec is not None:
                    rec.unresolved("src", f"source of {rname}", i.index)
            else:
                rec and rec.unresolved("regaddr", "register-supplied register address", i.index)
            return cur
        if i.op == "ldr" and len(a) >= 2:
            if (m := IMM.match(a[1])):
                reg = int(m.group(2), 0) * 4
                emit(("R", reg), "read", f"into {a[0]}")
                setreg(a[0], V("val", origin=("R", reg)))
            else:
                rec and rec.unresolved("regaddr", "register-supplied register address", i.index)
                setreg(a[0], UNKNOWN)
            return cur
        if (c := _call_target(i)) is not None:
            rec and rec.fx(i.index, f"call {c:#x}")
            return cur
        if i.op in ("ba", "br"):
            if pinfo and rec is not None:
                p, neg = pinfo
                t = _target(i)
                if p and p.origin and t is not None:
                    rec.branch(p, neg, i.index, t)
                elif t is not None:
                    rec.unresolved("branch", "branch on a predicate of unknown origin", i.index)
            return cur
        if i.op in ("ldad", "stad", "ldaw"):
            return self._mem(cur, i, rec, pinfo, setreg, emit, flow, guard)
        if not a or i.op in edmtrace.NO_WRITE:
            return cur
        # ALU
        test = next((m[4:] for m in i.mods if m.startswith("test")), None)
        dst, srcs = (a[0], a[2:]) if test else (a[0], a[1:])
        vals = [self.get(cur, s) for s in srcs]
        for s in srcs:
            if (mi := SA_INDEXED.match(s)):
                fam = self.family(cur, int(mi.group(1)))
                if fam is None:
                    rec and rec.unresolved("sa_indexed", "indexed secondary attribute", i.index)
                elif i.op == "mov":
                    emit(("A", fam), "read", f"into {dst} (indexed)")
            elif SA.match(s.split(".")[0]) and i.op == "mov":
                emit(("A", int(SA.match(s.split(".")[0]).group(1))), "read", f"into {dst}")
        res = self._alu(i.op, vals)
        if i.op != "mov" and not test and rec is not None:
            for v in vals:
                if v.kind == "val" and v.origin and res.kind == "val" and res.origin == v.origin:
                    emit(v.origin, "arith", res.ops[len(v.ops):].strip() or i.op)
                elif v.kind == "val" and v.origin:
                    emit(v.origin, "arith", i.op)
        if test:
            p = self._pred(i.op, test, srcs, vals, compound=bool(i.pred))
            if p.origin and rec is not None:
                emit(p.origin, "tested", p.subject or p.t)
            prs[a[1]] = p
        if dst and not dst.startswith("!"):
            setreg(dst, res)
        return cur

    def _cond(self, pinfo) -> str:
        p, neg = pinfo
        if not p or not p.origin:
            return "?"
        return f"{self.oname(p.origin)} {p.full(neg)}"

    def _alu(self, op: str, vals: list[V]) -> V:
        if op == "mov":
            return vals[0] if vals else UNKNOWN
        sym = {"and": "&", "or": "|", "xor": "^", "shl": "<<", "shr": ">>", "rol": "rol",
               "isub16": "-", "usub16": "-", "iaddu32": "+"}
        if op in sym and len(vals) == 2:
            x, y = vals
            if x.kind == y.kind == "const":
                fn = {"and": lambda p, q: p & q, "or": lambda p, q: p | q,
                      "xor": lambda p, q: p ^ q, "shl": lambda p, q: p << (q & 31),
                      "shr": lambda p, q: p >> (q & 31), "isub16": lambda p, q: p - q,
                      "usub16": lambda p, q: p - q, "iaddu32": lambda p, q: p + q}.get(op)
                return const(fn(x.value, y.value)) if fn else UNKNOWN
            if x.kind == "val" and y.kind == "const":
                return V("val", origin=x.origin, ops=f"{x.ops} {sym[op]} {y.value:#x}")
            if y.kind == "val" and x.kind == "const":
                return V("val", origin=y.origin, ops=f"{y.ops} {sym[op]} {x.value:#x}")
            if x.kind == "val":
                return V("val", origin=x.origin, ops=f"{x.ops} {sym[op]} ?")
            return UNKNOWN
        if op in ("imae", "ima32", "ima16") and len(vals) >= 3:
            x, y, z = vals[:3]
            if x.kind == y.kind == "const":
                prod = const(x.value * y.value)
            elif y.kind == "const" and y.value == 1:
                prod = x
            elif x.kind == "val" and y.kind == "const":
                prod = V("val", origin=x.origin, ops=f"{x.ops} * {y.value:#x}")
            else:
                prod = UNKNOWN
            if prod.kind == z.kind == "const":
                return const(prod.value + z.value)
            for p_, q in ((prod, z), (z, prod)):
                if p_.kind == "ptr":
                    if q.kind == "const":
                        return V("ptr", struct=p_.struct, off=p_.off + q.value, origin=p_.origin)
                    if p_.struct in ARRAYS and p_.off == 0:
                        return V("ptr", struct=ARRAYS[p_.struct], origin=p_.origin)
                    return UNKNOWN
            if prod.kind == "val" and z.kind == "const":
                return V("val", origin=prod.origin, ops=f"{prod.ops} + {z.value:#x}")
            if z.kind == "val" and prod.kind == "const":
                return V("val", origin=z.origin, ops=f"{z.ops} + {prod.value:#x}")
            if prod.kind in ("unknown", "idx") and z.kind == "const":
                return V("idx", value=z.value)       # keeps the constant part of an index
            return UNKNOWN
        return UNKNOWN

    def _pred(self, op, cc, srcs, vals, compound) -> Pred:
        x = next((v for v in vals if v.kind in ("val", "ptr") and v.origin), None)
        if x is None:
            return Pred((), "", "?", "?")
        other = [v for v in vals if v is not x]
        y = other[0] if other else UNKNOWN
        named = x.origin[0] == "S" and not x.ops       # a flag bit of a structure word

        def flag(b: int) -> str:
            return f" ({tok_flag(*x.origin[1:], b)})" if named else ""
        zero = {"taz": True, "tanz": False}.get(cc)
        if op == "and" and y.kind == "const" and zero is not None:
            m = y.value
            if m and m & (m - 1) == 0:
                b = m.bit_length() - 1
                subj = f"bit {b}" + flag(b)
                t, f = ("clear", "set") if zero else ("set", "clear")
            else:
                subj = f"& {m:#x}"
                t, f = ("== 0", "!= 0") if zero else ("!= 0", "== 0")
            return Pred(x.origin, subj, t, f, compound)
        if op in ("and", "or") and len(srcs) == 2 and srcs[0] == srcs[1] and zero is not None:
            t, f = ("== 0", "!= 0") if zero else ("!= 0", "== 0")
            return Pred(x.origin, "", t, f, compound)
        if op == "xor" and zero is not None:
            what = self.describe(y)
            t, f = (f"== {what}", f"!= {what}") if zero else (f"!= {what}", f"== {what}")
            return Pred(x.origin, "", t, f, compound)
        if op == "shl" and y.kind == "const" and cc in ("nat", "pat"):
            b = 31 - y.value
            subj = f"bit {b}" + flag(b)
            t, f = ("set", "clear") if cc == "nat" else ("clear (rest nonzero)", "not so")
            return Pred(x.origin, subj, t, f, compound)
        word = {"taz": "== 0", "tanz": "!= 0", "nat": "< 0", "pat": "> 0"}.get(cc, f"test {cc}")
        neg = {"taz": "!= 0", "tanz": "== 0", "nat": ">= 0", "pat": "<= 0"}.get(cc, "not so")
        sym = {"isub16": "-", "usub16": "-", "iaddu32": "+", "or": "|", "xor": "^"}.get(op, op)
        subj = f"{sym} {self.describe(y)}"
        return Pred(x.origin, subj, word, neg, compound)

    def _mem(self, cur, i, rec, pinfo, setreg, emit, flow, guard):
        regs = cur[0]
        a = i.args
        if i.op == "ldaw":
            rec and rec.unresolved("mem", "16-bit load", i.index)
            setreg(a[0], UNKNOWN)
            return cur
        mem_arg, other = (a[1], a[0]) if i.op == "ldad" else (a[0], a[1])
        acc = edmtrace.mem_dwords(i.mods, mem_arg)
        if acc is None:
            rec and rec.unresolved("mem", "register-indexed memory operand", i.index)
            if i.op == "ldad":
                for r in _dests(i):
                    setreg(r, UNKNOWN)
            return cur
        base_reg, dwords, stepn = acc
        base = self.get(cur, base_reg)
        if base.kind != "ptr":
            if base.kind == "val" and base.origin and rec is not None:
                emit(base.origin, "pointer", "untyped" + (f"{base.ops}" if base.ops else ""))
            rec and rec.unresolved("mem", "base of unknown structure", i.index)
        elif base.origin and rec is not None:
            emit(base.origin, "pointer", f"to {base.struct}")
        for k, d in enumerate(dwords):
            loc = canon(base.struct, base.off + 4 * d) if base.kind == "ptr" else None
            if i.op == "ldad":
                r = edmtrace._next_reg(other, k)
                if loc:
                    emit(("S", *loc), "read", f"into {r}")
                    t = self.pointers.get(loc)
                    v = V("ptr", struct=t, origin=("S", *loc)) if t else \
                        V("val", origin=("S", *loc))
                else:
                    v = UNKNOWN
                setreg(r, v)
            else:
                src = edmtrace._next_reg(other, k) if edmtrace.REG.match(other) else other
                v = self.get(cur, src)
                if loc:
                    name = tok_word(*loc)
                    c = f" (when {self._cond(pinfo)})" if pinfo else ""
                    emit(("S", *loc), "write", self.describe(v) + c)
                    flow(v, "to_word", name + c)
                    guard(f"st {name} <- {self.describe(v)}")
                    rec and rec.fx(i.index, f"st {name}")
                    rec and rec.store(("S", *loc), v)
        if stepn:
            if base.kind == "ptr":
                setreg(base_reg, V("ptr", struct=base.struct, off=base.off + 4 * stepn,
                                   origin=base.origin))
            else:
                setreg(base_reg, UNKNOWN)
        return cur


class _Recorder:
    def __init__(self, an: _Analysis):
        self.an = an
        self.rows: list[Row] = []
        self.effects: dict[int, list[str]] = defaultdict(list)
        self.branches: list[tuple[Row, Pred, bool, int, int]] = []
        self.stores: dict[tuple, list[V]] = defaultdict(list)

    def add(self, origin: tuple, use: str, detail: str, insn: int):
        kind = {"S": "word", "R": "reg", "A": "sa"}[origin[0]]
        self.rows.append(Row(kind, _key(origin), use, detail, insn))

    def unresolved(self, use: str, detail: str, insn: int):
        self.rows.append(Row("unresolved", "-", use, detail, insn))

    def fx(self, insn: int, text: str):
        self.effects[insn].append(text)

    def store(self, loc: tuple, v: V):
        self.stores[loc].append(v)

    def branch(self, p: Pred, neg: bool, insn: int, target: int):
        row = Row({"S": "word", "R": "reg", "A": "sa"}[p.origin[0]], _key(p.origin), "branch",
                  "", insn)
        self.rows.append(row)
        self.branches.append((row, p, neg, insn, target))

    def finish(self):
        by = self.an.by
        for row, p, neg, insn, t in self.branches:
            text = f"{p.full(neg)}: to {t:#x}"
            if t <= insn:
                text += " (loop)"
            elif t - insn <= SKIP_MAX:
                fx, jumps = [], None
                for j in range(insn + 1, t):
                    fx.extend(self.effects.get(j, []))
                    i = by.get(j)
                    if i and i.op in ("ba", "br") and not i.pred and "savelink" not in i.mods:
                        jumps = _target(i)
                        break
                if fx or jumps is not None:
                    text += f"; {p.other(neg)}: runs " + (", ".join(fx) if fx else "nothing")
                    if jumps is not None:
                        text += f", then to {jumps:#x}"
            if p.compound:
                text += " (compound test)"
            row.detail = text


def _key(origin: tuple) -> str:
    if origin[0] == "S":
        return f"{origin[1]}+{origin[2]:#05x}"
    if origin[0] == "R":
        return f"0x{origin[1]:04x}"
    return f"sa{origin[1]}"


def _infer(stores: dict[tuple, list[V]], known) -> dict[tuple, str]:
    """Slots that receive pointers to one structure and otherwise only 0, plain copies of other
    slots or values the analysis lost. A transformed value, a register read, a non-zero
    constant or another type rules the slot out; so does, beside a lost value, a pointer whose
    provenance (a typed word or an entry value) was merged away at a join."""
    out = {}
    for loc, vs in stores.items():
        lost = any(v.kind in ("unknown", "idx") for v in vs)
        types = {v.struct for v in vs if v.kind == "ptr" and v.off == 0}
        bad = any(v.kind == "val" and (v.ops or v.origin[0] == "R")
                  or v.kind == "ptr" and lost and not v.origin
                  or v.kind == "ptr" and v.off != 0
                  or v.kind == "const" and v.value != 0 for v in vs)
        if len(types) == 1 and not bad and loc not in known:
            out[loc] = types.pop()
    return out


def analyze(insns, labels: list[int], glossary=None, handlers=None) -> Result:
    """The dataflow of every instruction. handlers: entry -> {reg: V} values at that entry;
    None means the kernel CCB handlers of HANDLERS. glossary is accepted and not used: the
    result names its subjects with tokens that render() resolves."""
    if handlers is None:
        handlers = {}
        for entry, (_cmd, r7) in HANDLERS.items():
            regs = {f"r{4 + k}": V("val", origin=("S", "COMMAND", 4 * k)) for k in range(8)}
            if r7:
                regs["r7"] = V("ptr", struct=r7, origin=("S", "COMMAND", 0x0c))
            handlers[entry] = regs
    pointers = {**_layout_pointers(), **GLOSSARY_POINTERS}
    sa_types = dict(SA_SEEDS)
    inferred: dict[tuple, str] = {}
    for _round in range(8):
        an = _Analysis(insns, labels, handlers, pointers, sa_types)
        an.run()
        rec = _Recorder(an)
        for j in sorted(an.state):
            an.step(an.state[j], an.by[j], rec)
        rec.finish()
        known = {("A", n) for n in sa_types} | {("S", *k) for k in pointers}
        new = _infer(rec.stores, known)
        if not new:
            break
        inferred.update(new)
        for loc, t in new.items():
            if loc[0] == "A":
                sa_types[loc[1]] = t
            else:
                pointers[(loc[1], loc[2])] = t
    rows = sorted(rec.rows, key=lambda r: r.insn)
    subjects = {r.subject: r.kind for r in rows if r.kind in ("word", "reg", "sa")}
    rngs = ranges(labels, an.n)
    reached = {j for j in an.state}
    coverage = {
        "insns": an.n, "reached": len(reached), "routines": len(rngs),
        "routines_reached": sum(1 for s, e in rngs if any(s <= j <= e for j in reached)),
        "roots": len(an.roots), "extra_roots": an.extra_roots,
        "words": sum(1 for k in subjects.values() if k == "word"),
        "registers": sum(1 for k in subjects.values() if k == "reg"),
        "sa": sum(1 for k in subjects.values() if k == "sa"),
    }
    return Result(rows, subjects, {_key(k): v for k, v in inferred.items()}, coverage, rngs,
                  pointers)


# --- TSV ---------------------------------------------------------------------------------

COLUMNS = ["kind", "subject", "use", "detail", "insn", "routine"]


def _routine(rngs, j: int) -> str:
    for s, e in rngs:
        if s <= j <= e:
            return f"{s:#x}-{e:#x}"
    return "-"


def write_tsv(res: Result, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(COLUMNS)
        for k, v in res.coverage.items():
            w.writerow(["meta", k, "", str(v), "", ""])
        for k, v in sorted(res.inferred.items()):
            w.writerow(["typing", k, "inferred", v, "", ""])
        for (pre, off), t in sorted(res.pointers.items()):
            w.writerow(["typing", f"{pre}+{off:#05x}", "given", t, "", ""])
        for r in res.rows:
            w.writerow([r.kind, r.subject, r.use, r.detail, f"{r.insn:#x}",
                        _routine(res.ranges, r.insn)])


def rows_of(res: Result) -> list[dict]:
    """The TSV's rows, as read_tsv gives them back, without writing the file."""
    out = [{"kind": "meta", "subject": k, "use": "", "detail": str(v), "insn": "",
            "routine": ""} for k, v in res.coverage.items()]
    out += [{"kind": "typing", "subject": k, "use": "inferred", "detail": v, "insn": "",
             "routine": ""} for k, v in sorted(res.inferred.items())]
    out += [{"kind": "typing", "subject": f"{pre}+{off:#05x}", "use": "given", "detail": t,
             "insn": "", "routine": ""} for (pre, off), t in sorted(res.pointers.items())]
    out += [{"kind": r.kind, "subject": r.subject, "use": r.use, "detail": r.detail,
             "insn": f"{r.insn:#x}", "routine": _routine(res.ranges, r.insn)} for r in res.rows]
    return out


def read_tsv(path: pathlib.Path) -> list[dict]:
    with open(path, newline="") as f:
        return [dict(r) for r in csv.DictReader(f, delimiter="\t")]


# --- the document ------------------------------------------------------------------------

USE_TEXT = [("read", "read {n}×"), ("write", "written {n}× from"), ("to_reg", "written to"),
            ("to_word", "stored to"), ("to_sa", "kept in"), ("tested", "tested"),
            ("branch", "branches"), ("guards", "guards"), ("pointer", "used as a pointer"),
            ("arith", "arithmetic")]
MAX_DETAILS = 8


def _routines(rs: set[str]) -> str:
    rs = sorted(rs, key=lambda x: int(x.split("-")[0], 16))
    return ", ".join(rs[:3]) + (f" +{len(rs) - 3}" if len(rs) > 3 else "")


_TOKEN = re.compile(r"\{([RWF]):([^{}]+)\}")
_FLAG_NOTE = re.compile(r" \(\{F:([^{}:]+)\+0x([0-9a-f]+):(\d+)\}\)")


def resolve(text: str, g: edmtrace.Glossary) -> str:
    """The glossary's names for the tokens of a detail: a term where it has one, else the
    offset; a flag bit with no term is just the bit."""
    def flag(m):
        name = g.flags.get((m.group(1), int(m.group(2), 16)), {}).get(int(m.group(3)))
        return f" ({name})" if name else ""

    def name(m):
        what, arg = m.groups()
        if what == "R":
            return edmtrace.reg_name(int(arg, 16), g.registers)
        pre, off = arg.split("+")
        return word_term(pre, int(off, 16), g) or edmtrace.word_name(pre, int(off, 16), {})
    return _TOKEN.sub(name, _FLAG_NOTE.sub(flag, text))


def word_term(prefix: str, off: int, g: edmtrace.Glossary) -> str:
    """The glossary's name of a structure word, or '': its term; for a word of a kick3d layout,
    the name edmtrace gives it, which reaches through the layouts nested in it (the TA
    command's shared block, the RT data in the set) and names a word of an array or a wide
    field after the field's first word (name[i], name+k)."""
    if (prefix, off) in g.fields:
        return g.fields[(prefix, off)]
    layout = edmtrace.KICK3D.get(prefix)
    if layout not in kick3d.STRUCTS or off % 4:
        return ""
    name = edmtrace._loc(layout, off // 4, g.fields)
    return "" if name == edmtrace.word_name(prefix, off, {}) else name


def term_of(row: dict, g: edmtrace.Glossary) -> str:
    """The glossary term of a data row's subject, or ''."""
    if row["kind"] == "word":
        pre, off = row["subject"].split("+")
        return word_term(pre, int(off, 16), g)
    if row["kind"] == "reg":
        return g.registers.get(int(row["subject"], 16), "")
    return ""


def _bullet(subject: str, term: str, rows: list[dict]) -> list[str]:
    by: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by[r["use"]].append(r)
    parts = []
    for use, label in USE_TEXT:
        rs = by.get(use)
        if not rs:
            continue
        if use == "read":
            parts.append(label.format(n=len(rs)) + f" ({_routines({r['routine'] for r in rs})})")
            continue
        details: dict[str, list[dict]] = defaultdict(list)
        for r in rs:
            details[r["detail"]].append(r)
        order = sorted(details, key=lambda d: (-len(details[d]), d))
        items = [f"{d} ({len(details[d])}×, {_routines({r['routine'] for r in details[d]})})"
                 for d in order[:MAX_DETAILS]]
        if len(order) > MAX_DETAILS:
            items.append(f"{len(order) - MAX_DETAILS} more")
        head = label.format(n=len(rs))
        sep = " " if use in ("write", "to_reg", "to_word", "to_sa") else ": "
        parts.append(head + sep + "; ".join(items))
    name = f"`{subject}`" + (f" `{term}`" if term else "")
    return textwrap.wrap(f"- {name}: " + ". ".join(parts) + ".", 100, subsequent_indent="  ",
                         break_long_words=False, break_on_hyphens=False)


def _para(text: str) -> list[str]:
    return textwrap.wrap(text, 100, break_long_words=False, break_on_hyphens=False) + [""]


def render(rows: list[dict], glossary: edmtrace.Glossary | None = None) -> str:
    """The document: the TSV's rows with the glossary's names (default: the glossary of this
    repository)."""
    g = glossary or edmtrace.load_glossary()
    rows = [{**r, "detail": resolve(r["detail"], g)} for r in rows]
    meta = {r["subject"]: r["detail"] for r in rows if r["kind"] == "meta"}
    out = ["<!-- SPDX-" "License-Identifier: MIT -->",
           "<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->",
           "# SGX545 EDM dataflow: every structure word and register", "",
           "*Generated from `firmware/edm-dataflow-11/edm_dataflow.tsv` (resgx545-data) by",
           "`harness/ukernel-extract/edm_dataflow.py`; do not edit.*", ""]
    out += _para(
        "A complete forward dataflow analysis of the EDM microkernel (the image is "
        "`$RESGX545_UKERNEL`): our disassembly of the firmware, for interoperability; facts "
        "only, no code. Every routine between the label "
        "addresses is analysed, without aiming at any field: values are followed through "
        "moves, arithmetic, loads, stores, branches (paths that disagree leave the value "
        "unknown) and calls. The analysis starts from instruction 0, from every label no code "
        "reaches (the PDS-entered tasks and the kernel CCB handlers) and from any code still "
        "unreached. Entry values: `sa0`, `sa1`, `sa2`, `sa22` and `sa43` point at TA3D_CTL, "
        "HOST_CTL, CCB_CTL, the kernel CCB and the HWPerf buffer (the captured TA3DCtl, "
        "`doc/specs/hw_spec.md` §11.1); a kernel CCB handler receives the command's words "
        "in `r4`-`r11`, `r7` typed by the command (`doc/specs/transfer.md` §5).")
    out += _para(
        "Names are glossary terms (`doc/glossary.md`) or, where the glossary has "
        "none, offsets: registers `0x0abc`, structure words `STRUCT+0xOFF`, secondary "
        "attributes `saN`. Routines and branch targets are instruction indices (byte address "
        "/ 8). Each use gives its count and up to three routines. `as & 0xffff` is the "
        "transform applied on the way; `when ...` the predicate that guards a write; "
        "\"branches\" gives the condition that takes the branch, its target and, for a short "
        "forward skip, what the other path runs. `?` is a value the analysis could not "
        "follow; such accesses are counted in §6, not guessed.")
    out += _para(f"Evidence: {EVIDENCE} (the dataflow record; dataset firmware-edm-dataflow-11).")
    out += ["## 1. Coverage", ""]
    unres = Counter(r["use"] for r in rows if r["kind"] == "unresolved")
    out += [f"- instructions: {meta.get('insns')}, all analysed ({meta.get('reached')} "
            "reached)",
            f"- routines (label ranges): {meta.get('routines')}, "
            f"{meta.get('routines_reached')} with analysed code",
            f"- entry points: {meta.get('roots')} (plus {meta.get('extra_roots')} for code no "
            "entry reaches)",
            f"- structure words seen: {meta.get('words')}; registers: {meta.get('registers')}; "
            f"secondary attributes: {meta.get('sa')}",
            "- unresolved: " + (", ".join(f"{k} {v}" for k, v in sorted(unres.items()))
                                or "none"), ""]
    out += ["## 2. Pointer typing", ""]
    out += _para(
        "Given: a pointer word a record establishes (E002, E015, `doc/specs/transfer.md` "
        "§2.2; E156-E161, E163-E165, E167, E200, E201 for the render context, the TA "
        "command, the render details, the RT data, the PB descriptor and block and the TA/3D "
        "control block), and the pointer words of kick3d.py's "
        "kernel-side layouts; the list repeats the "
        "inferred structure words, which each later round takes as given. Inferred: a slot the "
        "firmware itself only ever fills with pointers to one structure.")
    typing = [r for r in rows if r["kind"] == "typing"]
    for how in ("inferred", "given"):
        sel = sorted((r for r in typing if r["use"] == how), key=lambda r: r["subject"])
        text = f"{how.capitalize()}: " + "; ".join(f"`{r['subject']}` → {r['detail']}"
                                                   for r in sel) + "."
        out += _para(text)
    data = [r for r in rows if r["kind"] in ("word", "reg", "sa")]
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in data:
        groups[(r["kind"], r["subject"])].append(r)
    out += ["## 3. Structure words", ""]
    words = sorted((k for k in groups if k[0] == "word"),
                   key=lambda k: (k[1].split("+")[0], int(k[1].split("+")[1], 16)))
    struct = None
    for k in words:
        pre = k[1].split("+")[0]
        if pre != struct:
            if struct is not None:
                out.append("")
            out += [f"### {pre}", ""]
            struct = pre
        out += _bullet(k[1], term_of(groups[k][0], g), groups[k])
    out += ["", "## 4. Registers", ""]
    for k in sorted((k for k in groups if k[0] == "reg"), key=lambda k: int(k[1], 16)):
        out += _bullet(k[1], term_of(groups[k][0], g), groups[k])
    out += ["", "## 5. Secondary attributes", ""]
    out += _para("On-chip copies of TA3D_CTL loaded at boot (hardware spec §11.1); "
                 "the EDM also keeps state in them.")
    for k in sorted((k for k in groups if k[0] == "sa"), key=lambda k: int(k[1][2:])):
        out += _bullet(k[1], "", groups[k])
    out += ["", "## 6. Unresolved, by routine", ""]
    by: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        if r["kind"] == "unresolved":
            by[r["routine"]][r["detail"]] += 1
    for rt in sorted(by, key=lambda x: int(x.split("-")[0], 16)):
        out += textwrap.wrap(f"- `{rt}`: " + "; ".join(f"{d} {c}" for d, c in
                                                       sorted(by[rt].items())),
                             100, subsequent_indent="  ", break_long_words=False)
    return "\n".join(out).rstrip() + "\n"


# --- main --------------------------------------------------------------------------------

def load_labels(paths=LABELS) -> list[int]:
    out = []
    for p in paths:
        if pathlib.Path(p).exists():
            for idx in edmtrace.load_labels(pathlib.Path(p).read_text().splitlines()):
                if idx < 0x10000000:            # skip the ESIL register-window flags
                    out.append(idx)
    return out


def main(argv: list[str]) -> int:
    ukernel, tsv, doc = UKERNEL, TSV, DOC
    rest, mode = list(argv), None
    while rest:
        flag = rest.pop(0)
        if flag == "--ukernel" and rest:
            ukernel = pathlib.Path(rest.pop(0))
        elif flag == "--tsv" and rest:
            tsv = pathlib.Path(rest.pop(0))
        elif flag == "--doc" and rest:
            doc = pathlib.Path(rest.pop(0))
        elif flag in ("--check", "--render"):
            mode = flag
        else:
            print(__doc__[__doc__.index("usage:"):].strip(), file=sys.stderr)
            return 2
    if mode == "--check":
        return 0 if doc.read_text() == render(read_tsv(tsv)) else 1
    if mode == "--render":          # the glossary grew: the same TSV, names resolved again
        doc.write_text(render(read_tsv(tsv)))
        return 0
    with open(ukernel, "rb") as f:
        if f.read(8) == FW_MAGIC:
            print(f"{ukernel}: a .fw container; give the cut image (00_ukernel.bin)",
                  file=sys.stderr)
            return 2
    listing = subprocess.run([str(USSE_DIS), str(ukernel)], capture_output=True, text=True,
                             check=True).stdout.splitlines()
    res = analyze(edmtrace.parse(listing), load_labels())
    write_tsv(res, tsv)
    doc.write_text(render(read_tsv(tsv)))
    c = res.coverage
    unres = Counter(r.use for r in res.rows if r.kind == "unresolved")
    print(f"{c['reached']}/{c['insns']} instructions, {c['routines']} routines, "
          f"{c['words']} words, {c['registers']} registers, {c['sa']} secondary attributes; "
          "unresolved: " + (", ".join(f"{k} {v}" for k, v in sorted(unres.items())) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
