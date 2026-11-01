+++
id = "E104"
claim = "In a triangle's pixel shader an instruction with .skipinv reaches exactly the 1062 covered pixels in all three repeats, and one without it also reaches 16 to 26 uncovered pixels of the quads the triangle covers, whole quads at a time (6 to 10 of the 42 partly covered quads); .skipinv skips the instances that cover no pixel"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/instance-masking.toml, probe usse-instance-masking-skipinv-tri (the 64x64 triangle's pixel shader writes o0 blue and green, one write with .skipinv, in both orders, and each write alone; every case three times, every pixel read back), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-instance-masking"]
terms = []
+++

**What runs.** Twelve cases: a `.skipinv` blue write then a plain green one, a plain blue write
then a `.skipinv` green one, the plain green write alone and the `.skipinv` green write alone,
three repeats each. The triangle covers 1062 pixels in 291 quads of 2x2 pixels: 249 quads are
fully covered and 42 partly (24 with two pixels covered, 18 with one), which leaves 102
uncovered pixels in covered quads. The `.skipinv`-only green write is the reference for the
covered set.

**Results.** Pixels outside the triangle's quads never change. Counts of pixels, by where they
fall (covered / uncovered pixel of a covered quad):

| pixel shader | covered pixels | uncovered pixels of covered quads |
|--------------|----------------|-----------------------------------|
| `.skipinv` green only | 1062 green | none (all three repeats) |
| plain green only | 1062 green | 20, 18, 18 green |
| `.skipinv` blue, then plain green | 1062 green | 22, 22, 26 green, no blue |
| plain blue, then `.skipinv` green | 1062 green | 20, 21, 16 blue, no green |

Every extra pixel lies in a quad the triangle partly covers, and in a quad that shows one extra
pixel all of its uncovered pixels show it (8, 8, 10 quads for the second row; 8, 7, 7 for the
plain green alone; 8, 8, 6 for the last row). The blue pixels of the last row are the plain
write's colour, which the `.skipinv` green write did not overwrite on the uncovered pixels.
The numbers change from repeat to repeat; no visibility counter counted in this run.

**What it shows.** An instruction without `.skipinv` runs for some instances that cover no
pixel, and its o0 reaches the tile for them; one with `.skipinv` does not run for them. Which
uncovered instances land, and why the count varies from run to run, as in E111 and E113.
