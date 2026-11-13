+++
id = "E1018"
claim = "Round 12 offline (Q201, on E064's kept sweep; no run): E606/E607's exact coverage test with each pixel (x, y) sampled at (x + lo/16, y + hi/16), lo = bits 3:0 and hi = bits 7:4 of cmd:16 (CR_ISP_MULTISAMPLECTL byte 0), predicts the triangle-pixel count of all 256 values of E064's sweep of the 64 x 64 triangle (31 of 31 one-nibble values E064 tabled, 225 of 225 two-nibble values held out) and parts the 256 values into exactly the 27 classes of the hardware's image hashes, 256 of 256 values in the right class; the rivals fail: the nibbles swapped 226 of 256 counts and 2 of 27 classes, a fixed centre 51 counts and one class, ((n + 0.5)/16) 197 counts and 0 classes; so 0x88 is the pixel centre and 0x26, under which E502 and E1010 read the position source at x + 0.375, y + 0.125, is the point (6, 2)/16 [HW data; infer: the position source reads the point byte 0 places, as the coverage sample does, since E437 read x + 0.5 under 0x88 and no kept job iterates a coordinate set under another byte 0]"
unit = "isp"
method = "Offline, no run (round 12, decision R12-2 a of the round 12 lead and closing12/plan/rank-round12.md, finding 1). Data: E064's sweep, raw.txt of the isp-sample-positions dataset (256 cases: the baseline 0x88 and 255 cases cmd:16^=X, byte 0 = 0x88 ^ X; per case the tool's triangle count and target hash). Check closing12/plan/c6-q201/: the rule sample0_rule.py (sha256 a1980fa58965057c11c9c2950f5cb342ae2050e63082388f71065c5c138c4b73, 2026-11-13T12:19:34Z in FREEZE.log, frozen after reading only the baseline and the ^=0x1 case of raw.txt, report.txt's head and the diff: column, all 256 zero and not scored), E606/E607's coverage ported from sgx-pipe's Tri::covers on the tool's triangle (8, 8), (56, 20), (20, 56) pixels, x = low nibble decided before the freeze from E278 and E339; scorer score.py (score.out); pass: all 256 counts equal and the partition of the 256 values by predicted image equal to the partition by observed hash. Fit-ish: the 31 one-nibble values of E064's tables; held out: the 225 others and the partition. This fold re-ran score.py with python -I and got byte-identical output, and sgx-pipe's isp::coverage_image_sampled replays the 256 values (tests/isp_sample_point.rs)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["isp-sample-positions", "cited-scratch:closing12/plan/c6-q201/", "cited-scratch:closing12/plan/rank-round12.md"]
terms = ["CR_ISP_MULTISAMPLECTL", "CR_ISP_MULTISAMPLECTL.SAMPLE0_X", "CR_ISP_MULTISAMPLECTL.SAMPLE0_Y"]
+++
**What was done.** E064 swept byte 0 of the render's cmd:16 word (`CR_ISP_MULTISAMPLECTL`, 0x88 in
the library's job) through all 256 values on the 64 x 64 triangle and kept, per value, the
triangle-pixel count and the image hash: 27 images, counts 1062 to 1098, and no pixels. It did not
say which nibble is x. The round 12 planner froze one rule before reading the per-case counts and
hashes: the single-sampled pixel is sampled at (x + lo/16, y + hi/16) with lo the low nibble and
hi the high one (E278: each sample byte is x in bits 3:0, y in bits 7:4; E339: 0x26 is (6, 2)),
and covered by E606/E607's exact edge test with the top-left tie rule at that point. The rule
scored the counts of all 256 values and the partition of the values into classes of equal image,
against three rivals.

**Results (score.out).** The rule held all 256 counts (31 of the 31 one-nibble values E064
tabled, 225 of the 225 values with both nibbles moved, never fitted) and its 27 predicted image
classes are the 27 observed hash classes, value for value. With the nibbles swapped 226 counts
hold and 2 of 27 classes; a fixed sample at the centre gives one image and 51 counts; samples at
((n + 0.5)/16) give 197 counts, 28 classes and none of them right (it also moves 0x88 off the
centre). The `diff:` column is 0 in every case: the tool's own edge-tolerant check, not used.

**What it shows.** [HW data] Byte 0 is the single-sampled pixel's sample point: x in bits 3:0, y
in bits 7:4, in sixteenths of a pixel from the pixel's top-left corner, with E606's exact test and
tie rule at that point. 0x88 is E606's pixel centre. E064's "8 is the centre of each nibble's
stair" is the point (0.5, 0.5), and its "which nibble is x" is now named: the low one.
[infer] E437 read the position source at x + 0.5, y + 0.5 under 0x88, and E502 and E1010 read it
at x + 0.375, y + 0.125 under 0xeaa26e26, whose byte 0 is 0x26, the point (6, 2)/16: the position
source reads the point byte 0 places, as the coverage does, and the two readings differ by setup,
not by hardware. sgx-pipe models the sample point (`isp::sample_offset`,
`isp::coverage_image_sampled`, any byte 0 on the 64 x 64 target, test
`tests/isp_sample_point.rs`) and refuses an attribute iterated under a byte 0 other than 0x88
(`iter::sample_point`, Q201).

**What it does not show.** The images: only counts and hashes are kept, so equal hashes were
matched to equal predicted images by class, not pixel for pixel. One triangle, one target, one run;
bytes 1 to 3 at 0. That an iterated coordinate set reads at the same point: no kept job iterates
one under a byte 0 other than 0x88 (E606's setups all ran under 0x88). Refuted by: a byte 0 value
whose count or image class differs from the rule's on another triangle, or a position source read
under 0x88 off x + 0.5, or under another byte 0 off its point.
