+++
id = "E1155"
claim = "r39-n3d-k stage own (N3d K, module 88ADCEB5, fork e1cf9d2b43ab, emitsk, image crumb3 at fw14, flagged, user present): our EDM task emitsk emitted our old word (sideband 0, s2 0) only on the pass of a host GETMISCINFO kick, with R4's crumb3 image in the firmware's PDS #14 page; every control passed (PG, K0: no tick pass emitted, K1, T0, B) and no frozen outcome held, 'N3d-K RULE: CANNOT TELL (no frozen outcome holds)': X0 0x5a5a3303, T (0x0acc) running, S1, M4 and state the host's fill and 0, as K-NEVER, but the tick stopped 7 ticks from the kick, outside K-NEVER's frozen band 8-11; the kit's reset recovered it (fill and triangle exact)"
unit = "edm"
method = "r39-n3d-k (render/closing-r39-n3d-k), stage own of the question-closing pass (round 39: session S1 of closing29/n3d/design.md, N3d, row K, the kick-pass emit, the user's flagged decision; flagged class, the user present with a reset ready), dataset render-closing-r39-n3d-k; attempt out/20261119-152848 (15:28:48; stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 88ADCEB5AD9F055D077A99C installed and loaded alike, linux fork r38-kernel e1cf9d2b43ab (closing29/kernel38/deliver/e1cf9d2b43ab/manifest; series KUnit all pass), the boot that ran r38-n3c-s4 and r38-n3c-s3 (E1153, E1154), no rebuild; stock firmware), the kit's owntask job kind (kit/ = resgx545 70e30d38, its fwtask_run.py byte for byte, with the runner's `kick` step): our task owntask/emitsk.blob (asm/fwtask/emitsk.s, sha256 75fb66a60316e7e33ce87a68f711ffa6cc78f22991b881c40d5baf252b1b2647, asm/fwtask/fwtask.map at 70e30d38) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14` after the stage's reset and health pair (the arm's log: `own_code: 684 bytes accepted`, `emit image 0x30011100 ... pds=crumb3 pdsat=fw14`), then one row c1-a of tester command 1 (`fwtask_run.py run`, `\"kick\": \"miscinfo\"`, timeout 200 ms counted from the kick, `ticks` on; the host first writing 0xdeadc0de into result slots 2-5; the record K0 read right after the command write, then one debugfs `miscinfo` read, a GETMISCINFO kick), the results page, the registers (snap0, snap9) and the runner's stop dump kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 a2c69390a8a710c87c31b9a8c48f5f1011940ce5d636eb6be7a8030da1096021 (48 files), PREDICTIONS.sha256 9bfbe96e3f91e138c7ee4398b55dc5f28388109c72824f8ef43867fbb89e3a9d (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsk.s and fwtask.map at 70e30d38; r35-sa's kept snap0 and E1148's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by hand on the kept directory (fold/reproduce-own.out: the stage stopped at its one row, rc 4, so the driver did not score it); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; the design's precondition O2d (0 emits in the firmware's own GETMISCINFO kick pass) is a fact of the data-private fwsim read, cited by the session's README"
tiers = ["HW", "infer"]
date = "2026-11-19"
data = ["render-closing-r39-n3d-k:out/20261119-152848/own/", "render-closing-r39-n3d-k:fold/"]
terms = []
+++
**What ran.** E1154's job (r38-n3c-s3, M-NEVER) with one change: the pass that issues the emit.
emitsk (asm/fwtask/emitsk.s) is emitsb with a gate in entry 0: on command 1 it reads `pa1` and
takes the emit path only when bit 8 is set, the bit a host GETMISCINFO kick sets on slot 0's pass
(E746); every other pass tail-calls the closed task with the command left at 1. On the kick pass
it stores M1 0x5a5a3301 and the run id in slot 1, clears the command, fences, emits our word
0xfb20b00000008184 (`emitpds.tasks.taske #0, r2, r3, r4, #0x0`: sideband 0, `s2` 0, ours since
round 33), stores **X0** 0x5a5a3303 at page dword 70 and tail-calls; its entry 1 (**S1**
0x5a5a3304 at dword 84, pa0-pa3, sa0-sa3, **M4** 0x5a5a3302 and the run id at dwords 80-81,
state 2) starts only if the emitted program's `doutu` names it. The arm and the image are E1154's
word for word: crumb3 (3 data rows, control word 0x01800100) at 0x30011100, offset 0x100 of the
firmware's PDS #14 page. The row wrote command 1, read K0 6.9 ms later (cmd 1, slot 1 the fill,
HostCtl dword 12 at 2108), then read debugfs `miscinfo` once (`GETMISCINFO answered after 203
us`, printed, not scored) and polled.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14
N3d-K RULE: CANNOT TELL (no frozen outcome holds)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 7 from the kick (K0) to 30 ms after the window; 15 from the command write (248.1 ms); 8 between the command write and K0
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 6; snap9: bit 16 1, count - tick 6; stop0-regs: bit 16 1, count - tick 6
```

**Results [HW].**

- Controls: PG (page dword 0 = 0x4e574f53), K0 (cmd 1 and slot 1 the fill at the kick: no tick
  pass emitted), K1 (slot 1 = M1 and run id 1, cmd 0: the gate fired), T0 (snap0's 0x0acc
  0x0105e396, running) and B (BIF_FAULT 0 in snap9) all passed.
- c1-a: no done within 200 ms (`fwtask_run.py run` rc 1, `firmware hung: the tick stopped`), the
  kit classed the job `hang` and stopped the stage (rc 4).
- The page: X0 = 0x5a5a3303; S1, M4 and slots 2-4 all 0xdeadc0de; state 0, echo 0.
- T = 0x0acc after the stop: 0x0101ecfd in snap9 and 0x0100b3fe in the stop dump, bit 24 set,
  bits 23:0 at most 400000, the two reads different: counting, none of crumb3's markers.
- The tick: Δtick 7 from the kick (K0's 2108 to 2115), 15 from the command write, over a 248.1 ms
  window; `alive_at_stop` false: the tick 2115 and `USE0_SERV_EVENT`'s count 67657 in each of the
  runner's three reads at the stop.
- BIF_FAULT 0 in every read; the kit's reset and its health pair after the stop: t30 triangle
  `diff: 0 of 4096` and fill `diff: 0 of 2048`, exact.

**The score.** K-NEVER's frozen row asks T running, S1 and M4 the fill, state 0 and Δtick from
the kick 8-11 (the design's §3 common table: R4's 9-11 from the command write, carried to the
kick). Every reading but the last matched; Δtick from the kick was 7. No outcome holds, so the
pre-declared score is **CANNOT TELL**, and that is this record's verdict.

**Informal reading [infer, post hoc, not scored].** Read without the band, the row is K-NEVER's:
with our word and `s2` 0, an emit issued from a GETMISCINFO kick pass did not start the program
either (T running, entry 1 never stored) and the tick stopped soon after, as after a tick-pass
emit (E1149, E1150, E1154). The band had been carried from tick-pass emits, timed from a command
write, to a kick-pass emit timed from the kick; nothing measured said what a kick-pass NEVER reads.

**What came of it.** Row Z (r39-n3d-z, E1156) had been frozen as conditional on K-NEVER. At the
user's choice, Z was refrozen before it ran without the tick band (its NEVER reads T and S1
alone, Δtick printed): its README, "When", and the closing plan's log. K stays CANNOT TELL.

**What it does not show.** That the kick pass alone cannot start an emitted program (the score is
CANNOT TELL; the reading above is informal); what stopped the tick; whether the PDS fetched the
image; one job only.
