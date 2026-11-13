+++
id = "E064"
claim = "Byte 0 of the render's cmd:16 word (0x88 in the job) moves the 64x64 triangle's edges: 10 of the 256 values (0x79, 0x88, 0x89, 0x97, 0x98, 0x99, 0x9a, 0xa8, 0xa9, 0xaa) leave the image as it is, the others give 26 other images whose triangle covers 1074, 1086 or 1098 pixels (or 1062 again, in a different image), and 8 is the centre of each nibble's stair; the data are pixel counts and hashes, so they do not say which nibble is x and which y"
unit = "isp"
method = "sweep of probes/isp/sample-positions.toml (sweep isp-sample-positions, host tri): all 256 values of cmd:16 bits 7:0 (255 xors plus the baseline), one job each on a fresh context, on the laptop with the linux fork and the debug option on; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-sample-positions"]
terms = [
    "CR_ISP_MULTISAMPLECTL", "CR_ISP_MULTISAMPLECTL.SAMPLE0_X", "CR_ISP_MULTISAMPLECTL.SAMPLE0_Y",
    "hw_render_details.isp_multisamplectl", "programmable sample positions",
]
+++

**What runs.** The triangle job writes 0x88 to cmd:16. Each case sets byte 0 to one of the 256
values (a xor of the job's value with the case's) and renders the 64x64 triangle. The tool counts
the pixels of triangle colour: 1062 in the baseline.

**Results.** All 256 jobs completed. 10 values give the baseline image (same hash as the unpoked
job): 0x79, 0x88, 0x89, 0x97, 0x98, 0x99, 0x9a, 0xa8, 0xa9 and 0xaa. The other 246 give 26 other
images, with 1074, 1086 or 1098 triangle pixels, one to three steps of 12 over the baseline (or 1062
again, in a different image). Moving one nibble and keeping the other at 8, the triangle pixels are:

| low nibble (bits 3:0) | 0-1 | 2-5 | 6-7 | 8-9 | a-d | e-f |
|---|---|---|---|---|---|---|
| high nibble at 8 | 1074 | 1086 | 1098 | 1062 | 1074 | 1086 |

| high nibble (bits 7:4) | 0 | 1-2 | 3-6 | 7 | 8-a | b-e | f |
|---|---|---|---|---|---|---|---|
| low nibble at 8 | 1086 | 1074 | 1086 | 1098 | 1062 | 1074 | 1086 |

The low nibble's series is a stair that grows with the distance from 8 on both sides, from 8 and 9
(no change) through a-d and e-f above, and 6-7, 2-5, 0-1 below. The high nibble's series has the
same 12-pixel step and the same centre (8 to a leave 1062), but is not monotone below 7: 0 gives
1086, 1 and 2 give 1074. With both nibbles moved the counts stay between 1062 and 1098 (0x00 gives
1062, 0xff gives 1086).

**What it does not show.** That the low nibble is the x position and the high nibble the y, and the
number of pixels each value moves, need the pixels of each image; the sweep keeps only counts and
hashes, and the tool's own check reports 0 wrong pixels in these cases (the moves stay within the
edge tolerance it allows). What the data do show is that the byte is a sampling position with a
centre at 8 on each nibble and a quantum finer than a pixel, since moving it changes only edge
pixels. The 1/16 pixel unit is not measured here. One run only.

**Correction 2026-11-13:** a note, the claim stands. E1018 (round 12 offline, a rule frozen before
the per-case counts and hashes were read) names the nibbles: with the pixel (x, y) sampled at
(x + lo/16, y + hi/16), lo = bits 3:0 and hi = bits 7:4, E606/E607's exact coverage test predicts
all 256 counts of this sweep (the 225 two-nibble values held out) and parts the values into the 27
image classes of the hashes, value for value; with the nibbles swapped 226 counts and 2 classes
hold. So the low nibble is x and the high nibble y, in sixteenths of a pixel, 8 the centre.
