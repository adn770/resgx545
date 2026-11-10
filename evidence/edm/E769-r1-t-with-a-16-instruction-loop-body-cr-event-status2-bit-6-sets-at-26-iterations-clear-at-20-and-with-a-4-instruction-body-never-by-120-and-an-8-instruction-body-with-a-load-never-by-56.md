+++
id = "E769"
claim = "In fills of 2048 pixels whose pixel program is a loop of our own (every job after a debugfs reset, the register read 0x400 before it, o0 = 0 on all 2048 pixels after it: the loop ran to its end), CR_EVENT_STATUS2 bit 6 set at 26, 27, 28, 29, 30 and 56 iterations of a 16-instruction body (14 multiply-adds, a counter update and a branch; clear at 20; 1 run each) but at no point of a 4-instruction body from 50 to 120 iterations (50, 80, 100, 105, 108, 110, 112, 115, 120; 1 run each) and at no point of an 8-instruction body with a load and a wait (ldad, wdf, four multiply-adds, counter, branch) at 40, 50, 53 and 56 iterations (1 run each), while E431's 8-instruction body (six multiply-adds) was clear at 53 and set at 56 in 2 of 2 runs each (the control, 0x400 and 0x440), so the latch is neither a count of 54 to 55 iterations (the body of 16 sets at 26) nor about 440 instructions of one instance (the body of 4 is clear at 480, the body with a load at 448, the body of 16 sets at 416); the frozen H-TIME = H-INSTR and H-ITER rows read refuted on these points, but the stage's own control rule (the job time must grow with the loop length in every fill ladder) failed for the 8-instruction ladder (4 jobs at 53 and 56) and the 4-instruction ladder (9 jobs, 721 to 1421 us, not monotone, single runs), so the frozen scorer ended 'the ladders are cannot tell'; with a stock vertex program (0 iterations) the register read 0x400 and a held TA fault 0x480 as predicted"
unit = "edm"
method = "R1-events stage t of the question-closing pass, round 2 (stock firmware, no task of ours; 56 jobs, 30 of them triangle jobs recorded apart in E770), run 1794299292-1110 of the dataset edm-closing-r1-events, on the laptop (host cedar), 2026-11-10 09:28 laptop time (08:28 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); per job a debugfs reset (about 0.2 s), the pre read of CR_EVENT_STATUS2 (a value other than 0x400 stops the stage), the tool's probe with one of our loop programs (asm/loop-b8-iN.s, loop-b16-iN.s, loop-b4-iN.s and loop-ld8-iN.s, assembled by the landed usse-asm: prologue of three moves (four for the load body), a body of six, fourteen, two or four multiply-adds, a counter update and a branch, and for ld8 a load and a wait, N iterations, o0 written from the counter) as the pixel program of a 64x32 fill, and the register read after the job; the T0 control (body 8, 53 and 56 iterations, twice each) is E431's threshold, the T1 ladder body 16 at 20, 26, 27, 28, 29, 30 and 56, the T2 ladder body 4 at 50 to 120, the T4 fill ladder the load body at 40, 50, 53 and 56, T6 the stock vertex program through probe --tri vtxuse (the landed asm/tri/use_vtx.s) and the held TA fault of S3's recipe (hold_recovery Y read back, tri --fault --wait-ms 20000 in the background, the register read 2.8 s and 1.0 s later, the debugfs reset with the hold still on, hold_recovery N read back); tables, predictions (predictions/t.tsv) and scorer frozen before the run (FROZEN.sha256, PREDICTIONS.sha256); scored by the frozen score/score_r1.py t (out/score-t.txt); the hypotheses were H-TIME (about 121 us of one instance, with the instruction-bound loop), H-INSTR (about 440 instructions of one instance) and H-ITER (54 to 55 iterations whatever the body), derived offline from E431 and E764 to E766 (note on Q082)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r1-events:out/t/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_STATUS2"]
+++
**What ran.** Q082 asks what sets `CR_EVENT_STATUS2` bit 6. E431 found a threshold between 53 and 55
iterations of an 8-instruction loop; the question was which of the loop's length in iterations, in
instructions or in time it measures. The stage keeps the instance's instruction mix and size and
changes the body (4, 8 with a load, 16 instructions) and the iteration count.

**Frozen verdict.** The scorer's summary (`out/score-t.txt`): `T0 control held; 11 void jobs;
hypotheses by ladder (H-TIME / H-INSTR-H-ITER): T1 False/False, T2 False/False, T3 None/None, T4
False/False`, with the refuted rows `H-INSTR = H-ITER (the body is 8 instructions)`, `H-ITER (54-55
iterations whatever the body)`, `H-TIME = H-INSTR (440 / 16 = 27.5)`, `H-TIME = H-INSTR (440 / 4 =
110)`, `H-INSTR (~440 instructions per instance)` and `H-TIME (a load's latency is hidden on a fill,
not on 8x8)`, and ends `a control failed or is void: the ladders are cannot tell`. The rows as
printed: held out: 47 held, 53 FAILED, 24 cannot tell or void; replicate: 6 held, 0 FAILED; control:
9 held, 0 FAILED. The 53 FAILED and 24 void rows count hypothesis rows of every job, the triangle
jobs of E770 included, and are not 53 jobs. The closing phrase comes from the stage's own control
rule: the job time of the fill ladders must grow with the iteration count, and the scorer printed
`T0 ... DOES NOT GROW` (966, 1011, 990 and 1233 us at 53, 53, 56 and 56 iterations), `T2 ...
DOES NOT GROW` (721 to 1421 us over 50 to 120 iterations, 1421 us at 115 and 1113 us at 120),
`T1 ... grows` and `T4 fill ... grows`. By that rule the ladders' verdicts are not established.

**Results [HW].** Every fill job read 0x400 before it and printed `o0 = 0 on 2048 pixels`, so the
loop of each instance ended.

| ladder (instructions in the body) | iterations clear | iterations set |
|---|---|---|
| T0, body 8 (the control, 2 runs each) | 53 | 56 |
| T1, body 16 | 20 | 26, 27, 28, 29, 30, 56 |
| T2, body 4 | 50, 80, 100, 105, 108, 110, 112, 115, 120 | none |
| T4, body 8 with ldad and wdf | 40, 50, 53, 56 | none |

Job times: T1 902 us at 20 and 1073 at 26, 1689 at 56; T4's fill 2137 us at 40, 2838 at 50, 2848
at 53 and 2874 at 56. T6: `t6-vtx0` (the stock vertex program, no loop) read 0x400 with o0 = 0 on
its one pixel; `t6-hang` (the held TA fault) read 0x480 at both snapshots, as predicted.

The iterations times the body's instructions at the points: the body of 16 is set at 416 (26
iterations) and clear at 320 (20); the body of 8 is clear at 424 (53) and set at 448 (56); the body
of 4 is clear at 480 (120) and the body with a load at 448 (56). The stage's frozen
instruction-count and iteration-count rows each fail on one of these (the body of 16 sets before
424, the body of 4 and the body with a load are clear at or above 448).

**Post hoc [infer; read after the run, not held out; one free parameter fitted to the same
points].** Counting only the multiply-adds an instance executes (6 an iteration for the body of 8,
14 for 16, 2 for 4, 4 for the body with a load), the points fall on one side of a single number:
clear at 224 (the load body at 56), 240 (body 4 at 120), 280 (body 16 at 20) and 318 (body 8 at
53), set at 336 (body 8 at 56) and 364 (body 16 at 26) and more, and E431's 54 iterations, 324
multiply-adds, were set in 2 of 3 runs. A threshold between about 318 and 336 multiply-adds
reproduces every point of this stage and E431's, but it is arithmetic on the rows that were read,
not a mechanism and not a prediction: the 4-instruction and the load ladders never reached it
(240 and 224), so they carry no test of it. What the data rule out is the count of iterations alone
and the count of all instructions alone; what they do not rule out is a count that depends on the
instruction mix, or a time that these single-run job times do not measure.

**Not shown.** What the threshold counts if it is the multiply-adds (or any pipe's work), whether a
body-4 ladder past 160 iterations or a body of another mix sets the bit where the fit says, bit 7
(the TA: a vertex loop was not built, T5 is not in this session), and the occupancy knob (E770: the
triangle jobs could not be used).
