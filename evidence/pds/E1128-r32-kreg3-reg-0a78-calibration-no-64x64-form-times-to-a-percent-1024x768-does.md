+++
id = "E1128"
claim = "r32-kreg3 on module 7CE8E38E (Q024), stage s0, a safe calibration of the many-triangles load (t30 probe --tri --vertices 1500, the triangle and 499 copies, no register write): eight references a form, reading the median of renders 2-N; their spread (interquartile range of the eight medians) is 4.42, 3.28 and 3.50 percent at 64x64 with 10, 20 and 40 renders a job (about 0.73 ms a render), and 0.32, 0.20 and 0.16 percent at 1024x768 (about 22.07 ms a render); the frozen pick: 's0's references draw; picked form l10 (48 of 48 rows decided)', the first form at most 0.8 percent; no 64x64 form qualifies, so more renders a job do not time the 64x64 load to a percent"
unit = "pds"
method = "r32-kreg3 (render/closing-r32-kreg3), stage s0 of the question-closing pass (round 32: Q024's last clause, the many-small-triangles load, by the user's decision of 2026-11-16 (answer a: the question's load as asked, more renders a job, a safe calibration stage with a frozen pick rule); the kit word kreg:0x0a78=V approved by the user in round 29 (as E1114 states), flagged class; records E1128 and E1129 assigned by the lead), dataset render-closing-r32-kreg3; attempt out/20261116-183256 (scores score-s0.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike), stock firmware, tools ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) and ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); every s0 reference `probe --tri pixel --width W --height H --vertices 1500` (t30) with bins/p1139-green.bin given N times (N renders on N contexts, each timed `tri WxH #1: T us`), six forms (64x64 at N = 10, 20, 40, then 1024x768 at N = 10, 20, 40), eight references each in eight rounds, each round its own frozen shuffle of the forms (gen/gen.py SEED 20261118), after c0-tri (t10, an exact 64x64 triangle), no register write; the reading the median of renders 2-N; the frozen pick rule (score.py pick): the first form in that order whose eight references all draw one image and spread (interquartile range in percent of their median) at most 0.8 percent, its flagged stage alone gated open; the rows tables/s0.txt, the frozen predictions predictions/s0.tsv); freezes: FROZEN.sha256 d51040cee70a84faec2e880fa1dd7bf1c124e6bfc2aa08906b8e585be3e09a72 (47 files), PREDICTIONS.sha256 9c28415068af5066431e615a7a51950905ef8dd3ab19ee7dc8913d13e0252f6a (7 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at bf0ba561, resgx545:tools/closing/kit/lib_kit.sh at bf0ba561, resgx545:tools/closing/kit/run_stage.sh at bf0ba561, resgx545:tools/closing/kit/kitscore.py at bf0ba561, resgx545:tools/closing/kit/fake/sudo at bf0ba561, resgx545:tools/closing/kit/fake/timeout at bf0ba561, resgx545:tools/closing/kit/fake/df at bf0ba561, resgx545:tools/closing/kit/fake/modinfo at bf0ba561, resgx545:tools/closing/kit/fake/sha256sum at bf0ba561, resgx545:tools/closing/kit/fake/tool.sh at bf0ba561, resgx545:tools/closing/kit/fake/tool.py at bf0ba561, resgx545:tools/closing/kit/fake/ssh.py at bf0ba561, resgx545:tools/closing/scorekit.py at bf0ba561, resgx545:tools/closing/sessioncheck.py at bf0ba561, data:render/closing-s1b/bins/p1139-green.bin at 6b5c5112, data:render/closing-r31-kreg2/fold/posthoc.txt at 6b5c5112, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main bf0ba56; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r32-kreg3:out/20261116-183256/s0/", "render-closing-r32-kreg3:fold/"]
terms = ["CR_PDS_REG_0A78"]
+++
**What ran.** Stage s0 (safe, no register write): c0-tri, then the many-triangles load of E1125,
`probe --tri pixel --vertices 1500` (t30) with the green pixel program given N times, so N
renders a job, each on its own context, in six candidate forms: 64x64 (the question's load) at
N = 10, 20 and 40, then 1024x768 at N = 10, 20 and 40 (E438: 1500 vertices complete there in the
default parameter buffer). Eight references a form, in eight rounds, each round its own frozen
shuffle of the six forms. Frozen before the run: the reading is the median of renders 2-N; a
form qualifies when its eight references all draw (N timed renders, no failure, one image) and
their spread, the interquartile range of the eight readings in percent of their median, is at
most 0.8 percent; the first qualifying form in that order is picked and only its flagged stage
runs (E1129); none: no flagged row.

**Frozen verdict (as printed).** attempt 20261116-183256, stage s0 (score-s0.txt): `SUMMARY: s0:
s0's references draw; picked form l10 (48 of 48 rows decided)`, with `PICK: l10 (500 triangles
(1500 vertices) at 1024x768, 10 renders a job; stage kl10; BOUND 1.000 %)`. The score and all six
gates reproduce byte for byte (fold/reproduce.out).

**Results [HW].** c0-tri exact. Every reference drew one image: 64x64 `o0 mixed 0xff00ff00 x2296
0xff203040 x1800` (as E1125), 1024x768 `o0 mixed 0xff203040 x547615 0xff00ff00 x238817`. The
eight medians and their spread (score-s0.txt, fold/posthoc.txt):

| form | renders a job | medians (us) | median | spread |
|---|---|---|---|---|
| 10 | 10 at 64x64 | 750 784 719 729 755 732 702 772 | 741 | 4.420 % |
| 20 | 20 at 64x64 | 741 720 706 742 733 699 713 730 | 725 | 3.276 % |
| 40 | 40 at 64x64 | 743 730 740 693 763 713 725 762 | 735 | 3.503 % |
| l10 | 10 at 1024x768 | 22003 22034 22089 22056 22117 22107 22034 22105 | 22072.5 | 0.324 % |
| l20 | 20 at 1024x768 | 22021 22009 22085 22041 22066 22076 22077 22099 | 22071 | 0.195 % |
| l40 | 40 at 1024x768 | 22004 22096 22059 22075 22112 22106 22084 22108 | 22090 | 0.161 % |

Within one job, renders 2-N spread 7.8 to 10.1 percent at the median at 64x64 and 0.23 to 0.27
percent at 1024x768.

**What it shows.** No 64x64 form reaches the 0.8 percent pick bound: going from 10 to 40 renders
a job leaves the job medians spread 3.3 to 4.4 percent, so most of the 64x64 noise is between
jobs, which more renders in a job do not average away [infer]. The same 500 triangles at 1024x768
take about 22 ms a render and time to a third of a percent at ten renders a job. The green covers
56 percent of the 64x64 target and 30.4 percent of the 1024x768 one; the copies move at most 31
pixels, so at 1024x768 each triangle covers about a quarter of the target [infer].

**What it does not show.** A verdict on any value (E1129 has it, at 1024x768); whether the 64x64
load, timed by another method (longer jobs, many more jobs), shows a dependence of a few percent.
