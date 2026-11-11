+++
id = "E841"
claim = "R4-pixel stage q4-t (Q082 bit 6 in triangles, 54 jobs: E806's relative 8-instruction loop with a MARK as the pixel program of the tool's triangle covering a W x H target, `--tri-full`): the 12 controls passed (the green triangle and the loop at N = 1 at 4x4, 8x8, 16x16, 32x16 and 64x32 clear with the MARK or green on every pixel; the 64 x 32 fill clear at 53 and set at 56, E804); bit 6 first set in (96, 104] at 8x8, (140, 170] at 4x4, (56, 60] at 32x16 and (60, 66] at 64x32, and 16x16 stayed clear at 46, 56 (twice), 60, 66 and 72; frozen verdict 'q4-t consistent none, refuted ['H-SEG', 'H-N', 'E806-DISC']': H-SEG (no progress for about 125 us, a piece of work at most a tile) REFUTED by 16x16 clear at 66 and 72 (21 held, 2 FAILED, 15 cannot tell of 38), H-N (a pass count near 57 to 62 at every size) REFUTED (18 held, 10 FAILED, 10 cannot tell), E806-DISC (56 or 110, 220 at 4x4) REFUTED (31 held, 7 FAILED); the time of the latch held the frozen first-piece reading (t6 = 250 + 0.43 N us after the burst's start to N = 290, then 250, +- 15) in 8 of 8 rows at 8x8 and 64x32, N 150 to 330 (t6 252 to 357 us)"
unit = "edm"
method = "R4-pixel stage q4-t of the question-closing pass, round 4 (decision: triangles a, the t6 row, without 2x2; plan closing4/pixel/exp-pixel-r4.md section 3.3), dataset render-closing-r4-pixel, on the laptop (host cedar, direct cable), 2026-11-11, attempt out/20261111-210423 (the second stage of the attempt, started 21:06 Mac time; run2.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803); the freeze of the first attempt (FROZEN.sha256 f9b0fa03...), no refreeze; every job after a debugfs reset, STATUS2 0x400 after the reset and read after the job, under `regtimeline 0 0.3 0x0008,0x0118,0x012c` (B the run of CR_CLKGATESTATUS not idle, t6 the first sample with bit 6 from the burst's start); each triangle job `probe --tri pixel --temps 32 --width W --height H --tri-full loop-rel-b8-iN.bin` (gen/r4loops.py, checked in sgx-sim), the fill controls `probe loop-rel-b8-iN.bin`, the stock green triangle `pix_green.bin`; four exploratory jobs on the default (partial) 64 x 64 triangle with no prediction; health ok after the stage; scored by the frozen score/score_r4.py q4-t (out/20261111-210423/score-q4-t.txt, gate-q4-t.txt: PASS), both reproduced byte for byte at the fold (2026-11-11)"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-pixel:out/20261111-210423/q4-t/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E806 found bit 6 in covering triangles first set at 56 iterations at some sizes, at
110 at others and at 220 at 4x4, with no order in the size. Read after its run (Q082's note of
2026-11-11), a tile's time at every size's last clear and first set point brackets 120 to 160 us.
Q4-t holds three readings out: H-SEG (the pixel side latches after about 125 us without progress,
progress being the end of a piece of work of at most a tile: 8x8 first set in 72 to 104, 4x4 clear
to 140, 16x16, 32x16 and 64x32 set at 66 and 72), H-N (a pass count near 57 to 62 at every size)
and E806-DISC (the first set points as E806 read them, 56 or 110, 220 at 4x4). A row at 150 to 330
iterations tests the time of the latch (the "first piece" reading).

**Frozen verdict (as printed).** `H-SEG: REFUTED (21 held, 2 FAILED, 15 cannot tell of 38)`,
`H-N: REFUTED (18 held, 10 FAILED, 10 cannot tell of 38)`, `E806-DISC: REFUTED (31 held, 7 FAILED,
0 cannot tell of 38)`, `first-piece reading of the latch time (t6 = 250 + 0.43 N to N = 290, then
250 us, +- 15): 8 held, 0 FAILED, 0 cannot tell of 8`, `SUMMARY: q4-t consistent none, refuted
['H-SEG', 'H-N', 'E806-DISC']; latch time 8 held, 0 FAILED, 0 cannot tell of 8`; `gate q4-t:
PASS`.

**Results [HW].** Bit 6 after the job (c, S), the burst B and t6 in us.

| size | N: bit 6 (B) | first set |
|---|---|---|
| 4x4 | 80 c (199), 110 c, 140 c (255), 170 S (267, t6 253), 200 S (292, t6 251) | (140, 170] |
| 8x8 | 60 c (247), 66 c, 72 c, 80 c, 88 c, 96 c (313), 104 S (322, t6 295) | (96, 104] |
| 16x16 | 46 c (265), 56 c, 56 c, 60 c, 66 c, 72 c (323) | above 72 |
| 32x16 | 46 c (267), 56 c, 56 c (288), 60 S (294, t6 246), 66 S, 72 S | (56, 60] |
| 64x32 | 46 c (617), 56 c, 56 c, 60 c (757), 66 S (822, t6 438), 72 S (878, t6 285) | (60, 66] |

The t6 rows: 64x32 at 150, 180, 250, 330 set with t6 317, 329, 357, 255 us (B 1666 to 3470); 8x8
at the same N set with t6 317, 325, 347, 252 (B 400 to 702). The exploratory default 64 x 64
triangle set at 150, 200, 280 and 400 (t6 567, 681, 845 and 250 us; B 1197 to 2940). The two
replicates at 56 agreed at every size.

**What it shows and does not.** In a triangle that covers the target, bit 6 first sets between 56
and 170 iterations of the same loop depending on the target's size, and the order is not the pixel
count's: 32x16 (512 pixels) at 60, 64x32 (2048) at 66, 8x8 (64) at 104, 4x4 (16) at 170, while 16x16
(256) stays clear to 72 (E806: set at 110). None of the three frozen readings places all five sizes:
not one pass count (H-N), not E806's discrete points (E806-DISC), and not a tile's time with a tile
as the largest piece of work (H-SEG fails only at 16x16, where the burst at 72, 323 us, is as long
as 32x16's set job at 66). The time of the latch held: in the long rows bit 6 shows 250 to 360 us
after the burst begins, rising with N to about 290 iterations, as written before the run. [infer] A
piece of work other than a tile, such as a task of instances, could place 16x16 with the others;
that is not tested. Not shown: the quantity bit 6 follows in a triangle; why the fill sets at 56
when the 64x32 triangle sets in (60, 66]; 16x16 beyond 72.
