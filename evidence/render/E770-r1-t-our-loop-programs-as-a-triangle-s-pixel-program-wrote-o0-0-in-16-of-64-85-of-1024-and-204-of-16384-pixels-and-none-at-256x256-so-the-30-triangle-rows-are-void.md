+++
id = "E770"
claim = "Our loop programs (E769's: 6 multiply-adds, a counter update and a branch an iteration, o0 written from the counter) run as the pixel program of a probe --tri pixel triangle left the image with o0 = 0 in only some of the pixels, the same ones whatever the iteration count: 16 of 64 pixels on 8x8 (with two stray words, 0x04000004 and 0x40800000, and 46 untouched; 12 jobs, T3 at 53 to 440 iterations and T4's load body at 20 to 56), 85 of 1024 on 32x32 (6 jobs, 53 to 440), 204 of 16384 on 128x128 at 53 iterations (with 18 pixels of 0xff00ff00, one of 0x881d6bc1 and 159 others) and no pixel at all on 128x128 at 56, 80, 130, 220 and 440 iterations and on 256x256 at 53 to 440 (the probe printed 'o0 0xff203040 (16384 of 16384)' and '(65536 of 65536)', rc 0 in all 11 jobs), and CR_EVENT_STATUS2 read 0x400 after every one of the 30 triangle jobs; the loops did not run, or did not write, in most of the pixels the triangles cover, so the 30 triangle rows (T3's four sizes, T4's 8x8 ladder) are void as readings of bit 6 and the occupancy and load-latency questions are not answered; the fill ladders of E769 are not affected"
unit = "render"
method = "R1-events stage t of the question-closing pass, round 2, the T3 jobs (targets of 8x8, 32x32, 128x128 and 256x256 at 53, 56, 80, 130, 220 and 440 iterations each) and the T4 jobs on 8x8 (20, 30, 40, 50, 53 and 56 iterations of the load body), run 1794299292-1110 of the dataset edm-closing-r1-events, the method of E769 for the rest (stock firmware, a debugfs reset and a pre read of 0x400 before each job, the tool ~/sgxfive-test-s1b, 2026-11-10 09:28 laptop time, kernel 7.3.0-resgx545); each job the tool's probe --tri pixel with the loop program as the triangle's pixel program, rc 0 and a completed job; the frozen scorer counted the pixels reading o0 = 0 and gave no result for a job with none (11 jobs: the 128x128 target from 56 iterations and all of the 256x256 target); the pixel counts of the tool's output were read after the run"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r1-events:out/t/"]
terms = ["CR_EVENT_STATUS2"]
+++
**What ran.** T3 was to read the latch against occupancy (smaller triangles, fewer resident
instances) and T4 the load's latency on an 8x8 triangle. The stage ran the same loop programs as
E769's fills, replacing the pixel program of the tool's triangle.

**Frozen verdict.** The 128x128 jobs of 56, 80, 130, 220 and 440 iterations and the six 256x256
jobs: void (the scorer's words: `no o0 = 0 pixel in the tool output: the loop did not end or the
job did not draw`), 11 jobs. The
other 19 triangle jobs the scorer read as `status2 0x400 after (pre 0x400), o0 = 0 on 16, 85 or 204
pixels` and used as clear points of the ladders (`T3 first-set iterations by size {8: None, 32:
None, 128: None, 256: None}`, `T4 ... tri8 [(20, False), ... (56, False)]`). Those points are not
usable, for the reasons below, and the scorer's verdicts that use them (T3 None, the tri8 half of
T4) are set aside here.

**Results [HW].** The number of pixels written does not move with the iteration count (16 on 8x8
at all twelve counts, 85 on 32x32 at all six) and is a small share of the target (1% at
128x128, 8% on 32x32, 25% on 8x8), fewer than a triangle of the kind of the 64x64 health triangle
covers (1062 of 4096, the tool's own line) [infer: the probe's triangle is not that one, its
covered count was not read]. At 128x128 the loop wrote 204 pixels at 53 iterations and no pixel at
56 or more, and on 256x256 none at any count; the image there was the background in every pixel.
Two 8x8 pixels held words that are not the loop's output (0x04000004, 0x40800000), and 128x128 at
53 iterations held 159 words of other values. `CR_EVENT_STATUS2` read 0x400 after all 30 jobs, among
them those of 440 iterations, where E769's fill with a body of 8 sets bit 6 from 56.

**Post hoc [infer; read after the run, not held out].** Whether the loop ended in the pixels that
did not write o0 is not known: a pixel that kept the background may not have run the program, may
have run it to a different end, or may have been overwritten. So the 0x400 after these jobs is
neither a clear point nor a set point of the latch. That a loop program that completes as a fill's
program (E769: o0 = 0 on 2048 of 2048 pixels) does not as a triangle's program is a fact about the
probe's triangle mode with our programs, not about bit 6; why is not shown (the program's size
against the pixel task's, the scratch buffer and the instance count are candidates that were not
told apart).

**Not shown.** The occupancy knob for the latch (a fill at another size is the untried way), the
load's latency on a small target, and why a triangle's pixels do not complete the loop.
