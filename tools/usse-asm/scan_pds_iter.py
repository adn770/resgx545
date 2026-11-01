#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The pixel PDS programs of captured allocations (CAPTURE/**/dump/alloc*_heapbeef0006_*.bin):
each program's code (the movs words before a halt) with the data rows it reads just before
it, disassembled with our pds-dis; tabulates each program's doutu U1, its douti word pairs
and whether it issues doutt, with how many programs share them and one place each is.

    scan_pds_iter.py CAPTURE_ROOT
"""
from __future__ import annotations

import collections
import pathlib
import re
import struct
import subprocess
import sys
import tempfile

DIS = pathlib.Path(__file__).resolve().parents[1] / "usse-dis" / "pds-dis"
HALT = 0xAF000000


def _dword(reg: str) -> int:
    """The data dword a ds operand reads: banks interleave by pairs of dwords."""
    bank, k = int(reg[2]), int(reg[4:-1])
    return 4 * (k // 2) + 2 * bank + k % 2


def _programs(ws: tuple):
    for h, w in enumerate(ws):
        if w != HALT:
            continue
        c = h
        while c > 0 and (ws[c - 1] >> 24) == 0x07:
            c -= 1
        if c < h:
            yield c, h


def scan(root: pathlib.Path) -> list:
    """[(key, count, first place)], commonest first; key = (U1, douti pairs, doutt)."""
    combos: collections.Counter = collections.Counter()
    first = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmpf = pathlib.Path(tmp) / "p.bin"
        for f in sorted(root.glob("**/dump/alloc*_heapbeef0006_*.bin")):
            d = f.read_bytes()
            ws = struct.unpack(f"<{len(d) // 4}I", d[:len(d) // 4 * 4])
            for c, h in _programs(ws):
                tmpf.write_bytes(struct.pack(f"<{h - c + 1}I", *ws[c:h + 1]))
                text = subprocess.run([str(DIS), str(tmpf), "0"], capture_output=True,
                                      text=True).stdout
                ins = [re.search(r"movs (\w+), (.*)", line) for line in text.splitlines()]
                ins = [(m[1], m[2].split(", ")) for m in ins if m]
                regs = [r for _, ops in ins for r in ops if r.startswith("ds")]
                if not regs:
                    continue
                n = 4 * (max(_dword(r) for r in regs) // 4 + 1)
                if c - n < 0:
                    continue
                data = ws[c - n:c]
                u1, fetch, iters = None, False, []
                for port, ops in ins:
                    v = [data[_dword(r)] for r in ops]
                    if port == "doutu":
                        u1 = v[1]
                    elif port == "douti":
                        iters.append((v[0], v[1]))
                    elif port == "doutt":
                        fetch = True
                if not iters:
                    continue
                key = (f"U1 {u1:#010x}" if u1 is not None else "no doutu",
                       " ".join(f"{a:#010x}/{b:#x}" for a, b in iters),
                       "doutt" if fetch else "-")
                combos[key] += 1
                first.setdefault(key, f"{f.relative_to(root)}@{4 * (c - n):#x}")
    return [(k, n, first[k]) for k, n in combos.most_common()]


def main(argv: list[str] | None = None) -> int:
    a = sys.argv[1:] if argv is None else argv
    if len(a) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    for k, n, where in scan(pathlib.Path(a[0])):
        print(n, *k, where, sep="  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
