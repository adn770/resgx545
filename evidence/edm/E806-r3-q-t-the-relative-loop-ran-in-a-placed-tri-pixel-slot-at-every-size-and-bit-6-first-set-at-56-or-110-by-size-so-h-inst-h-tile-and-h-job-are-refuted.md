+++
id = "E806"
claim = "R3-pixel stage q-t (93 jobs: triangles that cover the whole target, `probe --tri pixel --tri-full`, at 8x8, 16x16, 32x16, 32x32, 64x32, 128x128 and 256x256, the pixel program in the --tri slot at code index 0x20 closed by a relative br with E804's MARK proof; 7 stock green controls, 7 loops at N = 1 and the 64x32 bridge at N = 53 and 56 as controls, the ladders N = 4 to 3520 and three 4x4 rows HELD OUT, three exploratory rows on the default 64x64 triangle): all 90 full-target jobs wrote their value on every pixel of the target (green or the MARK of their N, W x H of W x H) and STATUS2 read 0x400 after every reset, so the relative loop runs to its end in a placed --tri slot; the bridge FAILED (the 64x32 triangle was clear at 53 and at 56, where E804's fill of the same 2048 pixels set), so the frozen cells were scaled by 110 / 56; bit 6 first set at N = 56 at 32x16, 32x32 and 128x128 (clear at 53) and at 110 at 8x8, 16x16, 64x32 and 256x256 (clear at 56), at 220 at 4x4 (clear at 56), every ladder monotone; the frozen first-set points of a per-instance threshold (which carries H-MA), a per-tile one (32x16 tiles, which carries H-WD) and a per-job one were REFUTED at 4, 6 and 6 of the 8 sizes; in 28 of the 32 jobs set at N >= 1.3 times their size's first set point bit 6 showed 120 to 340 us after the burst began; on the default triangle (1062 covered pixels) the loop wrote its MARK on the 1062 and bit 6 stayed clear at 53, 56 and 110"
unit = "edm"
method = "R3-pixel stage q-t of the question-closing pass, round 3 (session L2, decisions R3-P2, R3-P5 and R3-P8; the fifth stage, started 16:20:50 Mac time, out-l2.log), dataset render-closing-r3-pixel, on the laptop (host cedar, direct cable), 2026-11-10, attempt out/20261110-160415, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), the stock firmware (core 545 rev 0x1000d, DDK 1.7.17 build 862890 in every health line), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803), R1's builds, not rebuilt; every job after a debugfs reset, CR_EVENT_STATUS2 read from the debugfs registers after the reset and after the job, the job under regtimeline 0 0.3 0x0008,0x0118,0x012c (the burst B is the run of CR_CLKGATESTATUS 0x0008 not idle, t6 and t7 the time of the first sample with bit 6 or 7 of 0x0118 from the burst's start); freeze FROZEN.sha256 8a0fa9aa... and PREDICTIONS.sha256 d1cdc86b... before the first job; health ok after every stage; each job `probe --tri pixel --temps 32 --width W --height H --tri-full PROGRAM` (the exploratory rows without --tri-full) with pix_green.bin or loop-rel-b8-iN.bin (E804's eight-instruction body) from bins/; the generator refused `ba` for a --tri slot (decision R3-P1); the gate was q-f0's kept output (gate-q-t.txt: open); scored by the frozen score/score_r3.py q-t (out/score-q-t.txt): the proof, the first set point per size against the frozen cells of each hypothesis, the time of the latch; the per-job bursts quoted in the body were read after the run with the session's own reader (score/r3job.py)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-pixel:out/20261110-160415/q-t/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E770's triangle loops never ran (the absolute branch, E770's note); q-t is the first
working loop in a triangle's pixel program. A triangle covering the whole target at seven sizes
gives 1 to 128 tiles of 32x16 at the same per-pixel work, so a per-instance threshold (which
carries H-MA), a per-tile one (which carries H-WD) and a per-job one predict different first set
points by size. The 64x32 bridge ties the triangle to the 2048-pixel fill of
E804 (frozen: clear at 53, set at 56).

**Frozen verdict (paraphrased: the printed line names the three hypotheses by labels).** The
per-instance threshold refuted at 32x16, 32x32, 128x128 and 4x4; the per-tile one at 8x8, 16x16,
32x16, 32x32, 128x128 and 4x4; the per-job one at 8x8, 16x16, 32x16, 32x32, 256x256 and 4x4 (4x4
named twice in the tile and job lists, for two of its three rows); `bridge FAILED; reference N 110;
void sizes []; control problems none`.

**Results [HW].**

| size | last clear N | first set N | burst at last clear / first set (us) | per instance | per tile | per job |
|---|---|---|---|---|---|---|
| 8x8 | 56 | 110 | 242 / 335 | ok | MISS | MISS |
| 16x16 | 56 | 110 | 288 / 429 | ok | MISS | MISS |
| 32x16 | 53 | 56 | 281 / 301 | MISS | MISS | MISS |
| 32x32 | 53 | 56 | 399 / 411 | MISS | MISS | MISS |
| 64x32 | 56 | 110 | 746 / 1268 | ok | ok | ok |
| 128x128 | 53 | 56 | 4084 / 4313 | MISS | MISS | ok |
| 256x256 | 56 | 110 | 16736 / 32493 | ok | ok | MISS |
| 4x4 | 56 | 220 | 190 / 306 | MISS | MISS | MISS |

Ladders: N = 4, 14, 28, 53, 56, 110, 220, 440, 880, 1760, 3520 (128x128 to 880, 256x256 to 220,
4x4 at 56, 220 and 880). The bridge jobs: o0 MARK on 2048 of 2048, STATUS2 0x400 after both.

**Read after the run [infer, no frozen row].** Unlike the fills of E805, the burst does not place
the bit in triangles: 32x16 set at a 301 us burst while 128x128 stayed clear at 4084 us. The first
set N is 56 or 110 at every size from 8x8 up, with no order in the size (32x16 and 128x128 at
56, 16x16 and 64x32 at 110). At 128x128 N = 56 the bit showed 4026 us after the burst began, the
only set job outside 120 to 351 us.

**What it shows and does not.** The loop form of E804 works in a placed --tri slot at every size
run, so E770's void is repaired for the program side; the absolute branch was not rerun in a slot
(the generator refuses it). None of the three frozen scalings of the threshold places the first
set point, and the triangle does not set where the fill of the same pixel count does (the
bridge). One run a point.
