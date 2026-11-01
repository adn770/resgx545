#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Write the kernel-word sweep tables, transfer/kernel-words.toml and render/kernel-words.toml.

Each sweep pokes the words of the firmware command the kernel builds (the kernel's debugfs
kpoke spaces ta, rd and tq) after it built them. The data sweeps take every bit, plus 0 and
~0, of the words that hold neither an address nor a count of addresses; the words userspace
passes through unchanged are left out (the command-words tables sweep those). The address
sweeps take the words that hold GPU addresses, counts of address arrays, sync objects or
register-address pairs, and the unknown bookkeeping between them, bits 0-11 only so that an
address moves within its own page; they are open and run after the data sweeps.

    gen_kernel_words.py      rewrite both tables beside the probes/ tree
    gen_kernel_words.py -    print them

The word lists below are read from the kernel fork's command builders (sgx_render.c,
sgx_xfer.c at the commit tools/sweep/kernel_masks.toml names); the pass-through words come
from that file.
"""
from __future__ import annotations

import pathlib
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
PROBES = HERE.parent
MASKS = PROBES.parent / "tools" / "sweep" / "kernel_masks.toml"
SIZE = {"ta": 176, "rd": 123, "tq": 306}
ADDR = {
    "ta": {0, *range(9, 142), 148, 150, 151, 157, *range(170, 176)},
    "rd": {0, 8, 10, 18, 23, *range(52, 73), *range(80, 123)},
    "tq": {0, 4, 6, 9, 15, 41, *range(43, 98), *range(102, 306)},
}
# the job each host runs, the kpoke spaces it reaches and the table that holds its sweeps
JOBS = {"copy": (["tq"], "transfer"), "fill": (["tq"], "transfer"), "tri": (["ta", "rd"], "render")}
HDR = "# SPDX-License-Identifier: MIT\n# SPDX-FileCopyrightText: 2026 Josep Torra\n"
BITS = "bits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]\nvalues = []\n"


def runs(ix) -> list[list[int]]:
    """The indices as [first, last] runs."""
    out: list[list[int]] = []
    for i in sorted(ix):
        if out and out[-1][1] == i - 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return out


def passed(masks: pathlib.Path = MASKS) -> dict[str, set]:
    """The words of each space that userspace's command passes through unchanged."""
    out: dict[str, set] = {s: set() for s in SIZE}
    for w in tomllib.loads(masks.read_text())["word"]:
        if w["action"] == "pass":
            for land in w["lands"]:
                s, n = land.split(":")
                a, _, b = n.partition("-")
                out[s] |= set(range(int(a), int(b or a) + 1))
    return out


def tables(masks: pathlib.Path = MASKS) -> dict[str, str]:
    """{unit/feature.toml: text} of the two tables."""
    skip = passed(masks)
    sweeps: dict[str, list] = {"transfer": [], "render": []}
    for kind in ("data", "addr"):
        for host in sorted(JOBS):
            spaces, unit = JOBS[host]
            name = f"{unit}-kernel-words-{host}-kernel" + ("-addr" if kind == "addr" else "")
            body = (f'[[sweep]]\nname = "{name}"\nabout = "{kind} words of the kernel-built '
                    f'firmware command of the {host} job"\nhost = "{host}"\n')
            body += BITS if kind == "addr" else ""
            for s in spaces:
                ix = ADDR[s] if kind == "addr" else set(range(SIZE[s])) - ADDR[s] - skip[s]
                for a, b in runs(ix):
                    body += f'\n[[sweep.range]]\nspace = "{s}"\nindices = [{a}, {b}]\n'
            sweeps[unit].append((name, kind, body))
    out = {}
    for unit, items in sweeps.items():
        opened = ", ".join(f'"{n}"' for n, k, _ in items if k == "addr")
        out[f"{unit}/kernel-words.toml"] = (
            f'{HDR}# {unit} kernel words: {len(items)} sweeps, 0 probes.\n'
            f'name = "{unit}-kernel-words"\nneeds = ["render", "kpoke"]\nopen = [{opened}]\n\n'
            + "\n".join(b for _, _, b in items))
    return out


def main(argv: list[str]) -> int:
    for rel, text in tables().items():
        if argv[:1] == ["-"]:
            sys.stdout.write(text)
        else:
            (PROBES / rel).write_text(text)
            print(rel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
