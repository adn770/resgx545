+++
id = "E071"
claim = "0x041c (rd:5) is the polygon offset in units of one ulp of the stored depth, 0x0424 (rd:7) caps the offset at its value with 0 meaning no cap and a negative cap leaving a positive offset alone, and the offset needs ISP1 bit 23; 0x0420 (rd:6) at 4.0 adds nothing to the flat triangle"
unit = "isp"
method = "the hand script depth-test.sh of probes/isp/depth-test.toml (function polygon_offset_clamp): the flat 64x64 triangle (depth 0.5, depth test less, depth written, ISP1 bit 23 poked on) with its depth stored through the ZLS into a scratch buffer filled with 1.0, 5 values of rd:5 times 5 of rd:7, on the laptop with the linux fork and the debug option on; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-depth-test"]
terms = [
    "CR_ISP_POLY_OFFSET_UNITS", "CR_ISP_POLY_OFFSET_FACTOR", "CR_ISP_POLY_OFFSET_CLAMP",
    "hw_render_details.poly_offset_units", "hw_render_details.poly_offset_factor",
    "hw_render_details.poly_offset_clamp", "ISP1.POLY_OFFSET",
]
+++

**What runs.** The ZLS store is set up (`ta:7` bit 7, the ZLS base, store control 0x17100c, the
store base at the scratch buffer), the scratch buffer is filled with 0x3f800000 (1.0), and the
triangle renders at depth 0.5 (0x3f000000) with ISP0 = 0x00400200. After each job the script prints
how many scratch dwords changed and the first changed dword of each of the first four pages. Every
job reported `job: ok`, 1062 dwords changed in four pages (120, 594, 312 and 36) and an image that
matches the CPU's, as many dwords as the triangle has pixels. In each case the four pages show the
same first value.

**Results.** With ISP1 bit 23 poked on, the first stored dword (units in rd:5, clamp in rd:7):

| rd:5 units | clamp 0 | 0.01 | -0.01 | 1.0 | 0x00000010 |
|---|---|---|---|---|---|
| 0 | 0x3f000000 | 0x3f000000 | 0x3f000000 | 0x3f000000 | 0x3f000000 |
| 1 | 0x3f000001 | 0x3f000001 | 0x3f000001 | 0x3f000001 | 0x3f000000 |
| 16 | 0x3f000010 | 0x3f000010 | 0x3f000010 | 0x3f000010 | 0x3f000000 |
| 4096 | 0x3f001000 | 0x3f001000 | 0x3f001000 | 0x3f001000 | 0x3f000000 |
| 1048576 | 0x3f100000 | 0x3f028f5c | 0x3f100000 | 0x3f100000 | 0x3f000000 |

The clamp columns are 0x3c23d70a (0.01), 0xbc23d70a (-0.01), 0x3f800000 (1.0) and the denormal
0x00000010. The stored depth is 0.5 plus exactly rd:5 ulps (an ulp of 2^-24 at 0.5), up to 2^20
(0.0625). A clamp of 0.01 caps only the largest offset, to 0.51 (0x3f028f5c); the denormal clamp
caps every non-zero offset to nothing (0.5); a negative clamp and a clamp of 1.0 do nothing, and 0
is no cap. Separately, rd:6 (0x0420) at 4.0 with rd:5 at 0 stores 0x3f000000 (no change), and
without the ISP1 bit 23 poke, rd:5 at 4096 stores 0x3f000000 too: the offset needs the flag.

**What it does not show.** The first dword of four pages stands for the stored triangle: the other
dwords were counted, not printed, and a per-pixel difference in the offset (as a slope term would
give) is not excluded for them. rd:6 was tried only on the flat triangle, where it has no slope to
act on, so what it multiplies is not shown. The clamp shows for one offset that exceeds the clamp;
negative offsets were not tried.
