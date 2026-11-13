+++
id = "E1013"
claim = "Round 11 offline (Q210; no run): over every kept DPM run of r5 to r10 with a published replay of E874's 1500-vertex scene (520 jobs read; 53 calibrations and 118 partial-render cells of the standard workload have an S6 step), the lower end of S6's sampled bracket is the replay R plus a class fixed per target: frozen before any kept sample beyond E1009's own, H-CLASS (R + 1 at E1009's five targets, R at its eight) held at 37 of 37 calibrations (16 held out) and 56 of 56 cells (50 held out); beyond the 13 the lower end is R + 1 at 2048x3072, 2560x3072 and 3072x2560 and R at 1024x1024, 2560x2560, 3072x2048, 3072x3072, 1024x2048 and 2048x4096, the same at every run of a target, calibration or cell; the frozen aspect rule (biased iff w/h > 2 or w < h, fitted on the 13) fails at 3072x2560, 1024x2048 and 2048x4096, and no simple rule of w, h, area or residue separates the eight biased targets from the fourteen others [HW, held out offline; the scope to the standard workload is post hoc: the 12 exceptions are `--vtx-coords`/`--slot` runs at 2048x2048, another scene]"
unit = "dpm"
method = "Offline, no run (round 11, decision R11-4 a of closing11/DECISIONS-R11.md and closing11/plan/rank-round11.md, finding 3). Data: every kept job of the published DPM sessions with a width, a height and a timeline (render-closing-r5-dpm, -r6-dpm, -r7-dpm, -r8-ldpm, -r9-ldpm, -r10-dpm; their cases.tsv and job outputs), read with r10-dpm's score/read.py (S6's bracket (a, max(a, b - 1)) from the 0x0724 high halves a and b of the samples around the global page step; the lower end a); the replay R from r10-dpm's gen/r9_tables.json (the 13 targets) and, for 11 more, r8-ldpm's gen/ol7_tables.json and r7-dpm's sibling-src/b/q210_targets.out (the same E874 replay; the 13 agree across the sources). Check closing11/plan/c5-q210/: s6bias_rule.py (sha256 ee0fe5e410b52e206b368738b6485e7c2cd10c333ea747c39045e567cffa6b95, FREEZE.log 2026-11-13T11:03:08Z: read before were E1009, r10-dpm's fold/brackets.py and .out, fold/readall.py, gen/plan.py, gen/r9_tables.json and score/read.py) freezes H-CLASS, H-LOW0 (lower end R everywhere), H-LOWPLUS1 (R + 1 everywhere) and a candidate H-RULE (biased iff w/h > 2 or w < h, fitted on E1009's 13, its predictions beyond them frozen as a formula); fit rows E1009's 15 replicates and control, E962's four and E961's 2048x2304 rows, all else held out; scorer s6bias_score.py (s6bias_score.out), notes NOTE.md. 183 runs had an S6 step and a replay; 12 `--vtx-coords`/`--slot` runs at 2048x2048 (E937's scene, which dpm.rs already refuses) were scoped out after the first pass. This fold re-ran s6bias_score.py with python -I and got a byte-identical output; sgx-pipe's `dpm::s6_bracket_lower_end` gives the lower end at the 22 kept targets and its test holds the table (s6_s_sampled_lower_end_is_the_replay_plus_a_per_target_class_e1013)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r5-dpm", "render-closing-r6-dpm", "render-closing-r7-dpm", "render-closing-r8-ldpm", "render-closing-r9-ldpm", "render-closing-r10-dpm", "cited-scratch:closing11/plan/c5-q210/", "cited-scratch:closing11/plan/rank-round11.md"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What was done.** E1009 read the lower end of S6's sampled bracket at the replay plus 1 at five
targets (4096x1024, 4096x1536, 3584x1024, 2048x512, 2048x2304; 15 of 15 replicates), where the
replay held at eight others, and fitted no rule for where the bias comes in. The round 11 planner
froze the class table and an aspect rule by hash, then read every kept DPM run of rounds 5 to 10
whose target has a published replay: calibrations and partial-render cells whose timeline shows
the sixth global page step before the first partial render.

**Results [HW, held out offline]** (s6bias_score.out), d = lower end - R:

- E1009's 13 targets, standard workload: H-CLASS 37 of 37 calibrations (21 fit, 16 held out) and 56
  of 56 cells (6 of E961, 50 held out). The eight unbiased (1280x1280, 1536x1536, 1792x1792,
  2048x2048, 2304x1792, 2304x2304, 2560x2048, 4096x2048) read d = 0 at every run, the five biased
  d = +1 at every run. H-LOW0 fails every biased run, H-LOWPLUS1 every unbiased one.
- Beyond the 13: d = +1 at 2048x3072 (5 calibrations, 7 cells), 2560x3072 (1, 5) and 3072x2560 (1,
  5); d = 0 at 1024x1024 (3, 6), 2560x2560 (2, 15), 3072x2048 (3, 5), 3072x3072 (18 cells),
  1024x2048 (1 calibration) and 2048x4096 (1 cell).
- d is the same at every run of a target, whichever session and whether calibration or cell.
- H-RULE: right at 2048x3072, 2560x3072, 1024x1024, 2560x2560, 3072x2048 and 3072x3072, wrong at
  3072x2560 (predicted unbiased, 6 runs biased), 1024x2048 and 2048x4096 (predicted biased, read
  unbiased): refuted as a rule.
- First pass, all workloads: the only runs off H-CLASS were 12 `--vtx-coords`/`--slot` jobs at
  2048x2048 (d = -154, -225, +113), another scene than the replay's (E937); scoped out post hoc.

Post hoc, the eight biased targets are 4096x1024, 4096x1536, 3584x1024, 2048x512, 2048x2304,
2048x3072, 2560x3072 and 3072x2560; no w, h, pixel count, aspect or residue of 256, 512 or 1024
separates them from the fourteen others (1024x1024 and 2048x3072 share residues). Kept targets
with no replay in a published table (E881's 2048x1024, 4096x4096, 1024x768) cannot be read.

**What it shows.** [HW, held out offline] The replay's miss at S6 is a fixed offset per target, one
page or none, not noise and not a property of the run: 22 targets, 171 runs, each target one value.
E1009's five-target reading holds and extends to three more biased targets; its note that the five
are "wider than 2:1" (with 2048x2304) does not give the class (an appended note there). [infer] The
offset belongs to the replay's own block or region counts at those targets, not to the sampler.
sgx-pipe's `dpm::s6_bracket_lower_end` gives the lower end at the 22 targets and refuses others.

**What it does not show.** Why a target is biased (the replay's block and region counts per target
would say where its count falls short), S3's offsets (sampled lower end +1 at 2048x2304 and
4096x1536, +2 at 3072x2560's calibration; E935 pinned 2048x4096's S3 three above by the abort's
count) and S2's (-1 at 4096x1536), targets not run, and other scenes. Refuted by: one run of a
listed target whose lower end is off its class.
