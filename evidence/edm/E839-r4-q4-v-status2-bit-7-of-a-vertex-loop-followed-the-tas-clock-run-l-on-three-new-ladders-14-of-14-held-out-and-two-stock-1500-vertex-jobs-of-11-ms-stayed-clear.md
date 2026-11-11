+++
id = "E839"
claim = "R4-pixel stage q4-v (Q082 bit 7, 28 jobs, 27 scored: a vertex program on the tool's triangle looping N times on a relative br, the stored depth word 0x3f200000 + N the loop proof, every job under regtimeline 0x0008, 0x0118, 0x012c; L = the longest run of CR_CLKGATESTATUS 0x000ccff8): the four bridge controls to E807 passed on the rgn4 module (no loop and N = 1 clear with L 9.4 and 4.6 us, E807's 880 clear with L 105.1 us and 1760 set with L 207.3 us); on three ladders E807 never ran (10 multiply-adds an iteration on 3 vertices, counter and branch only on 3, E807's 8-instruction body on 24 vertices) the six FIT points were clear as the model placed them, and the frozen rule 'bit 7 set iff L >= 129.5 us' held in 14 of 14 decided held-out rows (clear to L 119.5 us, set from 138.6 us; the one row in the edge 122 to 136 us, L 133.2 us, set, not scored), the bit showing 121.9 to 129.7 us after the run began in 10 of 10 set jobs (frozen window 118 to 138); the stock program with 1500 vertices at 2048 x 2048 kept bit 7 clear in 2 of 2 with L 11189.2 and 11209.7 us (H-STALL, frozen: a long but progressing TA does not latch; H-PHASE refuted in those rows); the 4096 x 4096 row returned -ENOSPC (the scene overflowed the parameter buffer at the default pages), void; frozen verdict 'bit 7 follows the TA clock run L (set iff L >= 129.5 us, edge 122..136) (14 of 15 rows decided)'"
unit = "edm"
method = "R4-pixel stage q4-v of the question-closing pass, round 4 (decisions R4 9a and the bit-7 scope a, plan closing4/pixel/exp-pixel-r4.md section 3.1), dataset render-closing-r4-pixel, on the laptop (host cedar, direct cable), 2026-11-11, attempt out/20261111-205726 (the second stage, started 21:00:36 Mac time; run.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the linux fork's branch resgx545 at a2788bd8; installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803), not rebuilt; freeze FROZEN.sha256 f9b0fa03... and PREDICTIONS.sha256 c939d0f5... before the first job; every job after a debugfs reset, CR_EVENT_STATUS2 read from the debugfs registers after the reset (0x400 in all 28) and after the job, the job under `regtimeline 0 0.3 0x0008,0x0118,0x012c` (reads only); each loop job `probe --temps 16 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 [--vertices 24] --dump-render DIR --slot pixel=pix_green.bin vloop-BODY-iN.bin` (gen/r4loops.py, every program checked in sgx-sim), each stock job `probe --tri pixel --width W --height H --vertices 1500 --dump-render DIR p1139-green.bin` (R3-geo g-c4's command); the ladders' five held-out points at 0.80, 0.92, 1.08, 1.20 and 1.60 x N* of the frozen offline model of L (score/r4const.py), two FIT points each run first; the runner stopped at the last row v-stock-4096 (rc 3, 'scene overflowed the parameter buffer, context kept (No space left on device)', no fault, STATUS2 0x400 before and after, health after it ok: a 64 x 64 triangle 0 of 4096 wrong), so the driver neither scored nor gated the stage; the lead's decision during the run: the row's premise (a complete render, as R3-geo g-c4 had on the older module) failed on the rgn4 module at the default 0x422 PB pages, so the row is void with that reason, health was clean, continue (the next attempt began at q4-f, E840); scored at the fold (2026-11-11) by the frozen score/score_r4.py q4-v on the kept files, fold/score-q4-v.txt, byte-identical on a second run, and its gate (fold/gate-q4-v.txt: PASS); the scorer's 'rule says set' for the two stock rows is the L rule applied to them, not their frozen prediction, which was clear (H-STALL)"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-pixel:out/20261111-205726/q4-v/", "render-closing-r4-pixel:fold/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E807's frozen counts placed none of its bit-7 points; read after the run, in all 74
of its jobs bit 7 was set iff the longest run L of `CR_CLKGATESTATUS` at 0x000ccff8 (the TA's
clocks while it works on the vertices; "TA clocks" is our name) reached about 130 us (Q082's note
of 2026-11-11, SEMI). Q4-v holds that rule out on bodies and a vertex count E807 never ran, and
asks whether a long TA phase without a loop sets the bit (H-PHASE) or not (H-STALL: what latches
is a TA that makes no progress, as in R3-geo g-c4's ten 1500-vertex jobs that ended 0x400).

**Frozen verdict (as printed, scored at the fold).** `FIT points (clear by the model; not
gating): 6 held, 0 FAILED, 0 cannot tell of 6`; `HELD OUT ladder rows, bit 7 follows L (the edge
band 122..136 us is not scored): 14 held, 0 FAILED, 1 cannot tell of 15`; `latch time (bit 7
shows 118..138 us after the run began) in the set jobs: 10 held, 0 FAILED, 0 cannot tell of 10`;
`stock rows: H-STALL in 2 of 3 rows (the others void)`; `SUMMARY: bit 7 follows the TA clock run
L (set iff L >= 129.5 us, edge 122..136) (14 of 15 rows decided); FIT 6 held, 0 FAILED, 0 cannot
tell of 6; latch window 10 held, 0 FAILED, 0 cannot tell of 10; stock: H-STALL in 2 of 3 rows (the
others void)`; `gate q4-v: PASS`.

**Results [HW].** L and bit 7 after the job (c clear, S set); t7 - start: from the start of the
run to the first sample with bit 7.

| ladder | set | N | L us | bit 7 | t7 - start us |
|---|---|---|---|---|---|
| b12v (10 imae, 3 vertices) | FIT | 340, 525 | 60.7, 92.7 | c, c | - |
| b12v | held out | 605, 695 | 105.2, 119.5 | c, c | - |
| b12v | held out | 815, 905, 1205 | 139.4, 153.4, 205.1 | S, S, S | 121.9, 126.9, 126.6 |
| b2v (counter, branch, 3 vertices) | FIT | 960, 1495 | 56.2, 89.6 | c, c | - |
| b2v | held out | 1710, 1965 | 99.9, 113.7 | c, c | - |
| b2v | held out (edge) | 2310 | 133.2 | S | 128.7 |
| b2v | held out | 2565, 3420 | 145.2, 194.2 | S, S | 123.3, 124.7 |
| v24 (b8v, 24 vertices) | FIT | 225, 350 | 69.7, 103.4 | c, c | - |
| v24 | held out | 400 | 118.2 | c | - |
| v24 | held out | 460, 540 | 138.6, 163.3 | S, S | 125.4, 128.3 |
| v24 | held out | 600, 800 | 177.3, 231.1 | S, S | 129.7, 126.5 |
| controls | control | none, 1, 880, 1760 | 9.4, 4.6, 105.1, 207.3 | c, c, c, S | -, -, -, 124.8 |
| stock 1500 vertices 2048 x 2048 | held out | a, b | 11189.2, 11209.7 | c, c | - |
| stock 1500 vertices 4096 x 4096 | held out | - | - | void (rc 3, -ENOSPC) | - |

Every loop job's depth word proved its loop; STATUS2 read 0x400 after each reset. The two
2048 x 2048 jobs returned rc 0 with identical parameter buffers and TA data.

**What it shows and does not.** For a vertex program that loops, bit 7 is set after the job iff the
TA's busy-clock run L lasted at least about 129.5 us, whatever the body (13, 8 and 2 instructions an
iteration) and the vertex count (3 and 24, with E807's 12 and 48); it shows about 125 us after that
run began: the rule written on E807's jobs holds out on three new ladders. A long TA phase that
progresses does not set it: the stock program's 1500 vertices kept the TA's clocks in that state for
11 ms with bit 7 clear (2 of 2), so the rule is not about the phase's length (H-PHASE refuted in
those rows) and L is a measure for a vertex loop, not for every TA. [infer] The bit latches when the
TA waits on one piece of vertex work for about 125 us; a vertex program that loops is one such wait,
and E764's 121 us from a fault word to bit 7 would be the same timeout, which is not tested. Not
shown: what "progress" is inside the TA; why E357's held TA hang set the bit with a run of 8 us (its
clocks read another value through the hang); bit 7 at 4096 x 4096 (void: on this module the
1500-vertex scene overflows the parameter buffer at the default pages).
