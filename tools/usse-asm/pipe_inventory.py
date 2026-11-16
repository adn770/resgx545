#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""The inventory of phase 12.0: which recorded data can become unit vectors or scene vectors
(doc/specs/vectors.md sections 5 and 6), by unit and by what is missing.

    pipe_inventory.py --data DATA [--out doc/specs/pipe-inventory.md]

Two scans of the data repository (read only): every triangle-host vector (`--tri` in
`provenance.options`) of the `*.vec.json` files, and every directory named `dumps`. The rules that
classify the dump directories are the table RULES below, first match wins; a directory no rule
matches is reported as `unclassified` (never an exception of the scan), and the generator
(`--out`) refuses to write the inventory while one exists, so a new dataset is classified on purpose.
"""
import argparse
import collections
import json
import os
import pathlib
import re
import sys

sys.dont_write_bytecode = True

Rule = collections.namedtuple("Rule", "pattern kind status records blockers phase note")
# status: built (unit vectors made in 12.0), unit-ready (data and a decoder exist, the rule is not
# coded), unit-blocked (an open question blocks the model), scene-only (checkable as a whole job
# only), exists (already vectors in the data repository)
RULES = [
    Rule(r"zls/store-layout-dumps/", "zls-store", "built", "E465 E489 E831", "Q107", "12.4",
         "18 cases, 36 depth dumps"),
    Rule(r"zls/store-format-dumps/", "zls-store", "unit-ready", "E466 E490", "Q120", "12.4",
         "formats 0 to 2 and the sign bit; the format rule is not coded"),
    Rule(r"isp/msaa-ident/", "isp-tile", "built", "E503 E502 E953", "-", "12.8", "48 runs, 96 dumps"),
    Rule(r"isp/msaa-te-dumps/", "te-region", "unit-blocked", "E507 E511", "Q086 Q003", "12.8",
         "TE words under 4x"),
    Rule(r"isp/msaa-resolve/", "isp-tile", "scene-only", "E281", "Q089 Q138", "12.8", "resolve"),
    Rule(r"isp/msaa-layout/", "isp-tile", "scene-only", "E210 E211 E1010", "Q089", "12.8", "sample layout"),
    Rule(r"isp/bg-object-pokes/", "isp-tile", "unit-blocked", "E069 E590", "Q066", "12.1",
         "169 jobs, the background object's words"),
    Rule(r"ta/tri-region/", "te-region", "built", "E542", "Q070", "12.2", "35 jobs"),
    Rule(r"ta/object-format/", "ta-object", "built", "E541", "Q070 Q165", "12.2", "59 jobs"),
    Rule(r"ta/regions/", "te-region", "unit-ready", "E177 E180 E305", "Q070", "12.2",
         "region_tiles.py's sweeps; E542's rule covers them"),
    Rule(r"ta/objects/", "ta-object", "unit-ready", "E176 E181 E306", "Q070", "12.2",
         "one object per state-word setting"),
    Rule(r"ta/object-words/", "ta-object", "unit-ready", "E306 E308", "Q070", "12.2", "random words"),
    Rule(r"ta/(line-point|points)/", "te-region", "unit-ready", "E543 E544", "Q159 Q161", "12.2",
         "lines and points; rules in recompute_p1131.py, not coded"),
    Rule(r"ta/mtile-", "te-macrotile", "unit-blocked", "E174 E175 E331", "Q100 Q139 Q086", "12.2",
         "fitted table (tiling3d.py); other words refuse"),
    Rule(r"ta/zero-words/", "ta-object", "unit-ready", "E054", "Q068", "12.2",
         "the twelve zero words: refuse a non-zero one"),
    Rule(r"(followup/)?vdm/(state1|state1-split|state-units|state2-)", "vdm-stream", "unit-blocked",
         "E185 E191", "Q047 Q042", "12.2", "state word fields"),
    Rule(r"vdm/(index-list|index-trailing|index2)/", "vdm-stream", "unit-blocked",
         "E188 E300 E346 E414", "Q112 Q042", "12.2", "index list words"),
    Rule(r"vdm/(vtask-capacity|vertex-tasks)", "vdm-stream", "unit-blocked", "E189 E190 E571",
         "Q094 Q163", "12.2", "vertices per task"),
    Rule(r"mte/", "mte", "unit-blocked", "E061 E063 E194 E287", "Q069 Q162", "12.2",
         "viewport, clip, 1/w, OUTSEL"),
    Rule(r"dpm/", "dpm", "unit-blocked", "E200 E456 E464", "Q191", "12.7",
         "state page, free list, partial renders"),
    Rule(r"bif/", "bif-walk", "unit-blocked", "E457 E573 E592", "Q076 Q108", "12.5",
         "client and render directories"),
    Rule(r"platform/event-bits/", "events", "unit-blocked", "E154 E357", "Q111", "12.6",
         "EVENT_STATUS per event"),
    Rule(r"render/kick-objects/", "te-region", "scene-only", "E306", "Q070", "12.2", "3 kicks' PB"),
    Rule(r"usse/globals-vertex-eot/", "vertex-task", "exists", "E372", "Q053", "-",
         "vertex vectors of 11.33 replay in sgx-sim"),
    Rule(r"usse/output-room-tiles/", "pbe-emit", "unit-blocked", "E043 E044", "Q302", "12.1",
         "end-of-tile output room per tile"),
]


UNCLASSIFIED = Rule("", "unclassified", "unclassified", "", "", "?", "no rule matches: add one to RULES")


def classify_dir(rel):
    for r in RULES:
        if re.search(r.pattern, rel):
            return r
    return UNCLASSIFIED


def classify_vector(v, has_dump):
    """(status, reason) of a triangle-host vector as a scene: hang and fault vectors are
    `expect.outcome` scenes, an image is `expect.image`, a dump beside it checks the rebuilt words."""
    rb = v["readback"]
    f = rb.get("failed")
    if f:
        if "hung" in f:
            return "hang", ""
        if "faulted" in f:
            return "fault", ""
        return "excluded", f + ": no image to compare"
    kind = "pixels" if rb.get("pixels") else "mixed" if rb.get("mixed") else None
    if kind is None:
        return "excluded", "no pixels, no counts"
    return "scene-" + kind + ("+pb" if has_dump else ""), ""


def vector_files(data):
    root = data / "vectors"
    for dp, dn, fn in os.walk(root):
        for f in sorted(fn):
            if f.endswith(".vec.json"):
                yield pathlib.Path(dp) / f


def scan_vectors(data):
    """Counts of the triangle-host vectors by unit and status."""
    by = collections.defaultdict(collections.Counter)
    t = {"vectors": 0, "files": 0, "by": by, "options": collections.Counter()}
    for p in vector_files(data):
        d = json.loads(p.read_text())
        rel = p.relative_to(data / "vectors").parts
        unit = rel[1] if rel[0] in ("followup", "knowledge", "semantics", "nokernel") else rel[0]
        raw = d["run"]["raw"]
        rawdir = os.path.dirname(raw[0] if isinstance(raw, list) else raw)
        has_dump = (data / rawdir / "dumps").is_dir()
        hit = False
        for v in d["vectors"]:
            o = (v.get("provenance") or {}).get("options") or []
            if "--tri" not in o:
                continue
            hit = True
            st, _ = classify_vector(v, has_dump and "--dump-render" in o)
            by[unit][st] += 1
            by[unit]["_dump"] += has_dump and "--dump-render" in o
            t["vectors"] += 1
            for x in o:
                if x.startswith("--"):
                    t["options"][x] += 1
        t["files"] += hit
    return t


def scan_dumps(data):
    out = []
    for dp, dn, fn in os.walk(data):
        parts = pathlib.Path(dp).relative_to(data).parts
        if ".git" in parts or not parts or parts[-1] != "dumps":
            continue
        rel = "/".join(parts)
        n = sum(len(f) for _, _, f in os.walk(dp))
        r = classify_dir(rel + "/")
        out.append({"dir": rel, "files": n, "rule": r})
    return sorted(out, key=lambda x: x["dir"])


STATUS = ["scene-pixels", "scene-pixels+pb", "scene-mixed", "scene-mixed+pb", "hang", "fault", "excluded"]


TAIL = """\
## 3. What is missing, by unit

- **zls**: nothing for the address rule (built). The formats 0 to 2 and the negation bit (E466,
  E490) have 22 dumps and no rule in `sgx-pipe`; loads (E467) have datasets (`zls/load-store`,
  `load-copy`) but no dump directory. The pixels past the target follow the band (E831) at even
  sizes and odd ones (E885, E903); the stencil's byte a pixel and its test are coded (E988);
  overflow store (Q107) and formats 3 to 7 (Q120) stay refused.
- **ta**: the region test, the object layout and its failures are built. Missing: the macrotile
  table of the target (a fitted table, `tiling3d.py`, right on 123 and 69 only: Q100, Q139, Q086),
  lines and points (rules in the dataset's recompute script, not coded: Q159 to Q161), the
  object's format bits above 7:0 and the masks beyond the settings seen (Q070), the prim word's
  extra dword (Q164), and the object writer as a whole (12.2).
- **vdm, mte**: 57 and 12 dump directories of PB and TA data that a stream parser and an MTE
  model would have to reproduce; they wait for Q047, Q069 and the state word rules. No unit
  vector is built: the inputs (the stream words, the vertex outputs) are in the render dumps
  only through the PB, so they need the scene's `memory`.
- **isp**: the multisample window is built (786 tiles, 13 with seam holes refused: E953).
  Everything else needs a scene (`memory`) and, for pixels, the arithmetic of coverage, depth and
  iteration (E606, Q200): none gives it. The sample position, line, polygon offset and stencil
  rules (E214, E279, E071, E216) are in `isp` triangle-host vectors, not in dump directories.
- **pbe, iter**: only whole-job vectors (`pbe` 206, the pixel-event and texture runs): the
  end-of-tile words and the pixel PDS launch are not in any dump. 12.1 needs `memory` from a
  scene.
- **dpm, bif, events**: dump directories of text (the state page, the directory words, EVENT_STATUS
  per event) that need their units (12.7, 12.5, 12.6) and the registers' semantics (`regs.rs`).

## 4. The MTE clipping and depth-range datasets

Read in 12.0: `mte/clipping` (E194, E063), `mte/depth-range` and `depth-range2` (E287); the
probes' images only, no dump. What they establish:

- The MTE clips in clip space at z = -w and z = w (E287: a flat triangle at clip z from -1 to 1
  draws whole at w 1, one at -1.01 or 1.01 is removed, a sloped one is cut where z passes the
  bound). The viewport's z offset and scale come after the clip and are not clipped to [0, 1]: a
  depth above 1 reaches the test as itself, a negative one compares as 0 (inferred from two
  values a side).
- The size of a triangle goes as 1/w, and below w 1e-5 it shrinks away; the state block's w clamp
  word (blk:14) sets that threshold (E194, four values of the word). The two TA command floats
  (ta:152, ta:153) change no clipping scene (E063: 176 images equal their baselines).
- A vertex crossing w = 0 draws (1216, 1258, 1273, 1394 pixels at the w values of E063): the
  hardware clips or handles it in a way the pixel counts show but no record states as a rule.
- **Not established**: whether x and y are clipped at a guard band or only at the z planes; the
  clipped polygon's vertices (only pixel counts of the result exist); anything below the 64 x 64
  target. So an MTE model can state the z clip volume and the w clamp as measured and must
  refuse x or y clipping (Q069; the region clip, E1060, is whole tiles), and the pixel counts of
  the clipped scenes can only be reproduced by a model of the ISP arithmetic (E606, Q200).

## 5. Corrections to the plan's numbers

- Dump directories that sit beside triangle-host vectors are 65 of the 2464 vectors' runs (the
  `--dump-render` ones), not "about 700": the other directories of section 2 belong to
  script tables with no vectors of this kind.
- The plan's 197 dump directories are right (a directory named `dumps`, any depth).
- The plan names `zls/store-layout-dumps` 36 and `store-format-dumps` 22 dumps: right.
"""


def report(data):
    t = scan_vectors(data)
    dumps = scan_dumps(data)
    L = []
    w = L.append
    w("# Pipeline simulator: the inventory of data for unit and scene vectors (12.0)")
    w("")
    w("What of the recorded data can become a unit vector (one unit, one rule) or a scene vector (a")
    w("whole job), by unit and by what is missing. Counts are from the data repository at the time")
    w("of the scan (`tools/usse-asm/pipe_inventory.py`); the classification rules are the table in")
    w("that script, so a new dataset must be classified on purpose.")
    w("")
    w("## 1. The triangle-host vectors")
    w("")
    w("%d vectors in %d files carry `--tri` in `provenance.options`; the instruction replay leaves" %
      (t["vectors"], t["files"]))
    w("them out (the readback is the scene's image, not the shader's output). As scenes:")
    w("")
    w("- `scene-pixels`, `scene-mixed`: the image is the recorded result (`expect.image` as every")
    w("  pixel, or as value counts); `+pb`: the run kept a render dump (`--dump-render`) beside it,")
    w("  so a rebuilt scene's words can be compared with the parameter buffer of the same run.")
    w("- `hang`, `fault`: the job did not complete; `expect.outcome` of a scene. Whether a hang")
    w("  repeats is not in the vector (D5: a repeated measurement turns it into an `either`).")
    w("- `excluded`: `no pixel written` (the probe reported a draw of nothing: no image).")
    w("")
    w("| unit | total | pixels | +pb | mixed | hang | fault | excluded |")
    w("|---|---|---|---|---|---|---|---|")
    tot = collections.Counter()
    for unit in sorted(t["by"]):
        c = t["by"][unit]
        w("| %s | %d | %d | %d | %d | %d | %d | %d |" % (
            unit, sum(v for k, v in c.items() if not k.startswith("_")), c["scene-pixels"], c["scene-pixels+pb"], c["scene-mixed"] + c["scene-mixed+pb"],
            c["hang"], c["fault"], c["excluded"]))
        tot.update(c)
    w("| all | %d | %d | %d | %d | %d | %d | %d |" % (
        sum(v for k, v in tot.items() if not k.startswith("_")), tot["scene-pixels"], tot["scene-pixels+pb"], tot["scene-mixed"] + tot["scene-mixed+pb"],
        tot["hang"], tot["fault"], tot["excluded"]))
    w("")
    w("What every one of them is missing: the scene's `memory` and `regs` (the words the kick")
    w("submitted). Until a run records them (`--record-scene`, vectors.md 6.4) they come from")
    w("`--emit-scene`, an offline rebuild through libsgxfive's mock backend from `provenance.options`")
    w("and the recorded programs, tagged `rebuilt`. Only the %d that kept a render dump (%d of them" %
      (tot["_dump"], tot["scene-pixels+pb"] + tot["scene-mixed+pb"]))
    w("with an image, the rest hangs and faults) can be checked against their own run's parameter")
    w("buffer; the other %d would be rebuilt unchecked, and the plan's" %
      (sum(v for k, v in tot.items() if not k.startswith("_")) - tot["_dump"]))
    w("figure of about 700 dumps to check them against counts dump directories of other tables")
    w("(section 2), not dumps of these runs.")
    w("")
    w("The units a scene goes through decide what it can check before its unit models exist: the")
    w("pixel side (`pbe`, `texture`, `pds`, `usse` rows) needs 12.1 and 12.3, `ta`, `vdm`, `mte`")
    w("rows need 12.2, and every `isp` row needs the ISP's arithmetic (E606, Q200) to be pixel exact.")
    w("")
    w("## 2. The dump directories")
    w("")
    w("%d directories named `dumps`. Status: `built` (unit vectors made in 12.0), `unit-ready` (data" %
      len(dumps))
    w("and a decoder exist, the rule is not coded), `unit-blocked` (an open question blocks the")
    w("model), `scene-only` (a whole job only), `exists` (vectors already in the data repository).")
    w("")
    w("| kind | status | dirs | files | records | blocked by | phase |")
    w("|---|---|---|---|---|---|---|")
    groups = collections.OrderedDict()
    for d in dumps:
        r = d["rule"]
        g = groups.setdefault((r.kind, r.status, r.records, r.blockers, r.phase), [0, 0])
        g[0] += 1
        g[1] += d["files"]
    order = {"built": 0, "unit-ready": 1, "unit-blocked": 2, "scene-only": 3, "exists": 4,
             "unclassified": 5}
    for (kind, st, rec, blk, ph), (n, f) in sorted(groups.items(), key=lambda kv: (order[kv[0][1]], kv[0])):
        w("| %s | %s | %d | %d | %s | %s | %s |" % (kind, st, n, f, rec, blk, ph))
    sc = collections.Counter()
    for d in dumps:
        sc[d["rule"].status] += 1
    w("")
    w("By status: " + ", ".join("%s %d" % (k, sc[k]) for k in sorted(sc, key=order.get)) +
      " (directories).")
    w("")
    w("The directories of each rule, with what is special about them:")
    w("")
    seen = set()
    for d in dumps:
        r = d["rule"]
        if r.pattern in seen:
            continue
        seen.add(r.pattern)
        n = sum(1 for x in dumps if x["rule"] is r)
        w("- `%s`: %d dir%s; %s." % (r.pattern, n, "" if n == 1 else "s", r.note))
    w("")
    lost = [d for d in dumps if d["rule"] is UNCLASSIFIED]
    if lost:
        w("Unclassified (no rule of the script matches; the generator refuses to write this file):")
        w("")
        for d in lost:
            w("- `%s`: %d files." % (d["dir"], d["files"]))
        w("")
    L.extend(TAIL.splitlines())
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", required=True, type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path)
    a = ap.parse_args(argv)
    text = report(a.data)
    lost = [d["dir"] for d in scan_dumps(a.data) if d["rule"] is UNCLASSIFIED]
    if a.out:
        if lost:
            sys.stderr.write("unclassified dump directories, not written: %s\n" % ", ".join(lost))
            return 1
        a.out.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
