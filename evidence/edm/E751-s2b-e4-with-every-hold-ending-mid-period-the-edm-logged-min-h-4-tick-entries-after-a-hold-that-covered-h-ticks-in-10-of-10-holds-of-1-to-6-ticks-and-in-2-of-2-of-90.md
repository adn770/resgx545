+++
id = "E751"
claim = "With the exit of every hold designed to fall mid-period (about 12500 CR_TIMER units from the two neighbouring grid ticks), a firmware task of ours that held the EDM for H tick periods was followed by exactly min(H, 4) tick entries before the next grid tick in all 12 holds (H = 1 x2, 2 x2, 3 x2, 4 x2, 6 x2, 90 x2 in e4m and e4l: ONE at H = 1, ALL at H = 2 to 4, PARTIAL(4) at H = 6 and 90), the frozen held-out prediction q = min(H, 4) of the frozen classifier, which also fits ALL at H = 1 to 4 and ONE at H = 1, and which the 6 and 90 tick holds separate from ALL and the 2 to 90 tick holds from ONE; the first min(H, 3) entries read pa2 = 0x01061a74 and for H >= 4 the fourth read an EVENT_TIMER sample 12599 to 12614 units old, within 25 units of the first entry's time after the last held tick (the frozen pa2 signature, 12 of 12), and the window count (entries logged plus drops) equalled open time x 0.99746 - H + min(H, 4) within 1.5 in 12 of 12 (the frozen second instrument; 0.8 at most); the three no-hold controls of e4c held (16 entries on the 25000 grid, 3 of 3); the conditions H = 1 to 4 are new, H = 6 and 90 repeat run 3's holds of S2 (E749) with their exits moved mid-period"
unit = "edm"
method = "S2b stages e4c (3 jobs, no hold, window 2), e4m (H = 1, 2, 3, 4, 6, two jobs each, n = ((H + 0.5) x 25000 - 82) / 1.5 rounded: 24945, 41612, 58279, 74945, 108279) and e4l (H = 90, n = 1508279, 2 jobs), paths relative to edm/closing-s2b/ of the dataset, runs 1794266844-31563, 1794266851-31645 and 1794266861-31729, on the laptop (direct cable), 2026-11-10 00:27, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4c...), tool ~/sgxfive-test-s1 (sha256 d776afbc...714e); blob ring_hold, byte-identical to E749's (asm/ring_hold.s, sha256 fa0f79dbb586...c168, 747 instructions, no sa write), one arm per stage, window 2 written back to back with the command, windows of 20 to 160 ms; each stage's gate computed by the frozen scorer and checked by the driver and the laptop's runner before the next stage (out/e4c to e5t, gates/*.gate); the design, the scorer and the predictions were rebuilt after E749's run (the one-sided guard of 1250 units after an exit, the burst defined as the entries between the exit and the next grid tick less 1250 units, the period 25000, 'no tick held' not a told class) and frozen before the run (FROZEN.sha256, PREDICTIONS.sha256, LAPTOP.sha256: 31 files, 5 predictions files); the scorer's fixes were tested on E749's 12 pages first; scored by the frozen score/score_s2.py e4c, e4m, e4l"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-s2b:out/e4c/", "edm-closing-s2b:out/e4m/", "edm-closing-s2b:out/e4l/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER", "CR_TIMER"]
+++
**What ran.** E749's holds could not be classified because every exit fell 79 to 86 units after a
tick of the old grid. S2b repeats E4 with each hold ending mid-period, a classifier whose guard is
one-sided, and two further instruments (the pa2 signature and the window count) that do not use the
stamps of the burst. Predictions frozen before the run: q = min(H, 4) labelled 'fit: S2 run 3' (the
queue E749 read after its run at 6, 18 and 90 ticks), against LOST (q = 0), ONE (q = 1) and ALL
(q = H); at H = 1 the cap, ONE and ALL coincide, H = 2 to 4 separate the cap from ONE, and H = 6 and
90 separate it from ALL.

**Frozen verdicts.** e4c: `control held [True, True, True]; median diff 25000`, gate open. e4m:
`shapes by H {1: ['ONE', 'ONE'], 2: ['ALL', 'ALL'], 3: ['ALL', 'ALL'], 4: ['ALL', 'ALL'], 6:
['PARTIAL(4)', 'PARTIAL(4)']}; cap q = min(H, 4) held in 10 of 10 told; pa2 signature 10/10;
window count 10/10 (10 valid, 10 jobs); gate passes`. e4l: `shapes by H {90: ['PARTIAL(4)',
'PARTIAL(4)']}; cap q = min(H, 4) held in 2 of 2 told; pa2 signature 2/2; window count 2/2`, gate
passes (out/score-e4c.txt, out/score-e4m.txt, out/score-e4l.txt). Every hold's knob (1.5 n + 15
within 0.2 % + 50 units) and design (exit mid-period, held ticks = H) held; busy flags 0 and
passes of slots 1 to 3 at 0 in every job.

**Results [HW].** Entries after the exit (units from the exit), slot 0, pa0 2, pa1 0x02000000:

| H | entries (pa2 low 24 bits) | then |
|---|---|---|
| 1 | +103 or +108 (0x061a74) | the grid at +12492 to +12504 |
| 2 | +103 to +107, +240 to +263 (0x061a74 x2) | the grid at +12494, +12503 |
| 3 | +103 to +106, +240 to +245, +385 to +389 (0x061a74 x3) | the grid at +12499, +12503 |
| 4 | the three above, then +528 to +530 (0x0306b8, 0x0306c2) | the grid at +12504 |
| 6 | the three above, then +530 and +557 (0x03068e, 0x03061a) | the grid at +12494, +12502 |
| 90 | the three above, then +528 and +535 (0x030698, 0x030708) | the grid at +12501, +12508 |

The fourth entry's age, (400000 - pa2 bits 23:0) / 16, is 12604.5 and 12603.9 at H = 4, 12614.4 and
12607.1 at H = 6 and 12606.5 and 12599.5 at H = 90, where the exit is 12493 to 12507 units after the
last held tick and the first entry 103 to 108 units after the exit. The holds were 37433 to 2262438
units; windows were 27 to 160 ms; entries logged plus drops 27, 27, 30, 29, 31, 30, 32, 32, 34, 33,
74 and 73 (the scorer's expected 27.5, 27.4, 29.5, 29.4, 30.5, 30.4, 32.5, 32.4, 33.2, 33.4, 74.2
and 73.9). e4c: 16 entries and 4, 4 and 5 drops, successive differences 24997 to 25003.

**Post hoc [infer; read after the run, not held out].** The queue is three events that were
latched on arrival (the three 0x01061a74 entries: 12 clocks after the reload, where a tick served
at once reads 16) and one pending event latched when the hold ended (the fourth entry's age is the
time between the last held tick and the drain, which no earlier hold could show because its exits
sat 80 units after a tick); the rest of the ticks held are dropped. 'Capped at 4' is therefore 3
queued plus 1 pending for ticks; whether the 3 and the 1 are different mechanisms or one counter,
and what a task other than the tick handler's does to them, is not shown. What the frozen cap does
not separate: at H = 1 to 4 it is ALL, so the jobs that tell the cap from ALL are the four holds
of 6 and 90 ticks.

**Not shown.** Holds of 5 ticks, holds that end near a grid tick with the one-sided guard, a task
other than the hold loop, other slots held, and holds above 91 ms.
