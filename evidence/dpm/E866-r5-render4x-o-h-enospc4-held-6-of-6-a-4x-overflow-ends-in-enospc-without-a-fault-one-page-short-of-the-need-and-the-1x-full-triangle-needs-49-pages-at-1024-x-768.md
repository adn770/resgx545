+++
id = "E866"
claim = "R5-render4x stage o (11 jobs, no fault): the controls passed (the tool's default 1x triangle at 1024 x 768 completed at render_pb_pages 0x35 with 19 scene pages and overflowed at 0x34; the 4x full triangle on four arrays completed at 1024 x 768 with P 0xe3 and 193 pages), and H-ENOSPC4 held, 6 of 6 rows decided: the 4x full triangle on a context made for 4x targets ended in -ENOSPC with no BIF line one page short of its need (1024 x 768 at 0xe2 and 288 x 144 at 0x23, replicates of E846; 640 x 480 at 0x6d and 512 x 384 at 0x52, held out) and completed with 0 wrong pixels at the need (640 x 480 at 0x6e, 76 pages; 512 x 384 at 0x53, 49 pages, held out); exploratory, the 1x full triangle at 1024 x 768 completed at 0x53 with 49 scene pages and overflowed at 0x52, the need the plan's per-macrotile model gave, not E846's frozen 97"
unit = "dpm"
method = "R5-render4x stage o (11 rows, fault limit 1: the first fault-class event ends the stage) of the question-closing pass, round 5 (decisions R5-3 a, the render plan's 4 a), dataset render-closing-r5-render4x, attempt out/20261112-100112 (stage o 10:03:13 Mac time; driver log run-r5x.log), laptop host cedar, 2026-11-12, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E865; render_pb_pages written per row after the row's reset and read back (0x35, 0x34, 0xe3, 0xe2, 0x23, 0x6e, 0x6d, 0x53, 0x52, 0x53, 0x52), 0x422 restored after each job; o1, o2 `tri --width 1024 --height 768 -n 1 --keep-going --keep-overflow --wait-ms 20000` (E827's ctl-u-1024-n1, the tool's default triangle), o3 to o9 the 4x full triangle of E845 (`tri --tri-full ... --aa4` with E824's words, own maximum), o10, o11 `tri --tri-full` at 1024 x 768 with the default CR_TE_AA, each with --dump-render and --regs 0x0700-0x072c; every frozen need taken from a kept twin of the row's own argv (gen/twins.py: the scene pages of published dumps of the same scene; 19 from three default-triangle dumps, 193, 76, 49 and 12 from E824's and E845's), o10, o11's 49 the plan's model, marked [model] and gating nothing (closing5/render4x/exp-render4x-r5.md section 1.6); the outcome and the page rule frozen in predictions/o.tsv before the first job (FROZEN.sha256 e24977b3..., PREDICTIONS.sha256 6c700fa8...); scored by the frozen score/score_r.py o in the run (score-o.txt), re-run on the kept files on 2026-11-12 with byte-identical output"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-render4x:out/20261112-100112/o/", "render-closing-r5-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "CR_BIF_FAULT"]
+++
**What ran.** E846 read, after the run and with its gate closed, that a 4x scene that overflows
the parameter buffer ends in -ENOSPC without a fault, as at 1x. Stage o froze that as H-ENOSPC4 and
held it out at two sizes not run before, one page either side of the need of each (640 x 480, 76
pages, and 512 x 384, 49, from E824's dumps), with E846's two overflows as replicates. Round 4's
control was frozen for another scene than its row ran (E846); here every need comes from a kept
dump of the row's own scene, and the control o1/o2 is the default triangle at its measured 19 pages,
one page apart. o10 and o11 are the 1x full-triangle pair round 4 meant to run, at the need the
round 5 plan's model gives (49 [model]), exploratory.

**Frozen verdict (as printed).** `H-ENOSPC4: a 4x scene that overflows the PB ends in -ENOSPC with
no BIF line, as at 1x, one page short of its kept twin's need (o7 640 x 480, o9 512 x 384), and
completes with 0 wrong at the need (o6, o8); o4, o5 replicate E846 (6 of 6 rows decided); the 1x
full pair: o10-1xf-1024x768-p53 complete, o11-1xf-1024x768-p52 overflow (the need is 49: E846's
sentence 'the frozen need 97 is the model of the full triangle' needs an appended correction)`.

**Results [HW].**

| job | scene | P (usable) | need (source) | set | outcome |
|---|---|---|---|---|---|
| o1 | 1x default, 1024 x 768 | 0x35 (19) | 19 (twins) | control | complete, 19 pages, PASS |
| o2 | the same | 0x34 (18) | 19 | control | -ENOSPC, PASS |
| o3 | 4x full, 1024 x 768 | 0xe3 (193) | 193 (twins) | control | complete, 193 pages, PASS |
| o4 | the same | 0xe2 (192) | 193 | replicate | -ENOSPC, held |
| o5 | 4x full, 288 x 144 | 0x23 (1) | 12 | replicate | -ENOSPC, held |
| o6 | 4x full, 640 x 480 | 0x6e (76) | 76 (E824 h6) | held out | complete, 76 pages, held |
| o7 | the same | 0x6d (75) | 76 | held out | -ENOSPC, held |
| o8 | 4x full, 512 x 384 | 0x53 (49) | 49 (E824 h5) | held out | complete, 49 pages, held |
| o9 | the same | 0x52 (48) | 49 | held out | -ENOSPC, held |
| o10 | 1x full, 1024 x 768 | 0x53 (49) | 49 [model] | explore | complete, 49 pages |
| o11 | the same | 0x52 (48) | 49 [model] | explore | -ENOSPC |

Every -ENOSPC row is the tool's `job: failed: scene overflowed the parameter buffer, context kept
(No space left on device)` with no BIF line in its kernel-log slice; every completed 4x row had 0
wrong pixels. The stage ran to its end with no fault-class event and health ok.

**What it shows.** [HW] At 4x on four arrays a scene that overflows the parameter buffer ends in
-ENOSPC without a fault, as at 1x, and the page rule (complete iff P - 0x22 >= the need) holds one
page either side of the need at 1024 x 768, 640 x 480 and 512 x 384 (the last two held out): the
fault of Q292 is not the overflow. The full triangle at 1x and 1024 x 768 needs 49 scene pages, one
page of the boundary measured, where E846's frozen need of the full triangle was 97. [infer] The
model behind 49 (one stream a 32 x 16 tile, the pages taken a macrotile, E773's HU1: 16 x 3 + 1)
fits its one kept dump and this boundary, two scenes; with E846's correction the 97 is wrong for 1x.

**What it does not show.** Why the overflowed 4x images differ (E846's 288 x 144 and 1024 x 768);
the 1x full triangle at any other size; the scene need of a 4x scene that is not the full triangle.
One run each, one boot.
