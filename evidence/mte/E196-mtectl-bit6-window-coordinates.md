+++
id = "E196"
claim = "With MTECTL bit 6 the MTE takes the vertex outputs x and y as window coordinates in pixels, as the shader wrote them, with no division by w and no viewport: the scaled triangle draws a 3-pixel corner at scale 8 and a 66-pixel corner at scale 32 whatever w is (1 or 2), and the object's third group of three dwords holds w itself"
unit = "mte"
method = "the probe mte-mtectl-mte-bit6 of probes/mte/mtectl.toml (vtx_wclip.s, blk:15 = 0x01555660, scale S 8 and 32, w 1 and 2, the S 32 w 1 case twice, render memory dumped) and the probe vdm-state1-mtectl-bit6 of probes/vdm/state1.toml, read with tools/usse-asm/pbdump.py, on the laptop with the linux fork and the debug option on; the second table also ran as the follow-up run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["mte-mtectl", "vdm-state1", "vdm-state1-followup"]
terms = ["MTECTL.NO_TRANSFORM", "PB_OBJ.RHW"]
+++

**What runs.** The vertex program multiplies the triangle's clip x and y (-0.75, -0.75), (0.75,
-0.375), (-0.375, 0.75) by S and writes w. With MTECTL bit 6 set (E062: it removes the triangle in
the job) the TA still writes an object and one region stream. Four cases: S 8 w 1, S 32 w 1, S 32 w
2 and S 32 w 1 again; each dumps the parameter buffer.

**Results.** The images: S 8, w 1 draws 3 pixels, S 32 draws 66 pixels whether w is 1, 2 or 1 again,
and the three S 32 images are the same row for row. The drawn pixels are those at the target's
origin: x and y from 0 to 1 at S 8 (the pixels with x + y of at most 1) and from 0 to 10 at S 32 (x
+ y of at most 10, 66 pixels). That is the corner of a triangle with vertices at S times the clip
coordinates taken as pixels, (-24, -24), (24, -12) and (-12, 24) at S 32, cut by the target's edge,
with its far edge at x + y = 12. The object holds 22 dwords in all four dumps; its three 1/w dwords
read 1.0 at w 1 and 2.0 at w 2, and the vertex words of the two S 32 dumps are the same at w 1 and w
2. In the state-block probe (the 64x64 job's own shader with bit 6) the TA also writes the object
and one region stream, 22 dwords and one non-empty region, in both runs.

**Reading [infer].** The MTE does not divide by w, since a w of 2 changes neither the image nor the
vertex words, and applies no viewport, since the positions are the clip values times S in pixels.
The dword that holds 1.0 and 2.0 is the w the shader wrote; whether the same dword holds 1/w without
the bit is not measured here (at w 1 both are 1.0).

**Not shown.** No dump here has the bit clear at w 2, so the 0.5 that the object would hold without
the bit is not measured; E063 and E194 give the images only. The positions are read from the images
and the pixel counts, not by decoding the object's vertex words. One run per case.
