+++
id = "E749"
claim = "A firmware task of ours that held the EDM in a three-instruction loop for 0.6 to 90 tick periods (n = 10000 to 1500000 iterations, CR_TIMER 15015 to 2250017 units, 1.5 units an iteration plus 15 within 2) was never overlapped by a pass of any slot (no slot-0 entry stamped inside a hold, busy flags 0 and passes of slots 1 to 3 at 0 in 12 of 12 holds) and the ticks resumed on the original 25000-unit grid after it; the frozen classifier said LOST for both holds of n = 10000 (a hold that no tick fell inside) and 'cannot tell' for all 8 holds of n = 100000, 300000 and 1500000, because every exit fell 79 to 86 units after a tick of the old grid (the design made it so); read after the run, every hold that covered 6, 18 or 90 ticks was followed by exactly four tick entries within 585 units (23.5 us) of its exit (10 of 10 holds: e4h, e4l and the two controls of e5c), the first three with pa2 = 0x01061a74 (400000 - 12) and the fourth with an EVENT_TIMER sample about 183 to 190 CR_TIMER units old, the age of the first entry after the last held tick, and a tick stream of 0x01061a70 on the old grid afterwards"
unit = "edm"
method = "S2 stages e4c (no hold, window 2, 3 jobs of 20 ms), e4h (n = 10000 x2, 100000 x3, 300000 x3) and e4l (n = 1500000 x2), run 3 of the session, paths relative to edm/closing-s2/ of the dataset, runs 1794265176-18866, 1794265183-18945 and 1794265192-19029, on the laptop (direct cable), 2026-11-09 23:59, plus the two no-trigger controls of e5c (ctl100 x2, run 1794265199-19105, 2026-11-10 00:00), the same job as e4l; kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1; blob ring_hold (asm/ring_hold.s, 747 instructions, sha256 fa0f79dbb586...c168): the ring of E746 plus pass counters, busy flags and, on command 1 in slot 0, CR_TIMER stamps at the entry and the exit of a slow loop of n iterations; one arm per stage (slots=0xf entry=0,1,2,3), window 2 written back to back with the command, window length 20 to 160 ms, the page read twice; the hold's entry is 64 to 70 units after the tick whose pass runs it; predictions frozen before the run (FROZEN.sha256, PREDICTIONS.sha256: H-ONE, fitted post hoc to E539's lags, with LE1 for n = 10000; the classifier names LOST, ONE, ALL, PARTIAL(q), OVERLAP and an off-grid class, and says 'cannot tell' when the exit falls within 50 us of a tick of the old grid); scored by the frozen score/score_s2.py; the stamps, the window counts and the pa2 values after the exit were read after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["edm-closing-s2:out/e4c/", "edm-closing-s2:out/e4h/", "edm-closing-s2:out/e4l/", "edm-closing-s2:out/e5c/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER", "CR_TIMER"]
+++
**What ran.** E539 and E605 held the EDM for up to 7 ms with a tick-only stream and saw the tick
counter 1.9 to 2.2 behind; The open question of 2026-11-09 asked what happens to a tick that falls
inside a long task (answered by E752). Here the task stamps its own entry and exit and the ring logs
every pass, so the order and the stamps of the entries after the exit are visible.

**Frozen verdicts.** e4c: `control held [True, True, True]; median diff 25000`, gate open. e4h:
`10000: LOST, LOST` (prediction LE1 held in 2 of 2 told); `100000` and `300000`: 'cannot tell (the
exit fell within 50 us of a tick of the old grid)' in 6 of 6; gate open on safety only (every hold
valid, tick and health fine). e4l: 'cannot tell' 2 of 2, gate open on safety only. The hold's
knob (exit minus entry within 0.7 to 1.5 times E539's rate for n) held in 12 of 12 jobs. The
experiment therefore told nothing for n >= 100000 and the LOST of n = 10000 is vacuous: no tick
fell inside a 15015-unit hold, so no hypothesis predicted an entry (out/score-e4c.txt,
out/score-e4h.txt, out/score-e4l.txt).

**Results [HW].** The hold began 64 to 70 units after the tick whose pass carried the command and
lasted 1.5 n + 15 units within 2 (15015, 150015 to 150016, 450015, 2250015 to 2250017), so for each
n here a multiple of 50000 the exit fell 79 to 86 units after a tick of the old grid. No entry was
stamped inside a hold, no slot found its state busy, and slots 1 to 3 had no pass. After the exit:

| n | ticks inside the hold | entries after the exit (units from the exit) | then |
|---|---|---|---|
| 10000 | 0 | none before the next grid tick (+9915, +9921) | the grid |
| 100000 | 6 | +102, +239 to +251, +379 to +393, +528 to +542 (3 of 3) | grid, +24918 to +24922 |
| 300000 | 18 | +102 to +103, +240, +379 to +380, +533 to +540 (3 of 3) | the grid |
| 1500000 | 90 | +103, +242 to +255, +382 to +415, +530 to +585 (4 of 4, e5c controls too) | grid |

All four entries: pa0 2, pa1 0x02000000. pa2 of the first three 0x01061a74 in every hold; of the
fourth 0x01060ea4 to 0x01060f12, an age of (400000 - pa2 bits 23:0) / 16 = 182.9 to 189.8 units,
against 181 to 189 units between the last tick inside the hold and the first entry's stamp. Every
tick outside these bursts read 0x01061a70. Window counts (entries logged plus drops): 26, 26 (open
26.2 and 26.5 ms), 32 x3 (34.5 ms), 38 x3 (52.3 to 52.6 ms), 74 x4 (160.3 to 160.7 ms) and, for
e4c, 20 x3 (20.4 to 20.6 ms).

**Post hoc [infer; read after the run, not held out].** The exits' alignment is the design: n and
the rate (E539) put each hold at a whole number of periods and a hold starts on a tick, so the
0.6-period holds end mid-period and every other hold ends just after a tick of the old grid. The
frozen guard is symmetric, but the tick 79 to 86 units before the exit fell inside the hold and
cannot be a natural tick after it, and four entries cannot be LOST or ONE whatever one of them is.
The scorer also takes the period as 25001 units (E009) where the clock control (E746) measured
25000, which puts the 1500000 exits 5 and 10 units before the 90th tick after the command's. With
the guard one-sided and the measured period the shape is PARTIAL(4) in 10 of 10 holds of 6, 18 and
90 ticks, and 'no tick held' at n = 10000. The window counts agree: open time x 0.9975 minus the
ticks held plus 4 gives 32.4, 38.4 and 74.1 against 32, 38 and 74 logged (26.1 against 26 at 10000),
where ONE would give 29.4, 35.3 and 71.1 (the draft analysis's 23.4 for 300000 was an arithmetic
slip) [counts that follow from the table, not a frozen prediction]. The pa2 values fit a queue that
took the first three tick events as they came (12 clocks after the reload, where a tick served at
once reads 16) and one more event pending, latched when the queue began to drain; the rest of the
ticks held were dropped (86 of 90 lost at 90 ms). E539's lag of 1.9 to 2.2 ticks at about six
periods is then 6 minus 4 (the tick of the command's pass aside). E750 and E751 and E752 test this.

**Not shown.** Holds of 1 to 5 periods (the queue reading predicts min(H, 4) entries, the first
min(H, 3) with 0x01061a74; E751 ran them), an exit away from the grid (E751), events of other
sources (E750), other slots held, and holds above 91 ms.
