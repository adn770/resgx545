#!/usr/bin/env python3
"""Phase 11.37 (prepared, not run): probe tables for the client-fill (pixel task) part of items 7, 8,
9 and 13 of fw-probe-requests-2.md, in the format of probes/usse (probe.py).  CLIENT PIXEL TASKS:
they do not answer the firmware (EDM) part of those items.  Expected readbacks are computed here
from the stated models; every hypothesis can fail.  Our own text; nothing closed.

    gen_client.py        write probes/usse/fw37-*.toml (templates in probes/usse/templates)
"""
import itertools, json, pathlib, random, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "probes" / "usse"
M = 0xffffffff
FILL = 0xD0000000


def sext(v):
    return v - (1 << 32) if v & 0x80000000 else v


def hx(v):
    return "0x%08x" % (v & M)


def toml_val(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return hx(v) if v >= 0 else str(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(toml_val(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join("%s = %s" % (json.dumps(str(k)) if not str(k).isidentifier() else k, toml_val(x))
                                for k, x in v.items()) + " }"
    raise TypeError(v)


class Table:
    def __init__(self, fname, comment):
        self.fname, self.comment, self.probes = fname, comment, []

    def probe(self, name, question, source, params, inputs, cases, labels, hyps, temps=None):
        assert len(cases) == len(labels)
        for h, e in hyps.items():
            assert len(e) == len(cases), (name, h)
        self.probes.append(dict(name=name, question=question, source=source, params=params, inputs=inputs,
                                cases=cases, labels=labels, hyps=hyps, temps=temps))

    def write(self):
        o = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
             "# " + self.comment, "# CLIENT PIXEL TASKS (fills), phase 11.37, PREPARED, NOT RUN.",
             'needs = ["render"]', ""]
        for p in self.probes:
            o += ["[[probe]]", "name = " + toml_val(p["name"]), "question = " + toml_val(p["question"]),
                  "source = " + toml_val(p["source"]), "params = " + toml_val(p["params"])]
            if p["temps"]:
                o.append("temps = %d" % p["temps"])
            o += ["inputs = " + toml_val(p["inputs"]), "labels = " + toml_val(p["labels"]),
                  "cases = " + toml_val(p["cases"]), "[probe.hypotheses]"]
            for h, e in p["hyps"].items():
                o.append("%s = %s" % (json.dumps(h), toml_val(e)))
            o.append("")
        (OUT / self.fname).write_text("\n".join(o) + "\n")
        return sum(len(p["cases"]) for p in self.probes)


def ex(v, dwords=None):
    d = {"o0": v}
    if dwords is not None:
        d["dwords"] = dwords
    return d


# ------------------------------------------------------------------ item 7: the compares
PAIRS = [(0, 0), (0, 1), (1, 0), (M, 0), (0, M), (0x80000000, 1), (1, 0x80000000),
         (0x7fffffff, 0x80000000), (0x80000000, 0x7fffffff), (0xffff, 0x10000), (0x10000, 0xffff),
         (M, M), (0x80000001, 0x80000000), (5, 5)]
rng = random.Random(1137)
PAIRS += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(2)]
TRIPLES = [("r5", "r6", "r7", None, "r5r6r7"), ("r26", "r27", "r28", None, "r26r27r28"),
           ("r31", "r30", "r25", None, "r31r30r25"), ("r64", "r65", "r66", 80, "r64r65r66"),
           ("r123", "r122", "r121", 124, "r123r122r121"), ("r1", "r2", "r1", None, "t-is-a")]


def ult(a, b):
    return int(a < b)


def slt(a, b):
    return int(sext(a) < sext(b))


def cmp_table():
    t = Table("fw37-compare.toml", "item 7: the compares on registers other than those run, and with i0 "
              "holding the previous high word (E501, E527, E528 ran r1, r2, r11 and i0 = 0x55 or untouched)")
    for sign, fn in (("u", ult), ("s", slt)):
        for ra, rb, rt, temps, tag in TRIPLES:
            cases, labels = [], []
            for a, b in PAIRS:
                e = fn(a, b)
                cases.append([a, b, 1 - e])
                labels.append("a=%s b=%s" % (hx(a), hx(b)))
            cp = "".join("mov %s, r%d\n" % (r, i) for i, r in ((1, ra), (2, rb)) if r != "r%d" % i)
            body = ("%sand.testtanz.chan0 !c0, p0, r3, r3\n"
                    "ima32.%s %s, i0, %s, c56, %s\n" % (cp, sign, rt, rb, ra))
            if sign == "u":
                body += "xor.testtanz.chan0 !c0, p0, %s, i0\n" % rb
            else:
                body += "xor.testtanz.chan0 !c0, p0, i0, #0\n"
            body += "mov r10, #0\np0 mov r10, #1"
            t.probe("fw37-%scmp-%s" % (sign, tag),
                    "%s a<b from `ima32.%s %s, i0, %s, c56, %s` and the test of the high word on registers "
                    "%s, %s, %s (r10 = a<b; p0 is set to the opposite first, so a p0 that is not written shows)"
                    % ("unsigned" if sign == "u" else "signed", sign, rt, rb, ra, ra, rb, rt),
                    "dump.s", {"OP": body, "OUT": "r10", "D": 0, "E": 0, "F": 0, "G": 0, "H": 0},
                    ["A", "B", "C"], cases, labels,
                    {"model: r10 = a<b %s" % ("unsigned" if sign == "u" else "signed"):
                     [ex(fn(a, b), [fn(a, b)]) for a, b in PAIRS],
                     "rival: p0 keeps the opposite (the compare did not write it)":
                     [ex(1 - fn(a, b), [1 - fn(a, b)]) for a, b in PAIRS]},
                    temps=temps)
    # the previous high word: pc/pd chosen so that a stale i0 gives the opposite p0
    for sign, fn in (("u", ult), ("s", slt)):
        cases, labels, fresh, stale = [], [], [], []
        k = 0
        for a, b in PAIRS:
            e = fn(a, b)
            for kind in ("adversarial", "random"):
                if sign == "u":
                    if kind == "adversarial":
                        pd = b if e else b ^ 0x40
                        pc = pd + 1 if pd < M else pd                      # pc >= pd: i0 = pd
                        pc = max(pc, pd)
                    else:
                        pc, pd = rng.getrandbits(32), rng.getrandbits(32)
                    prev_i0 = (pd - ult(pc, pd)) & M
                    stale_p0 = int((b ^ prev_i0) != 0)
                else:
                    if kind == "adversarial":
                        pc, pd = (5, 3) if e else (3, 5)                    # prev high word 0 / -1
                    else:
                        pc, pd = rng.getrandbits(32), rng.getrandbits(32)
                    prev_i0 = M if slt(pc, pd) else 0
                    stale_p0 = int(prev_i0 != 0)
                cases.append([a, b, 1 - e, pc, pd])
                labels.append("a=%s b=%s prev (%s, %s) %s" % (hx(a), hx(b), hx(pc), hx(pd), kind))
                fresh.append(ex(e, [e]))
                stale.append(ex(stale_p0, [stale_p0]))
        body = ("and.testtanz.chan0 !c0, p0, r3, r3\n"
                "ima32.%s r12, i0, r5, c56, r4\n"                 # the previous compare leaves i0
                "ima32.%s r11, i0, r2, c56, r1\n" % (sign, sign))
        body += ("xor.testtanz.chan0 !c0, p0, r2, i0\n" if sign == "u" else
                 "xor.testtanz.chan0 !c0, p0, i0, #0\n")
        body += "mov r10, #0\np0 mov r10, #1"
        t.probe("fw37-%scmp-prev-i0" % sign,
                "the %s compare right after another compare that left i0 = its high word: does the "
                "second test read the second compare's high word (r10 = a<b) or the previous one" %
                ("unsigned" if sign == "u" else "signed"),
                "dump.s", {"OP": body, "OUT": "r10", "G": 0, "H": 0},
                ["A", "B", "C", "D", "E", "F"], [c + [0] for c in cases], labels,
                {"model: the fresh high word (r10 = a<b)": fresh,
                 "rival: the previous high word is read": stale})
    return t


# ------------------------------------------------------------------ item 8: predicated forms
def pred_table():
    t = Table("fw37-pred.toml", "item 8: the predicated forms the backend emits, p0 kept across gaps "
              "(E477 ran p0 over control flow; E536 ran `p0 mov r, #n` in a firmware task)")
    gaps = [("imm", ""), ("mov1", "mov r12, #0x11370001\n"),
            ("mov4", "".join("mov r%d, #0x1137%04x\n" % (12 + i, i) for i in range(4))),
            ("mov16", "".join("mov r%d, #0x1137%04x\n" % (12 + i % 16, i) for i in range(16))),
            ("mov64", "".join("mov r%d, #0x1137%04x\n" % (12 + i % 16, i) for i in range(64))),
            ("ld1", "ldad r13, [r29,+#20], drc0\nwdf drc0\n"),
            ("ld4", "".join("ldad r%d, [r29,+#%d], drc0\n" % (13 + i, 20 + i) for i in range(4)) + "wdf drc0\n"),
            ("ld16", "".join("ldad r%d, [r29,+#%d], drc0\n" % (13 + i, 20 + i) for i in range(16)) + "wdf drc0\n")]
    forms = [("p0-mov-reg", "p0 mov r10, r11", lambda P, C: C if P else 0xA0A1A2A3),
             ("notp0-mov-reg", "!p0 mov r10, r11", lambda P, C: 0xA0A1A2A3 if P else C),
             ("p0-mov-imm", "p0 mov r10, #0x0c0ffee1", lambda P, C: 0x0c0ffee1 if P else 0xA0A1A2A3),
             ("notp0-mov-imm", "!p0 mov r10, #0x0d0ffee2", lambda P, C: 0xA0A1A2A3 if P else 0x0d0ffee2)]
    drng = random.Random(11370)
    used = set()

    def marker():
        while True:
            v = drng.getrandbits(32) | 0x80000000
            if v not in used and v != 0xA0A1A2A3:
                used.add(v)
                return v
    for tag, line, fn in forms:
        cases, labels, exp = [], [], []
        for gname, g in gaps:
            for P in (0, 1):
                C = marker()
                cases.append([P, 0, C, "and.testtanz.chan0 !c0, p0, r1, r1\n%s%s" % (g, line)])
                labels.append("P=%d gap %s" % (P, gname))
                exp.append(ex(fn(P, C)))
        t.probe("fw37-pred-%s" % tag,
                "`%s` with p0 = (P != 0) set before a gap of movs or ldad and wdf: r10 is the case's "
                "marker (r11) or the preset 0xA0A1A2A3" % line,
                "pred37.s", {}, ["A", "B", "C", "OP"], cases, labels,
                {"model: the form follows p0 over every gap": exp})
    # the predicated ba that is not taken (the taken ba needs a placed program: place-ctl2 d-ba)
    for tag, line, takenP in (("p0-ba-not-taken", "p0 ba #8198", 0), ("notp0-ba-not-taken", "!p0 ba #8198", 1)):
        cases, labels, exp = [], [], []
        for gname, g in gaps[:5]:
            C = marker()
            cases.append([takenP, 0, C, "and.testtanz.chan0 !c0, p0, r1, r1\n%s%s\nmov r10, r11" % (g, line)])
            labels.append("P=%d gap %s" % (takenP, gname))
            exp.append(ex(C))
        t.probe("fw37-pred-%s" % tag,
                "`%s` with the predicate false: not taken, the next `mov r10, r11` runs (r10 = the marker)" % line,
                "pred37.s", {}, ["A", "B", "C", "OP"], cases, labels,
                {"model: falls through": exp,
                 "rival: a predicated ba that is not taken still jumps (r10 keeps the preset)":
                 [ex(0xA0A1A2A3) for _ in cases]})
    return t


# ------------------------------------------------------------------ item 9: the high word, aliased
def partitions(n):
    def rec(i, groups):
        if i == n:
            yield list(groups)
            return
        for g in range(max(groups, default=-1) + 2):
            yield from rec(i + 1, groups + [g])
    yield from rec(0, [])


def hi_table():
    t = Table("fw37-ima32hi-repeat.toml", "item 9: `ima32.u|s d, i0, a, b, c` with every partition of "
              "{d, a, b, c} into registers (15 of them); E525/E526 ran d distinct from a, b, c")
    REGS = ["r10", "r1", "r2", "r3"]                      # d, a, b, c group representatives
    CORN = [(M, M, M), (M, 0x80000000, 0), (0x80000000, 0x80000000, M), (0x10001, M, 1)]
    for sign in ("u", "s"):
        for part in partitions(4):
            if part[0] == part[1] == part[2] == part[3] and False:
                pass
            names = {}
            reg = []
            for slot, g in enumerate(part):
                names.setdefault(g, REGS[slot])
                reg.append(names[g])
            d, a, b, c = reg
            tag = "".join("dabc"[i] if True else "" for i in range(4))
            pname = "".join(chr(ord("a") + g) for g in part)            # e.g. abca: d=a-group..
            prng = random.Random(1137 * 31 + sum(g * 7 ** i for i, g in enumerate(part)) + (sign == "s"))
            cases, labels, lo, hi = [], [], [], []
            for k in range(10):
                if k < len(CORN):
                    base = CORN[k]
                else:
                    base = tuple(prng.getrandbits(32) for _ in range(3))
                # value of each register group; the d group's register also holds d's initial value
                val = {}
                for slot, g in enumerate(part):
                    val.setdefault(g, prng.getrandbits(32) | 0x80000000 if slot == 0 else base[slot - 1])
                # operands read the registers' initial values
                va, vb, vc = (val[part[1]], val[part[2]], val[part[3]])
                if sign == "u":
                    full = va * vb + vc
                else:
                    full = sext(va) * sext(vb) + sext(vc)
                full &= (1 << 64) - 1
                inputs = {"r1": 0, "r2": 0, "r3": 0, "r10": 0}
                for slot, g in enumerate(part):
                    inputs[REGS[slot]] = val[g] if names[g] == REGS[slot] else inputs[REGS[slot]]
                cases.append([inputs["r1"], inputs["r2"], inputs["r3"], inputs["r10"], 0x0a5a5a00 + 17 * k])
                labels.append("d,a,b,c = %s: a=%s b=%s c=%s" % (",".join(reg), hx(va), hx(vb), hx(vc)))
                lo.append(full & M)
                hi.append(full >> 32)
            op = ("mov r10, r4\nmov i0, r8\nima32.%s %s, i0, %s, %s, %s\nmov r11, i0" % (sign, d, a, b, c))
            # the template presets r1..r3 from A..C, r4 from D (the value of r10), r8 from H (i0's marker)
            t.probe("fw37-hi%s-%s" % (sign, pname),
                    "ima32.%s %s, i0, %s, %s, %s (registers shared as %s): r10 = low word, r11 = high word of "
                    "a*b+c read before the write" % (sign, d, a, b, c, "/".join(sorted(set(reg), key=reg.index))),
                    "dump.s", {"OP": op, "OUT": "r10", "E": 0, "F": 0, "G": 0},
                    ["A", "B", "C", "D", "H"], cases, labels,
                    {"model: sources read before the write; r10 = low, r11 = high of the 64-bit result":
                     [ex(l, [l, h]) for l, h in zip(lo, hi)],
                     "rival: i0 is not written (r11 reads i0's preset marker)":
                     [ex(l, [l, 0x0a5a5a00 + 17 * k]) for k, l in enumerate(lo)]})
    return t


# ------------------------------------------------------------------ item 13: narrow memory
V1, V2 = 0x9C8DB6A7, 0x7E6D5C4B            # bytes A7 B6 8D 9C | 4B 5C 6D 7E
SRC = 0xAABBCCDD
BASEADDR = 0x5CAF0040                       # scratch dword 16 (the sim and the tool patch 0x5CAFnnnn)


IMG = V1 | V2 << 32 | (FILL | 18) << 64 | (FILL | 19) << 96      # scratch dwords 16..19


def mem_bytes(off, n):
    return (IMG >> (8 * off)) & ((1 << (8 * n)) - 1)


def narrow_table():
    t = Table("fw37-narrow.toml", "item 13: ldab, ldaw, stab, staw (zero or sign extension, offset units, "
              "unaligned, only its own bytes); the isa tables have the forms (class 29/30, amdt field), no "
              "record ran them; a firmware task cannot (the verifier refuses them)")

    def dump(r10):
        return [r10] + [0xA4A5A6A7, 0xA8A9AAAB, 0xACADAEAF, 0xB0B1B2B3, 0xB4B5B6B7, 0xB8B9BABB, 0xBCBDBEBF] + \
               [FILL | i for i in range(8, 16)] + [V1, V2]

    def sx8(x):
        return x | 0xffffff00 if x & 0x80 else x

    def sx16(x):
        return x | 0xffff0000 if x & 0x8000 else x
    # loads: base aligned (BOFF = 0)
    for op, size, ext in (("ldab", 1, "b"), ("ldaw", 2, "w")):
        cases, labels = [], []
        for off in range(0, 8):
            cases.append([V1, SRC, V2, hx(BASEADDR), "%s r10, [r28,+#%d], drc0" % (op, off)])
            labels.append("%s offset #%d (aligned base)" % (op, off))
        zero_unit, sign_unit, dword_unit = [], [], []
        for off in range(0, 8):
            raw = mem_bytes(off * size, size)                               # element units
            zero_unit.append(ex(raw))
            sign_unit.append(ex((sx8 if size == 1 else sx16)(raw)))
            dword_unit.append(ex(mem_bytes(4 * off, size)))
        hy = {"model: offset counts elements of the access size, zero-extended": zero_unit,
              "rival: offset counts elements, sign-extended": sign_unit,
              "rival: offset counts dwords (the narrow value at dword #off)": dword_unit}
        if size == 2:
            hy["rival: offset counts bytes, zero-extended"] = [ex(mem_bytes(off, 2)) for off in range(8)]
        t.probe("fw37-%s-offsets" % op,
                "%s r10, [r28,+#n]: the value read from the 8 bytes a7 b6 8d 9c 4b 5c 6d 7e (aligned): "
                "zero or sign extension (the high bit is set in a7, b6, 8d, 9c), the unit of n" % op,
                "narrow.s", {}, ["A", "B", "C", "BASE", "OP"], cases, labels, hy)
    # loads: unaligned base
    cases, labels, mod, aligned, nowhere = [], [], [], [], []
    for op, size in (("ldaw", 2), ("ldad", 4)):
        for boff in (1, 2, 3):
            cases.append([V1, SRC, V2, hx(BASEADDR + boff), "%s r10, [r28,+#0], drc0" % op])
            labels.append("%s at base + %d (unaligned for its size)" % (op, boff))
            mod.append(ex(mem_bytes(boff, size)))
            aligned.append(ex(mem_bytes(boff - boff % size, size)))
            nowhere.append(ex(0))
    t.probe("fw37-ld-unaligned",
            "ldaw and ldad at an address that is not a multiple of their size: ldad is documented to read "
            "those bytes (usse_isa 7.10); is that so for ldaw",
            "narrow.s", {}, ["A", "B", "C", "BASE", "OP"], cases, labels,
            {"model: reads the bytes at the address": mod, "rival: reads the aligned-down element": aligned,
             "rival: reads zero": nowhere})
    # stores
    for op, size in (("stab", 1), ("staw", 2)):
        cases, labels, own, lane, none_ = [], [], [], [], []
        for boff in range(0, 4):
            if size == 2 and boff % 2:
                continue
            for off in (0, 1, 2, 3):
                if boff + off * size + size > 8:
                    continue                      # stay inside the two preset dwords
                cases.append([V1, SRC, V2, hx(BASEADDR + boff), "%s [r28,+#%d], r5" % (op, off)])
                labels.append("%s [base+%d, +#%d]" % (op, boff, off))
                addr = boff + off * size
                img = (V2 << 32) | V1
                m = (1 << (8 * size)) - 1
                new = (img & ~(m << (8 * addr))) | ((SRC & m) << (8 * addr)) if addr < 8 else img
                own.append(ex(0xA0A1A2A3, dump(0xA0A1A2A3)[:-2] + [new & M, new >> 32]))
                none_.append(ex(0xA0A1A2A3, dump(0xA0A1A2A3)[:-2] + [V1, V2]))
                lane_img = img
                lane.append(ex(0xA0A1A2A3, dump(0xA0A1A2A3)[:-2] + [new & M, new >> 32]))
        t.probe("fw37-%s" % op,
                "%s [r28,+#n], r5 (r5 = 0xaabbccdd) into the dwords 9c8db6a7 and 7e6d5c4b: only its own "
                "bytes change, the low %d byte(s) of r5 land at byte (base + n * %d)" % (op, size, size),
                "narrow.s", {}, ["A", "B", "C", "BASE", "OP"], cases, labels,
                {"model: byte(s) at base + n*size take the low bytes of r5, nothing else changes": own,
                 "rival: the store lands nowhere": none_})
    # a plain stad control at the same addresses (documented: an unaligned stad lands nowhere)
    cases, labels, own, none_ = [], [], [], []
    for boff in (0, 1, 2):
        cases.append([V1, SRC, V2, hx(BASEADDR + boff), "stad [r28,+#0], r5"])
        labels.append("stad at base + %d" % boff)
        img = (V2 << 32) | V1
        if boff == 0:
            new = (img & ~M) | SRC
        else:
            new = img                             # documented: lands nowhere, no fault
        own.append(ex(0xA0A1A2A3, dump(0xA0A1A2A3)[:-2] + [new & M, new >> 32]))
        none_.append(ex(0xA0A1A2A3, dump(0xA0A1A2A3)[:-2] + [V1, V2]))
    t.probe("fw37-stad-unaligned-control",
            "the documented stad at an unaligned address lands nowhere and does not fault (usse_isa 7.10): the "
            "control for the narrow stores", "narrow.s", {}, ["A", "B", "C", "BASE", "OP"], cases, labels,
            {"model: aligned lands, unaligned lands nowhere": own, "rival: all land at the address": own if False else
             [ex(0xA0A1A2A3, dump(0xA0A1A2A3)[:-2] + [V1, V2]) for _ in cases]})
    return t


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for tab in (cmp_table(), pred_table(), hi_table(), narrow_table()):
        n = tab.write()
        print("%-26s %2d probes %4d cases" % (tab.fname, len(tab.probes), n))


if __name__ == "__main__":
    main()
