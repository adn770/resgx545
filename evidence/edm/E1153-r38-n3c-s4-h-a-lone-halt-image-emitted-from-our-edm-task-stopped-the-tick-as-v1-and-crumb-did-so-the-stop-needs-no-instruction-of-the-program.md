+++
id = "E1153"
claim = "r38-n3c-s4 stage own (N3c R5 H, module 88ADCEB5, fork e1cf9d2b43ab, image halt, flagged, user present): our EDM task emitsb emitted E1149's form with the halt image, v1's two data rows and a lone halt (no douta, no doutu, no tim), control 0x01000100, in the kernel's own image page at 0x30022000; X0 0x5a5a3303 was written, S1, M4 and slots 2-4 kept the host's fill, state 0, and the EDM's tick stopped 9 ticks after the command write (alive false, the tick and USE0_SERV_EVENT's count frozen in the runner's three reads) with no BIF fault: every control passed, 'N3c-H RULE: H-STOP: any program stops the EDM, no instruction needed'; the kit's reset recovered it (fill and triangle exact)"
unit = "edm"
method = "r38-n3c-s4 (render/closing-r38-n3c-s4), stage own of the question-closing pass (round 38: session S4 of closing29/n3c/design.md, N3c, row R5 H, the program floor; flagged class, the user present with a reset ready), dataset render-closing-r38-n3c-s4; attempt out/20261119-112618 (11:26:18; stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 88ADCEB5AD9F055D077A99C installed and loaded alike, linux fork r38-kernel e1cf9d2b43ab (closing29/kernel38/deliver/e1cf9d2b43ab/manifest; series KUnit all pass), built for N3c and booted once on 2026-11-19, this the first session on that boot, r38-n3c-s3 (E1154) the second; stock firmware), the kit's owntask job kind (kit/ = resgx545 94a7de5, its fwtask_run.py byte for byte): our task owntask/emitsb.blob (asm/fwtask/emitsb.s, sha256 83c25ac3cfc0a87473649979a41b8ddd0b49441d52a8eb9a7f405bb2866d7c2c as asm/fwtask/fwtask.map at 94a7de5 gives) armed once with own_arm `slots=0x1 entry=0 pds=halt` after the stage's reset and health pair (the arm's log: `emit image 0x30022000 ... pds=halt pdsat=own`), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the runner's stop dump kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 3e4d4959297eda241593ed2d40ee9be3041062a83d72c0fdc0e9dd498f607211 (48 files), PREDICTIONS.sha256 4b5b38212f3136213be1d65f34e5db44799111e3ab199692cb49be926ee0260a (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb.s and fwtask.map at 94a7de5; r35-sa's kept snap0 and E1148's kept snapshots at data 5fa30750; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by hand on the kept directory (fold/reproduce-own.out: the stage stopped at its one row, rc 4, so the driver did not score it); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; stage post (the t30 triangle and fill) did not run: a halt job cannot report done, so its row ends in a runner stop by design"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r38-n3c-s4:out/20261119-112618/own/", "render-closing-r38-n3c-s4:fold/"]
terms = []
+++
**What ran.** E1149's job, word for word, with one change at the arm: `pds=halt`. The kernel
built the halt image (asm/fwtask/pds/halt.s) instead of v1: v1's 8 data dwords (2 rows, the same
U0, V0 and V2 fills) and then the one instruction `halt`; no `douta`, no `doutu` and no `movs
tim`. The control word was 0x01000100, v1's, and the image sat in the kernel's own read-only image
page at 0x30022000, as in E1148-E1150 (`pdsat=own`). emitsb's entry 0 stores the marker
0x5a5a3301 and the run id, clears the command, fences, emits, stores **X0** 0x5a5a3303 at page
dword 70 and tail-calls the closed task; its entry 1 (**S1** 0x5a5a3304 at dword 84 first) cannot
start, since no `doutu` names it. The arm logged `own_code: 644 bytes accepted` and `emit image
0x30022000 ... pds=halt pdsat=own`, `own_arm` read `... pds=halt pdsat=own blob=644`, and the
arm was healthy (ticks 198, 228, 255, at 962 Hz). One row, as frozen: any stop ends the session.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30022000 pds=halt pdsat=own
N3c-H RULE: H-STOP: any program stops the EDM, no instruction needed
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 9 from the command write to 30 ms after the window (237.4 ms)
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 5; snap9: bit 16 1, count - tick 5; stop0-regs: bit 16 1, count - tick 5
```

**Results [HW].**

- Controls: PG (page dword 0 = 0x4e574f53), E0 (slot 1 = 0x5a5a3301 and run id 1, cmd 0), T0
  (snap0's 0x0acc 0x0100c93b, running) and B (BIF_FAULT 0 in snap9) all passed.
- c1-a: no done within 200 ms (`fwtask_run.py run` rc 1, `firmware hung: the tick stopped`), the
  kit classed the job `hang` and stopped the stage (rc 4).
- The page: X0 = 0x5a5a3303; S1, M4 and slots 2-4 all 0xdeadc0de; state 0, echo 0.
- The tick: Δtick 9 over a 237.4 ms window (9-11 frozen for H-STOP; E1149 and E1150 counted 10);
  `alive_at_stop` false: the tick 2554 and `USE0_SERV_EVENT`'s count 68095 in each of the runner's
  three reads at the stop.
- 0x0acc 0x01059309 in snap9 and 0x0104a155 in the stop dump, bit 24 set and counting: the halt
  image writes no `tim`, so this is no reading of the program.
- BIF_FAULT 0 in every read; the kit's reset and its health pair after the stop: t30 triangle
  `diff: 0 of 4096` and fill `diff: 0 of 2048`, exact.

**What it shows.** With a program of no instruction but `halt`, the emit from our task stops the
EDM's tick as v1's (E1148, E1149) and crumb's (E1150) did, within the same 9-10 ticks, with the
issuer going on past the emit. So the stop needs no instruction of the emitted program: neither a
`douta`, nor a `doutu`, nor a `tim` write is what stops the tick (H-ALIVE refuted). With E1151
(the same task without the emit runs to done), the stop is in the emit itself or in what the PDS
does before or instead of the program's first instruction.

**What it does not show.** Whether the PDS fetched or started the halt image at all (`halt`
leaves no mark); whether the program's page, its flags, the rows or the control word matter
(E1154 answers that for #14's page, rows and control word); whether the `s2` operand or the pass
our task issues from (a timer pass, where the firmware emits from its kick pass) is the cause;
one job only.
