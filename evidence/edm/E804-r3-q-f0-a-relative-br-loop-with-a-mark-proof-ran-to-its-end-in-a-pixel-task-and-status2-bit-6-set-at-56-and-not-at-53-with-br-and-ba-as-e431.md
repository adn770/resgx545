+++
id = "E804"
claim = "R3-pixel stage q-f0 (10 fill jobs of 2048 pixels, all controls: loops closed by a relative `p0 br` back to the body with a MARK proof, o0 = 0xC0DE0000 | N written only where the counter reached zero, and E431's absolute `ba` loop, which ends with o0 = 0): the relative loop ran to its end on 2048 of 2048 pixels in all 6 of its rows (N = 16, 53, 53, 56, 56 and 136), so a backward relative branch loops in a pixel task as in a vertex task (E784), and the `ba` loop wrote o0 = 0 on 2048 of 2048 in its 4 rows; CR_EVENT_STATUS2 read 0x400 after every reset and, after the job, 0x400 at N = 16 and 53 and 0x440 at 56 and 136 with either branch (2 of 2 each at 53 and 56), as E431; the burst was 200 us at N = 16 and 1284 us at 136 (frozen 205 +- 125 and 1287 +- 125 from E431's fit) and bit 6 showed 211 us after the burst began at 136 (frozen 120 to 340); the frozen scorer opened the loop gate with 0 misses of 13 frozen quantities"
unit = "edm"
method = "R3-pixel stage q-f0 of the question-closing pass, round 3 (session L2, decisions R3-P1 to R3-P11; the second of six stages, started 16:10:30 Mac time, out-l2.log), dataset render-closing-r3-pixel, on the laptop (host cedar, direct cable), 2026-11-10, attempt out/20261110-160415, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), the stock firmware (core 545 rev 0x1000d, DDK 1.7.17 build 862890 in every health line), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053) and ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803), R1's builds, not rebuilt; every job after a debugfs reset, CR_EVENT_STATUS2 read from the debugfs registers after the reset and after the job, the job under regtimeline 0 0.3 0x0008,0x0118,0x012c (the burst B is the run of CR_CLKGATESTATUS 0x0008 not idle, t6 and t7 the time of the first sample with bit 6 or 7 of 0x0118 from the burst's start); freeze FROZEN.sha256 8a0fa9aa... and PREDICTIONS.sha256 d1cdc86b... before the first job; health ok after every stage; each job `probe PROGRAM` (a fill) with the program staged from bins/ (loop-rel-b8-iN.bin: prologue, E431's eight-instruction body with six multiply-adds, the counter, `p0 br` back; loop-abs-b8-iN.bin: E431's `ba` loop); the loop proof, the bit and the burst read by the frozen score/score_r3.py q-f0 (out/score-q-f0.txt); the driver gated q-f1a, q-f1b and q-t on its kept output (gate-*.txt: open)"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-pixel:out/20261110-160415/q-f0/"]
terms = ["CR_EVENT_STATUS2", "CR_CLKGATESTATUS", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E770's triangle loops were void, and the note of 2026-11-10 on it read the cause as
the absolute `ba` that closed them, which counts from the code base. Round 3 closes every loop with
a relative `p0 br` and ends with `xor.end o0, r1, r30` (r30 = MARK from the prologue), so a pixel
holds MARK only if its counter reached zero; an unwritten output register cannot pass. A backward
`br` had run in a vertex task (E784), never in a pixel task: this stage is the gate of every later
pixel loop (a failed proof stops it, rc 17, and the pixel loop stages are skipped).

**Frozen verdict (as printed).** `q-f0 loop gate OPEN: rel loop proved on 6 rows; frozen bits all
as E431 (53 clear, 56 set); 0 misses of 13 frozen quantities`.

**Results [HW].**

| job | branch | N | o0 on 2048 pixels | STATUS2 after | burst B (us) | t6 (us) |
|---|---|---|---|---|---|---|
| f0-rel-b8-53, -53b | br | 53 | 0xc0de0035 (2048, 2048) | 0x400, 0x400 | 520, 532 | - |
| f0-rel-b8-56, -56b | br | 56 | 0xc0de0038 (2048, 2048) | 0x440, 0x440 | 557, 561 | 283, 283 |
| f0-abs-b8-53, -53b | ba | 53 | 0 (2048, 2048) | 0x400, 0x400 | 531, 534 | - |
| f0-abs-b8-56, -56b | ba | 56 | 0 (2048, 2048) | 0x440, 0x440 | 554, 557 | 275, 285 |
| f0-rel-b8-16 | br | 16 | 0xc0de0010 (2048) | 0x400 | 200 | - |
| f0-rel-b8-136 | br | 136 | 0xc0de0088 (2048) | 0x440 | 1284 | 211 |

STATUS2 read 0x400 after every reset (10 of 10).

**What it shows and does not.** A relative backward branch loops in a pixel program, and the two
loop forms set bit 6 at the same points in a fill, so E431's and E769's fill readings (absolute
loops at code index 0) stand and the loop form is not a variable of the latch. Fills only: the
loop in a placed `--tri` slot is E806's.
