+++
id = "E746"
claim = "A firmware task of ours that logs every pass of the four PDS #13 slots with CR_TIMER (ring_e1, window 2) saw one GETMISCINFO kick with no job as exactly one entry that is not a plain tick, in slot 0, with pa0 = 0 and pa1 bits 23:0 = 0x100 in 3 of 3 jobs (a gated control, rebuilt after run 2 of the stage and so a fit of run 2); held out of that fit and read on the new run: pa1 bits 31:24 are a count K that every event carries (2 on every tick before the first kick, K = 2, 3 and 4 on the three kicks in job order, K + 1 on every tick after a kick, 3 of 3), and pa2 bits 23:0 of the kick is a sample of EVENT_TIMER counting down from 400000 core clocks (the time since the last tick, (400000 - pa2) / 16 CR_TIMER units, agrees with the stamps within 5.3 units, 3 of 3); the ticks were pa0 = 2, pa1 bits 23:0 = 0 and pa2 = 0x01061a70 on a grid of 25000 CR_TIMER units, and a filtered 50 ms window logged nothing before the kicks (3 of 3) and after them (2 of 2); E538's 'kick' words (pa1 = 0x03000000, pa2 = 0x01061a70) are those of the tick after the kick"
unit = "edm"
method = "S2 stage e1c of the question-closing pass (10 jobs, 4 conditions: q50 x3, q8 x2, kick x3, q50k x2), paths below relative to edm/closing-s2/ of the dataset, run 1794265136-18511 (the third run of the stage, the valid one), on the laptop (direct cable), 2026-11-09 23:58, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4c...162b0a), tool ~/sgxfive-test-s1 (sha256 d776afbc...714e); blob ring_e1 (asm/ring_e1.s, 640 instructions, sha256 0453863a8ebb...da7f, accepted by the landed verifier, armed with own_arm slots=0xf entry=0,1,2,3): each slot a ladder of rungs (flag, pa0, pa1, pa2, CR_TIMER from ldr of register 81), 16 rungs in slot 0 and 8 in the others; window 1 logs every pass but a plain tick (pa0 = 2 with the count byte masked out), window 2 every pass, window 0 none; the runner opened the window, ran the trigger (nothing, or one GETMISCINFO through the debugfs), closed the window and read the page twice (the second read must equal the first: the window-0 proof); tables, predictions and scorer frozen before the run (FROZEN.sha256, PREDICTIONS.sha256; the verification is printed in the stage logs), the kick rows rebuilt after run 2 of the stage and labelled 'fit: S2 run 1' in the frozen predictions (that is run 2 of the files: out/e1c.run2-gate-closed, whose gate stayed closed, was read after its run; out/e1c.run1-stopped is an earlier stop of the runner on a kernel-log marker, with no ring data); scored by the frozen score/score_s2.py e1c; the sample age of pa2 and the comparison with E538 were read after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["edm-closing-s2:out/e1c/", "edm-closing-s2:out/e1c.run2-gate-closed/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_TIMER", "CR_TIMER"]
+++
**What ran.** E538 read the kick as the words a firmware stub kept: one slot per task, the last
non-tick hit, no history. This stage logs every pass instead (E1 of the events proposal). Three
earlier attempts of the stage exist and are kept: run 1 stopped at its first job on the runner's
kernel-log marker (no ring data), run 2 (`e1c.run2-gate-closed`, same blob and tool) ran all eight
of its jobs and closed its own gate because the kick control, frozen from E538's words, failed 0 of
3; run 3 is this record's. The kick rows of run 3 were rebuilt after reading run 2 (window 2, a
filter that masks pa1 bits 31:24, a new control q50k for the quiet window after the kicks); the
frozen predictions label them 'fit: S2 run 1', which is run 2 of the files.

**Frozen verdict.** `GATE e1c OPEN`: quiet 50 ms windows 3 of 3, ticks 2 of 2, kick identity 3 of 3
(one entry, pa0 0, pa1 bits 23:0 0x100), quiet windows after the kicks 2 of 2, clock control
median 25000; kick counts [2, 3, 4]; held out of the run-2 fit: pa2 phase 3 of 3, count + 1 3 of
3, pa2 range 3 of 3, ticks 3 of 3 (out/score-e1c.txt). The scorer's held-out label means held out of
the run-2 reading, not predicted before any kick had been logged.

**Results [HW].** Every entry was in slot 0 and slots 1 to 3 logged nothing in any job. The three
kicks:

| job | kick pa1 | kick pa2 | ticks logged before / after | phase residual | tool call |
|---|---|---|---|---|---|
| kick | 0x02000100 | 0x01022935 | 0 / 15 | -5.3 units | 3.69 ms |
| kick-r2 | 0x03000100 | 0x010608d9 | 1 / 14 | -1.4 | 3.61 ms |
| kick-r3 | 0x04000100 | 0x0103a24a | 0 / 15 | -2.6 | 3.52 ms |

The phase residual compares the kick's pa2 with its stamp: (400000 - pa2 bits 23:0) / 16 is the
time since the last tick in CR_TIMER units; in the first and third jobs that age plus the time to
the next tick's stamp (8846 and 14882 units) falls 5.3 and 2.6 units short of the 25000 period, in
the second the kick's stamp follows its tick's by 281 units against an age of 282.4 (-1.4). The
last column is the wall time of the tool call (the firmware's own answer took 200, 147 and 200 us).
Ticks: pa0 = 2, pa1 bits 23:0 = 0 and pa2 =
0x01061a70 in every tick entry; pa1 bits 31:24 = 2 on the ticks before the first kick, 3 after it,
4 after the second and 5 after the third (the arm is done once per stage, so the count carries
across the jobs). Two 8 ms windows (q8) held 8 and 9 entries for 8.58 and 8.56 ms open, with
tick-to-tick CR_TIMER differences of 24998 to 25002 (median 25000, counting up); the 50 ms windows
q50 (3) and q50k (2, after the three kicks, count 5) held no entry. Each kick ring held 16 entries
and dropped 9.

Run 2 (not the verdict of this record, the data it was read from): the same three kicks with the
window-1 filter masking only pa1 bit 25 gave the same single kick entry (pa0 0, pa1 0x02000100,
0x03000100, 0x04000100) and tick entries with pa1 0x03000000, 0x04000000 and 0x05000000 after
them, which the filter passed because bit 24 was then set; that is what filled its rings with
ticks.

**Reading of E538 and E532 [infer].** E538's stubs kept, per slot, the last entry with pa1 and
0xfdffffff non-zero; each E538 run reloaded the firmware (count 2 at the arm), so the tick after
its one kick carried count 3 and the stub kept 0x03000000 with pa0 = 2 and pa2 = 0x01061a70, which
are a tick's words. The kick's own words are the entry above. So the frozen prediction of E538
(pa1 and 0xfdffffff = 0x100) described the kick and its verdict 'failed' was the stub's; bit 24 and
bit 25 of pa1 are bits 0 and 1 of the count byte, not event bits. pa2 is not a constant: it is the
EDM's event timer, bits 31:24 = 0x01, bits 23:0 counting down from 400000 (HostCtl dword 6, E009)
at the core clock, so a tick, served at its reload plus 16 core clocks, reads 400000 - 16 =
0x061a70, and a kick at any phase reads another value. That the kick's count K is 2, 3, 4 and a tick
after a kick carries K + 1 says a kick advances the count; E747 shows every client job's own kick
entry does too.

**Not shown.** What the count counts besides these entries and why it is 2 after the arm (an
arm's own GETMISCINFO read is one guess, not tested), a kick with a job in flight (E749 to E752
hold the EDM while one arrives), two kicks within one tick, and whether pa2 is the time the event
was latched or the time its pass ran (E749 and E750 separate them for events that wait behind a
task of ours).
