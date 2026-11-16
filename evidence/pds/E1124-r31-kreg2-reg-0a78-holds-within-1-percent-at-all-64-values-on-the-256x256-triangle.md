+++
id = "E1124"
claim = "r31-kreg2 on module 7CE8E38E (Q024), stage k1: CR_PDS_REG_0A78 written to each of its 64 values 0x00-0x3f on two shuffled passes before a 256x256 triangle job of six renders; by the frozen rule (the median of renders 2-6 against the sixteen 0x2c controls' median 67004.5 us, a value failing only when both passes lie more than 1 percent out on the same side) H0 held for all 64 values: 'CR_PDS_REG_0A78 at every value 0x00-0x3f leaves the 256x256 triangle's render time within 1.00 percent of 0x2c's on two shuffled passes (64 of 64 rows decided)'; the controls lay -0.61 to +0.10 percent of s0's references (67138 us), none outside the band, spread 0.332 percent; three of 128 readings lay over 1 percent, each on one pass only (0x11 +1.53, 0x2e +1.34, 0x15 +1.25)"
unit = "pds"
method = "r31-kreg2 (render/closing-r31-kreg2), stages s0, k1 of the question-closing pass (round 31: Q024's rerun of r29-kreg (E1114) with the control rule fixed before the run (the median of renders 2-6, at most one 0x2c control a stage outside its band) and the second load timed by t30; the kit word kreg:0x0a78=V approved by the user in round 29 (as E1114 states), flagged class; records E1124 and E1125 as the builder named them), dataset render-closing-r31-kreg2; attempt out/20261116-145122 (scores score-k1.txt, score-s0.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1, linux fork 8bc0877e8603; installed and loaded alike), stock firmware, tools ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) and ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); every k1 job `tri --width 256 --height 256 -n 6` (t10) after a debugfs reset and a debugfs kreg write of 0x0a78 read back before the job, 0x2c written and read back after it; the rows tables/s0.txt and tables/k1.txt (gen/gen.py SEED 20261117), the frozen predictions predictions/s0.tsv and k1.tsv); freezes: FROZEN.sha256 28ae6ecf7ed7ce7808ea5d80f9e8f40986a0a12e5876f8c71289b677e0273eb3 (40 files), PREDICTIONS.sha256 b41d2cfe17ffba18783e917135cf4598540f47d8133eaa2924c939c5300a2107 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2ffa9a93, resgx545:tools/closing/kit/lib_kit.sh at 2ffa9a93, resgx545:tools/closing/kit/run_stage.sh at 2ffa9a93, resgx545:tools/closing/kit/kitscore.py at 2ffa9a93, resgx545:tools/closing/kit/fake/sudo at 2ffa9a93, resgx545:tools/closing/kit/fake/timeout at 2ffa9a93, resgx545:tools/closing/kit/fake/df at 2ffa9a93, resgx545:tools/closing/kit/fake/modinfo at 2ffa9a93, resgx545:tools/closing/kit/fake/sha256sum at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.sh at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.py at 2ffa9a93, resgx545:tools/closing/kit/fake/ssh.py at 2ffa9a93, resgx545:tools/closing/scorekit.py at 2ffa9a93, resgx545:tools/closing/sessioncheck.py at 2ffa9a93, data:pds/reg-0a78-timing/output.txt at dc838e60, data:render/closing-s1b/bins/p1139-green.bin at dc838e60, data:render/closing-r29-kreg/fold/posthoc.txt at dc838e60, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 2ffa9a9; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r31-kreg2:out/20261116-145122/s0/", "render-closing-r31-kreg2:out/20261116-145122/k1/", "render-closing-r31-kreg2:fold/"]
terms = ["CR_PDS_REG_0A78"]
+++
**What ran.** Stage s0 (safe, no register write): c0-tri, an exact 64x64 triangle; r1-r8, the
256x256 triangle six renders a job (t10), and v1-v8, the second load (E1125), at the register's
reset value. Stage k1 (flagged, gated on c0-tri and r1-r8): every value 0x00-0x3f once in pass A
(rows aVV, the fit) and once in pass B (rows bVV, held out), each pass its own frozen shuffle;
before every 8 value rows a control writing 0x2c (c01-c16); last c-end, an exact 64x64 triangle
with no write. Frozen before the run, from E1114's failure: a job's reading is the median of
renders 2-6; each 0x2c control within 1 percent of s0's r1-r8 median, at most one control a stage
outside it (named, left out); the in-band controls' interquartile range at most 0.5 percent; a
value fails (a dependence) when both its readings lie more than 1 percent from the controls'
median on the same side.

**Frozen verdict (as printed).** attempt 20261116-145122, stage s0 (score-s0.txt): `SUMMARY: s0:
s0's references draw and time (17 of 17 rows decided)`; stage k1 (score-k1.txt): `SUMMARY: k1:
CR_PDS_REG_0A78 at every value 0x00-0x3f leaves the 256x256 triangle's render time within 1.00
percent of 0x2c's on two shuffled passes (64 of 64 rows decided)`. `score.py q024`: `Q024: NARROW
(decided on k1 only)`. The scores reproduce byte for byte (fold/reproduce.out). 307 jobs in the
session, rc 0, no fault, no hang, no stop; every kreg write read back, 0x0a78 at 0x2c after.

**Results [HW].** s0: every row exact, r1-r8 median 67138 us. k1: every row exact (no wrong
pixel); c01-c16 read -0.61 to +0.10 percent of s0's median, none outside the band (`OUTLIERS:
none`), their interquartile range 0.332 percent of their median 67004.5 us. Per value
(score-k1.txt): 61 values within 1 percent on both passes; 0x11 +0.19 (A) and +1.53 (B), 0x2e
+1.34 (A) and +0.17 (B), 0x15 +1.25 (A) and +0.57 (B). E141's slow values read 0x01 +0.34 and
-0.22, 0x20 +0.24 and +0.11 percent.

**What it shows.** The 256x256 clause of Q024 by a frozen verdict: no value of the register moves
that triangle's render time by more than 1 percent on both passes; E141's 5.5 and 2.6 percent
(0x01, 0x20) were noise, as E396 and E1114's readings suggested. [infer] The rule's two
changes were chosen knowing E1114 (its tests replay E1114 and hold 64 of 64); this run is new
data under that rule, and it did not need the outlier allowance.

**What it does not show.** Nothing below about 1 percent, and nothing about another load (E1125:
the many-small-triangles load could not be read). Not what 0x0a78 does.
