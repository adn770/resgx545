+++
id = "E282"
claim = "ISP word 0 bits 24:22 are the depth compare, 0 never, 1 less, 4 greater, 7 always, and 2 equal, 3 less or equal, 5 not equal and 6 greater or equal by the order of the stencil compare [infer: no depth here equals another, so 2 draws as 0, 3 as 1, 5 as 7 and 6 as 4]; bit 20 set stops the object writing depth; bit 21 set stops it writing colour while it still writes depth (one run); bits 9, 10, 12 to 14, 19 and 29 to 31 change nothing over five overlapping copies (one run)"
unit = "isp"
method = "probes/isp/depth-compare.toml and probes/isp/tag-write.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle at clip z c/16 (copy c drawn after copy c - 1), each pixel carrying its copy's z through a coordinate set (vtx_z.s, pds_iter_done.s, o0 = pa0), ISP word 0 bits 24:22 at 0 to 7 with bit 20 clear and set, against the clear depth 1.0 and 0.0 (render command word 14); ISP word 0 0x00400200 with ten other bits flipped; two objects (copy 0, then copy 1 in blue, depth less) with bit 21 on the first; every pixel read back and read by copy with isp_words.py copies; the compare probes twice, the bits and tag-write probes once"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-depth-compare", "isp-tag-write"]
terms = ["ISP0", "ISP0.DCMP_MODE", "ISP0.DWRITE_DISABLE", "ISP0.TAGWRITE_DISABLE", "ISP0.BIT9", "CR_ISP_BGOBJDEPTH"]
+++

**What runs.** The five copies sit at depths 0.5 + c/32 (the viewport's z offset and scale are
both 0.5), so copy 0 is nearest and is drawn first. Each pixel stores its copy's z (c/16 as a
float), so the image says which copy won where. `isp-depth-compare-bg1` and `-bg0` (each twice)
set ISP word 0 to 0x200 plus bits 24:22 = d and bit 20 = w, for d = 0 to 7 and w = 0, 1, with
the clear depth (`CR_ISP_BGOBJDEPTH`, through the render command's word 14) at 1.0 and 0.0.
`isp-depth-compare-bits` flips bits 9, 10, 12, 13, 14, 19, 21, 29, 30 and 31 of 0x00400200
(compare 1, writes on). `isp-tag-write-b210` and `-b211` draw copy 0 as one object (ISP word 0
0x00400200, and with bit 21) and copy 1 as a second, blue, with depth compare 1. The bits and
tag-write probes ran once.

**Results.** "Nearest" is 1062 pixels of copy 0 and 36 of copy 1; "last" is 1074 pixels of copy
4 and 24 of copy 2; "none" leaves the 4096 background pixels. All four compare probes gave:

| bits 24:22 | clear 1.0, writes | clear 1.0, bit 20 | clear 0.0, writes | clear 0.0, bit 20 |
|---|---|---|---|---|
| 0 | none | none | none | none |
| 1 | nearest | last | none | none |
| 2 | none | none | none | none |
| 3 | nearest | last | none | none |
| 4 | none | none | last | last |
| 5 | last | last | last | last |
| 6 | none | none | last | last |
| 7 | last | last | last | last |

Flipping bit 21 drew nothing; each of the other nine bits gave the nearest copy, as the unflipped
word does. With two objects, bit 21 clear: 1062 pixels of the first (green) and 36 of the second
(blue); bit 21 set: no green, and the same 36 blue pixels, the rest background.

**What it shows.** Against 1.0 only the compares that pass for a smaller depth draw (1, 3, 5, 7),
and with writes on 1 and 3 keep the nearest copy, which later copies then fail: 1 is less. 7 lets
every later copy through at both clear values, always; against 0.0 only 4 to 7 draw, and 4 keeps the
last copy: greater. 0 never draws. No copy's depth (0.5 + c/32) equals the clear depth or an earlier
copy's, so the equal case is not seen: in all four probes 2 gives the image of 0, 3 that of 1, 5
that of 7 and 6 that of 4. Reading 2 as equal, 3 as less or equal, 5 as not equal and 6 as greater
or equal follows the stencil compare's order, where the equal case is measured (E284) [infer]; a
clear depth of 0.5, where copy 0 sits, would show it. With bit 20 set every copy that passes the
clear depth wins over the earlier ones, so the copies do not write depth: bit 20 is the depth-write
disable. Bit 21 removes the object's colour, while the second object is still hidden where the first
one lies: the first wrote its depth without its colour, a tag-write (colour) disable. Clearing bit 9
changes nothing in this block (`ISP0.BIT9`): what it selects is not shown, and the block's layout
does not move with it [infer].
