#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Where the closed compiler uses the USSE instruction forms whose meaning is still open, over
every USSE program the 3D captures hold (state3d.py's paths: the programs each kick's PDS
programs start with doutu, and the end-of-tile task). A form is open when no vector of the
simulator's coverage passes on it (doc/isa/sim-coverage.json), or when it is one of the forms
the simulator gives no semantics (OPEN_NAMES). The report gives, per open form, its name, the
distinct programs that use it, how often, and the runs they come from: names and counts only,
never a program's words (the captures are closed-driver output, kept private).

--guard counts instead, by the kind of program (the path that reaches it), the programs that
open, past their leading phas and nop, with a load predicated never to run and a wait on it:
and.testtanz of two zero immediates into p0, then p0 ldad ... drc0, then wdf drc0.

    opscan3d.py DIR...          each DIR a capture run (dump3d/) or a directory of runs
    opscan3d.py --guard DIR...
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
USSE_DIS = ROOT / "tools" / "usse-dis" / "usse-dis"
COVERAGE = ROOT / "doc" / "isa" / "sim-coverage.json"
# the forms with no semantics in the simulator (crates/sgx-sim), by name
OPEN_NAMES = ("smoa", "smr", "smlsi", "smbo", "imo", "setfc", "moest", "setm", "wop", "pcoeff",
              "atst8", "depthf", "phas")
_PROG = re.compile(r"(.*\.usse\d+|(?:k\d+\.)?eot)\.i(\d+)")
# the never-taken load and its wait, as usse-dis prints them
GUARD = (r"and\.\S*testtanz\S* \S+, p0, #0x0+, #0", r"p0 ldad\S* .*, drc0", r"wdf drc0")
# a program's kind by the path that reaches it (state3d.py)
KINDS = (("vertex", r"\.vtx\.usse\d+"), ("state copy", r"\.vdm\.b\d+\.pds\.usse\d+"),
         ("secondary", r"\.sec\.usse\d+"), ("primary", r"\.pri\.usse\d+"),
         ("end of tile", r"(?:^|\.)eot"), ("end of render", r"\.eor\.usse\d+"))


def mnemonic(pattern: str) -> str:
    """A form's name: the first word of its pattern, its fields left out."""
    words = re.sub(r"\{\d+\}", "", pattern).split()
    m = re.match(r"[a-z][a-z0-9]*", words[0]) if words else None
    return m.group(0) if m else "?"


def forms(listing: str) -> dict[int, str]:
    """{form index: name} from usse-dis --forms (index, mask, value, bits read, pattern)."""
    out = {}
    for ln in listing.splitlines():
        f = ln.split("\t")
        if len(f) >= 5 and f[0].strip().isdigit():
            out[int(f[0])] = mnemonic(f[4])
    return out


def fill_names(names: dict[int, str], coverage: pathlib.Path) -> dict[int, str]:
    """names, with the coverage file's op name for a form whose pattern starts with a field
    (the dual-issue forms)."""
    cov = json.loads(pathlib.Path(coverage).read_text())
    ops = {f["form"]: f.get("op") for f in cov["forms"]}
    return {i: (ops.get(i) or n) if n == "?" else n for i, n in names.items()}


def open_forms(coverage: pathlib.Path, names: dict[int, str]) -> dict[int, str]:
    """{form index: why it is open}."""
    cov = json.loads(pathlib.Path(coverage).read_text())
    out = {}
    for f in cov["forms"]:
        passed = sum(p[0] for p in f.get("probes", {}).values())
        if passed == 0:
            out[f["form"]] = "no passing vector"
        elif names.get(f["form"]) in OPEN_NAMES:
            out[f["form"]] = "no semantics in the simulator"
    return out


def programs(words: dict[str, int]) -> dict[tuple, list[str]]:
    """{program's instructions: [paths]} of one run's state3d words."""
    by: dict[str, dict[int, int]] = {}
    for k, v in words.items():
        m = _PROG.fullmatch(k)
        if m:
            by.setdefault(m.group(1), {})[int(m.group(2))] = v
    out: dict[tuple, list[str]] = {}
    for path in sorted(by):
        ins = tuple(by[path][i] for i in sorted(by[path]))
        out.setdefault(ins, []).append(path)
    return out


def which_of(lines: list[str]) -> list[int]:
    """The form index of each line of usse-dis --which."""
    out = []
    for ln in lines:
        m = re.search(r"\t#(\d+)\s*$", ln)
        out.append(int(m.group(1)) if m else -1)
    return out


def _which(tool: pathlib.Path, insns) -> list[str]:
    with tempfile.NamedTemporaryFile(suffix=".bin") as f:
        f.write(b"".join(struct.pack("<Q", w) for w in insns))
        f.flush()
        out = subprocess.run([str(tool), "--which", f.name], capture_output=True, text=True,
                             check=True)
    return out.stdout.splitlines()


def disassembler(tool: pathlib.Path = USSE_DIS):
    """A function from a program's instructions to the form index of each."""
    return lambda insns: which_of(_which(tool, insns))


def lister(tool: pathlib.Path = USSE_DIS):
    """A function from a program's instructions to the text of each, as usse-dis prints it."""
    return lambda insns: [ln.split("\t")[1] for ln in _which(tool, insns) if "\t" in ln]


def guarded(text: list[str]) -> bool:
    """Whether a program opens, past its leading phas and nop, with the never-taken load and
    its wait (GUARD)."""
    i = 0
    while i < len(text) and re.match(r"(phas|nop)\b", text[i]):
        i += 1
    head = text[i:i + len(GUARD)]
    return len(head) == len(GUARD) and all(re.fullmatch(g, t) for g, t in zip(GUARD, head))


def kind(path: str) -> str:
    """A program's kind by the path that reaches it."""
    for name, pat in KINDS:
        if re.search(pat + "$", path):
            return name
    return "other"


def guards(runs: dict[str, dict[str, int]], text) -> dict[str, dict]:
    """{kind: {programs, guarded, runs}} over the runs' distinct programs; a program reached
    by paths of several kinds counts under each."""
    kinds: dict[tuple, dict[str, set[str]]] = {}
    for run, words in runs.items():
        for ins, paths in programs(words).items():
            for p in paths:
                kinds.setdefault(ins, {}).setdefault(kind(p), set()).add(run)
    out: dict[str, dict] = {}
    seen: dict[str, set[str]] = {}
    for ins, ks in kinds.items():
        g = guarded(text(ins))
        for k, rs in ks.items():
            e = out.setdefault(k, {"programs": 0, "guarded": 0, "runs": 0})
            e["programs"] += 1
            e["guarded"] += g
            seen.setdefault(k, set()).update(rs)
    for k, e in out.items():
        e["runs"] = len(seen[k])
    return out


def guard_report(rep: dict[str, dict]) -> str:
    order = [k for k, _ in KINDS] + ["other"]
    return "".join(f"{k}: {rep[k]['guarded']} of {rep[k]['programs']} programs open with the "
                   f"never-taken load and its wait ({rep[k]['runs']} runs)\n"
                   for k in order if k in rep)


def scan(runs: dict[str, dict[str, int]], dis, open_: dict[int, str]) -> dict[int, dict]:
    """{open form: {programs, uses, runs}} over the runs' distinct programs."""
    seen: dict[tuple, list[int]] = {}
    where: dict[tuple, set[str]] = {}
    for run, words in runs.items():
        for ins in programs(words):
            if ins not in seen:
                seen[ins] = dis(ins)
            where.setdefault(ins, set()).add(run)
    out: dict[int, dict] = {}
    for ins, fs in seen.items():
        for f in sorted(set(fs) & set(open_)):
            e = out.setdefault(f, {"programs": 0, "uses": 0, "runs": set()})
            e["programs"] += 1
            e["uses"] += fs.count(f)
            e["runs"] |= where[ins]
    for e in out.values():
        e["runs"] = sorted(e["runs"])
    return out


def report(rep: dict[int, dict], names: dict[int, str], open_: dict[int, str],
           total_programs: int) -> str:
    lines = [f"{total_programs} distinct USSE programs; open forms used: {len(rep)} of "
             f"{len(open_)}"]
    for f in sorted(open_, key=lambda f: (names.get(f, "?"), f)):
        e = rep.get(f)
        n = names.get(f, "?")
        if e is None:
            lines.append(f"form {f:3d} {n:8s} unused ({open_[f]})")
            continue
        tables = sorted({r.split("/")[0] for r in e["runs"]})
        lines.append(f"form {f:3d} {n:8s} {e['programs']} programs, {e['uses']} uses, "
                     f"{len(e['runs'])} runs ({open_[f]}); tables: {', '.join(tables)}")
    return "\n".join(lines) + "\n"


def _runs(dirs: list[str]) -> dict[str, pathlib.Path]:
    out = {}
    for d in map(pathlib.Path, dirs):
        if (d / "dump3d").is_dir():
            out[f"{d.parent.name}/{d.name}"] = d
        else:
            for r in sorted(p for p in d.iterdir() if (p / "dump3d").is_dir()):
                out[f"{d.name}/{r.name}"] = r
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    import state3d
    guard = argv[0] == "--guard"
    argv = argv[1:] if guard else argv
    if guard:
        runs = {name: state3d.extract_capture(d) for name, d in _runs(argv).items()}
        print(guard_report(guards(runs, lister())), end="")
        return 0
    listing = subprocess.run([str(USSE_DIS), "--forms"], capture_output=True, text=True,
                             check=True).stdout
    names = fill_names(forms(listing), COVERAGE)
    open_ = open_forms(COVERAGE, names)
    runs = {}
    for name, d in _runs(argv).items():
        try:
            runs[name] = state3d.extract_capture(d)
        except Exception as e:                     # a run the walker cannot read
            print(f"opscan3d.py: {name}: {type(e).__name__}", file=sys.stderr)
    total = len({p for w in runs.values() for p in programs(w)})
    print(report(scan(runs, disassembler(), open_), names, open_, total), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
