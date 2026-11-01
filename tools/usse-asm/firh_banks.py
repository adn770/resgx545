#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""firh's fixed banks 1 and 2: the tap families the simulator's FIXED_BANKS table holds.

E079 measured each fixed set's change for a byte raised by 0x20 on a pedestal, and E293 bank
2's sets 2 and 3 on a lifted line; a 0x20 step moves the result by one count per 4/128 of tap,
so the taps are known to about 4 in 128ths. The family of a set is every tap vector within
WINDOW per tap of its centre (CENTRES: E079's changes times 4, E293's taps, in 128ths, shift
7) for which some bias fits on every case of the set, with the bias range those cases allow.
The cases are the single-firh fill vectors of the data repository whose job loads the filter
block at CR_USE_COEFFS_MODE 1 or 2: usse-filter-banks, usse-filter-control (modes 1 and 2) and
usse-filter-bank2, centred from -4. WINDOW = 5 is a choice ([infer]): it holds the measured
filter and the vectors near it that the 0x20 steps cannot tell apart.

The simulator gives a result only where every member agrees, and counts such a match as
fitted, not as a hardware check: the families are fitted to these same vectors (E292).

    firh_banks.py [--data DIR]          print the Rust table (crates/sgx-sim/src/usse.rs)
    firh_banks.py check [--data DIR]    exit 1 unless usse.rs holds exactly that table
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
USSE_RS = ROOT / "crates" / "sgx-sim" / "src" / "usse.rs"
WINDOW = 5
SHIFT = 7
# (bank, set): (centre taps in 128ths, position of the first tap)
CENTRES = {
    (1, 2): ([-8, 72, 72, -8], -1), (1, 3): ([-8, 72, 72, -8], -1),
    (1, 4): ([-8, 108, 36, -4], -1), (1, 5): ([-8, 104, 36, -8], -1),
    (2, 2): ([16, -64, 64, -16], -1), (2, 3): ([128, -256, 64, 64], -2),
    (2, 4): ([16, 32, 32, 32, 16], -2), (2, 5): ([32, 32, 32, 32], -2),
}
DIRS = ("usse", "followup/usse", "knowledge/usse")
_OP = re.compile(r"firh r10, r1, r2, r3, (u8|s8|o8), (rep|msc|mdc), fcs(\d), #(-?\d+), #(\d)$")
EDGE = {"rep": 0, "msc": 1, "mdc": 2}
BEGIN = "// firh_banks.py: begin"
END = "// firh_banks.py: end"


def data_dir(arg: str | None = None) -> pathlib.Path:
    return pathlib.Path(arg or os.environ.get("RESGX545_DATA") or ROOT.parent / "resgx545-data")


def _sidecar_jobs(vec: pathlib.Path, vectors: pathlib.Path) -> dict:
    rel = vec.relative_to(vectors)
    side = vectors / "jobs" / rel.parent / (rel.name.removesuffix(".vec.json") + ".job.json")
    return json.loads(side.read_text())["jobs"] if side.exists() else {}


def _mode(job: dict | None) -> int | None:
    """CR_USE_COEFFS_MODE bits 1:0 of a job, 0 for one that loads nothing, None if unknown."""
    if job is None:
        return None
    c = job["use_coeffs"]
    return int(c["mode"], 16) & 3 if c["load"] else 0


def _line(regs: dict, fmt: str) -> list[int]:
    line = [(int(regs[r], 16) >> (8 * j)) & 0xff for r in ("r1", "r2", "r3") for j in range(4)]
    if fmt == "s8":
        return [b - 256 if b > 127 else b for b in line]
    if fmt == "o8":
        return [b - 128 for b in line]
    return line


def cases(data: pathlib.Path) -> list[dict]:
    """The single-firh fill vectors under the filter tables at banks 1 and 2: mode, set, edge,
    centre, line and the byte written."""
    vectors = data / "vectors"
    out = []
    for d in DIRS:
        for f in sorted((vectors / d).glob("filter-*/*.vec.json")):
            side = _sidecar_jobs(f, vectors)
            for v in json.loads(f.read_text())["vectors"]:
                if v["readback"].get("failed"):
                    continue
                m = _OP.match(v["provenance"]["inputs"].get("OP", "").strip())
                if not m:
                    continue
                mode = _mode(v["init"].get("job") or side.get(v["id"]))
                s, k = int(m[4]), int(m[5])
                if mode not in (1, 2) or int(m[3]) not in range(2, 6) or s < -4:
                    continue
                out.append({"id": v["id"], "bank": mode, "set": int(m[3]), "edge": EDGE[m[2]],
                            "s": s, "line": _line(v["init"]["regs"], m[1]),
                            "byte": int(v["readback"]["scratch"]["0x000"], 16) >> (8 * k) & 0xff})
    return out


def at(line: list[int], edge: int, i: int) -> int:
    """Position i of the line, folded by the edge mode (rep, msc, mdc) inside -4..18."""
    if 0 <= i <= 11:
        return line[i]
    if edge == 0:
        return line[0] if i < 0 else line[11]
    if edge == 1:
        return line[-i] if i < 0 else line[22 - i]
    return line[-1 - i] if i < 0 else line[23 - i]


def interval(cs: list[dict], taps: list[int], frm: int) -> tuple[int, int] | None:
    """The bias range for which sat((sum + bias) >> SHIFT) gives every case's byte, or None."""
    lo, hi = -10**9, 10**9
    for c in cs:
        s = sum(t * at(c["line"], c["edge"], c["s"] + frm + n) for n, t in enumerate(taps))
        r = c["byte"]
        lo = max(lo, -10**9 if r == 0 else (r << SHIFT) - s)
        hi = min(hi, 10**9 if r == 255 else ((r + 1) << SHIFT) - 1 - s)
        if lo > hi:
            return None
    return lo, hi


def families(cs: list[dict]) -> dict:
    """(bank, set) -> (number of cases, [(taps, bias low, bias high)])."""
    out = {}
    for key, (centre, frm) in CENTRES.items():
        own = [c for c in cs if (c["bank"], c["set"]) == key]
        fam = []
        for ds in itertools.product(range(-WINDOW, WINDOW + 1), repeat=len(centre)):
            taps = [a + d for a, d in zip(centre, ds)]
            iv = interval(own, taps, frm)
            if iv:
                fam.append((taps, *iv))
        out[key] = (len(own), fam)
    return out


def rust(fams: dict) -> str:
    """The FIXED_BANKS table, between its BEGIN and END marker lines."""
    lines = [BEGIN, "#[rustfmt::skip]", "const FIXED_BANKS: &[Family] = &["]
    for (bank, st), (n, fam) in fams.items():
        frm = CENTRES[(bank, st)][1]
        lines.append(f"    // bank {bank} set {st}: {n} cases, {len(fam)} members")
        lines.append(f"    ({bank}, {st}, {frm}, {SHIFT}, &[")
        lines += [f"        (&{t}, {lo}, {hi})," for t, lo, hi in fam]
        lines.append("    ]),")
    lines += ["];", END]
    return "\n".join(lines) + "\n"


def in_tree(path: pathlib.Path = USSE_RS) -> str:
    text = path.read_text()
    a, b = text.index(BEGIN), text.index(END)
    return text[a:b + len(END)] + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=["check"])
    ap.add_argument("--data")
    a = ap.parse_args(argv)
    table = rust(families(cases(data_dir(a.data))))
    if a.cmd == "check":
        if table != in_tree():
            print(f"{USSE_RS}: FIXED_BANKS differs from firh_banks.py's", file=sys.stderr)
            return 1
        return 0
    sys.stdout.write(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
