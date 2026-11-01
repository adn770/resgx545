#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Writes everything of p1132 that is generated: the probe tables (probes/), the staged programs
(stage-bins/), the run scripts, specs.json, declared.tsv and predictions-declared.tsv.

    python3 -B gen/gen_p1132.py            (from p1132/; reads ~/src/resgx545, writes nothing there)
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
P = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(P / "recompute"))
sys.path.insert(0, str(pathlib.Path.home() / "src/resgx545/tools/usse-asm"))
import build      # noqa: E402
import catalog    # noqa: E402
import probe      # noqa: E402
import shell      # noqa: E402
import texmodel   # noqa: E402

TEMPLATES = P / "templates"
QUESTIONS = {
    "gate": "Q104,Q050", "shapes": "Q104", "fields": "Q104", "twiddle": "Q104,N1",
    "lod-grad": "Q050,Q115", "lod-auto": "Q050,Q115", "afilt": "Q115", "border": "Q050,Q078",
    "t3bits": "Q078,Q115", "t3vals": "Q078", "t3risky": "Q078", "types": "Q113,Q114",
    "types-risky": "Q113,Q114", "formats-names": "Q050", "formats-blocks": "Q050",
    "formats-yuv-nocsc": "Q050", "formats-yuv-csc": "Q050", "douti4": "Q021",
}
# script -> (groups, about, gate, every-job health)
SCRIPTS = {
    "tx-gate": (["gate"], "the controls: a twiddled and a strided identity map, a chain level, a mirror; "
                "known results. The gate: a declared image that is not read stops the batch", 1, 0),
    "tx-twiddle": (["twiddle"], "where texel (x, y) of a twiddled texture lies at 16 to 128 wide and 8 to 128 high",
                   0, 0),
    "tx-shapes": (["shapes"], "the levels of a non-square chain: offsets, sizes, count, per LOD", 0, 0),
    "tx-fields": (["fields"], "T0's maximum level, bias and MIPFILTER on non-square chains", 0, 0),
    "tx-lod": (["lod-grad", "lod-auto", "afilt"], "what LOD the gradients, the quad's own derivatives and a "
               "bias give, and whether anything filters anisotropically", 0, 0),
    "tx-border": (["border"], "the address modes 4 to 7 over coordinates from -1.5 to 2.5", 0, 0),
    "tx-t3": (["t3bits", "t3vals"], "T3's unexplained bits and its low byte in smp", 0, 0),
    "tx-types": (["types"], "smp3d (never run before) on the known TEXTYPEs; whether a bit makes the third "
                 "coordinate act; a health check after every job", 0, 1),
    "tx-formats": (["formats-names", "formats-blocks", "formats-yuv-nocsc", "formats-yuv-csc"],
                   "formats 23 to 29: block order and index bits, YUV through colour-space set 0", 0, 0),
    "tx-t3-risky": (["t3risky"], "RISKY, last: T3 bits 13 and 19 (E274: faults) and pairs", 0, 1),
    "tx-types-risky": (["types-risky"], "RISKY, last: TEXTYPE 1, 2, 4, 5, 7 under smp2d and smp3d", 0, 1),
}
# groups whose jobs have no hypothesis to declare (explorations of formats and TEXTYPEs the records do not
# model): the dumps are tables, not tests
NO_MODEL = {"formats-names", "formats-blocks", "types-risky"}
ORDER = ["tx-gate", "tx-twiddle", "tx-shapes", "tx-fields", "tx-lod", "tx-border", "tx-t3", "tx-types",
         "tx-formats", "tx-douti4", "tx-t3-risky", "tx-types-risky"]


def hyp_label(h: dict) -> str:
    return ",".join(f"{k}={v}" for k, v in sorted(h.items())) or "base"


def tstr(s: str) -> str:
    return json.dumps(s)


def write_table(group: str, cases: list) -> pathlib.Path:
    pokes = []
    if group == "formats-yuv-csc":
        pokes = ["xfer:17^=0x1", "xfer:18=0x00950095", "xfer:19=0x00000095", "xfer:20=0x010203ce",
                 "xfer:21=0x039800cc", "xfer:22=0"]
    q = QUESTIONS[group]
    lines = ["# SPDX-License-Identifier: MIT", "# SPDX-FileCopyrightText: 2026 Josep Torra",
             f"# tx-{group}: {len(cases)} cases, written by tools/texture/p1132/gen/gen_p1132.py (phase 11.32); "
             f"questions {q}.",
             'needs = ["render"]', "", "[[probe]]", f'name = "tx-{group}"',
             f"question = {tstr('smp on a 64 x 32 fill, one coordinate rule a pixel (' + q + '): ' + group)}",
             'source = "tx_map.s"', "coords = true", "pixels = true", "params = { }",
             'inputs = ["PRE", "SETUP", "SMP"]']
    if pokes:
        lines.append("pokes = [" + ", ".join(tstr(k) for k in pokes) + "]")
    lines.append("labels = [" + ", ".join(tstr(c["label"]) for c in cases) + "]")
    rows = [build.case_inputs(c["spec"]) for c in cases]
    lines.append("cases = [" + ", ".join("[" + ", ".join(tstr(x) for x in r) + "]" for r in rows) + "]")
    f = P / "probes" / "texture" / f"tx-{group}.toml"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("\n".join(lines) + "\n")
    return f


def main() -> None:
    for old in (P / "stage-bins").glob("*.bin"):      # no stale program of an earlier generation
        old.unlink()
    by_group: dict = {}
    for fn in catalog.GROUPS.values():
        for c in fn():
            by_group.setdefault(c["group"], []).append(c)
    specs, declared, preds, tables = {}, [], [], {}
    for group, cases in by_group.items():
        f = write_table(group, cases)
        probes = probe.load(f)
        assert len(probes) == 1 and len(probes[0].cases) == len(cases)
        out = P / "stage-bins"
        probe.build(probes[0], out, TEMPLATES)
        for i, c in enumerate(cases):
            c["bin"] = f"tx-{group}__{i}.bin"
            nbytes = (out / c["bin"]).stat().st_size
            assert nbytes % 8 == 0 and nbytes // 8 <= 256, (c["name"], nbytes)
            specs[c["name"]] = {"group": group, "bin": c["bin"], "set": c["set"], "risk": c["risk"],
                                "spec": c["spec"], "hyps": [hyp_label(h) for h in c["hyps"]],
                                "rules": c["hyps"]}
            pix = {}
            for h in ([] if group in NO_MODEL else c["hyps"]):
                px = texmodel.render(c["spec"], h)
                if px is not None:
                    pix[hyp_label(h)] = texmodel.digest(px)
            c["pred"] = pix
            declared.append((SCRIPT_OF[group], c["name"], c["set"], c["risk"], QUESTIONS[group]))
            for hl, sha in pix.items():
                preds.append((SCRIPT_OF[group], c["name"], c["set"], hl, sha))
        tables[group] = (probes[0], cases)
    # ---- the scripts
    for sname, (groups, about, gate, every) in SCRIPTS.items():
        rows, qs = [], sorted({QUESTIONS[g] for g in groups})
        for g in groups:
            p, cases = tables[g]
            opts = " ".join(a for k in p.pokes for a in ("--poke", k)) or "-"
            for c in cases:
                pred = "-"
                if (c["set"] == "control" or len(c["hyps"]) == 1) and c["pred"] and (gate or c["set"] == "control"):
                    pred = c["pred"][hyp_label(c["hyps"][0])]
                rows.append((c["name"], c["bin"], c["set"], c["risk"], pred, opts))
        text = shell.script(sname, ",".join(qs), about, rows, gate=gate, every=every)
        (P / f"{sname}.sh").write_text(text)
    douti4(declared)
    runall()
    (P / "gen" / "specs.json").write_text(json.dumps(specs, indent=0, sort_keys=True))
    (P / "declared.tsv").write_text(
        "script\tcase\tset\trisk\tquestion\n" + "".join("\t".join(r) + "\n" for r in declared))
    (P / "predictions-declared.tsv").write_text(
        "script\tcase\tset\thypothesis\tpix_sha256\n" + "".join("\t".join(r) + "\n" for r in preds))
    disc = collections.defaultdict(lambda: [0, 0, 0])
    for gname, (pr, cs) in tables.items():
        for c in cs:
            d = disc[gname]
            d[0] += 1
            d[1] += len(set(c["pred"].values())) > 1
            d[2] += len(c["pred"]) == 0
    (P / "out" / "discrimination.tsv").write_text(
        "group\tcases\tcases whose hypotheses predict different images\tcases without a model\n"
        + "".join(f"{g}\t{a}\t{b}\t{c}\n" for g, (a, b, c) in sorted(disc.items())))
    for f in ("declared.tsv", "predictions-declared.tsv"):
        print(f, hashlib.sha256((P / f).read_bytes()).hexdigest(), sum(1 for _ in open(P / f)) - 1, "rows")
    print("cases", len(specs))


def runall() -> None:
    names = " ".join(ORDER)
    (P / "run-all-1132.sh").write_text(f"""#!/bin/bash
# run-all-1132.sh: the 11.32 batch on the laptop in the order of plan.md section 8 (the gate first, the
# safe scripts, then the two risky ones last, one job at a time with a health check after each), each with
# its own log. Run it on the laptop after stage-p1132.sh has put the programs in ~/sgxprobes-stage-1132;
# the tool is ~/sgxfive-test-1126. It stops after the first script that stopped itself (the gate, three
# failed recoveries): read dmesg before another run. Never writes a clock-gate register: no script here
# writes a register.
set -u
cd "$(dirname "$0")"
OUT=${{OUT:-$HOME/p1132-out}}
mkdir -p "$OUT"
for s in {names}; do
	echo "#### $s $(date +%T)"
	bash "./$s.sh" > "$OUT/$s.out" 2>&1
	rc=$?
	echo "rc $rc, $(grep -c '^== ' "$OUT/$s.out") jobs, $(grep -c 'kept ' "$OUT/$s.out") kept, $(grep -c 'MISMATCH' "$OUT/$s.out") declared mismatches"
	grep -E "^## abort|^  health|^## journalctl" "$OUT/$s.out" | head -4
	[ "$rc" -ne 0 ] && {{ echo "stopped after $s"; break; }}
done
""")


SCRIPT_OF = {g: s for s, (gs, *_rest) in SCRIPTS.items() for g in gs}
SCRIPT_OF["douti4"] = "tx-douti4"


def douti4(declared: list) -> None:
    """Q021: pa2 to pa5 of a four-component douti on a vertex whose fourth component is x + y."""
    def table(pa: int) -> str:
        cases = [[0x40C00801, 0, 0x2000004]] * 5 + [[0x40800801, 0, 0x2000004]] * 2
        labels = ["bits 23:22 = 3"] * 5 + ["bits 23:22 = 2 (control)"] * 2
        return "\n".join([
            "[[probe]]", f'name = "tx-douti4-pa{pa}"',
            f'question = "DOUTI0 bits 23:22 = 3 on a vertex with a four-dword set (0.25 and x + y): pa{pa}, five fresh runs"',
            'source = "pds_tex_iter.s"', 'host = "tri"', 'slot = "pixpds"',
            f'slots = {{ pixel = "pix_pa{pa}.s", vtxuse = "vtx_coords4.s" }}', "vtx_coords = 4",
            "size = [0x40, 0x40]", "pixels = true", 'inputs = ["A", "B", "U"]',
            "cases = [" + ", ".join("[0x%08x, %d, 0x%x]" % tuple(c) for c in cases) + "]",
            "labels = [" + ", ".join(tstr(x) for x in labels) + "]", ""])
    text = ("# SPDX-License-Identifier: MIT\n# SPDX-FileCopyrightText: 2026 Josep Torra\n"
            "# tx-douti4: 4 probes (phase 11.32 draft). Q021: the fourth component of a DOUTI0 with bits 23:22 = 3\n"
            "# from a source whose fourth component is x + y, not 1.0 (E420's vertex set was x and y only).\n"
            'needs = ["render"]\n\n' + "\n".join(table(pa) for pa in (2, 3, 4, 5)))
    f = P / "probes" / "texture" / "tx-douti4.toml"
    f.write_text(text)
    ps = probe.load(f)
    out = P / "stage-bins"
    rows = []
    for p in ps:
        probe.build(p, out, TEMPLATES)
        args = probe._tri_args(p, TEMPLATES)
        for i, c in enumerate(p.cases):
            o = []
            it = iter(args)
            for a in it:
                o.append(a)
                if a == "--slot":
                    nm, fl = next(it).split("=", 1)
                    o.append(f"{nm}=@S@/{fl}")
            rows.append((f"{p.name}-r{i}", f"{p.name}__{i}.bin", "explore", "safe", "-", " ".join(o)))
            declared.append(("tx-douti4", f"{p.name}-r{i}", "explore", "safe", "Q021"))
    probe.build_helpers(ps, out, TEMPLATES)
    text = shell.script("tx-douti4", "Q021", "four components from a source whose fourth is not 1.0", rows, tri=True)
    (P / "tx-douti4.sh").write_text(text)


def follow(tag: str, t0: int, t1: int, t3: int) -> None:
    """The second step of Q113 and Q114, for one configuration (T0, T1, T3) that the first step showed
    to make smp3d read its third coordinate: six cube directions (the major axis +-1, the other two
    coordinates -0.75 to 0.75) and two slice sweeps (the third coordinate 0 to 2 and -1 to 1 down the
    rows). Writes tx-types-follow-TAG.sh, its table and programs; no model (everything is exploration)."""
    cc, ZERO = catalog, catalog.ZERO
    a, b = cc.linx(1.5, -2.25), cc.liny(1.5, -2.25)
    cases = []
    for sign, nm in ((1.0, "p"), (-1.0, "n")):
        k = cc.const(sign)
        for axis, (u, v, w) in {"z": (a, b, k), "x": (k, a, b), "y": (a, k, b)}.items():
            cases.append(cc.case(f"types-follow-{tag}", f"fo-{tag}-{axis}{nm}", dict(
                t0=t0, t1=t1, t3=t3, u=u, v=v, w=w, ins="3d"), "explore"))
    uu = cc.mapx(4)
    for nm, w in (("w02", cc.liny(2.0, -2.0)), ("w11", cc.liny(2.0, -3.0))):
        cases.append(cc.case(f"types-follow-{tag}", f"fo-{tag}-{nm}", dict(
            t0=t0, t1=t1, t3=t3, u=uu, v=cc.const(0.53125), w=w, ins="3d"), "explore"))
    group = f"types-follow-{tag}"
    QUESTIONS[group] = "Q113,Q114"
    f = write_table(group, cases)
    ps = probe.load(f)
    probe.build(ps[0], P / "stage-bins", TEMPLATES)
    rows = [(c["name"], f"tx-{group}__{i}.bin", "explore", "risky", "-", "-") for i, c in enumerate(cases)]
    (P / f"tx-{group}.sh").write_text(shell.script(
        f"tx-{group}", "Q113,Q114", f"smp3d on T0 {t0:#x}, T1 {t1:#x}, T3 {t3:#x}: six cube directions and "
        "two slice sweeps", rows, every=1))
    print("wrote", f"tx-{group}.sh", len(cases), "jobs")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--follow"]:
        follow(sys.argv[2], *(int(x, 0) for x in sys.argv[3:6]))
    else:
        main()
