# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""fwtask: assemble, verify and pack our own firmware (EDM) task code (phase 11.29).

A task is written in assembler (asm/fwtask/*.s) with `usse-asm` text, plus three conveniences:

    @entry N              the next instruction is the entry point of PDS #13 slot N
    ; @patch res+0x40     (on a `mov.skipinv rD, #0xdeadbeef` line) the kernel patches this
                          immediate with the results page address plus 0x40
    ; @patch cont2        ... with the instruction index of the closed task slot 2 started
                          (taken from the replaced FACT record: no closed index is in a source)
    ; @patch cont4        ... with the index of the closed tasks' shared exit (round 3, R3-K11):
                          the kernel resolves it only for the firmware file whose digest the
                          index was read from (E154), and refuses the arm otherwise
    p0 br @label          a branch to a label; written out as a numeric `br` offset
    ; @patch pds0         ... with the control word of the kernel's PDS image (pds1: its address
                          shifted right by four, pds2: the argument, 0): the three sources of the
                          one emitpds form a task may hold (round 33, N3)
    own_end               the exit of a task that ends itself (E793, E817, E818, E830): the
                          `phas #0, #0, pixel, end, parallel` that declares the end, then `nop.end`;
                          a `.end` without that `phas` before it is a lint warning (lint()), not a
                          refusal: the verifier is unchanged, so an experiment may end otherwise

The default-deny verifier below is the one the kernel repeats (sgxfive_owntask.c, from the table
gen_verify.py writes): a word is accepted only if it matches an allowed form, and `ldr`/`str`
only on the registers of regs.toml. Nothing here reads a closed binary.
"""
from __future__ import annotations

import dataclasses
import functools
import hashlib
import json
import os
import pathlib
import re
import struct
import subprocess
import sys
import tempfile
import tomllib
import warnings

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]       # the repository
ASM = ROOT / "asm" / "fwtask"   # our own task sources and their sha256 map
MAGIC = b"SGXOWN01"
OWN_INDEX = 0x4000          # instruction index of the code page (heap + 0x20000)
MAX_INSNS = 1024            # the code page is 8 KiB
MAX_PATCHES = 256
MAX_ENTRIES = 4
PATCH_KINDS = {"res": 1, "cont": 2, "pds": 3}
PDS_SLOTS = 3               # a pds patch's slot: 0 the control word, 1 the address >> 4, 2 the argument
# the one emitpds form (N3): its sources, s0 to s2, are these registers (E488's operand order)
EMIT_REGS = (2, 3, 4)
EMIT_ENTRY = 1              # the blob's entry the kernel's PDS image starts (its doutu)
# the emitpds words a task may hold: our word (`emitpds.tasks.taske #0, r2, r3, r4, #SB`) with one
# of these 14-bit sidebands, every other field ours; own_arm's form= names them (own the default).
# Round 33 (N3): own, 0; round 39 (N3d row Z): fw14, #14's 0x0843 (N3d O1); round 40 (N3e §3.2,
# the user's decision A (a)): the 16 subsets of 0x843's set bits {0, 1, 6, 11} plus #11's 0x0c43
# and 0x403 (bit 10 without 6 and 11), in the design's order; round 42 (N3g §2 item 1, the user's
# decisions A (a) and F (a)): 0x402 (bit 10 with bits 1:0 = 2, row Q) and 0x400 (bit 10 alone, the
# word only), appended so no earlier index moves. The kernel arms a blob only with the form= that
# names its word (sgx_own_regs.h's sgx_own_emit_forms, generated from this list).
EMIT_BASE = 0xFB20B00000008184
EMIT_SIDEBANDS = (("own", 0x000), ("sb001", 0x001), ("sb002", 0x002), ("sb003", 0x003),
                  ("sb040", 0x040), ("sb041", 0x041), ("sb042", 0x042), ("sb043", 0x043),
                  ("sb800", 0x800), ("sb801", 0x801), ("sb802", 0x802), ("sb803", 0x803),
                  ("sb840", 0x840), ("sb841", 0x841), ("sb842", 0x842), ("fw14", 0x843),
                  ("sbc43", 0xC43), ("sb403", 0x403), ("sb402", 0x402), ("sb400", 0x400))


def emit_word(sideband: int) -> int:
    """Our emitpds word with a 14-bit sideband (usse-dis form #149: value bits 5:0 at word bits
    27:22, 11:6 at 40:35, 13:12 at 55:54; N3d O1)."""
    assert 0 <= sideband < 1 << 14
    return (EMIT_BASE | (sideband & 0x3F) << 22 | (sideband >> 6 & 0x3F) << 35
            | (sideband >> 12 & 3) << 54)


EMIT_FORMS = [(n, sb, emit_word(sb)) for n, sb in EMIT_SIDEBANDS]
EXIT_SLOT = 4               # a continue patch's slot 4: the shared exit, not a slot of PDS #13
# the one firmware file the kernel resolves cont4 for (tools/fwcutter/README.md's cut, format v3)
EXIT_FW_SHA256 = "6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a"


class VerifyError(Exception):
    pass


class LintWarning(UserWarning):
    """A task source that assembles and verifies but ends in a way the records say stalls."""


# ---- the register lists ----------------------------------------------------------------------
@dataclasses.dataclass
class Clock:
    name: str
    offset: int
    record: str


class Regs:
    def __init__(self, doc: dict):
        self.clockgate = [Clock(c["name"], c["offset"], c["record"]) for c in doc["clockgate"]]
        self._allow = {a["offset"] // 4: a for a in doc["allow"]}
        self._deny = [(d["lo"], d["hi"]) for d in doc["deny"]]
        self._clock = {c.offset // 4: c for c in self.clockgate}

    def deny_ranges(self):
        return list(self._deny)

    def why_refused(self, idx: int, op: str) -> str | None:
        """None when `op` ('ldr' or 'str') on register index `idx` is allowed."""
        idx &= 0x3fff
        if idx in self._clock:
            return f"clock gate register {self._clock[idx].name}: never touched"
        a = self._allow.get(idx)
        if a is None:
            return f"register 0x{idx * 4:04x} is not on the allow list"
        if op not in a["use"].split("+"):
            return f"{a['name']} is not allowed for {op}"
        return None

    def ldr_ok(self, idx: int) -> bool:
        return self.why_refused(idx, "ldr") is None

    def str_ok(self, idx: int) -> bool:
        return self.why_refused(idx, "str") is None


def load_regs(path: pathlib.Path | None = None) -> Regs:
    return Regs(tomllib.loads((path or HERE / "regs.toml").read_text()))


def regwidth_deny():
    """tools/campaign/regwidth.py's DENY, the table this one extends."""
    text = (ROOT / "tools/campaign/regwidth.py").read_text()
    m = re.search(r"^DENY = \((.*?)^\)", text, re.S | re.M)
    return [(int(a, 16), int(b, 16)) for a, b in re.findall(r"\((0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+)\)", m.group(1))]


# ---- the form classes ------------------------------------------------------------------------
# (name, kind, mask, value). Default deny, and canonical: an allowed row's mask pins every bit that
# no field of the form names, so a word with a stray bit set is not that form (the hardware's
# reading of such a bit is not established). The fields a row leaves free are the register
# numbers, the immediates, the branch offset and, for br and the limm, the predicate; every bank,
# flag, mode and extension bit is pinned to what our sources (asm/fwtask) assemble to.
# gen_verify.py re-checks each row against the form listing of doc/specs/usse_isa.md (a row
# refines a listing row) and the tests assemble every form. First match wins.
SRC2N = 0x7f                    # source 2 register number, enc[6:0]
SRC1N = 0x7f << 7               # source 1, enc[13:7]
SRC0N = 0x7f << 14              # source 0 / base, enc[20:14]
DSTN = 0x7f << 21               # destination, enc[27:21]
ALL = (1 << 64) - 1
_LIMM_FREE = 0x1FFFFF | 0x1F << 36 | 0x3F << 44 | 7 << 41 | DSTN        # imm, predicate, dst
_MOV_FREE = SRC1N | 3 << 30 | DSTN | 1 << 51                             # src1 and bank, dst, bank
_ALU_FREE = SRC2N | SRC1N | 3 << 28 | 1 << 48 | 1 << 15 | 3 << 34 | 3 << 40
_LDR_FREE = SRC2N | SRC0N | DSTN
_STR_FREE = SRC2N | SRC0N | SRC1N
FORMS = [
    ("mov-limm", "MOVLIMM", ALL & ~_LIMM_FREE, 0xFC20000000000000),                    # #0
    ("mov-reg", "MOVREG", ALL & ~_MOV_FREE, 0x2801100020000000),                       # #1
    # round 3 (R3-K3, Q098): a mov whose destination is a pa register (bank 2: enc[33:32] = 2,
    # enc[51] = 0); the number is checked in pass 1, only pa2 to pa4 (pa0 and pa1 are what the
    # closed task reads, E748, E537)
    ("mov-reg-pa", "MOVPA", ALL & ~(SRC1N | 3 << 30 | DSTN), 0x2801100220000000),      # #1
    ("mov-to-pclink", "MOVPCLINK", ALL & ~SRC1N, 0xF80000C000000000),                  # #126
    ("mov-from-pclink", "MOVFROMPC", ALL & ~DSTN, 0xF800010000000000),                 # #127
    ("nop", "NOP", ALL & ~(1 << 50), 0xF800014000000000),                              # #128
    ("idf", "PLAIN", 0xFFFFFFFEFFFFFFFF, 0xF820000000000000),                          # #6
    ("wdf", "PLAIN", 0xFFFFFFFEFFFFFFFF, 0xF920000000000000),                          # #7
    # round 3 (R3-K11): the two words of the closed tasks' shared exit that no row above has
    # (readings R-1), each as the one exact word, nothing else of its form
    ("cfi-exit", "PLAIN", ALL, 0xF843B300A0000180),                                    # #158
    ("phas-exit", "PLAIN", ALL, 0xFA44070000000000),                                   # #8
    ("br", "BR", ALL & ~(7 << 56 | 0x3FFFF), 0xF800004000000000),                      # #13
    ("lapc", "LAPC", ALL, 0xF800008000000000),                                         # #125
    ("alu-test", "PLAIN", ALL & ~_ALU_FREE, 0x48081081000C0000),                       # #24: and, xor, no write
    ("ima32", "IMA32", ALL, 0xD002008081020089),                                       # #179
    # round 33 (N3): the emitpds form, exactly `emitpds.tasks.taske #0, r2, r3, r4, #SB` with SB
    # one of EMIT_SIDEBANDS (round 33 own, 0; round 39 fw14, 0x0843; round 40 N3e's list); its
    # sources must hold the kernel's patched values (pass 6) and it runs once per task (pass 7),
    # whichever word; the kernel takes each only at the form= that names it
    *[(f"emitpds-{n}", "EMITPDS", ALL, w) for n, _, w in EMIT_FORMS],                  # #149
    ("ldad", "LOAD_ABS", ALL & ~(DSTN | SRC0N | SRC1N), 0xE82B0002A0000000),               # #30
    ("stad", "STORE_ABS", ALL & ~_STR_FREE, 0xF022000080000000),                            # #33
    ("ldr-imm", "LDR", ALL & ~_LDR_FREE, 0xFE21000020000000),                          # #145
    ("str-imm", "STR", ALL & ~_STR_FREE, 0xFE29000020000000),                          # #147
    # the loose forms, kept so that a refusal has a reason: they match what a canonical row left
    ("ldr-any", "DENY", 0xFF38000000000000, 0xFE20000000000000),                       # #146, #145
    ("str-any", "DENY", 0xFF38000000000000, 0xFE28000000000000),                       # #148, #147
    ("ba", "DENY", 0xF87801C000000000, 0xF800000000000000),                            # #12
    ("br-any", "DENY", 0xF87801C000000000, 0xF800004000000000),                        # #13
    ("lapc-any", "DENY", 0xF87001C000000000, 0xF800008000000000),                      # #125
    ("mov-pclink-any", "DENY", 0xF87001C000000000, 0xF80000C000000000),                # #126
    ("nop-any", "DENY", 0xF87001C000000000, 0xF800014000000000),                       # #128
    ("mov-limm-any", "DENY", 0xFF30000000000000, 0xFC20000000000000),                  # #0
]


def classify(w: int) -> tuple[str, str]:
    for name, kind, mask, value in FORMS:
        if w & mask == value:
            return kind, name
    return "UNKNOWN", "unknown"


LIMM_MASK = 0x0003F1F0001FFFFF       # e[20:0], e[40:36], e[49:44]


def limm_set(insn: int, imm: int) -> int:
    """The 32-bit immediate of a `mov rN, #imm` word: imm[20:0] to e[20:0], imm[25:21] to e[40:36],
    imm[31:26] to e[49:44] (fw_format section 4)."""
    v = (imm & 0x1FFFFF) | (imm >> 21 & 0x1F) << 36 | (imm >> 26 & 0x3F) << 44
    return (insn & ~LIMM_MASK) | v


def limm_get(insn: int) -> int:
    return (insn & 0x1FFFFF) | (insn >> 36 & 0x1F) << 21 | (insn >> 44 & 0x3F) << 26


def apply_patches(words, patches, res_addr: int, cont: dict[int, int],
                  pds: dict[int, int] | None = None) -> list[int]:
    """What the kernel overlay does to the blob: res+N -> res_addr + N, contK -> cont[K] (cont[4]:
    the shared exit's index, which the caller has to give), pdsK -> pds[K] (the image's control
    word, address >> 4 and argument)."""
    out = list(words)
    for p in patches:
        if p.kind == "res":
            v = res_addr + p.addend
        elif p.kind.startswith("pds"):
            v = (pds or {})[int(p.kind[3:])]
        else:
            v = cont[int(p.kind[4:])] + p.addend
        out[p.index] = limm_set(out[p.index], v & 0xFFFFFFFF)
    return out


def reg_index(w: int) -> int:
    """The 14-bit immediate index of an ldr/str: enc[6:0] low, enc[20:14] high."""
    return (w & 0x7f) | (w >> 14 & 0x7f) << 7


def br_target(i: int, w: int) -> int:
    off = w & 0x3ffff
    if off & 0x20000:
        off -= 0x40000
    return i + off


def limm_dest(w: int) -> int:
    return w >> 21 & 0x7f


def mov_pclink_src(w: int) -> int:
    return w >> 7 & 0x7f


def dst_num(w: int) -> int:
    return w >> 21 & 0x7f


def base_num(w: int) -> int:
    return w >> 14 & 0x7f


def offset_imm(w: int) -> int:
    return w >> 7 & 0x7f


def pred_of(kind: str, w: int) -> int:
    return w >> 41 & 7 if kind == "MOVLIMM" else w >> 56 & 7


@dataclasses.dataclass(frozen=True)
class Patch:
    index: int
    kind: str       # "res" or "cont<slot>"
    addend: int = 0


def _patch_kind(kind: str) -> tuple[int, int] | None:
    if kind == "res":
        return PATCH_KINDS["res"], 0
    m = re.fullmatch(r"cont(\d+)", kind)
    if m and int(m.group(1)) < 256:
        return PATCH_KINDS["cont"], int(m.group(1))
    m = re.fullmatch(r"pds(\d+)", kind)
    if m and int(m.group(1)) < 256:
        return PATCH_KINDS["pds"], int(m.group(1))
    m = re.fullmatch(r"kind(\d+)", kind)           # a kind byte of a hand-made blob (tests)
    if m and int(m.group(1)) < 256:
        return int(m.group(1)), 0
    return None


RES_SIZE = 0x1000           # the results page (the kernel's SGX_OWN_RES_SIZE)
TRACKED = 32                # the registers a store or load base may name (the stock 32 temporaries)
TOP = 0xffff                # a register's state in the base analysis: unknown (else the page offset)
PDS_STATE = 0xfff0          # + slot: the register holds the kernel's pds<slot> value


class Why:
    """The reasons a blob is refused. The first line of each is the kernel's `why` string
    (sgxfive_owntask.c), the same text on both sides: the differential test compares them."""
    CLOCK = "clock gate register"
    STR = "str of a register not on the list"
    LDR = "ldr of a register not on the list"
    DENY = "form not allowed"
    UNKNOWN = "unknown form"
    BR_OUT = "br leaves the blob"
    PATCH_LIMM = "patch not on an unpredicated mov limm"
    PATCH_TWICE = "two patches on one word"
    PATCH_SLOT = "bad slot"
    PATCH_KIND = "unknown patch kind"
    PATCH_ADD = "patch addend out of range"
    LAPC = "lapc is not the patched continue triple"
    PCLINK = "mov pclink outside the continue triple"
    BR_TRIPLE = "branch into the continue triple"
    LAST = "the last word does not end the task"
    ENTRY = "entry outside the blob or inside a continue triple"
    BASE = "load or store base is not the results page"
    PA = "mov to a pa register not on the list"
    EMIT_ARGS = "emitpds sources are not the kernel's image"
    EMIT_ONCE = "emitpds can run twice"
    EMIT_ENTRY = "emitpds without the started task's entry"


PA_OK = (2, 3, 4)           # the pa registers a mov may write (R3-K3)


def verify_why(words: list[int], patches: list[Patch], regs: Regs, entries=(),
               base: int = OWN_INDEX) -> list[tuple[int | None, str, str]]:
    """Every reason the blob is refused as (instruction, why, detail), pass by pass, the first
    pass that finds any ending the scan; empty: accepted. The passes and their order are the
    kernel's: forms, patches, the continue triple, the last word, the entries, the bases."""
    n = len(words)
    if not 0 < n <= MAX_INSNS:
        return [(None, "size", f"{n} instructions: need 1 to {MAX_INSNS}")]
    err: list[tuple[int | None, str, str]] = []
    cls = [classify(w) for w in words]
    kinds = [c[0] for c in cls]
    # pass 1: every word a canonical form; ldr and str on the lists; branches inside the blob
    for i, w in enumerate(words):
        kind, name = cls[i]
        if kind == "UNKNOWN":
            err.append((i, Why.UNKNOWN, f"unknown form 0x{w:016x}"))
        elif kind == "DENY":
            err.append((i, Why.DENY, f"form {name} (0x{w:016x}) is not allowed"))
        elif kind in ("LDR", "STR"):
            op = kind.lower()
            why = regs.why_refused(reg_index(w), op)
            if why:
                key = Why.CLOCK if why.startswith("clock gate") else Why.STR if op == "str" else Why.LDR
                err.append((i, key, f"{op} #{reg_index(w)}: {why}"))
        elif kind == "BR":
            t = br_target(i, w)
            if not 0 <= t < n:
                err.append((i, Why.BR_OUT, f"br leaves the blob (target {t})"))
        elif kind == "MOVPA" and dst_num(w) not in PA_OK:
            err.append((i, Why.PA, f"mov to pa{dst_num(w)}: only pa2 to pa4"))
        elif kind == "EMITPDS" and kinds[:i].count("EMITPDS"):
            err.append((i, Why.EMIT_ONCE, "a second emitpds"))
    if err:
        return err
    # pass 2: the patches
    pk = [0] * n            # 0 none, 1 res, 2 cont
    padd = [0] * n
    for p in patches:
        if not 0 <= p.index < n or kinds[p.index] != "MOVLIMM" or pred_of("MOVLIMM", words[p.index]):
            err.append((p.index, Why.PATCH_LIMM, f"patch at {p.index}: not an unpredicated mov limm"))
            continue
        k = _patch_kind(p.kind)
        if k is not None and ((k[0] == PATCH_KINDS["cont"] and k[1] > EXIT_SLOT) or
                              (k[0] == PATCH_KINDS["pds"] and k[1] >= PDS_SLOTS)):
            err.append((p.index, Why.PATCH_SLOT, f"patch at {p.index}: slot {k[1]}"))
        elif k is None or k[0] not in PATCH_KINDS.values():
            err.append((p.index, Why.PATCH_KIND, f"patch at {p.index}: unknown kind {p.kind}"))
        elif pk[p.index]:
            err.append((p.index, Why.PATCH_TWICE, f"patch at {p.index}: a second patch"))
        elif k[0] in (PATCH_KINDS["cont"], PATCH_KINDS["pds"]) and p.addend != 0:
            err.append((p.index, Why.PATCH_ADD, f"patch at {p.index}: a continue or pds patch has no addend"))
        elif k[0] == PATCH_KINDS["res"] and p.addend >= RES_SIZE:
            err.append((p.index, Why.PATCH_ADD, f"patch at {p.index}: addend 0x{p.addend:x} past the page"))
        else:
            pk[p.index] = k[0]
            padd[p.index] = k[1] if k[0] == PATCH_KINDS["pds"] else p.addend
    if err:
        return err
    # pass 3: the continue triple, and nothing else touches pclink or branches into it
    for i in range(n):
        if kinds[i] == "LAPC":
            if (i < 2 or kinds[i - 1] != "MOVPCLINK" or kinds[i - 2] != "MOVLIMM" or
                    pk[i - 2] != PATCH_KINDS["cont"] or
                    mov_pclink_src(words[i - 1]) != limm_dest(words[i - 2])):
                err.append((i, Why.LAPC, "lapc without a patched limm and mov pclink of its own"))
        elif kinds[i] == "MOVPCLINK":
            if i + 1 >= n or kinds[i + 1] != "LAPC":
                err.append((i, Why.PCLINK, "mov pclink not followed by lapc"))
        elif kinds[i] == "BR":
            t = br_target(i, words[i])
            if kinds[t] in ("MOVPCLINK", "LAPC"):
                err.append((i, Why.BR_TRIPLE, f"br to {t}, inside the continue triple"))
    if err:
        return err
    # pass 4: the task ends: the last word cannot fall off the blob
    last = words[n - 1]
    ends = (kinds[n - 1] == "LAPC" or (kinds[n - 1] == "BR" and not pred_of("BR", last)) or
            (kinds[n - 1] == "NOP" and last >> 50 & 1))
    if not ends:
        return [(n - 1, Why.LAST, "falls off the end of the blob")]
    # pass 5: the entries
    for e in entries:
        if not 0 <= e < n or kinds[e] in ("MOVPCLINK", "LAPC"):
            err.append((None, Why.ENTRY, f"entry {e}"))
    if err:
        return err
    if "EMITPDS" in kinds and len(entries) <= EMIT_ENTRY:
        return [(kinds.index("EMITPDS"), Why.EMIT_ENTRY, "an emitpds needs the started task's entry 1")]
    # pass 6: a load or store base is a register that every path from an entry set to the results
    # page, never written since, and the address stays in the page (the EDM's page directory maps
    # the closed code and data too: a base from anywhere else could store into it); the emitpds's
    # sources hold the kernel's pds0 to pds2 the same way
    err = _check_bases(words, kinds, pk, padd, entries)
    if err:
        return err
    # pass 7: the emitpds runs once per task: nothing after it reaches it again, nor does the task
    # the image starts (entry 1)
    if "EMITPDS" in kinds:
        e = kinds.index("EMITPDS")
        if e in _reach(words, kinds, [e + 1, entries[EMIT_ENTRY]]):
            return [(e, Why.EMIT_ONCE, "the emitpds is reached again")]
    return []


def _succ(i: int, w: int, kind: str) -> list[int]:
    """The words control goes to after word i (none past the end, after an end or a lapc)."""
    if kind == "LAPC" or (kind == "NOP" and w >> 50 & 1):
        return []
    if kind == "BR":
        return [br_target(i, w)] + ([i + 1] if pred_of("BR", w) else [])
    return [i + 1]


def _reach(words, kinds, starts) -> set[int]:
    """Every word some path from one of `starts` reaches (the starts included)."""
    n = len(words)
    seen: set[int] = set()
    work = [s for s in starts if 0 <= s < n]
    while work:
        i = work.pop()
        if i in seen:
            continue
        seen.add(i)
        work += [j for j in _succ(i, words[i], kinds[i]) if 0 <= j < n]
    return seen


def _effects(kind: str, w: int, k: int, add: int, st: list[int]) -> list[int]:
    """The base-analysis state after one word (a copy)."""
    out = list(st)
    d = dst_num(w)
    if kind == "MOVLIMM":
        if d < TRACKED:
            out[d] = add if k == PATCH_KINDS["res"] else PDS_STATE + add if k == PATCH_KINDS["pds"] else TOP
    elif kind == "MOVREG":
        if not w >> 51 & 1 and d < TRACKED:
            out[d] = TOP
    elif kind in ("MOVFROMPC", "LDR", "LOAD_ABS"):
        if d < TRACKED:
            out[d] = TOP
    elif kind == "IMA32":
        for r in (d, d + 1):
            if r < TRACKED:
                out[r] = TOP
    return out


def _check_bases(words, kinds, pk, padd, entries):
    n = len(words)
    st: list[list[int] | None] = [None] * n
    work: list[int] = []
    for e in entries:
        st[e] = [TOP] * TRACKED
        work.append(e)

    def flow(j: int, s: list[int]):
        cur = st[j]
        if cur is None:
            st[j] = list(s)
            work.append(j)
            return
        new = [a if a == b else TOP for a, b in zip(cur, s)]
        if new != cur:
            st[j] = new
            work.append(j)

    while work:
        i = work.pop()
        w, kind = words[i], kinds[i]
        out = _effects(kind, w, pk[i], padd[i], st[i])
        if kind == "LAPC" or (kind == "NOP" and w >> 50 & 1):
            continue
        if kind == "BR":
            flow(br_target(i, w), out)
            if pred_of("BR", w):
                flow(i + 1, out)
        else:
            flow(i + 1, out)
    err = []
    for i in range(n):
        if st[i] is not None and kinds[i] == "EMITPDS":
            if any(st[i][r] != PDS_STATE + s for s, r in enumerate(EMIT_REGS)):
                err.append((i, Why.EMIT_ARGS, "an emitpds source is not the kernel's pds value"))
            continue
        if st[i] is None or kinds[i] not in ("LOAD_ABS", "STORE_ABS"):
            continue
        b = base_num(words[i])
        v = st[i][b] if b < TRACKED else TOP
        if v == TOP or v + 4 * (offset_imm(words[i]) + 1) > RES_SIZE:
            err.append((i, Why.BASE, f"base r{b} is not the results page, or the offset leaves it"))
    return err


def verify(words: list[int], patches: list[Patch], regs: Regs, entries=(),
           base: int = OWN_INDEX) -> list[str]:
    """Every reason the blob is refused (empty: accepted)."""
    return [d if i is None else f"insn {i}: {d}" for i, _, d in verify_why(words, patches, regs, entries, base)]


# ---- the blob --------------------------------------------------------------------------------
@dataclasses.dataclass
class Blob:
    words: list[int]
    patches: list[Patch]
    entries: list[int]


def pack_blob(words, patches, entries) -> bytes:
    out = MAGIC + struct.pack("<HHHH", len(words), len(patches), len(entries), 0)
    out += b"".join(struct.pack("<Q", w) for w in words)
    for p in patches:
        k, slot = _patch_kind(p.kind)
        out += struct.pack("<HBBI", p.index, k, slot, p.addend)
    out += b"".join(struct.pack("<H", e) for e in entries)
    return out


def parse_blob(b: bytes) -> Blob:
    if len(b) < 16 or b[:8] != MAGIC:
        raise VerifyError("bad magic")
    n, np_, ne, _ = struct.unpack_from("<HHHH", b, 8)
    need = 16 + 8 * n + 8 * np_ + 2 * ne
    if len(b) != need:
        raise VerifyError("bad length")
    words = list(struct.unpack_from(f"<{n}Q", b, 16))
    patches = []
    for k in range(np_):
        idx, kind, slot, add = struct.unpack_from("<HBBI", b, 16 + 8 * n + 8 * k)
        patches.append(Patch(idx, "res" if kind == 1 else f"cont{slot}" if kind == 2 else
                             f"pds{slot}" if kind == 3 else f"kind{kind}", add))
    entries = list(struct.unpack_from(f"<{ne}H", b, 16 + 8 * n + 8 * np_))
    return Blob(words, patches, entries)


def refusal(b: bytes, regs: Regs) -> str | None:
    """The first reason a blob is refused (a Why string, "parse" for a malformed blob), None if it
    is accepted: the verdict the kernel's verifier gives, to compare with it."""
    try:
        p = parse_blob(b)
    except (VerifyError, struct.error):
        return "parse"
    if len(p.entries) > MAX_ENTRIES or len(p.patches) > MAX_PATCHES:
        return "parse"
    err = verify_why(p.words, p.patches, regs, p.entries)
    if not err:
        return None
    return "parse" if err[0][1] == "size" else err[0][1]


def verify_blob(b: bytes, regs: Regs) -> list[str]:
    try:
        p = parse_blob(b)
    except (VerifyError, struct.error) as e:
        return [str(e)]
    if len(p.entries) > MAX_ENTRIES or len(p.patches) > MAX_PATCHES:
        return ["too many entries or patches"]
    return verify(p.words, p.patches, regs, p.entries)


# ---- the assembler front end -----------------------------------------------------------------
@functools.cache
def usse_asm_path() -> str:
    if os.environ.get("FWTASK_USSE_ASM"):
        return os.environ["FWTASK_USSE_ASM"]
    d = ROOT / "tools" / "usse-asm"
    r = subprocess.run(["make", "-s", "-C", str(d), "usse-asm"], capture_output=True, text=True)
    if r.returncode:
        raise FileNotFoundError(f"cannot build the assembler in {d}:\n{r.stderr}")
    return str(d / "usse-asm")


def assemble_text(text: str) -> list[int]:
    """Plain usse-asm text to 64-bit words."""
    with tempfile.TemporaryDirectory() as d:
        src, out = pathlib.Path(d, "a.s"), pathlib.Path(d, "a.bin")
        src.write_text(text if text.endswith("\n") else text + "\n")
        r = subprocess.run([usse_asm_path(), "-o", str(out), str(src)], capture_output=True, text=True)
        if r.returncode:
            raise VerifyError(r.stderr.strip())
        data = out.read_bytes()
    return list(struct.unpack(f"<{len(data) // 8}Q", data))


OWN_END = ["phas #0, #0, pixel, end, parallel", "nop.end"]
EXIT_PHAS = re.compile(r"^phas\b.*\bend\b")
HAS_END = re.compile(r"^(?:\w+\s*:\s*)*[\w.]*\.end\b")


def lint(src: str) -> list[str]:
    """Warnings for a task source: an instruction with `.end` whose previous instruction is not
    the exit `phas ... end` (E817 and E830: such an end, 7 of 7 times without it, stops the EDM
    tick). `own_end` writes the right pair."""
    lines = preprocess(src)[0]
    return [f"instruction {i}: `{ln}` ends the task without the exit `phas ... end` before it "
            f"(use own_end)"
            for i, ln in enumerate(lines)
            if HAS_END.match(ln) and not (i and EXIT_PHAS.match(lines[i - 1]))]


LABEL = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


def preprocess(src: str):
    """-> (usse-asm lines, entries, patch markers, label table); br @label made numeric."""
    lines, entries, patches, labels = [], [], [], {}
    pending_br = []
    for raw in src.splitlines():
        code, _, comment = raw.partition(";")
        code = code.strip()
        m = LABEL.match(code)
        while m:
            labels[m.group(1)] = len(lines)
            code = m.group(2).strip()
            m = LABEL.match(code)
        if code == "own_end":
            lines.extend(OWN_END)
            continue
        if code.startswith("@entry"):
            entries.append(len(lines))
            continue
        if not code:
            continue
        pm = re.search(r"@patch\s+(\S+)", comment)
        if pm:
            spec = pm.group(1)
            kind, _, add = spec.partition("+")
            patches.append(Patch(len(lines), kind, int(add, 0) if add else 0))
        bm = re.search(r"\bbr\s+@(\w+)", code)
        if bm:
            pending_br.append((len(lines), bm.group(1)))
        lines.append(code)
    for i, lab in pending_br:
        if lab not in labels:
            raise VerifyError(f"undefined label {lab}")
        off = labels[lab] - i
        txt = f"-#0x{-off:08x}" if off < 0 else f"#0x{off:08x}"
        lines[i] = re.sub(r"\bbr\s+@\w+", "br " + txt, lines[i])
    return lines, entries, patches


def assemble_source(src: str) -> list[int]:
    return assemble_text("\n".join(preprocess(src)[0]))


def build_blob_text(src: str, regs: Regs | None = None) -> bytes:
    lines, entries, patches = preprocess(src)
    for w in lint(src):
        warnings.warn(w, LintWarning, stacklevel=2)
    words = assemble_text("\n".join(lines))
    regs = regs or load_regs()
    err = verify(words, patches, regs, entries)
    if err:
        raise VerifyError("; ".join(err))
    return pack_blob(words, patches, entries)


def build_map(sources, outdir: pathlib.Path) -> dict:
    """Assemble each source to <name>.blob in outdir; the map has the sha256 of source and blob."""
    m = {}
    outdir = pathlib.Path(outdir)
    for s in sources:
        s = pathlib.Path(s)
        blob = build_blob_text(s.read_text())
        (outdir / f"{s.stem}.blob").write_bytes(blob)
        m[s.stem] = {"source": s.name, "source_sha256": hashlib.sha256(s.read_bytes()).hexdigest(),
                     "sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob),
                     "insns": parse_blob(blob).words.__len__()}
    (outdir / "fwtask.map").write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    return m


def sources() -> list[pathlib.Path]:
    return sorted(ASM.glob("*.s"))


def blob_of(name: str) -> bytes:
    """The blob of asm/fwtask/<name>.s, assembled and verified now."""
    return build_blob_text((ASM / f"{name}.s").read_text())


def current_map() -> dict:
    """The sha256 map of every source and the blob it assembles to, as build_map writes it."""
    with tempfile.TemporaryDirectory() as d:
        return build_map(sources(), pathlib.Path(d))


def main(argv: list[str]) -> int:
    if argv[1:2] == ["map"]:        # rewrite asm/fwtask/fwtask.map
        (ASM / "fwtask.map").write_text(json.dumps(current_map(), indent=1, sort_keys=True) + "\n")
        return 0
    if len(argv) < 3:
        print("usage: fwtask.py map | fwtask.py OUTDIR source.s...", file=sys.stderr)
        return 2
    out = pathlib.Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    warnings.simplefilter("always", LintWarning)
    try:
        m = build_map(argv[2:], out)
    except VerifyError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    for k, v in m.items():
        print(f"{k}: {v['insns']} insns, sha256 {v['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
