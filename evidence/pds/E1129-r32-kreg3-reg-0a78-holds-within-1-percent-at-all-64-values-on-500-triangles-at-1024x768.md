+++
id = "E1129"
claim = "r32-kreg3 on module 7CE8E38E (Q024), stage kl10, H0 held for all 64 values: CR_PDS_REG_0A78 at each value 0x00-0x3f on two shuffled passes leaves the render time of 500 triangles (t30 probe --tri --vertices 1500, the triangle and 499 copies moved c/16 pixel) at 1024x768, ten renders a job, about 22.07 ms a render, within 1.00 percent of the 0x2c controls: 'CR_PDS_REG_0A78 at every value 0x00-0x3f leaves the render time of 500 triangles (1500 vertices) at 1024x768, 10 renders a job within 1.00 percent of 0x2c's on two shuffled passes (64 of 64 rows decided)'; the farthest value 0x1d at 0.48 percent; at this target each triangle covers about a quarter of the render, so the load is many large overlapping triangles, not small ones"
unit = "pds"
method = "r32-kreg3 (render/closing-r32-kreg3), stages s0, kl10 of the question-closing pass (round 32: Q024's last clause, the many-small-triangles load, by the user's decision of 2026-11-16 (answer a: the question's load as asked, more renders a job, a safe calibration stage with a frozen pick rule); the kit word kreg:0x0a78=V approved by the user in round 29 (as E1114 states), flagged class; records E1128 and E1129 assigned by the lead), dataset render-closing-r32-kreg3; attempt out/20261116-183256 (scores score-kl10.txt, score-s0.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike), stock firmware, tools ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) and ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); every kl10 job the s0 form l10 (`probe --tri pixel --width 1024 --height 768 --vertices 1500` with bins/p1139-green.bin given ten times) after a debugfs reset and a debugfs kreg write of 0x0a78 read back before the job, 0x2c written and read back after it; the 64 values on two passes, each its own frozen shuffle (SEED 20261118 + 1), c01-c16 writing 0x2c and c-end (t10, an exact 64x64 triangle, no write); the rows tables/kl10.txt, the frozen predictions predictions/kl10.tsv; k10, k20, k40, kl20 and kl40 shut by their gates (gate-*.txt)); freezes: FROZEN.sha256 d51040cee70a84faec2e880fa1dd7bf1c124e6bfc2aa08906b8e585be3e09a72 (47 files), PREDICTIONS.sha256 9c28415068af5066431e615a7a51950905ef8dd3ab19ee7dc8913d13e0252f6a (7 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at bf0ba561, resgx545:tools/closing/kit/lib_kit.sh at bf0ba561, resgx545:tools/closing/kit/run_stage.sh at bf0ba561, resgx545:tools/closing/kit/kitscore.py at bf0ba561, resgx545:tools/closing/kit/fake/sudo at bf0ba561, resgx545:tools/closing/kit/fake/timeout at bf0ba561, resgx545:tools/closing/kit/fake/df at bf0ba561, resgx545:tools/closing/kit/fake/modinfo at bf0ba561, resgx545:tools/closing/kit/fake/sha256sum at bf0ba561, resgx545:tools/closing/kit/fake/tool.sh at bf0ba561, resgx545:tools/closing/kit/fake/tool.py at bf0ba561, resgx545:tools/closing/kit/fake/ssh.py at bf0ba561, resgx545:tools/closing/scorekit.py at bf0ba561, resgx545:tools/closing/sessioncheck.py at bf0ba561, data:render/closing-s1b/bins/p1139-green.bin at 6b5c5112, data:render/closing-r31-kreg2/fold/posthoc.txt at 6b5c5112, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main bf0ba56; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r32-kreg3:out/20261116-183256/s0/", "render-closing-r32-kreg3:out/20261116-183256/kl10/", "render-closing-r32-kreg3:fold/"]
terms = ["CR_PDS_REG_0A78"]
+++
**What ran.** Stage kl10 (flagged, gated on s0's pick, E1128): the form s0 picked, `probe --tri
pixel --width 1024 --height 768 --vertices 1500` (t30) with the green pixel program given ten
times, so ten renders a job of the triangle and 499 copies, each moved c/16 pixel. The 64 values
on two passes, each its own frozen shuffle, c01-c16 writing 0x2c before every eight value rows,
and c-end. Frozen (E1124's rules): the reading is the median of renders 2-10; BOUND = max(1.0, 3 x
the spread of s0's l10 references) = 1.000 percent, the controls' band around s0's median 22072.5
us; at most one control outside it allowed; the in-band controls' spread at most BOUND / 2; a value
FAILED when both passes lie more than BOUND from the controls' median on the same side.

**Frozen verdict (as printed).** attempt 20261116-183256, stage kl10 (score-kl10.txt): `SUMMARY:
kl10: CR_PDS_REG_0A78 at every value 0x00-0x3f leaves the render time of 500 triangles (1500
vertices) at 1024x768, 10 renders a job within 1.00 percent of 0x2c's on two shuffled passes (64
of 64 rows decided)`. The score reproduces byte for byte (fold/reproduce.out). `score.py q024
out/20261116-183256` prints `Q024: RETIRE (...)` by its frozen rule.

**Results [HW].** Every row drew the references' image, ten timed renders, no failure; c-end exact;
0x0a78 read back each value and 0x2c after every job. c01-c16 read 21995-22123 us, -0.35 to +0.23
percent of s0's median (no outlier), their spread 0.295 percent of 22040 us. The 128 value rows
read 21976-22146 us, -0.29 to +0.48 percent of the controls' median (IQR 0.36 percent); the
farthest values 0x1d 0.48, 0x05 0.46, 0x04 0.45 and 0x1f 0.43 percent; no reading over 1 percent
on either pass. E141's slow values read 0x01 -0.11 / -0.05 and 0x20 +0.39 / -0.17 percent.

**What it shows.** No value of CR_PDS_REG_0A78 moves this render's time by 1 percent; with E1124
(the 256x256 triangle) neither load timed to a percent depends on it. The load is 500 overlapping
triangles each covering about a quarter of a 1024x768 target [infer, E1128]: many triangles, not
small ones.

**What it does not show.** Whether many small triangles (the 64x64 load, about 0.73 ms a render)
depend on the register by less than its noise of a few percent (E1125, E1128); what the register
controls.
