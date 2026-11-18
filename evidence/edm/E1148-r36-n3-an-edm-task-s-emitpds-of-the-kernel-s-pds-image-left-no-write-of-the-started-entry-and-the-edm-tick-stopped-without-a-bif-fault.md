+++
id = "E1148"
claim = "r36-n3 stage own (module C01FB320, fork c78059370315, flagged, user present): our EDM task emitsa, armed on slot 0, ran the one allowed emitpds form (the firmware's `.tasks.taske` word, the kernel's control word 0x01000100, image address >> 4 and 0) on its first tester command and its entry 1, which the kernel's PDS image starts with doutu, left no write within 200 ms (slots 2-4 kept the host's fill, state 0): 'N3 RULE: NONE: entry 1 never ran after the emit (e1-a): the landing stays open', 'Q128 RULE: NARROW'; post hoc, the EDM's tick had stopped by the end of the window with no BIF fault, and the kit's reset recovered it (fill and triangle exact); where an emitted douta lands stays open"
unit = "edm"
method = "r36-n3 (render/closing-r36-n3), stage own of the question-closing pass (round 36: N3 of closing29/kernel33/design.md, the own-task emitpds form the user allowed on 2026-11-16, and the N3 row of closing29/plan/rank-round34.md; flagged class, the user present with a reset ready), dataset render-closing-r36-n3; attempt out/20261118-152130; on the laptop at home (kernel 7.3.0-resgx545, module srcversion C01FB3203FDA4FEF01E4891 installed and loaded alike, linux fork c78059370315; stock firmware), the kit's owntask job kind (kit/ = resgx545 b9098a4, its fwtask_run.py byte for byte): our task owntask/emitsa.blob (asm/fwtask/emitsa.s, sha256 3dc8152d846cc7a100cc2224e28d2ad83c71fd978206aac82f7b1486940579e1 as asm/fwtask/fwtask.map at b9098a4 gives) armed once with own_arm `slots=0x1 entry=0` after the stage's reset and health pair, then rows of one tester command 1 each (`fwtask_run.py run`, timeout 200 ms, the host first writing 0xdeadc0de into result slots 2-4), the results page and registers kept per row; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7) for the kit's health pair and the own-task gate; freezes: FROZEN.sha256 0f03a0c64d4ee1af7a9d2d2e4bd5abb7a790a8d26b9d6a68576b3a1e35898f12 (46 files), PREDICTIONS.sha256 d19941a28d43d6513f7874018822b7f985bc70ba3a0e3af990e7c4c2b826bd2a (2 files), pins in FROZEN.commits (the kit at b9098a4, asm/fwtask/emitsa.s and fwtask.map at b9098a4, r35-sa's kept snap0 at data 6b293844, t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py; the stage stopped at its first row e1-a (runner rc 1, stage rc 4), so the driver did not score it and the frozen scorer was run by hand on the kept directory (fold/reproduce-own.out); post hoc reading fold/posthoc.py (fold/posthoc.out), not frozen; stage post (the t30 triangle and fill) did not run"
tiers = ["HW"]
date = "2026-11-18"
data = ["render-closing-r36-n3:out/20261118-152130/own/", "render-closing-r36-n3:fold/"]
terms = []
+++
**What ran.** The kernel armed our task emitsa on slot 0 (the general task the tick runs) with the
one `emitpds` form of the round-33 design: at the arm it patched the task's `pds0`-`pds2` limms
with the control word 0x01000100 (2 data rows, addend 0x100), the image's address >> 4 and 0, and
built its PDS image (`douta` V0 to attribute 0, `douta` V2 to attribute 2, `doutu` the blob's entry
1 on our code page, `halt`; V0, V2 = TA3DCtl dwords 0 and 2, the values sa0 and sa2 hold, E002).
The arm logged `emit image 0x30022000` and was healthy (ticks advancing at 996 Hz, GETMISCINFO
matched, no bad kernel line). On command 1, entry 0 stores a marker 0x5a5a3301 and the run id in
result slot 1, clears the command, fences, runs the `emitpds`, then tail-calls the closed task;
entry 1 stores pa0-pa3 in slot 2, sa0-sa3 in slot 3, a marker 0x5a5a3302 and the run id in slot
4, then state 2. Ten rows were planned (2 exploration, 8 held out), then the t30 triangle and
fill after the disarm. The first row, e1-a, ended the session.

**Frozen verdict (as printed).** By hand on the kept directory (the driver scores a stage only
when it ends 0 or 24):

```
SUMMARY: own: H-PA: controls FAILED: e1-a:E1: FAILED; e1-a:SA: cannot tell; e1-a:PA13: cannot tell
SUMMARY: own: H-SA: controls FAILED: e1-a:E1: FAILED; e1-a:SA: cannot tell; e1-a:PA13: cannot tell
SUMMARY: own: H-NONE: H-NONE on the kept rows (1 of 1 rows decided)
N3 RULE: NONE: entry 1 never ran after the emit (e1-a): the landing stays open
Q128 RULE: NARROW (the firmware's emitpds form from an EDM task, our image: NONE); never RETIRE from this session
```

**Results [HW].**

- e1-a: no done within 200 ms (`fwtask_run.py run`: rc 1, the stop dump kept); the kit classed
  the job `fail` and stopped the stage (rc 4).
- The results page after it: slot 1 = 0x5a5a3301 and run id 1, cmd 0 (entry 0 ran this command
  past its command clear); slots 2, 3 and 4 all 0xdeadc0de (the host's fill), state 0, echo 0:
  entry 1 wrote nothing.
- Post hoc (fold/posthoc.out, not frozen): the EDM's tick (HostCtl dword 12) read 1943 right
  before the job and 2467 both in the stop dump after the 200 ms window and in the registers about
  0.3 s later (kernel log 4528.52 s for the run's start, 4529.02 s for the last read);
  USE0_SERV_EVENT stayed at 0x000109a8 between the two reads. BIF_INT_STAT 0x00080000, BIF_FAULT 0
  and no BIF fault counted in every read; no fault, hang or recovery line in the kernel log.
- The kit's reset after the stop and its health pair: t30 fill `diff: 0 of 2048` and triangle
  `diff: 0 of 4096`, exact.
- A kit message after the arm, `lib_kit.sh: line 78: !v: unbound variable`, comes from the runner
  looking up a tool path for the tool `owntask`, which has none; owntask rows never use it, and
  nothing kept changed (harmless; the kit is to be fixed).

**What it shows.** With the firmware's `emitpds` form from an EDM task of ours and the kernel's
PDS image, the started task's entry 1 left no write within 200 ms, and the EDM stopped ticking
within that window without a BIF fault [the stop: post hoc]; the kit's debugfs reset brought the
firmware back to exact draws. One job: the session ended on it, as frozen.

**What it does not show.** Whether the emitted PDS program ran at all, or ran and its `doutu` did
not start our task (the design's [infer] U1 = U2 = 0 and U0's TRC 8 and code index), or started
it and entry 1 stopped before its first store; whether the tick stopped because of the `emitpds`
or later in the closed task's tail [infer: after the emit, since entry 0 had cleared the command];
where an emitted `douta` lands (pa or sa: the question of fwsim's M2 kick, E1133). The kit read no
tick after the stop (an owntask stop is classed `fail`, never `hang`), so the stop's time within
the window is not measured.
