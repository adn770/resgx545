# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The kept register snapshots fwsim reads (resgx545-data, public): the `sgx/regs` dumps of
platform/boot-registers (E006, E008: before load, loaded, booted, stopped, booted again) and
platform/edm-tick (E009: 200 snapshots of the idle firmware). A dump line is `reg 0xOOOO value`,
`skip` (the register file does not read it) or `=` (the same as the dump before), or
`hostctl 0xOO value`."""
from __future__ import annotations

import os
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent.parent

LINE = re.compile(r"(reg|hostctl|ta3dctl) (0x[0-9a-f]+) (\S+)")


def data_dir() -> pathlib.Path | None:
    """The public data repository ($RESGX545_DATA or ../resgx545-data), None when absent."""
    d = pathlib.Path(os.environ.get("RESGX545_DATA") or REPO.parent / "resgx545-data")
    return d if (d / "platform").is_dir() else None


def snapshots(text: str) -> list[tuple[str, dict[str, dict[int, int]]]]:
    """The dumps of an output.txt in order: (title, {"reg": {offset: value}, "hostctl": ...}),
    `=` resolved against the dump before, `skip` left out."""
    out: list[tuple[str, dict[str, dict[int, int]]]] = []
    prev: dict[str, dict[int, int]] = {}
    cur = None
    for line in text.splitlines():
        if line.startswith("#### "):
            if line.startswith("#### read "):          # edm-tick's stamp after a read
                cur = None
                continue
            cur = {"reg": {}, "hostctl": {}, "ta3dctl": {}}
            out.append((line[5:].strip(), cur))
            continue
        m = LINE.match(line)
        if not m or cur is None:
            continue
        kind, off, val = m[1], int(m[2], 16), m[3]
        if val == "skip":
            continue
        if val == "=":
            if off not in prev.get(kind, {}):
                continue
            cur[kind][off] = prev[kind][off]
        else:
            cur[kind][off] = int(val, 16)
        prev.setdefault(kind, {})[off] = cur[kind][off]
    return out


def boot_registers(data: pathlib.Path) -> dict[str, dict[str, dict[int, int]]]:
    """platform/boot-registers by title: before load, loaded, booted, stopped, booted again."""
    return dict(snapshots((data / "platform" / "boot-registers" / "output.txt").read_text()))


def edm_tick(data: pathlib.Path) -> list[dict[str, dict[int, int]]]:
    """platform/edm-tick's 200 snapshots of the idle firmware, in order."""
    return [s for _, s in snapshots((data / "platform" / "edm-tick" / "output.txt").read_text())]


def stable_resets(data: pathlib.Path) -> dict[int, int]:
    """Register offsets whose value is the same in every kept snapshot of a loaded or running
    firmware and before the load (boot-registers before load, loaded, booted, booted again;
    edm-tick's 200): the reset values a fwsim run may answer a read with. A register the
    hardware or the host moves in any of them is left out, so its read must come from elsewhere."""
    br = boot_registers(data)
    dumps = [br[t]["reg"] for t in ("before load", "loaded", "booted", "booted again")]
    dumps += [s["reg"] for s in edm_tick(data)]
    first = dumps[0]
    return {off: v for off, v in first.items() if all(d.get(off) == v for d in dumps)}
