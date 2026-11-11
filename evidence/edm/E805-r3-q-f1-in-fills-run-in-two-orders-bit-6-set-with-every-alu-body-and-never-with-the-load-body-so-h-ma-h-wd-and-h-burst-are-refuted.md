+++
id = "E805"
claim = "R3-pixel stages q-f1a and q-f1b (54 fill jobs each, one table run in two opposite orders; relative loops with the MARK proof of E804 over six bodies, each with a counter update and the branch: b16 with 14 multiply-adds, b12 with 10, b4 with 2, b2 with none, b8n with six `or`, ld8 with a load, a wait and 4 multiply-adds; the two shortest points of each ladder FIT, the other 42 HELD OUT): every loop proof held and STATUS2 read 0x400 before every job (108 of 108); bit 6 set from b16 N = 25 (clear at 24 in both orders, at 25 in q-f1a only: an edge), from b12 35 (clear at 34), from b4 130 (clear at 80), at every point of b2 (500 to 16000) and of b8n (60 to 3840) and at no point of ld8 (20 to 320, bursts up to 13.4 ms), the two orders agreeing everywhere else; H-MA (bit 6 when an instance's multiply-adds reach M* in (318, 336]) is REFUTED by all six ladders, H-WD (when a tile's time (B - 60.2) / 4 reaches 121.8 us, N* from each ladder's FIT points) and H-BURST (when the burst reaches 536 +- 20 us) are REFUTED by ld8 alone, and H-WD-busy (H-WD counting only time without a load) is open, ld8 having no set point; in the 48 jobs set at N >= 1.3 N* bit 6 showed 120 to 340 us after the burst began (H-EARLY 48 of 48, H-END 0); read after the run (no frozen row), in the 106 fill jobs of q-f0, q-f1a and q-f1b without a load every job with bit 6 set had a burst of at least 535.9 us and every clear one at most 539.3 us"
unit = "edm"
method = "R3-pixel stages q-f1a and q-f1b of the question-closing pass, round 3 (session L2, decisions R3-P3 and R3-P5; started 16:11:36 and 16:16:14 Mac time, out-l2.log), dataset render-closing-r3-pixel, on the laptop (host cedar, direct cable), 2026-11-10, attempt out/20261110-160415, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), the stock firmware (core 545 rev 0x1000d, DDK 1.7.17 build 862890 in every health line), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803), R1's builds, not rebuilt; every job after a debugfs reset, CR_EVENT_STATUS2 read from the debugfs registers after the reset and after the job, the job under regtimeline 0 0.3 0x0008,0x0118,0x012c (the burst B is the run of CR_CLKGATESTATUS 0x0008 not idle, t6 and t7 the time of the first sample with bit 6 or 7 of 0x0118 from the burst's start); freeze FROZEN.sha256 8a0fa9aa... and PREDICTIONS.sha256 d1cdc86b... before the first job; health ok after every stage; each job `probe PROGRAM` (a fill of 2048 pixels) with loop-rel-BODY-iN.bin from bins/; the gate of both stages was q-f0's kept output (gate-q-f1a.txt, gate-q-f1b.txt: open); each stage scored alone by the frozen score/score_r3.py (out/score-q-f1a.txt, out/score-q-f1b.txt: single-order views) and the two orders together by score_r3.py verdict (out/verdict.txt), which refutes a hypothesis by one ladder whose two orders agree and contradict it; the burst bound of the last clause read after the run with the session's own reader (score/r3job.py) over the kept timelines of the 106 jobs, scratch arithmetic not in the copy"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-pixel:out/20261110-160415/q-f1a/", "render-closing-r3-pixel:out/20261110-160415/q-f1b/", "render-closing-r3-pixel:out/20261110-160415/q-f0/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E769 refuted an iteration count and an instruction count as what sets bit 6 in a
fill. The proposal for round 3 read E431's and E357's kept timelines (FIT) and offered two readings
that fit E769: H-MA, a count of multiply-adds of one instance, and H-WD, a watchdog of about 121.8
us on a tile's pixel work (the fill's four 32x16 tiles in equal shares of the burst), with H-BURST
(a fixed burst length) and H-WD-busy (H-WD with time waiting on a load not counted) beside them.
Six bodies separate them: b2 and b8n have no multiply-add, ld8 waits on a load. Each ladder ran in
both orders so that an order effect shows as an edge, not as a refutation.

**Frozen verdict (as printed, out/verdict.txt).** `Q082-F: H-MA REFUTED by ['b16', 'b12', 'b4',
'b2', 'b8n', 'ld8']; H-WD REFUTED by ['ld8']; H-WD-busy open (unreplicated [], no decided point
['ld8']); H-BURST REFUTED by ['ld8']`, with `time of the latch (jobs set at N >= 1.3 N*): 48
jobs; t6 in [120, 340] us (H-EARLY): 48; within 15% of B (H-END): 0`.

**Results [HW].** Bit 6 by ladder (S set, c clear, E the orders differ; the same in both orders
unless E):

| body | FIT points | HELD OUT points | H-WD N* (from the FIT slope) |
|---|---|---|---|
| b16 (14 imae) | 6 c, 12 c | 21 c, 22 c, 23 c, 24 c, 25 E, 104 S | 25.9 +- 28% |
| b12 (10 imae) | 8 c, 16 c | 28 c, 30 c to 34 c, 35 S, 36 S, 38 S, 136 S | 31.0 +- 26% |
| b4 (2 imae) | 40 c, 80 c | 130 S to 640 S (13 points) | 119.1 +- 20% |
| b2 (none) | 500 S, 1000 S | 2000 S to 16000 S (4 points) | 184.8 +- 8% |
| b8n (6 or) | 60 S, 120 S | 240 S to 3840 S (5 points) | 54.6 +- 8% |
| ld8 (load, wait, 4 imae) | 20 c, 70 c | 79 c, 84 c, 160 c, 320 c | 11.7 +- 8% |

The bursts of the edge, b16 at 25: 537 us (clear, q-f1a) and 536 us (set, q-f1b); b12 at 34 and
35: 539 and 538 us clear, 554 and 547 us set. ld8's bursts: 877 to 896 us at 20, 13382 and 13450
us at 320, never set. H-MA's frozen points (24 S at b16, 34 S at b12, 160 to 168 at b4, never at
b2 and b8n, 84 S at ld8) miss in every ladder; H-WD and H-BURST place every ladder but ld8.

**Read after the run [infer, no frozen row].** Over the 106 fills without a load (q-f0's 10 and
the 96 non-ld8 jobs of q-f1a and q-f1b), bit 6 set in 68: all 68 had a burst of 535.9 us or more
and all 38 clear ones 539.3 us or less, whatever the body (no multiply-add at all in b2 and b8n),
so in those fills the bit followed the burst's length and not a count of instructions; ld8's
loads break that (a 13 ms burst stayed clear). The latch was early in the job: 148 to 305 us
after the burst began in every set job but the edge one (522 us).

**What it shows and does not.** No frozen reading survives every ladder: the multiply-add count
is refuted outright, and the tile-time and burst readings fail only on the load body, where
H-WD-busy (time waiting on a load not counted) is untested, ld8 having no set point up to 320.
The latch is not at the job's end (H-END 0 of 48). Fills of 2048 pixels only; triangles are E806.

**Correction 2026-11-11:** This adds a second reading of the kept timelines, made offline in
round 4's pixel planning (`closing4/pixel/rule_px.txt`, `px_rule.out`, `fill_d6.out`), and leaves
the claim as is. [data; FIT on this record's and E804's fills, SEMI on E431's and E357's, whose
timelines were scored after the rule was written] With one constant, a tile's time (B - 60.2) / 4
against 125 us with an edge band of 118 to 132 us, the 106 load-free fills of q-f0, q-f1a and q-f1b
fall 92 on the predicted side and 14 in the band, and the 81 fills of platform/event-fine,
event-steps and event-trigger 67 and 14: 187 of 187, no miss. A latch-time model written in the
same file fits these fills and fails on the older data (30 of 48), so by its own rule it is not
offered; what stands [data] is that in the long fills the bit shows 121 to 128 us after the 3D's
clocks come on. [infer] The load body (ld8, clear to 320 iterations, bursts of 13.4 ms) does not
fit a sum of non-waiting time (that would set it near 75 iterations); either a wait ends a piece of
work and restarts the timer, or a program that waits on a load never latches. Not held out (Q082).
