+++
id = "E1150"
claim = "r37-n3b-b stage own (N3b step B, module 77917296, fork 4f35fc20ffa9, image crumb, flagged, user present): with the crumb image, E1148's image whose first instruction is a movs tim of a stopped 0 and which marks its douta and doutu passes the same way, our task emitsb's one job wrote X0 0x5a5a3303 past the emitpds, entry 1 stored nothing (S1, M4, state 0), the EDM's tick stopped 10 ticks after the command write with no BIF fault, and CR_EVENT_TIMER (0x0acc) still counted after the stop (0x0101fc6d, then 0x010585dc, bit 24 set): every control passed, 'N3b-B RULE: B-1: (1) the program never ran'; that reading rests on the inference that a movs tim from an emitted program writes the 0x0acc the host reads (measured only from a client fill's PDS program); the kit's reset recovered it (fill and triangle exact)"
unit = "edm"
method = "r37-n3b-b (render/closing-r37-n3b-b), stage own of the question-closing pass (round 37: step B of closing29/n3b/design.md, N3b, the crumb image the user approved with its planned stop of the tick; flagged class, the user present with a reset ready), dataset render-closing-r37-n3b-b; attempt out/20261118-213042 (21:30:42), the same boot as r37-n3b-a (E1149); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 77917296568EB311B89B0DA installed and loaded alike, linux fork r37-kernel 4f35fc20ffa9 (closing29/kernel37/deliver/4f35fc20ffa9/manifest); stock firmware), the kit's owntask job kind (kit/ = resgx545 7925c98, its fwtask_run.py byte for byte): our task owntask/emitsb.blob (asm/fwtask/emitsb.s, sha256 83c25ac3cfc0a87473649979a41b8ddd0b49441d52a8eb9a7f405bb2866d7c2c as asm/fwtask/fwtask.map at 7925c98 gives) armed once with own_arm `slots=0x1 entry=0 pds=crumb` after the stage's reset and health pair, then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the runner's stop dump kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 fc17ff5dd491b0adee10359bd69fe08d3935072c129830f97afe6a212148bedc (48 files), PREDICTIONS.sha256 e6310494e31087184ab286c73f52a3a6bac92d1dc10aaab42f294cfeccec8008 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb.s and fwtask.map at 7925c98; r35-sa's kept snap0 and E1148's kept snapshots at data fb461acf; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by hand on the kept directory (fold/reproduce-own.out: the stage stopped at its one row, rc 4, so the driver did not score it); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; stage post (the t30 triangle and fill) did not run"
tiers = ["HW"]
date = "2026-11-18"
data = ["render-closing-r37-n3b-b:out/20261118-213042/own/", "render-closing-r37-n3b-b:fold/"]
terms = []
+++
**What ran.** As E1149 (the task emitsb, its X0 and S1 breadcrumbs, one row of command 1), with
the arm's `pds=crumb`: the kernel built the crumb image instead of v1, with v1's two data rows,
control word 0x01000100, address rule and U0/V0/V2 fills, data dword 7 = 0x005a3305, and the
program (asm/fwtask/pds/crumb.s)

```
movs tim,   ds1[1], ds1[1], ds1[1], ds1[1]   ; T1: tim <- 0x000      (the program started)
movs douta, ds0[2], ds1[1], ds0[2], ds0[2]   ; V0 to attribute 0     (as v1)
movs douta, ds0[3], ds1[2], ds0[3], ds0[3]   ; V2 to attribute 2     (as v1)
movs tim,   ds1[2], ds1[2], ds1[2], ds1[2]   ; T2: tim <- 0x200      (past both douta)
movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]   ; start entry 1         (as v1)
movs tim,   ds1[3], ds1[3], ds1[3], ds1[3]   ; T3: tim <- 0x005a3305 (past the doutu)
halt
```

Each marker has bit 24 clear, so a `movs tim` that runs leaves the counter stopped at it until a
reset (doc/isa/content/pds/probe/inputs.md). The arm logged `emit image 0x30022000 ... pds=crumb`,
`own_arm` read `... pds=crumb blob=644`, and it was healthy (ticks advancing at 963 Hz).

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
N3b-B RULE: B-1: (1) the program never ran
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: T1 stops the tick by design: the tick readings say nothing about what stopped it whenever T1 ran; only the B-1 row (T running) reads as step A
TICK: Δtick 10 from the command write to 30 ms after the window (237.7 ms)
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 5; snap9: bit 16 1, count - tick 5; stop0-regs: bit 16 1, count - tick 5
```

**Results [HW].**

- Controls: PG, E0 (slot 1 = 0x5a5a3301 and run id 1, cmd 0), T0 (snap0's 0x0acc 0x010177dc,
  running) and B (BIF_FAULT 0 in snap9) all passed.
- c1-a: no done within 200 ms (`fwtask_run.py run` rc 1, `firmware hung: the tick stopped`), the
  kit classed the job `hang` and stopped the stage (rc 4).
- The page: X0 = 0x5a5a3303; S1, M4 and slots 2-4 all 0xdeadc0de; state 0, echo 0.
- T = 0x0acc after the stop: 0x010585dc in the runner's stop dump and 0x0101fc6d in snap9, read
  later, both before the kit's reset: bit 24 set, bits 23:0 at most 400000, the two reads
  different, so counting. None of T1's 0, T2's 0x200 or T3's 0x005a3305.
- The tick: Δtick 10 over a 237.7 ms window, as E1149. HostCtl dword 12 read 0x615 at snap0 and
  0x82b in the stop dump and snap9 (the runner's three reads at the stop 2091 each,
  `USE0_SERV_EVENT`'s count 67632 each); `CR_CLKGATESTATUS` 0x20, then 0x000ccfa0. BIF_INT_STAT
  0x00080000 and BIF_FAULT 0 in every read; no fault line.
- The kit's reset and its health pair: t30 fill `diff: 0 of 2048` and triangle `diff: 0 of
  4096`, exact.
- `USE0_SERV_EVENT` bit 16 set at snap0 (0x0001061a) and after the stop (0x00010830), count minus
  tick 5 in all three reads, as E1149 and E1148's snap0: it does not mark the stop (printed, not
  scored, as frozen).

**What it shows.** Measured: the issuer went on past the `emitpds` (X0), the started task never
made its first store (S1), the tick stopped within 10 ticks of the command write, the same count
as E1149's v1 job, without a BIF fault; and no crumb value reached 0x0acc as the host reads it.
Inferred from the last: the emitted PDS program never executed its first instruction (T1), up to
the snap9 read after the stop, so the `emitpds` our task issues stops the EDM's tick with the
program it emits not started. That excludes E1148's causes (2), a `doutu` that ran and did not
start our task, and (3), entry 1 started and stopped before its first store, with the residual
of (2b) (entry 1 dying in its first three instructions) and causes (1'), (2a) of the design. T1
never ran, so the stop was not T1's: the tick readings are clean here and read as E1149's.

**The inference [infer].** That a `movs tim` from a program started by `emitpds` from an EDM task
writes the same CR_EVENT_TIMER (0x0acc) the host reads. `movs tim` was measured only from client
PDS programs (a fill's secondary program in the probes `pds-timer-tim-*`, read back through the
PDS in later jobs: doc/isa/content/pds/probe/inputs.md, pds_isa.md `tim`); `pds-timer-tim-host`
asked for the host's read of 0x0acc but its kept files hold only the PDS's own reads. The host
reads 0x0acc as the firmware's running timer (E1131, E1133), and the register naming (`tim` is
`EUR_CR_EVENT_TIMER` 0xacc, GPL DDK) makes them one register [GPL]. If the inference is false,
B-1 cannot be told from B-1p, B-2a or B-2b, and only E1149's measured readings stand.

**What it does not show.** Why the emitted program does not start (the PDS not taking an emit
from the EDM's own context, an emit queue the stopped EDM no longer serves, or the form); what
stops the tick, and whether the stop comes before the PDS would take the program or the program
is never taken at all; where an emitted `douta` lands (pa or sa: never reached).

**Correction 2026-11-19:** The inference above is now measured in part. E1152 (r38-n3c-s1, N3c
R2, the same module) ran the recorded `pds-timer-tim-host` probe under regtimeline on 0x0acc:
the host's 0x0acc, running before, read the client PDS program's `movs tim` value 0x00abcde0
from 13.13 ms on the timeline's clock to its end and in snap9 after the job, as the program's
own `tim` reads did (V0-HOLDS). So the CR_EVENT_TIMER the host reads is the register a PDS
`movs tim` writes **[HW]**, not only by the register names; "`pds-timer-tim-host` asked for the
host's read of 0x0acc but its kept files hold only the PDS's own reads" no longer leaves that
side open. What stays inferred is narrower: that a program started by an `emitpds` from an EDM
task writes it the same way as a client fill's program **[infer]** (no emitted program's `movs
tim` has been seen to run). The reading B-1 rests on that much only, and V0-NOT, which would
have voided it, is refuted. E1151 (R1 of the same session) adds that the same task without the
`emitpds` ran to done with the tick going, so the stop here needs the emit. The rest stands.
