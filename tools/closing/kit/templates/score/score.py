#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""score.py: @NAME@'s scorer. Every verdict rule comes from kit/scorekit.py, the kept files are
read through kit/kitscore.py (byte copies of resgx545 @COMMIT12@, pinned in FROZEN.commits).

  score.py STAGE KEPT_DIR [ROOTS...]   ROW and CONTROL lines, then SUMMARY lines (exit 0)
  score.py gate STAGE ROOTS...         exit 0 when every control of GATES[STAGE] passed
  score.py premise STAGE KEPT_DIR      STOP lines and exit 1 when a control has no reading

REQUIRED: the files each stage's scorer reads (the runner and sessioncheck.py kept check them:
".suffix" for each row that ended ok, "fault:.suffix", "hang:.suffix" or "any:.suffix" for each
row that ended so or for every row, a plain name once);
read_files(STAGE, DIR) reads exactly what score() reads; producible(row) is the set of reading
keys a row's job can produce (the freeze refuses a control that reads anything else)."""
import os
import sys

KP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KP, "kit"))
import kitscore as K  # noqa: E402
import scorekit as SK  # noqa: E402

REQUIRED = {"s0": (".txt", "cases.tsv", "void.tsv", "readings.tsv")}
GATES = {}          # {stage: the earlier stage whose controls gate it}


def producible(row):
    return {"diff"} if row["args"].split()[:1] in (["tri"], ["fill"]) else set()


def reading(text):
    for ln in text.splitlines():
        if ln.startswith("diff: "):
            return {"diff": ln.split()[1]}
    return {}


def read_files(stage, d):
    cases = K.rows(d, "cases.tsv")
    K.rows(d, "void.tsv")
    for n in cases:
        K.text(d, n + ".txt")


def verdicts(stage, d):
    preds = K.predictions(KP, stage)
    cases = K.rows(d, "cases.tsv")
    controls, rows, lines = {}, [], []
    for r in K.table(KP, stage):
        n = r["name"]
        got = reading(K.text(d, n + ".txt")).get("diff") if n in cases and \
            cases[n]["class"] == "ok" else None
        want = preds.get(n, {}).get("diff", {})
        state = None if got is None or not want else got in want.values()
        if r["set"] == "control":
            controls[n] = state
            lines.append(f"CONTROL {n}: diff {got} (frozen {sorted(want.values())}): "
                         f"{'PASS' if state else 'FAILED' if state is False else 'cannot tell'}")
        else:
            rows.append(state)
            lines.append(f"ROW {n}: diff {got}: "
                         f"{'held' if state else 'FAILED' if state is False else 'cannot tell'}")
    return controls, rows, lines


def main(argv):
    if len(argv) >= 3 and argv[1] == "gate":
        dep = GATES.get(argv[2])
        if dep is None:
            return 0
        for root in argv[3:]:
            d = os.path.join(root, dep)
            if os.path.isdir(d):
                g = SK.gate(verdicts(dep, d)[0])
                print(f"gate {argv[2]} on {dep}: {'open' if g.ok else '; '.join(g.problems)}")
                return 0 if g.ok else 1
        print(f"gate {argv[2]}: {dep} has not run")
        return 1
    if len(argv) == 4 and argv[1] == "premise":
        stops = K.premise(KP, argv[2], argv[3])
        print("\n".join(stops) if stops else f"premise {argv[2]}: every control read")
        return 1 if stops else 0
    if len(argv) >= 3 and argv[1] in REQUIRED:
        controls, rows, lines = verdicts(argv[1], argv[2])
        print("\n".join(lines))
        print("SUMMARY: " + argv[1] + ": " + SK.headline("TODO the claim", controls, rows))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
