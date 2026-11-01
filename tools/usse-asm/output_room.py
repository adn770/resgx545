#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Where the output registers of a tagged pixel shader land (usse/output-room probes).

The shader (pix_tags_x.s, pix_tags_y.s) writes o0 to o7, each the pixel's own x (or y) as the
float of primary attribute 0 (or 1), with the register's number plus one in the low 16 bits. A
pixel of the target then names, by its low bits, the register that reached it, and by its high
bits the pixel that wrote it: a register on its own pixel when the two agree.

    output_room.py report RAW TABLE PROBE     the probe's cases (a label with "from y" is read by row)
"""
from __future__ import annotations

import collections
import struct
import sys

import pixels

BG = pixels.BG
TAG_MASK = 0xffff


def own(coord: int, size: int) -> int:
    """The float bits primary attribute 0 (or 1) holds at pixel column (row) coord."""
    return struct.unpack("<I", struct.pack("<f", (coord + 0.5) / (size / 2) - 1))[0]


def classify(rows: list[list[int]], axis: str, size: int) -> dict:
    """{tag: {"pixels": n, "own": n}} over a target's rows, plus "background" (the tool's
    background colour) and "untagged" counts; a pixel is own when the high bits of its
    value are its own coordinate's float."""
    res: dict = {}
    for y, row in enumerate(rows):
        for x, v in enumerate(row):
            if v == BG:
                res["background"] = res.get("background", 0) + 1
                continue
            tag = v & TAG_MASK
            mine = own(x if axis == "x" else y, size)
            slot = res.setdefault(tag, {"pixels": 0, "own": 0})
            slot["pixels"] += 1
            slot["own"] += (v & ~TAG_MASK) == mine
    return res


def report(raw: str, labels: list[str], axis=("x",), size: int = 64) -> str:
    """Per case of a run (probe NAME__i): its label, then each tag's pixel and own counts."""
    img, fail = pixels.parse(raw)
    names = sorted(set(img) | set(fail), key=lambda n: int(n.rsplit("__", 1)[1]))
    out = []
    for n in names:
        i = int(n.rsplit("__", 1)[1])
        label = labels[i] if i < len(labels) else n
        if n in fail:
            out.append(f"{label}: FAILED {fail[n]}")
            continue
        flat = img[n]
        rows = [flat[k:k + size] for k in range(0, len(flat), size)]
        ax = axis[i] if i < len(axis) else axis[-1]
        res = classify(rows, ax, size)
        out.append(label + ":")
        out += [f"  tag {t}: {c['pixels']} pixels, {c['own']} own" for t, c in sorted(
            (t, c) for t, c in res.items() if isinstance(t, int))]
        if "background" in res:
            out.append(f"  background: {res['background']}")
    return "\n".join(out) + "\n"


def axes(labels: list[str]) -> list[str]:
    """The axis each case's tags come from: "y" when its label says "from y", else "x"."""
    return ["y" if "from y" in lab else "x" for lab in labels]


def main(argv=None) -> int:
    import tomllib
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) != 4 or a[0] != "report":
        print(__doc__)
        return 2
    probe = next(p for p in tomllib.load(open(a[2], "rb"))["probe"] if p["name"] == a[3])
    raw = "\n".join(ln for ln in open(a[1]).read().splitlines() if f"probe {a[3]}__" in ln)
    size = probe.get("size", [64, 64])[0]
    print(report(raw, probe["labels"], axes(probe["labels"]), size), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
