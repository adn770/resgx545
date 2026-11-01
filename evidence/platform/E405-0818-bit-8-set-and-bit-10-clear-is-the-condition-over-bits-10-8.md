+++
id = "E405"
claim = "Of 24 values of 0x0818 (bits 10:8 in every combination, a low byte of 0x00, 0x7f or 0xff), exactly the six with bit 8 set and bit 10 clear (bit 9 either) make the second of two triangles of different sizes draw wrong, with the same count of wrong pixels in all three repeats (2439 of 16384 for 96 then 128, 2155 of 9216 for 128 then 96); the other 18 draw exactly"
unit = "platform"
method = "probes/platform/register-limits-combos.toml (register-limits-combos.sh) on the laptop, linux fork f1fad0ed9d0e with the debug option on: each value written through kreg, the two triangles of a pair run as two tool processes (a fresh context each), the register restored to 0x7ff; 24 values, the pairs 96 then 128 and 128 then 96, three repeats (144 runs of two jobs)"
tiers = ["HW"]
date = "2026-11-07"
data = ["platform-register-limits-combos"]
terms = ["CR_REG_0818"]
+++

**Cases.** The values `hi << 8 | lo` for hi 0 to 7 (bits 10:8) and lo 0x00, 0x7f and 0xff, with both
pairs of sizes, three repeats: 24 values x 2 pairs x 3 repeats = 144 runs. The first job of each
pair drew exactly in all 144.

**What was seen.** The second job drew wrong for 0x100, 0x17f, 0x1ff, 0x300, 0x37f and 0x3ff (hi 1
and 3: bit 8 set, bit 10 clear, bit 9 clear and set; the three low bytes), with 2439 wrong pixels
of 16384 for 96 then 128 and 2155 of 9216 for 128 then 96, the same counts in all three repeats
(36 of 36 runs of those values). For the other 18 values (0x000, 0x07f, 0x0ff, 0x200, 0x27f, 0x2ff,
0x400 to 0x7ff) both jobs drew every pixel exactly in all three repeats (108 of 108). The counts
equal those of E404's pairs at 0x3ff.

**What it shows.** The condition E404 found among 32 values holds over bits 10:8 and three low
bytes: bit 8 set and bit 10 clear, whatever bit 9 and these low bytes. The wrong pixels are the
same in every repeat, so the effect is deterministic here.

**What it does not show.** What bit 8 and bit 10 do (a state the render path keeps from one render
to the next [infer]); whether other low bytes matter (three of 256 tried); pairs of equal sizes
with moved geometry, which E404's equal-size pairs did not cover.
