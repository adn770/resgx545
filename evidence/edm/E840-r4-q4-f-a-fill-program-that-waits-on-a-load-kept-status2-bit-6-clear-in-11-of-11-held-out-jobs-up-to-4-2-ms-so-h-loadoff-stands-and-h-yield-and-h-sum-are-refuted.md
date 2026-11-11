+++
id = "E840"
claim = "R4-pixel stage q4-f (Q082 bit 6, 16 fills of 64 x 32 whose pixel program ends in a MARK only when its loop counters end): the five bridge controls to E804 and E805 passed on the rgn4 module (the relative 8-instruction loop clear at 16 and 53, set at 56 and 136 iterations; E805's load body ld8 clear at 70); in 11 of 11 held-out jobs whose program waits on a load, one load then the 8-instruction ALU loop K times (K = 28, 53, 70, 110) or M rounds of a load and K iterations ((K, M) = (28, 4), (28, 16), (40, 8), (70, 1), (70, 4), (110, 2), (220, 1)), bit 6 stayed clear, with bursts of 311 us to 4.2 ms, also where the ALU loop after the load ran 70 to 220 iterations, longer than the 56 that sets it without a load; frozen verdict 'q4-f H-LOADOFF alone is consistent (H-YIELD, H-SUM refuted)' (H-LOADOFF 11 held of 11, H-YIELD 4 held 6 FAILED 1 cannot tell, H-SUM 1 held 9 FAILED 1 cannot tell)"
unit = "edm"
method = "R4-pixel stage q4-f of the question-closing pass, round 4 (plan closing4/pixel/exp-pixel-r4.md section 3.2), dataset render-closing-r4-pixel, on the laptop (host cedar, direct cable), 2026-11-11, attempt out/20261111-210423 (run/r4.sh --from q4-f after the lead's decision on q4-v's last row, E839; the first stage of the attempt, started 21:04:23 Mac time; run2.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803); the same freeze as the first attempt (FROZEN.sha256 f9b0fa03..., verified at the attempt's start), no refreeze; every job after a debugfs reset, STATUS2 0x400 after the reset, read again after the job, the job under `regtimeline 0 0.3 0x0008,0x0118,0x012c` (the burst B is the run of CR_CLKGATESTATUS not idle, d6 the time of the first sample with bit 6 from the burst's start); the programs from gen/r4loops.py (two-level counters, the load `ldad.bypassl1` and `wdf` of E769's ld8 body, MARK on o0 only when both counters end, each checked in sgx-sim at code index 0), each job `probe PROGRAM` (the tool's default fill, 64 x 32); MARK on every pixel proved the loops; health ok after the stage; scored by the frozen score/score_r4.py q4-f (out/20261111-210423/score-q4-f.txt, gate-q4-f.txt: PASS), both reproduced byte for byte at the fold (2026-11-11); d6 was recorded with no prediction"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-pixel:out/20261111-210423/q4-f/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** In E805 every ALU body set bit 6 in a fill once a tile's time passed about 125 us,
and the body with a load and a wait (ld8) never did, to 320 iterations and bursts of 13.4 ms.
Three readings were left (Q082's note of 2026-11-11): H-YIELD, a wait ends a piece of work and
the timer starts again at every load (so an ALU loop long enough after the last load sets it);
H-LOADOFF, a program that waits on a load never latches; H-SUM, the tile's busy time with waits
not counted is summed. Q4-f puts one load in front of the loop that sets the bit on its own
(ld0-K) and alternates loads with loops (ldo-K-M).

**Frozen verdict (as printed).** `H-YIELD: REFUTED (4 held, 6 FAILED, 1 cannot tell of 11)`,
`H-LOADOFF: consistent (11 held, 0 FAILED, 0 cannot tell of 11)`, `H-SUM: REFUTED (1 held, 9
FAILED, 1 cannot tell of 11)`, `SUMMARY: q4-f H-LOADOFF alone is consistent (H-YIELD, H-SUM
refuted)`; `gate q4-f: PASS`.

**Results [HW].** Bit 6 after the job and the burst B.

| job | set | program | bit 6 | B us | frozen: YIELD / LOADOFF / SUM |
|---|---|---|---|---|---|
| f-rel-b8-16, -53 | control | the 8-instruction loop, 16 and 53 times | c, c | 198, 531 | c, c |
| f-rel-b8-56, -136 | control | the same, 56 and 136 times | S, S | 558, 1309 | S, S |
| f-ld8-70 | control | E805's ld8, 70 times | c | 2973 | c |
| f-ld0-k28 | held out | one load, then the loop 28 times | c | 311 | c / c / c |
| f-ld0-k53 | held out | one load, then 53 | c | 534 | either / c / either |
| f-ld0-k70 | held out | one load, then 70 | c | 689 | S / c / S |
| f-ld0-k110 | held out | one load, then 110 | c | 1077 | S / c / S |
| f-ldo-k28-m4 | held out | 4 x (load, 28) | c | 1097 | c / c / S |
| f-ldo-k28-m16 | held out | 16 x (load, 28) | c | 4198 | c / c / S |
| f-ldo-k40-m8 | held out | 8 x (load, 40) | c | 2996 | c / c / S |
| f-ldo-k70-m1 | held out | 1 x (load, 70) | c | 700 | S / c / S |
| f-ldo-k70-m4 | held out | 4 x (load, 70) | c | 2653 | S / c / S |
| f-ldo-k110-m2 | held out | 2 x (load, 110) | c | 2052 | S / c / S |
| f-ldo-k220-m1 | held out | 1 x (load, 220) | c | 2039 | S / c / S |

**What it shows and does not.** One load and wait at the start of a fill's pixel program keeps bit 6
clear even when the ALU loop after it runs 70, 110 or 220 times, two to four times the 56 that sets
it without the load; so the load does not restart a timer (H-YIELD) and the tile's busy time is not
summed (H-SUM): with a load anywhere in the program this latch was not seen. [infer] Whatever the
latch watches is not armed, or is reset for good, once an instance waits on memory; a hardware
reason (the instance leaves the ALU's run queue, a watchdog that counts only for programs that never
wait) is not shown. Not shown: a load after the loop instead of before, a load without its `wdf`, a
texture fetch, bit 6 in a triangle (E841), and bit 7 with a load (no vertex loop with a load was
run).
