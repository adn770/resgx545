+++
id = "E1149"
claim = "r37-n3b-a stage own (N3b step A, module 77917296, fork 4f35fc20ffa9, image v1, flagged, user present): our EDM task emitsb, E1148's emitsa with two breadcrumbs, ran the same emitpds form with the same kernel PDS image on its one command; entry 0 stored X0 0x5a5a3303 right after the emitpds, entry 1 stored nothing, not even S1, its first store (S1, M4 and slots 2-4 kept the host's fill, state 0), and the EDM's tick stopped 10 ticks after the command write with no BIF fault: every control passed, 'N3b-A RULE: A-PAST: issuer on; no entry-1 store: (1), (2) or early (3)'; the kit's reset recovered it (fill and triangle exact)"
unit = "edm"
method = "r37-n3b-a (render/closing-r37-n3b-a), stage own of the question-closing pass (round 37: step A of closing29/n3b/design.md, N3b, the breadcrumbs that split E1148's causes, the user's flagged decision; flagged class, the user present with a reset ready), dataset render-closing-r37-n3b-a; on the laptop at home (kernel 7.3.0-resgx545, module srcversion 77917296568EB311B89B0DA installed and loaded alike, linux fork r37-kernel 4f35fc20ffa9, built and booted once for N3b (closing29/kernel37/deliver/4f35fc20ffa9/manifest); stock firmware), the kit's owntask job kind (kit/ = resgx545 7925c98, its fwtask_run.py byte for byte): our task owntask/emitsb.blob (asm/fwtask/emitsb.s, sha256 83c25ac3cfc0a87473649979a41b8ddd0b49441d52a8eb9a7f405bb2866d7c2c as asm/fwtask/fwtask.map at 7925c98 gives) armed once with own_arm `slots=0x1 entry=0` (no pds= word: the module's v1 image, the one E1148 ran) after the stage's reset and health pair, then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on: HostCtl dword 12 from right before the command write to 30 ms after the window; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the runner's stop dump kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 3bfd8a63f38191131e40e47dcd4c3d0b4ac4a110f3c13e499091d479f645a71a (48 files), PREDICTIONS.sha256 e8bb18d7b6532ed774695960d3fe4c9e73aad05bb55d9ec97d3858255d5fff96 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb.s and fwtask.map at 7925c98; r35-sa's kept snap0 and E1148's kept snapshots at data fb461acf; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by hand on the kept directory (fold/reproduce-own.out: the stage stopped at its one row, rc 4, so the driver did not score it); three attempts kept: out/20261118-212839 (the driver's verify refused the session before staging, a lead log at its top; nothing reached the laptop), out/20261118-212845 (void: stage own exited 13 at the stage's first debugfs reset, `No such device`, the firmware not yet loaded after the boot; no arm, no row, nothing armed; no reading of it is used) and out/20261118-212949 (the lead attempt, 21:29:50); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; stage post (the t30 triangle and fill) did not run"
tiers = ["HW"]
date = "2026-11-18"
data = ["render-closing-r37-n3b-a:out/20261118-212949/own/", "render-closing-r37-n3b-a:out/20261118-212845/own/", "render-closing-r37-n3b-a:fold/"]
terms = []
+++
**What ran.** The kernel armed our task emitsb on slot 0 (the general task the tick runs) with
E1148's `emitpds` form and image: the control word 0x01000100, the image's address >> 4 and 0;
the v1 image `douta` V0 to attribute 0, `douta` V2 to attribute 2, `doutu` the blob's entry 1,
`halt`. The arm logged `emit image 0x30022000 ... pds=v1` and was healthy (ticks advancing at
995 Hz, GETMISCINFO matched, no bad kernel line). emitsb is emitsa (E1148) with two stores, each
followed by a fence: **X0** 0x5a5a3303 at page dword 70 right after the `emitpds`, before the tail
call to the closed task, and **S1** 0x5a5a3304 at page dword 84 as entry 1's first work, before
its `pa` and `sa` reads. On command 1, entry 0 stores the marker 0x5a5a3301 and the run id, clears
the command, fences, emits, stores X0 and tail-calls the closed task; entry 1 stores S1, pa0-pa3,
sa0-sa3, the marker 0x5a5a3302 (M4) and the run id, then state 2. One row, as frozen: any stop
ends the session.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
N3b-A RULE: A-PAST: issuer on; no entry-1 store: (1), (2) or early (3)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 10 from the command write to 30 ms after the window (237.1 ms)
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 5; snap9: bit 16 1, count - tick 5; stop0-regs: bit 16 1, count - tick 5
```

**Results [HW].**

- Controls: PG (page dword 0 = 0x4e574f53), E0 (slot 1 = 0x5a5a3301 and run id 1, cmd 0), T0
  (snap0's 0x0acc 0x010295f9, running) and B (BIF_FAULT 0 in snap9) all passed.
- c1-a: no done within 200 ms (`fwtask_run.py run` rc 1, `firmware hung: the tick stopped`), the
  kit classed the job `hang` and stopped the stage (rc 4).
- The page: X0 = 0x5a5a3303; S1 (dword 84), M4 (dwords 80-81) and slots 2-4 all 0xdeadc0de (the
  host's fill); state 0, echo 0.
- The tick: Δtick 10 over a 237.1 ms window (the record's `ticks`). HostCtl dword 12 read 0x7a2
  at snap0 and 0x9b9 in the stop dump and in snap9; the runner's three reads at the stop were
  2489 each, `USE0_SERV_EVENT`'s count 68030 each. `CR_CLKGATESTATUS` read 0x20 at snap0 and
  0x000ccfa0 after the stop; 0x0acc still counted (0x01038295 in the stop dump, 0x01017336 in
  snap9, bit 24 set). BIF_INT_STAT 0x00080000 and BIF_FAULT 0 in every read; no fault line.
- The kit's reset after the stop and its health pair: t30 fill `diff: 0 of 2048` and triangle
  `diff: 0 of 4096`, exact.
- `USE0_SERV_EVENT` bit 16 was set at snap0 (0x000107a7), before the command, and after the stop
  (0x000109be); its count minus HostCtl dword 12 was 5 in all three reads. E1148 read the same
  bit set at its snap0 (0x0001079c) and r37-n3b-b (E1150) too, so bit 16 does not mark these
  stops; the SIGNATURE line is printed, not scored, as frozen.

**What it shows.** E1148 reproduced with breadcrumbs, one job: the issuing EDM task went on past
its `emitpds` (X0), and the task the emitted image was to start never made its first store (S1),
while the EDM's tick stopped within 10 ticks of the command write without a BIF fault; the kit's
reset brought the firmware back to exact draws. So the emit neither stops nor ends the task that
issues it (A-ISSUER refuted), and E1148's job did not end with entry 1 stopping after a store
(A-E1 refuted).

**What it does not show.** Which of E1148's causes holds: (1) the emitted program never ran, (2)
it ran and its `doutu` did not start our task, or (3) entry 1 started and died within its first
three instructions (two `mov` and the S1 store); that is step B's (E1150). What stopped the tick,
and when within its 10 ticks the closed task's tail ran: the stop is dated against the command
write only. Where an emitted `douta` lands. Why bit 16 reads set here where the stops of hw_spec's
list read it clear (that list's stops are a different kind [infer]).
