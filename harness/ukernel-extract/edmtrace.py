#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Trace what an EDM code range reads and writes: SGX registers and structure fields.

A linear value tracer over usse-dis output ("<idx>: 0x<ENC16>\\t<text>"). It walks the
instructions of a range in order (no branches are followed) and keeps a value for each
register: a constant, a field of a named structure, a pointer into a named structure or
unknown. Seeds say which registers point at which structures when the range starts
(e.g. r1 = the TA command the TA kick runs: cmd_ta, or the glossary's prefix CMDTA). Names come
from the glossary (glossary/, loaded by tools/clean-room/glossary.py): a register prints as its
term, or as its offset (0x0abc) when the glossary has none; a structure word as its term, an
element of an array as the array's term with its index (hw_render_details.src_syncs[1]+2), a
later dword of a field wider than one as the field's term with that dword
(cmd_ta.patches_3d+1), or as STRUCT+0xOFF (CMDTA+0x0f8).
kick3d.py's layouts give the offsets and the pointer typing: a word whose kick3d name is a
structure's address (cmd_ta.hw_render_details_dev_vaddr) yields, when it is loaded, a pointer
into that structure, so the loads and stores through it are named too; a layout nested in
another (the RT data in the RT data set) names its words as its own. A glossary row with no
location is placed by the kick3d field of the same name. kick3d's names are printed only where
the glossary has the same term.

Events, in instruction order:
    W REG <- value         an SGX register write (str #idx), the value as traced
    R REG -> rN            an SGX register read (ldr rN, #idx)
    ld S.field, ...        a load through a pointer into a named structure
    st S.field <- value    a store through such a pointer (or through *S.field, a pointer
                           loaded from a field, or [rN+#k] when the base is unknown)
    call 0xN label         a ba.savelink

Memory operands follow tools/usse-dis/README.md: [b,+#k] is dword b+k, [b,#k++] is b then
b += k, .fetchN [b,+#k] is b+k+1 .. b+k+N, .fetchN [b,#k++] is b+k .. b+k+N-1 then b += N.
The trace is an aid for reading the disassembly, not an emulator: a predicated write or any
instruction it does not model makes the destination unknown, and branch targets do not merge
values.

    usage: edmtrace.py <disasm.txt> <start> <end> [--seed rN=STRUCT[+0xOFF]]...
                       [--labels <file.r2>]... [--glossary <glossary dir>]
"""
from __future__ import annotations

import pathlib
import re
import sys
from dataclasses import dataclass, field

import kick3d

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "clean-room"))
import glossary  # noqa: E402  (the glossary records' loader)

GLOSSARY = ROOT / "glossary"

LINE = re.compile(r"^\s*(\d+):\s+0x[0-9A-Fa-f]{16}\s+(.*)$")
PRED = re.compile(r"^(!?p\d+)\s+(.*)$")
LABEL = re.compile(r"^f\s+(\S+)\s+@\s+(0x[0-9A-Fa-f]+)\s*$")
MEM = re.compile(r"^\[(\w+),(?:([+-])#(\d+)|#(\d+)\+\+)\]$")
REG = re.compile(r"^(r|sa)(\d+)$")
IMM = re.compile(r"^(~?)#(0x[0-9A-Fa-f]+|\d+)$")
HALF = re.compile(r"^(\w+|#0x[0-9A-Fa-f]+|#\d+)(?:\.(low|high))?$")

NO_WRITE = {"str", "stad", "ba", "br", "lapc", "wdf", "idf", "nop", "phas", "smlsi", "ci",
            "cfi", "lock", "emitpds"}

# kick3d layout -> the glossary's structure prefix (the sgx545 column, STRUCT+0xOFF). A layout
# that only lies inside another (the TA register block in the TA command, the 3D register block
# in the render details) is located through the one holding it and has none.
PREFIX = {
    "cmd_ta": "CMDTA", "SGXMKIF_CMDTA_SHARED": "CMDTA_SHARED",
    "hw_render_details": "HWRENDERDETAILS", "hw_rt_data": "HWRTDATA",
    "hw_rt_data_set": "HWRTDATASET", "hw_render_context": "HWRENDERCONTEXT",
    "hw_pb_desc": "HWPBDESC", "pb_block": "PB_BLOCK",
    "SGXMKIF_HWDEVICE_SYNC_LIST": "HWDEVICE_SYNC_LIST", "SGX_CCB_KICK": "SGX_CCB_KICK",
    "PVRSRV_BRIDGE_IN_DOKICK": "DOKICK", "ta3d_ctl": "TA3D_CTL",
}
KICK3D = {v: k for k, v in PREFIX.items()}   # prefix -> layout, for seeds

# The address fields whose name does not end with a layout's: the destination sync list is a
# device sync list, its entry for render target i at 8 + 16 * i (E164); the PB descriptor's
# first block and a block's next are PB blocks (E200, E201).
POINTER_ALIASES = {"dst_sync_list": "SGXMKIF_HWDEVICE_SYNC_LIST", "first_block": "pb_block",
                   "next_block": "pb_block"}
POINTER_SUFFIX = "_dev_vaddr"
PIPES = ("_ta", "_3d")     # the glossary's ta3d_ctl.hw_pb_desc_ta: a layout's address, per pipe


def points_at(structs: dict) -> dict[str, str]:
    """{kick3d field name: the layout it points at}: every field named <x>_dev_vaddr where x
    is in POINTER_ALIASES or ends with a layout's name, with or without its hw_
    (ta_render_details -> hw_render_details), and every field named <layout>_ta or
    <layout>_3d. A layout or a pointer field kick3d gains is typed with no change here."""
    out = {}
    leaves = {path.rsplit(".", 1)[-1] for fields in structs.values()
              for path, _o, width, _c, _a in kick3d._layout(fields) if width == 1}
    for leaf in sorted(leaves):
        if leaf.endswith(PIPES) and leaf[:-3] in structs:
            out[leaf] = leaf[:-3]
        if not leaf.endswith(POINTER_SUFFIX):
            continue
        stem = leaf[:-len(POINTER_SUFFIX)]
        if stem in POINTER_ALIASES:
            out[leaf] = POINTER_ALIASES[stem]
            continue
        words = stem.split("_")
        for k in range(len(words)):
            tail = "_".join(words[k:])
            hit = tail if tail in structs else "hw_" + tail
            if hit in structs:
                out[leaf] = hit
                break
    return out


POINTS_AT = points_at(kick3d.STRUCTS)


def named_layout(shape) -> str | None:
    """The kick3d layout a nested field's shape is, if it is one."""
    return next((k for k, v in kick3d.STRUCTS.items() if v is shape), None)


@dataclass(frozen=True)
class Glossary:
    """Our terms by location: registers by offset, structure words and flag bits by
    (STRUCT, byte offset)."""
    registers: dict[int, str]
    fields: dict[tuple[str, int], str]
    flags: dict[tuple[str, int], dict[int, str]]


TIER_ORDER = {"1": 0, "1c": 1, "2o": 2, "3": 3, "4": 4, "ours": 5}
_REG_LOC = re.compile(r"^0x([0-9a-fA-F]{4})$")
_FIELD_LOC = re.compile(r"([A-Z][A-Z0-9_/]*)\+0x([0-9a-fA-F]+)")
_FLAG_BIT = re.compile(r"\bbit(\d+)\b")
_FRAG_FLAG = re.compile(r"^render flags bit(\d+)\b")


def load_glossary(path: pathlib.Path | str = GLOSSARY) -> Glossary:
    """The best-tier term per register offset, per STRUCT+0xOFF and per flag bit."""
    rows = glossary.load(pathlib.Path(path))
    best: dict[tuple, tuple[int, str]] = {}

    def offer(key, row):
        rank = TIER_ORDER.get(row["tier"], 9)
        if key not in best or rank < best[key][0]:
            best[key] = (rank, row["name"])

    frag, unplaced = [], set()
    for r in rows:
        loc = r["sgx545"].strip()
        if r["kind"] == "register" and (m := _REG_LOC.match(loc)):
            offer(("R", int(m.group(1), 16)), r)
        elif r["kind"] == "field" and " bit" not in loc:
            for m in _FIELD_LOC.finditer(loc):
                for prefix in m.group(1).split("/"):
                    offer(("F", prefix, int(m.group(2), 16)), r)
            if not _FIELD_LOC.search(loc):
                unplaced.add(r["name"])
        elif r["kind"] == "flag":
            if (m := _FRAG_FLAG.match(loc)):
                frag.append((int(m.group(1)), r))
            elif (m := _FIELD_LOC.search(loc)) and (b := _FLAG_BIT.search(loc[m.end():])):
                for prefix in m.group(1).split("/"):
                    offer(("B", prefix, int(m.group(2), 16), int(b.group(1))), r)
    words = {(k[1], k[2]) for k, (_, n) in best.items()
             if k[0] == "F" and n.rsplit(".", 1)[-1] == "frag_flags"}
    for bit, r in frag:
        for prefix, off in words:
            offer(("B", prefix, off, bit), r)
    for name in sorted(unplaced):
        if (where := _kick3d_word(name)) and ("F", *where) not in best:
            best[("F", *where)] = (TIER_ORDER["ours"], name)
    regs, fields, flags = {}, {}, {}
    for k, (_, name) in best.items():
        if k[0] == "R":
            regs[k[1]] = name
        elif k[0] == "F":
            fields[(k[1], k[2])] = name
        else:
            flags.setdefault((k[1], k[2]), {})[k[3]] = name
    return Glossary(regs, fields, flags)


def _kick3d_word(name: str) -> tuple[str, int] | None:
    """(prefix, byte offset) of the kick3d word a glossary term names (pb_block.page_count),
    for the rows that give no location."""
    struct, _, leaf = name.partition(".")
    if struct not in PREFIX or struct not in kick3d.STRUCTS:
        return None
    for path, off, _w, _c, _a in kick3d._layout(kick3d.STRUCTS[struct]):
        if path.rsplit(".", 1)[-1] == leaf:
            return PREFIX[struct], 4 * off
    return None


def word_name(prefix: str, off: int, fields: dict[tuple[str, int], str]) -> str:
    """A structure word: its glossary term, else STRUCT+0xOFF."""
    return fields.get((prefix, off), f"{prefix}+{off:#05x}")


def reg_name(reg: int, names: dict[int, str]) -> str:
    """An SGX register: its glossary term, else its offset."""
    return names.get(reg, f"0x{reg:04x}")


@dataclass(frozen=True)
class Insn:
    index: int
    pred: str | None
    op: str
    mods: list[str]
    args: list[str]
    text: str


@dataclass(frozen=True)
class Event:
    index: int
    text: str


@dataclass(frozen=True)
class Val:
    kind: str            # "const", "field", "ptr", "unknown"
    value: int = 0       # constant, or byte offset of a pointer, or dword of a field
    struct: str = ""
    name: str = ""       # unknown: what it was (a register or an SGX register name); a
    #                      pointer: the structure word it was loaded from


def _split_args(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def parse(lines) -> list[Insn]:
    out = []
    for ln in lines:
        m = LINE.match(ln)
        if not m:
            continue
        text = m.group(2).strip()
        pred, body = None, text
        if (p := PRED.match(text)):
            pred, body = p.group(1), p.group(2)
        word, _, rest = body.partition(" ")
        op, *mods = word.split(".")
        out.append(Insn(int(m.group(1)), pred, op, mods, _split_args(rest), text))
    return out


def load_labels(lines) -> dict[int, str]:
    out = {}
    for ln in lines:
        if (m := LABEL.match(ln.strip())):
            out[int(m.group(2), 16) // 8] = m.group(1)
    return out


def mem_dwords(mods: list[str], operand: str):
    """(base register, dword offsets accessed, post-increment in dwords), or None."""
    m = MEM.match(operand)
    if not m:
        return None
    base, sign, k, post = m.group(1), m.group(2), m.group(3), m.group(4)
    n = next((int(x[5:]) for x in mods if x.startswith("fetch") and x[5:].isdigit()), None)
    if post is not None:
        k = int(post)
        return (base, list(range(k, k + n)), n) if n else (base, [0], k)
    k = int(k) * (-1 if sign == "-" else 1)
    return (base, list(range(k + 1, k + 1 + n)), 0) if n else (base, [k], 0)


def _layout_path(struct: str, dword: int) -> str | None:
    """kick3d's path of a dword (internal: for pointer typing only, never printed)."""
    if struct not in kick3d.STRUCTS:
        return None
    for path, off, width, count, _array in kick3d._layout(kick3d.STRUCTS[struct]):
        if off <= dword < off + width * count and width == 1:
            return path
    return None


def _levels(struct: str, dword: int) -> tuple[list[tuple[str, int]], tuple | None]:
    """The named layouts holding a dword, the outer first, each with the dword's index in it;
    and the leaf (dword of its first element in the deepest layout, element dwords, whether it
    is an array) when the dword is one of an array or of a field wider than one dword."""
    out = [(struct, dword)]
    while struct in kick3d.STRUCTS:
        off, inner = 0, None
        for f in kick3d.STRUCTS[struct]:
            shape, count = f[1], f[2] if len(f) > 2 else 1
            n = kick3d._dwords(shape) if isinstance(shape, list) else shape
            if off <= dword < off + n * count:
                if isinstance(shape, list) and (inner := named_layout(shape)) and count == 1:
                    struct, dword = inner, dword - off
                    out.append((struct, dword))
                    break
                inner = None
                arr = (off, n, count > 1) if count > 1 or n > 1 else None
                return out, arr
            off += n * count
        if inner is None:
            break
    return out, None


def _loc(struct: str, dword: int, fields: dict[tuple[str, int], str]) -> str:
    """A structure word as the glossary names it: at the location in any of the layouts that
    hold it, else as a dword of a named array or wide field (name[i]+k, name+k), else
    STRUCT+0xOFF."""
    levels, arr = _levels(struct, dword)
    for s, d in levels:
        if s in PREFIX and (PREFIX[s], 4 * d) in fields:
            return fields[(PREFIX[s], 4 * d)]
    if arr:
        first, width, indexed = arr      # in the deepest layout
        index, part = divmod(levels[-1][1] - first, width)
        for s, d in levels:
            at = d - index * width - part    # the array's first dword in this layout
            if s in PREFIX and (PREFIX[s], 4 * at) in fields:
                return (fields[(PREFIX[s], 4 * at)] + (f"[{index}]" if indexed else "")
                        + (f"+{part}" if part else ""))
    return word_name(PREFIX.get(struct, struct), 4 * dword, fields)


def _points_at(path: str | None) -> str | None:
    return POINTS_AT.get((path or "").rsplit(".", 1)[-1])


def _next_reg(r: str, i: int) -> str:
    m = REG.match(r)
    return f"{m.group(1)}{int(m.group(2)) + i}" if m else r


@dataclass
class _State:
    regs: dict[str, Val] = field(default_factory=dict)
    fields: dict[tuple[str, int], str] = field(default_factory=dict)

    def get(self, r: str) -> Val:
        if (m := IMM.match(r)) and not m.group(1):
            return Val("const", int(m.group(2), 0))
        return self.regs.get(r, Val("unknown", name=r))

    def set(self, r: str, v: Val) -> None:
        if REG.match(r):
            self.regs[r] = v

    def forget(self, r: str) -> None:
        self.set(r, Val("unknown", name=r))


def describe(v: Val, fields: dict[tuple[str, int], str] | None = None) -> str:
    if v.kind == "const":
        return f"{v.value:#x}"
    if v.kind == "field":
        return _loc(v.struct, v.value, fields or {})
    if v.kind == "ptr":
        # a pointer loaded from a structure word prints as that word
        return v.name if v.name and not v.value else \
            f"&{PREFIX.get(v.struct, v.struct)}+{v.value:#x}"
    return v.name


def _load_val(base: Val, dword: int, fields: dict[tuple[str, int], str]) -> Val:
    d = base.value // 4 + dword
    target = _points_at(_layout_path(base.struct, d))
    return Val("ptr", 0, target, _loc(base.struct, d, fields)) if target \
        else Val("field", d, base.struct)


def _operand(st: _State, a: str) -> tuple[Val, bool]:
    """Value of an imae source (reg or #imm, optional .low/.high) and whether it is 16-bit."""
    m = HALF.match(a)
    if not m:
        return Val("unknown", name=a), False
    v = st.get(m.group(1))
    if m.group(2) and v.kind == "const":
        v = Val("const", (v.value >> 16 if m.group(2) == "high" else v.value) & 0xFFFF)
    return v, bool(m.group(2))


def _imae(st: _State, args: list[str]) -> Val:
    a, _ = _operand(st, args[1])
    b, _ = _operand(st, args[2])
    c, _ = _operand(st, args[3])
    if a.kind == b.kind == "const":
        prod = Val("const", a.value * b.value)
    elif b.kind == "const" and b.value == 1:
        prod = a
    else:
        return Val("unknown", name=args[0])
    if prod.kind == c.kind == "const":
        return Val("const", (prod.value + c.value) & 0xFFFFFFFF)
    if prod.kind == "const" and c.kind == "ptr":
        return Val("ptr", c.value + prod.value, c.struct)
    if prod.kind == "ptr" and c.kind == "const":
        return Val("ptr", prod.value + c.value, prod.struct)
    return Val("unknown", name=args[0])


def _logic(st: _State, op: str, args: list[str]) -> Val:
    a = st.get(args[1])
    m = IMM.match(args[2])
    b = Val("const", int(m.group(2), 0)) if m else st.get(args[2])
    if a.kind != "const" or b.kind != "const":
        return Val("unknown", name=args[0])
    bv = ~b.value & 0xFFFFFFFF if m and m.group(1) else b.value
    res = {"or": a.value | bv, "and": a.value & bv, "xor": a.value ^ bv}[op]
    return Val("const", res)


def trace(insns: list[Insn], start: int, end: int, names: dict[int, str],
          seeds: dict[str, tuple[str, int]], labels: dict[int, str],
          fields: dict[tuple[str, int], str] | None = None) -> list[Event]:
    """Events of insns[start..end]; seeds may name a kick3d layout or a glossary prefix."""
    st = _State(fields=fields or {})
    for r, (struct, off) in seeds.items():
        st.set(r, Val("ptr", off, KICK3D.get(struct, struct)))
    out: list[Event] = []
    for i in insns:
        if not start <= i.index <= end:
            continue
        ev = _step(st, i, names, labels)
        out.extend(Event(i.index, t) for t in ev)
    return out


def _step(st: _State, i: Insn, names, labels) -> list[str]:
    a = i.args
    if i.op == "str" and len(a) >= 2 and (m := IMM.match(a[0])):
        reg = int(m.group(2), 0) * 4
        return [f"W {reg_name(reg, names)} <- {describe(st.get(a[1]), st.fields)}"]
    if i.op == "ldr" and len(a) >= 2 and (m := IMM.match(a[1])):
        name = reg_name(int(m.group(2), 0) * 4, names)
        st.set(a[0], Val("unknown", name=name) if not i.pred else Val("unknown", name=a[0]))
        return [f"R {name} -> {a[0]}"]
    if i.op == "ba" and "savelink" in i.mods and a and (m := IMM.match(a[0])):
        tgt = int(m.group(2), 0)
        return [f"call {tgt:#x}" + (f" {labels[tgt]}" if tgt in labels else "")]
    if i.op in ("ldad", "stad") and len(a) >= 2:
        return _memop(st, i)
    if i.op in NO_WRITE or not a:
        return []
    dst = a[0]
    if i.pred:
        st.forget(dst)
    elif i.op == "mov" and len(a) == 2:
        st.set(dst, st.get(a[1]))
    elif i.op == "imae" and len(a) >= 4:
        st.set(dst, _imae(st, a))
    elif i.op in ("or", "and", "xor") and not i.mods and len(a) == 3:
        st.set(dst, _logic(st, i.op, a))
    else:
        st.forget(dst)
    return []


def _memop(st: _State, i: Insn) -> list[str]:
    a = i.args
    mem_arg, other = (a[1], a[0]) if i.op == "ldad" else (a[0], a[1])
    acc = mem_dwords(i.mods, mem_arg)
    if acc is None:
        if i.op == "ldad":
            st.forget(other)
        return []
    base_reg, dwords, step = acc
    base = st.get(base_reg)
    events = []
    if i.op == "ldad":
        for n, d in enumerate(dwords):
            r = _next_reg(other, n)
            if base.kind == "ptr" and not i.pred:
                st.set(r, _load_val(base, d, st.fields))
            else:
                st.forget(r)
        if base.kind == "ptr":
            events.append("ld " + ", ".join(_loc(base.struct, base.value // 4 + d, st.fields)
                                            for d in dwords))
    else:
        srcs = [st.get(_next_reg(other, n)) if REG.match(other) else st.get(other)
                for n in range(len(dwords))]
        for d, v in zip(dwords, srcs):
            if base.kind == "ptr":
                where = _loc(base.struct, base.value // 4 + d, st.fields)
            elif base.kind == "field":
                where = "*" + _loc(base.struct, base.value, st.fields) + (f"+{d}" if d else "")
            else:
                where = f"[{base_reg}+#{d}]"
            events.append(f"st {where} <- {describe(v, st.fields)}")
    if step:
        if base.kind == "ptr":
            st.set(base_reg, Val("ptr", base.value + 4 * step, base.struct))
        else:
            st.forget(base_reg)
    return events


def format_events(events: list[Event]) -> str:
    return "\n".join(f"{e.index:#06x}  {e.text}" for e in events)


def _parse_seed(s: str) -> tuple[str, tuple[str, int]]:
    reg, _, rhs = s.partition("=")
    struct, _, off = rhs.partition("+")
    return reg, (struct, int(off, 0) if off else 0)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("\n".join(ln.strip() for ln in __doc__.strip().splitlines()[-2:]),
              file=sys.stderr)
        return 2
    listing, start, end, rest = argv[0], int(argv[1], 16), int(argv[2], 16), argv[3:]
    seeds, label_files, glossary = {}, [], GLOSSARY
    while rest:
        flag = rest.pop(0)
        if flag == "--seed" and rest:
            reg, seed = _parse_seed(rest.pop(0))
            seeds[reg] = seed
        elif flag == "--labels" and rest:
            label_files.append(rest.pop(0))
        elif flag == "--glossary" and rest:
            glossary = rest.pop(0)
        else:
            print(f"edmtrace: unknown flag or missing value: {flag}", file=sys.stderr)
            return 2
    g = load_glossary(glossary)
    labels = {}
    for f in label_files:
        labels.update(load_labels(pathlib.Path(f).read_text().splitlines()))
    insns = parse(pathlib.Path(listing).read_text().splitlines())
    print(format_events(trace(insns, start, end, g.registers, seeds, labels, fields=g.fields)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
