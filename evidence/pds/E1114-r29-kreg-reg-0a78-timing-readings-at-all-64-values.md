+++
id = "E1114"
claim = "r29-kreg on module E0CC4027 (Q024), readings only, no verdict: CR_PDS_REG_0A78 written to each of its 64 values 0x00-0x3f on two shuffled passes before a 256x256 triangle job of six renders; the mean of renders 2-6 of 62 values lies within 1 percent of the sixteen 0x2c controls' median (67162 us) on both passes (-0.60 to +0.97 percent), 0x23 read +4.77 percent on pass A only and 0x39 +2.26 percent on pass B only, each from one slow render (82956 and 74235 us), so no value lies outside 1 percent on both passes; the frozen score is 'controls FAILED: c11: FAILED' because control c11 (0x2c) read 69190 us, +3.02 percent of s0's references (67164 us), from two slow renders (71090 and 74071 us) in one job, with the register read back at 0x2c before it and its neighbours c10 and c12 at -0.07 and -0.54 percent"
unit = "pds"
method = "r29-kreg (render/closing-r29-kreg), stages s0, k1 of the question-closing pass (round 29: closing29/kreg/design.md section 5, the kit word kreg:OFF=V of resgx545 adca992, flagged class, approved by the user in round 29 as relayed by the lead; k2 dropped: no timed many-triangle form in t10), dataset render-closing-r29-kreg; attempt out/20261116-061842 (scores score-k1.txt, score-s0.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06), every timed job `tri --width 256 --height 256 -n 6` after a debugfs reset and, in k1, a debugfs kreg write of 0x0a78 read back before the job and 0x2c written and read back after it (144 writes, all read back); the rows tables/s0.txt and tables/k1.txt (gen/gen.py SEED 20261116), the frozen predictions predictions/s0.tsv and k1.tsv); freezes: FROZEN.sha256 76930559001d391846c69f46f71786e30e4a47b3a9ab16353d06f630980fc59b (33 files), PREDICTIONS.sha256 d38cddae1823d022bb571484b7a29a945ca2f4d3bedfbcdf6841914d724840ea (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at adca9929, resgx545:tools/closing/kit/lib_kit.sh at adca9929, resgx545:tools/closing/kit/run_stage.sh at adca9929, resgx545:tools/closing/kit/kitscore.py at adca9929, resgx545:tools/closing/kit/fake/sudo at adca9929, resgx545:tools/closing/kit/fake/timeout at adca9929, resgx545:tools/closing/kit/fake/df at adca9929, resgx545:tools/closing/kit/fake/modinfo at adca9929, resgx545:tools/closing/kit/fake/sha256sum at adca9929, resgx545:tools/closing/kit/fake/tool.sh at adca9929, resgx545:tools/closing/kit/fake/tool.py at adca9929, resgx545:tools/closing/kit/fake/ssh.py at adca9929, resgx545:tools/closing/scorekit.py at adca9929, resgx545:tools/closing/sessioncheck.py at adca9929, data:pds/reg-0a78-timing/output.txt at 73e058d5, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; pinned commits named by the session: resgx545 main adca992; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r29-kreg:out/20261116-061842/s0/", "render-closing-r29-kreg:out/20261116-061842/k1/", "render-closing-r29-kreg:fold/"]
terms = ["CR_PDS_REG_0A78"]
+++
**What ran.** Stage s0 (safe, no register write): c0-tri, an exact 64x64 triangle, and r1-r8, the
256x256 triangle six renders a job at the register's reset value (the preflight read 0x2c).
Stage k1 (flagged, gated on s0): every value 0x00-0x3f once in pass A (rows aVV, the fit) and
once in pass B (rows bVV, held out), each pass its own frozen shuffle; before every 8 value rows
a control writing 0x2c (c01-c16); last c-end, an exact 64x64 triangle with no write. A job's
reading is the mean of renders 2-6 (E141, E396). Frozen: a value fails (a dependence) when both
its readings lie more than 1 percent from the controls' median on the same side; each 0x2c
control within 1 percent of s0's references' median; the controls' interquartile range at most
0.5 percent. The second load of the design (many small triangles) was not run: t10 has no timed
form for it.

**Frozen verdict (as printed).** attempt 20261116-061842, stage s0 (score-s0.txt): `SUMMARY: s0:
s0's references draw exactly (9 of 9 rows decided)`; stage k1 (score-k1.txt): `SUMMARY: k1:
controls FAILED: c11: FAILED`. No verdict on the values. The scores reproduce byte for byte
(fold/reproduce.out). 154 jobs, rc 0, no fault, no hang, no stop; every kreg write read back.

**Results [HW].** s0: every row exact; references r1-r8 median 67164 us. k1: every row exact
(no wrong pixel); the 0x2c controls c01-c10 and c12-c16 read -0.54 to +0.37 percent of s0's
median, with no trend over the run, and c11 +3.02 percent (renders 70807 71090 74071 67271 66885
66636 us); the controls' interquartile range 0.30 percent of their median 67162 us. Per value
(fold/k1-values.txt, the controls' median as reference): 62 values within 1 percent on both
passes, the farthest 0x04 +0.97 (pass A) and 0x20 -0.60 (pass A); 0x23 +4.77 (A) and +0.02 (B),
its pass A render 6 at 82956 us; 0x39 +0.31 (A) and +2.26 (B), its pass B render 6 at 74235 us.
Four of the 720 renders 2-6 ran more than 5 percent slow (c11 render 3, a23 render 6, b39
render 6, a04 render 2), on three values and one 0x2c control.

**What it shows.** [infer, post hoc, after the run] c11's failure is a one-job spike of two
renders, not drift (c10 and c12 sit at the other controls' level, no trend over the 16) and not a
value written before it lingering (the runner and the kernel read 0x0a78 at 0x2c before c11's
job; b11 before it wrote 0x11 and read -0.13 percent itself): the kind of slow render E396 saw
once (a 0x01 run with renders of 73110 and 74396 us). The same spikes explain 0x23's and 0x39's
one-pass readings. Read by the median of renders 2-6 in place of the mean (fold/posthoc.py, not
the frozen rule), every value lies within 0.82 percent of the controls on both passes.

**What it does not show.** No frozen verdict: the frozen control rule failed, so these are
readings. Nothing about a load with many small triangles (not run). Nothing below about 1
percent: the bound was 1 percent and a render's own noise is about 0.3 percent.
