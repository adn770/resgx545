#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
"""Re-judge a saved stage B run (data directory) against the frozen predictions: no laptop."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run_stage as R

d = pathlib.Path(sys.argv[1])
class Dummy:
    def save(self, f, o):
        (d / f).write_text(o if isinstance(o, str) else json.dumps(o, indent=1, sort_keys=True) + "\n")
ctl = json.loads((d / "b-controls.json").read_text())
out = json.loads((d / "b-rounds.json").read_text())
m = json.loads((d / "b-markers.json").read_text())
R.check_frozen_predictions()
R.judge_b(Dummy(), ctl, out, m["markers"], m["p_pattern"])
