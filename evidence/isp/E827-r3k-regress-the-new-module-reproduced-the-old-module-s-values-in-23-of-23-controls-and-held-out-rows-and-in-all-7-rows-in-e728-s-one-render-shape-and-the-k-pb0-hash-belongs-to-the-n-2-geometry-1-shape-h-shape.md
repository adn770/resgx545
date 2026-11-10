+++
id = "E827"
claim = "R3k-regress (the lead's regression session on the new module, srcversion 230E0EF5): 23 of 23 rows of stage rg-ctl, taken from closing sessions that passed on the old module (E773 g-u1 tri and geometry jobs at 1024 x 768 and other sizes, E806 green fills 8 x 8 to 256 x 256, E798 g-dd probes, E763 and E788 r2-a-safe TE 0x20 and 0xe0 jobs; 2 controls, 21 held out), reproduced their old kept values (return code, echo, target hash, diff, first wrong pixel, triangle counts, renders ok and the dump hashes where the old job had a dump); in stage rg-pb 7 of 7 held-out rows in E728's one-render shape (TE 0x40 four times, one in mode 0 and one at 128 x 128, TE 0x80 and 0xc0, all held out) and its two controls (TE 0x20 and 0xe0) reproduced E728's target hash, diff, parameter buffer dwords and dump sha256s, so the module did not change E728's image; the same job in K2's shape (-n 2 --geometry 1, TE 0x40) gave 0x8ea26cdfee74a325, 3969 of 4096 pixels wrong, in 3 of 3 jobs, the value of E825's k-pb0, and the twin row (TE 0x60) gave 0xd2bfb75560f4c325, 0 wrong, again E825's twin value (H-SHAPE: the hash difference of E825 belongs to the job shape, not to the module [infer]); frozen verdicts 'rg-ctl: control 2 PASS of 2; heldout 21 PASS of 21; every row reproduced its old value (no module regression in these classes)' and 'rg-pb: E728-shape 7 of 7 held-out rows as H-OLD, controls {'pb-e20-m2-64': 'PASS', 'pb-ee0-m2-64': 'PASS'}; -n 2 --geometry 1: 3 of 3 as H-NEW, twin row H-NEW; H-SHAPE'"
unit = "isp"
method = "R3k-regress, the lead's module-regression session (not a stage of K2; built overnight 2026-11-10/11 by regress-build from the K2 framework, dataset render-closing-r3k-regress), run 2026-11-10, attempt out/20261110-222647 (one driver call, run/k.sh: rg-ctl 22:26:47, rg-pb 22:29:06 Mac time; out/k.log), kernel 7.3.0-resgx545, the new module of round 3 (srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at the preflight), the laptop (host cedar) on the home LAN, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, R1's build, not rebuilt; the old values of E728 come from another build of the tool, ~/sgxfive-test-1138b, a confound that did not change one value); 36 jobs frozen and run (rg-ctl 23, rg-pb 13), a debugfs reset before each job and nothing else written (no knob, render_rgn_arrays read back at the exit as 0x00000001, hold_recovery N), health ok after each stage; FROZEN.sha256 (verified at the start) and PREDICTIONS.sha256 written before the first job; the frozen predictions are the OLD kept values of the records and files named in the last column of predictions/rg-ctl.tsv and predictions/rg-pb.tsv (E773 g-u1, E806 q-t, E798 g-dd, E763 and E788 r2-a-safe, E728's p1141tex msaa-b-te29 jobs), the rg-pb rows in K2's shape frozen from E825's k-pb0 values (H-NEW, so those 3 rows ask only whether the value repeats); the gate of rg-pb (rg-ctl all ran, class ok) was open; scored by the frozen score/score_rg.py (out/20261110-222647/score-rg-ctl.txt, score-rg-pb.txt) and its verdict from the two stages. Rescored from the copy in resgx545-data (python score/score_rg.py rg-ctl|rg-pb out/20261110-222647/STAGE and verdict, the freeze verify passing in the copy) with the SUMMARY lines and the stage files byte-identical to the kept ones. The preflight (PREFLIGHT.md) reads the diff of the fork between the old and new module (10 commits) as giving no suspect for the render path at default knob values; that is a reading of the diff, not a measurement. Disclosures: README.md and PREFLIGHT.md are the pre-run documents (README.md says prepared, not run); debug/ and the scratch files of the freeze script are not in the copy; tests/fixtures/ holds copies of landed data used by the offline tests"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3k-regress:out/20261110-222647/rg-ctl/", "render-closing-r3k-regress:out/20261110-222647/rg-pb/", "render-closing-r3k-regress:out/20261110-222647/score-rg-ctl.txt", "render-closing-r3k-regress:out/20261110-222647/score-rg-pb.txt", "render-closing-r3k-regress:out/20261110-222647/gate-rg-pb.txt"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)"]
+++
**What ran.** E825 found that stage k-pb0 of K2, on the new module, gave target hashes that differ
from the values frozen from E728's one-render jobs, and read the cause as the job shape (K2's rows
add `-n 2 --geometry 1`, two renders, the tool checks render 2 drawn on another background). That
was an inference from the kept files. The lead's session R3K-regress asks the question directly: did
the new module change any image? It has two stages. `rg-ctl` re-runs 23 jobs from closing sessions
that passed on the old module, each with its old kept value frozen as the prediction: the E773 g-u1
tri and geometry jobs at 1024 x 768 (n 1 to 4, moves, geometry-only renders) and at other sizes, the
E806 green fills from 8 x 8 to 256 x 256, the E798 g-dd probes p1 and p2, and the E763 and E788
r2-a-safe jobs at 320 x 400 (TE 0x20) and 256 x 160 and 320 x 128 (dumps). `rg-pb` runs the k-pb0
job in two shapes: E728's own (one render, TE 0x20, 0x40, 0x80, 0xc0, 0xe0, `cmd:13` 0x80000002, 64
x 64 and 128 x 128, TE 0x40 three times) with E728's values frozen (H-OLD), and K2's shape (`-n 2
--geometry 1`, TE 0x40 three times and the TE 0x60 twin) with the values k-pb0 gave (H-NEW). It
writes nothing but the debugfs `reset`.

**Frozen verdict (as printed).**

```
SUMMARY: rg-ctl: control 2 PASS of 2; heldout 21 PASS of 21; every row reproduced its old value (no module regression in these classes)
SUMMARY: rg-pb: E728-shape 7 of 7 held-out rows as H-OLD, controls {'pb-e20-m2-64': 'PASS', 'pb-ee0-m2-64': 'PASS'}; -n 2 --geometry 1: 3 of 3 as H-NEW, twin row H-NEW; H-SHAPE: the module did not change E728's image (7 of 7 E728-shape rows reproduce E728's hash, diff, dwords and dump sha256s, both E728 controls too); k-pb0's value is reproducible (3 of 3 -n 2 --geometry 1 rows give 0x8ea26cdfee74a325) and belongs to that job shape, not to the module [infer: the shape differs from E728's, the tool prints render 2 in other colours]
```

The gate: `gate rg-pb: open (every rg-ctl row ran, class ok; image mismatches are results, not a
closed gate)`.

**Results [HW].**

| stage | rows | as frozen | what the rows are |
|---|---|---|---|
| rg-ctl | 23 | 23 (controls 2 of 2, held out 21 of 21) | E773 11 (1024 x 768 jobs and four other sizes), E806 7 (green fills), E798 2, E763/E788 3 |
| rg-pb, E728 shape | 9 | 9 (controls TE 0x20 and 0xe0 PASS; held out 7 of 7: TE 0x40 x3, mode 0, 128 x 128, TE 0x80, TE 0xc0) | target hash, diff, first wrong pixel, triangle counts, TA data and parameter buffer sha256, stream and dwords 11 to 26 |
| rg-pb, K2 shape | 4 | 4 | TE 0x40 x3: target hash 0x8ea26cdfee74a325, 3969 of 4096 wrong; TE 0x60 twin: 0xd2bfb75560f4c325, 0 wrong |

The three TE 0x40 rows in K2's shape give k-pb0's value again (0x8ea26cdfee74a325, the value of
E825's d0 and p1), the twin gives k-pb0's twin value, and the same job in E728's shape (one render)
gives E728's 0xfc5ff15e0434a325 on the new module. The hash therefore moves with the job shape on
one module, not with the module.

**What it shows.** On the new module with default knobs, and for the jobs above, the images, return
codes, triangle counts and dump hashes are the old module's. E825's failure of the three k-pb0
controls is the shape of the frozen values, as E825 read it [infer]: the explanation (render 2 drawn
on 0xff000080) rests on the kept outputs and the tool source, and K2's shape was never run on the
old module, so that part of H-SHAPE is an inference. The three H-NEW rows were frozen from k-pb0's
own values; they show that the value repeats, not that it is right.

**What it does not cover.** No fault job (no held hang, BIF fault or reset recovery); no firmware
task of ours; no 4x region-header arrays and nothing at large sizes in the 4x layout (E824's k-f4
stays the only measurement of those; rg-ctl's 1024 x 768, 1280 x 1024 and 2048 x 1536 rows are at
the default of one array); no knob other than its default (render_rgn_arrays 1, hold_recovery N,
render_pb_pages 0x422 were read, none written); one tool build (r1) against old values taken with
others; one boot. A class that is not in the 36 jobs is not covered; a regression in a path these
jobs do not touch would not show.
