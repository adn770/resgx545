+++
id = "E1125"
claim = "r31-kreg2 on module 7CE8E38E (Q024), stage k2, cannot tell by its frozen premise: CR_PDS_REG_0A78 at each of its 64 values on two shuffled passes before a job of six renders of 500 small triangles (t30 probe --tri --vertices 1500 at 64x64, about 0.72 ms a render); s0's eight references v1-v8 spread 8.27 percent (interquartile range of their medians, 687-822 us), so the frozen bound BOUND2 = 3 x 8.27 = 24.8 percent exceeded its 2.5 percent cap: 'k2: cannot tell: no row decided; controls: bound2: cannot tell'; every row drew one image and no render failed; post hoc readings (no verdict): every value's two medians lie -6.0 to +11.4 percent of the controls' median 722.5 us, within the load's noise"
unit = "pds"
method = "r31-kreg2 (render/closing-r31-kreg2), stages s0, k2 of the question-closing pass (round 31: Q024's rerun of r29-kreg (E1114) with the control rule fixed before the run (the median of renders 2-6, at most one 0x2c control a stage outside its band) and the second load timed by t30; the kit word kreg:0x0a78=V approved by the user in round 29 (as E1114 states), flagged class; records E1124 and E1125 as the builder named them), dataset render-closing-r31-kreg2; attempt out/20261116-145122 (scores score-k2.txt, score-s0.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1, linux fork 8bc0877e8603; installed and loaded alike), stock firmware, tools ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) and ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); every k2 job `probe --tri pixel --width 64 --height 64 --vertices 1500` (t30) with bins/p1139-green.bin given six times (six renders on six contexts, each timed `tri 64x64 #1: T us`) after a debugfs reset and a debugfs kreg write of 0x0a78 read back before the job, 0x2c written and read back after it; the rows tables/s0.txt and tables/k2.txt (gen/gen.py SEED 20261117 + 1), the frozen predictions predictions/s0.tsv and k2.tsv); freezes: FROZEN.sha256 28ae6ecf7ed7ce7808ea5d80f9e8f40986a0a12e5876f8c71289b677e0273eb3 (40 files), PREDICTIONS.sha256 b41d2cfe17ffba18783e917135cf4598540f47d8133eaa2924c939c5300a2107 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2ffa9a93, resgx545:tools/closing/kit/lib_kit.sh at 2ffa9a93, resgx545:tools/closing/kit/run_stage.sh at 2ffa9a93, resgx545:tools/closing/kit/kitscore.py at 2ffa9a93, resgx545:tools/closing/kit/fake/sudo at 2ffa9a93, resgx545:tools/closing/kit/fake/timeout at 2ffa9a93, resgx545:tools/closing/kit/fake/df at 2ffa9a93, resgx545:tools/closing/kit/fake/modinfo at 2ffa9a93, resgx545:tools/closing/kit/fake/sha256sum at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.sh at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.py at 2ffa9a93, resgx545:tools/closing/kit/fake/ssh.py at 2ffa9a93, resgx545:tools/closing/scorekit.py at 2ffa9a93, resgx545:tools/closing/sessioncheck.py at 2ffa9a93, data:pds/reg-0a78-timing/output.txt at dc838e60, data:render/closing-s1b/bins/p1139-green.bin at dc838e60, data:render/closing-r29-kreg/fold/posthoc.txt at dc838e60, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 2ffa9a9; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r31-kreg2:out/20261116-145122/s0/", "render-closing-r31-kreg2:out/20261116-145122/k2/", "render-closing-r31-kreg2:fold/"]
terms = ["CR_PDS_REG_0A78"]
+++
**What ran.** Stage s0 as E1124, with v1-v8: the second load, `probe --tri pixel --width 64
--height 64 --vertices 1500` (t30) with the green pixel program given six times, so six renders a
job, each on its own context, each of the triangle and 499 copies moved c/16 pixel. Stage k2
(flagged, gated on c0-tri and v1-v8): the 64 values on two passes, each its own frozen shuffle,
c01-c16 writing 0x2c and c-end, as k1. Frozen: the reading is the median of renders 2-6; k2's
bound and its controls' band BOUND2 = max(1.0, 3 x the interquartile range of v1-v8 in percent of
their median), cannot tell when above 2.5 percent (E141's smaller excursion); a k2 row must draw
v1's image.

**Frozen verdict (as printed).** attempt 20261116-145122, stage s0 (score-s0.txt): `SUMMARY: s0:
s0's references draw and time (17 of 17 rows decided)`, with `REF2 719.5 us (v1-v8), their IQR
8.270 %: BOUND2 24.809 % (cap 2.5 %)`; stage k2 (score-k2.txt): `SUMMARY: k2: cannot tell: no row
decided; controls: bound2: cannot tell`. The scores reproduce byte for byte (fold/reproduce.out).

**Results [HW].** v1-v8 drew `o0 mixed 0xff00ff00 x2296 0xff203040 x1800` six times each, and so
did every k2 row; no render failed, c-end exact. v1-v8 medians 703 774 695 687 750 697 736 822 us.
c01-c16 read 671-787 us (interquartile range 8.03 percent of 722.5 us). All 760 renders 2-6 of
the load: median 739 us, 606-1751 us, interquartile range 10.7 percent; within one job the five
renders spread 6.05 percent at the median (fold/posthoc.txt).

**What it shows.** [infer, post hoc] The load is too short to time to a percent: a render of
about 0.72 ms carries tens of microseconds of jitter, within a job (6 percent) and between jobs
(8 percent); drift is smaller (the run-order medians fall about 2.4 percent over the stage). Read
anyway, every value's two medians lie -6.0 to +11.4 percent of the controls' median, the 128 value
rows' median +2.3 percent, no value apart from that noise on both passes; a dependence under about
25 percent cannot be seen.

**What it does not show.** No verdict on the many-small-triangles load: Q024's clause stays
open. A rerun needs a longer render of the same kind (a larger target or more work a render),
chosen by a safe calibration stage before any flagged row.
