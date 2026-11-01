#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Phase 11.35: the register-write tests of E485 and E487 with a marker of its own in every job.

    gen_temps.py DIR SEED

writes DIR/temps-fresh-a.toml and temps-fresh-b.toml (E485's tables, probes/usse/temps-max.toml and
temps-sparse.toml: the same 25 jobs in the table's order and in the reverse order; every
register a job writes gets (half << 16 | register number) with a half of its own, the low half
naming the register so that a wrap shows as another register's number) and temps-fresh-c.toml (E487's
jobs on E535's template: T = 132, 136, 144, 160 started with 8 and T = 192 started with 8, 32, 64
and 128, one marker each). The seeds are SEED, SEED + 1 and SEED + 2. The hypotheses are the old
tables', with the values of each job (a list of changed dwords becomes {dwords = the 32 shown,
scratch_more = the rest, o0 = the top register}, since the tool shows 32 changed dwords and counts
the rest). It reads the old tables from the repository it is in.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "usse-asm"))
import markers  # noqa: E402
import probe  # noqa: E402

OLD = re.compile(r"#0x(7E57|1E57)([0-9A-Fa-f]{4})")


def _int(v: int) -> str:
    return "0x%08X" % v


def _val(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return _int(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, list):
        return "[" + ", ".join(_val(x) for x in v) + "]"
    return "{ " + ", ".join(f"{k} = {_val(x)}" for k, x in v.items()) + " }"


def _remap(v, half: int):
    """The old marker values (upper half 0x7E57 or 0x1E57) with the job's half."""
    if isinstance(v, int):
        return half << 16 | v & 0xffff if v >> 16 in (0x7E57, 0x1E57) else v
    if isinstance(v, list):
        return [_remap(x, half) for x in v]
    if isinstance(v, dict):
        return {k: _remap(x, half) for k, x in v.items()}
    return v


def _expect(v: list, case: int) -> object:
    """A list of dwords as the tool shows them (32) and counts them; the sweeps' last dword is
    the top register, the pixel."""
    if len(v) < 4 or case > 1:
        return v
    return {"dwords": v[:32], "scratch_more": max(0, len(v) - 32), "o0": v[-1]}


def probe_text(p: probe.Probe, name: str, cases: list, hyps: dict, labels: list) -> str:
    lines = ["[[probe]]", f"name = {json.dumps(name)}", f"question = {json.dumps(p.question)}",
             f"source = {json.dumps(p.source)}", f"temps = {p.temps}",
             f"params = {_val(p.params) if p.params else '{  }'}",
             f"inputs = {json.dumps(p.inputs)}", f"labels = {json.dumps(labels)}",
             f"cases = {json.dumps(cases)}", "[probe.hypotheses]"]
    for h, exp in hyps.items():
        lines.append(f"{json.dumps(h)} = {_val(exp)}")
    return "\n".join(lines) + "\n"


def sweeps(order: str, seed: int) -> tuple[str, list]:
    olds = [(t, p) for t in ("temps-max", "temps-sparse")
            for p in probe.load(probe.PROBES / "usse" / f"{t}.toml")]
    jobs = [(t, p, i) for t, p in olds for i in range(len(p.cases))]
    if order == "b":
        jobs.reverse()
    halves = markers.fresh_halves(len(jobs), seed)
    per: dict = {}
    rec = []
    for (t, p, i), half in zip(jobs, halves):
        case = [OLD.sub(lambda m: "#0x%04X%s" % (half, m.group(2)), c) for c in p.cases[i]]
        hyps = {h: _expect(_remap(exp[i], half), i) for h, exp in p.hypotheses.items()}
        d = per.setdefault((t, p.name), {"p": p, "cases": [], "labels": [], "hyps": {}})
        d["cases"].append(case)
        d["labels"].append(p.labels[i])
        for h, e in hyps.items():
            d["hyps"].setdefault(h, []).append(e)
        rec.append({"job": len(rec), "probe": p.name, "case": i, "half": "0x%04x" % half})
    out = [f"# SPDX-License-Identifier: MIT\n# SPDX-FileCopyrightText: 2026 Josep Torra\n"
           f"# phase 11.35: E485's {len(jobs)} jobs (temps-max, then temps-sparse"
           f"{', in reverse' if order == 'b' else ''}) with a marker of its own in every job "
           f"(gen_temps.py, seed {seed})\nneeds = [\"render\"]\n"]
    for (t, name), d in per.items():
        feat = t.removeprefix("temps-")
        new = name.replace(f"usse-{t}-", f"usse-temps-fresh-{order}-{feat}-")
        out.append(probe_text(d["p"], new, d["cases"], d["hyps"], d["labels"]))
        for r in rec:
            if r["probe"] == name:
                r["probe"] = new
    out[1:] = [x for x in out[1:]]
    return "\n".join(out), rec


def e487(seed: int) -> tuple[str, list]:
    jobs = [(8, 132), (8, 136), (8, 144), (8, 160), (8, 192), (32, 192), (64, 192), (128, 192)]
    halves = markers.fresh_markers(len(jobs), seed)
    out = ["# SPDX-License-Identifier: MIT\n# SPDX-FileCopyrightText: 2026 Josep Torra\n"
           f"# phase 11.35: E487's jobs E535 did not cover, a marker of its own in each (gen_temps.py, "
           f"seed {seed})\nneeds = [\"render\"]\n"]
    rec = []
    by_start: dict = {}
    for (start, t), m in zip(jobs, halves):
        by_start.setdefault(start, []).append((t, m))
    k = 0
    for start, js in by_start.items():
        p = probe.Probe(name="x", question=f"a two-phase fill started with {start} temporaries whose "
                        "phas asks for T; r123 written with a marker no other job writes",
                        source="temps_phas.s", params={}, inputs=["T", "HI", "MARK"], cases=[],
                        hypotheses={}, temps=start)
        cases = [[str(t), "123", _int(m)] for t, m in js]
        labels = [f"--temps {start}; phas asks for {t} for phase 1; r123 written with a marker "
                  "of its own" for t, _ in js]
        hyps = {"every write landed (o0 is the job's own marker)": [{"o0": m} for _, m in js],
                "a read of an earlier job's value (o0 is not the job's own marker)":
                    [{"o0_not": m} for _, m in js]}
        name = f"usse-temps-fresh-c-start{start}"
        out.append(probe_text(p, name, cases, hyps, labels))
        for i, (t, m) in enumerate(js):
            rec.append({"job": k, "probe": name, "case": i, "T": t, "start": start,
                        "marker": _int(m)})
            k += 1
    return "\n".join(out), rec


def main(argv: list[str]) -> int:
    out, seed = pathlib.Path(argv[0]), int(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for n, (name, (text, rec)) in enumerate([("a", sweeps("a", seed)), ("b", sweeps("b", seed + 1)),
                                             ("c", e487(seed + 2))]):
        (out / f"temps-fresh-{name}.toml").write_text(text)
        (out / f"temps-fresh-{name}.jobs.json").write_text(json.dumps(rec, indent=0))
        print(f"temps-fresh-{name}: {len(rec)} jobs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
