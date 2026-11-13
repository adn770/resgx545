#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Scene vectors (doc/specs/vectors.md section 6) of the fill and copy runs of the data repository.

Every table whose host is `fill` or `copy` ran `sgxfive-test fill|copy` once per case, with pokes
(`--poke SPACE:INDEX=VALUE`) on the words of the built job; its raw.txt keeps the command line,
the outcome (`job: ok | failed | rejected`), the target's hash, the pixels that differ from the CPU
reference and the dwords written outside the target. This tool rebuilds each case's words offline
(`sgxfive-test --mock ... --emit-scene`, no laptop) and pairs them with that recorded outcome:

    transfer_scenes.py --data DATA --tool build/sgxfive-test --out OUT [--table transfer/command-words]

One file per run directory, `OUT/transfer/<table>/<run>.scene.json`: the words of each distinct
unpoked job once (`bases`) and per case only the words the pokes changed (`delta`). The words are
REBUILT (the builder's, not a capture) and no recorded dump of a transfer's words exists to check
them against; the only check is the one every baseline carries: the CPU reference image's hash,
recomputed here, equals the recorded one. Cases the kernel rejected never reached the hardware
and are listed in `excluded`, not made into vectors.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
TOOL = "transfer_scenes.py 1"
SENTINEL = 0xDEADBEEF
JOB = re.compile(r"^job: (ok|failed: job faulted|failed: job hung|rejected|failed: (.*))")
# the job's command line ends at the shell's `;` (a kreg case wraps the job in `; rc=$?; ...`)
CMD = re.compile(r"-- \./sgxfive-test (fill|copy)((?: [^;]*)?)(?:;|$)")
KREG = re.compile(r"\bput kreg\b")


class Case:
    def __init__(self, name):
        self.name, self.cmd, self.args, self.kreg = name, None, [], False
        self.job = self.hash = self.diff = self.of = self.outside = None

    def __repr__(self):
        return f"Case({self.name!r}, {self.cmd}, {self.job})"


def fnv64(words):
    h = 0xCBF29CE484222325
    for w in words:
        for b in w.to_bytes(4, "little"):
            h = ((h ^ b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def copy_reference(w, h, src_stride_words, sx, sy, plain=True, every_value=False):
    """The copy's source pattern at (sx + x, sy + y) (pattern() of sgxfive-test)."""
    out = []
    for y in range(h):
        for x in range(w):
            X, Y = sx + x, sy + y
            n = (Y * src_stride_words + X) & 0xFF
            if every_value:
                out.append(n << 24 | ((n * 167 + 13) & 0xFF) << 16 | ((n * 29 + 101) & 0xFF) << 8 | ((n * 93 + 57) & 0xFF))
            else:
                out.append(0xA5000000 | (Y & 255) << 16 | (X & 255) << 8 | ((X ^ Y) & 255))
    return out


def parse_raw(text):
    cases, cur = [], None
    for line in text.splitlines():
        if line.startswith("=== case "):
            cur = Case(line[len("=== case "):].strip())
            cases.append(cur)
        elif cur is None:
            continue
        elif line.startswith("$ "):
            m = CMD.search(line)
            if m:
                cur.cmd, cur.args = m.group(1), shlex.split(m.group(2))
                cur.kreg = bool(KREG.search(line))
        elif (m := JOB.match(line)):
            s = m.group(1)
            cur.job = "ok" if s == "ok" else "rejected" if s == "rejected" else "fault" if "faulted" in s \
                else "hang" if "hung" in s else "failed"
        elif (m := re.match(r"^target: (\d+)x(\d+) hash (0x[0-9a-f]+)", line)):
            cur.hash = int(m.group(3), 16)
        elif (m := re.match(r"^diff: (\d+) of (\d+) pixels", line)):
            cur.diff, cur.of = int(m.group(1)), int(m.group(2))
        elif (m := re.match(r"^outside: (\d+) dwords", line)):
            cur.outside = int(m.group(1))
    return cases


def split_pokes(args):
    base, pokes, i = [], [], 0
    while i < len(args):
        if args[i] == "--poke" and i + 1 < len(args):
            pokes.append(args[i + 1])
            i += 2
        else:
            base.append(args[i])
            i += 1
    return base, pokes


def expect_of(c, reference=None):
    """What the hardware did, as a scene's `expect`; None for a job that never reached it."""
    if c.job in ("rejected", None):
        return None
    if c.job in ("fault", "hang"):
        return {"outcome": c.job}
    if c.job != "ok" or c.hash is None:
        return None
    img = {"hash": f"{c.hash:#018x}"}
    if reference is not None:
        if fnv64(reference) != c.hash:
            raise ValueError(f"{c.name}: the reference image does not hash to the recorded {c.hash:#x}")
        if len(set(reference)) == 1:
            img["o0"] = f"{reference[0]:#010x}"
    e = {"image": img}
    if c.outside is not None:
        e["outside"] = c.outside
    return e


def expect_many(cases):
    """One expectation for the runs of one case: the same result, or an `either`."""
    es = []
    for c in cases:
        e = expect_of(c)
        if e is not None and e not in es:
            es.append(e)
    if not es:
        return None
    return es[0] if len(es) == 1 else {"outcome": "either", "either": es}


# The questions a poked word is open under: what the pipeline simulator's transfer model (sgx_pipe::
# xfer) may refuse the job with when it cannot explain the word, by the space the word lives in.
# The model names the one that applies; a vector lists the set so that a refusal is counted by
# question and an unlisted question is reported, not hidden.
# Q207 is a PDS program or input the simulator does not know (a program that is not a template the
# records ran included), Q003 a job whose completion is not known and an access outside the scene's
# memory (with Q076).
SPACE_QUESTIONS = {
    "xfer": ["Q011", "Q206", "Q207", "Q076", "Q003"],
    "bg": ["Q066", "Q200", "Q076", "Q003", "Q206", "Q207"],
    "tex": ["Q078", "Q076", "Q003", "Q206"],
    "pds:pixev": ["Q074", "Q206", "Q207", "Q003"],
    "pds:prim": ["Q180", "Q078", "Q076", "Q003", "Q206", "Q207"],
    "pds:sec": ["Q206", "Q207", "Q076", "Q003"],
}


def refuse_of(pokes):
    """The questions a job with these pokes may be refused under (none for an unpoked job)."""
    qs = set()
    for p in pokes:
        m = re.match(r"(pds:\w+|\w+):", p)
        qs.update(SPACE_QUESTIONS.get(m.group(1) if m else "", ["Q206"]))
    return sorted(qs)


def delta(base, scene):
    d = {}
    xf = {str(i): v for i, (a, v) in enumerate(zip(base["xfer"], scene["xfer"])) if a != v}
    if xf:
        d["xfer"] = xf
    mem = []
    for b, s in zip(base["memory"], scene["memory"]):
        at = {str(i): v for i, (x, v) in enumerate(zip(b["dwords"], s["dwords"])) if x != v}
        if at:
            mem.append({"base": b["base"], "at": at})
    if mem:
        d["memory"] = mem
    return d


def sparse(dwords):
    """A segment's dwords without its trailing zero run (zeros are what an unmapped page reads
    as in a freshly allocated buffer, and the loader zero-fills the page)."""
    n = len(dwords)
    while n and dwords[n - 1] == "0x0":
        n -= 1
    return dwords[:n]


def emit(tool, kind, args):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "s.json")
        r = subprocess.run([*tool, kind, *args, "--emit-scene", out], capture_output=True, text=True, timeout=60)
        if not os.path.exists(out):
            raise RuntimeError(f"{kind} {args}: {r.stdout[-200:]}{r.stderr[-200:]}")
        return json.load(open(out))


def build_file(raw, tool, run, table, raw_path, raw_sha):
    cases = parse_raw(raw)
    bases, base_of, scenes, excluded = [], {}, [], []
    groups = {}
    for c in cases:
        groups.setdefault(c.name, []).append(c)
    ref_cache = {}
    for name, cs in groups.items():
        c = cs[0]
        if c.cmd is None:
            excluded.append({"case": name, "why": "not a fill or copy job"})
            continue
        if any(x.kreg for x in cs):
            excluded.append({"case": name, "why": "a kernel register write (put kreg) the scene cannot carry"})
            continue
        if any("--kpoke" in a for a in c.args):
            excluded.append({"case": name, "why": "a kernel poke: the words are not the host's"})
            continue
        if all(x.job == "rejected" for x in cs):
            excluded.append({"case": name, "why": "rejected by the kernel: never reached the GPU"})
            continue
        base_args, pokes = split_pokes(c.args)
        key = (c.cmd, tuple(base_args))
        try:
            if key not in base_of:
                b = emit(tool, c.cmd, base_args)
                base_of[key] = len(bases)
                bases.append({k: b[k] for k in ("kind", "target", "xfer", "layout")} |
                             {"memory": [{"base": m["base"], "source": m.get("source", "rebuilt"),
                                          "dwords": sparse(m["dwords"])} for m in b["memory"]]} |
                             {"_full": b["memory"], "args": base_args})
            s = emit(tool, c.cmd, c.args) if pokes else None
        except RuntimeError as e:
            excluded.append({"case": name, "why": f"the builder refused: {e}"})
            continue
        bi = base_of[key]
        full = {"xfer": bases[bi]["xfer"], "memory": bases[bi]["_full"]}
        e = expect_many(cs)
        if not pokes:  # the unpoked job: its CPU reference is checked against the recorded hash
            t = bases[bi]["target"]
            ref = (copy_reference(t["w"], t["h"], 64, 0, 0, every_value="--every-value" in base_args)
                   if c.cmd == "copy" and not any(a.startswith("--ramp") for a in base_args) else
                   [int(base_args[base_args.index("--colour") + 1], 0) if "--colour" in base_args else 0xFF336699] * (t["w"] * t["h"])
                   if c.cmd == "fill" else None)
            if ref is not None and len(cs) == 1 and cs[0].job == "ok" and cs[0].diff == 0:
                try:
                    e = expect_of(cs[0], ref)
                except ValueError as err:
                    excluded.append({"case": name, "why": f"reference check: {err}"})
                    continue
        if e is None:
            excluded.append({"case": name, "why": "no hardware result"})
            continue
        if pokes:
            e["refuse"] = refuse_of(pokes)
        scene = {"id": f"{run}:{name}", "base": bi, "delta": delta(full, s) if s else {}, "expect": e,
                 "provenance": {"case": name, "poke": pokes, "runs": len(cs),
                                "jobs": sorted({x.job for x in cs})}}
        scenes.append(scene)
    for b in bases:
        b.pop("_full", None)
    return {"format": "sgx545-scene-vectors", "version": 1,
            "run": {"raw": raw_path, "raw_sha256": raw_sha, "table": table, "tool": TOOL,
                    "words": "rebuilt offline (sgxfive-test --mock --emit-scene); no recorded dump to check against"},
            "bases": bases, "scenes": scenes, "excluded": excluded}


def runs(data, table):
    d = data / table
    for p in sorted(d.rglob("raw.txt")):
        yield p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", required=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--table", action="append", default=None)
    a = ap.parse_args(argv)
    data, out = pathlib.Path(a.data), pathlib.Path(a.out)
    tables = a.table or TABLES
    total = 0
    for t in tables:
        for p in runs(data, t):
            raw = p.read_text(errors="replace")
            if "sgxfive-test fill" not in raw and "sgxfive-test copy" not in raw:
                continue
            rel = p.parent.relative_to(data)
            f = build_file(raw, [a.tool, "--mock"], str(rel), t, str(p.relative_to(data)),
                           hashlib.sha256(p.read_bytes()).hexdigest())
            dest = out / "transfer" / (str(rel) + ".scene.json")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(f, separators=(",", ":")) + "\n")
            total += len(f["scenes"])
            print(f"{rel}: {len(f['scenes'])} scenes, {len(f['excluded'])} excluded", file=sys.stderr)
    print(f"{total} scenes", file=sys.stderr)


TABLES = ["transfer/command-words", "isp/background-object", "pds/end-of-tile", "pds/pixel-event-word2",
          "pds/data-words", "pds/douti-fields", "pbe/emit-words", "pbe/emit-words-followup",
          "texture/sampler-bits", "texture/state-words", "texture/tpu-csc", "isp/render-only-registers",
          "platform/untouched-registers", "platform/init-register-copy"]

if __name__ == "__main__":
    main()
