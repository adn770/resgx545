+++
id = "E419"
claim = "With the vertex shader of the perspective probes (two coordinate sets, w = x + 2) and a texture-and-iterate pixel program, OUTSEL 0x63000 and 0x61000 give one object (three dwords a vertex with the 1/w, format 0x00040303) and 0x62000 and 0x60000 another (two dwords a vertex, 0x00000202), and all four give the same image, whose iterated value fits an affine interpolation of the vertex values on all 1062 pixels (maximum error 1.7e-16) and not a perspective-correct one, in two of two runs"
unit = "mte"
method = "probes/mte/outsel-persp.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the probe of probes/mte/rhw.toml (vtx_persp.s: w = x + 2, o4, o5 the vertex's x and y; pds_tex_iter.s with DOUTI0 0x40000801 and U1 0x2000004; pix_pa0.s) with the state block's OUTSEL (blk:13) at 0x63000, 0x62000, 0x61000 and 0x60000, twice, the render memory dumped (8 jobs), the image fitted by pixels.py persp"
tiers = ["HW"]
date = "2026-11-07"
data = ["mte-outsel-persp"]
terms = ["OUTSEL", "VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE", "PRESENCE"]
+++

**What was seen.** In both runs, OUTSEL with bit 12 set (0x63000, 0x61000) gave the object whose
format word is 0x00040303 with the vertex's 1/w (0.8, 0.364, 0.615: 3f4ccccc, 3eba2e8b, 3f1d89d8)
among the three dwords a vertex; with bit 12 clear (0x62000, 0x60000) 0x00000202, two dwords a
vertex (E286). Bit 13 changed nothing: 0x63000 and 0x61000, 0x62000 and 0x60000 gave the same object
and the same image. All eight images were the same: 1062 pixels whose iterated pa0 fits the affine
interpolation of three vertex values (-0.75, 0.75, -0.375: the vertices' x before the multiply by w)
with a maximum error of 1.7e-16 on all 1062 pixels, while the perspective-correct fit has a maximum
error of 0.26 and fits 1 pixel of 1062.

**What it shows.** In this setup the iteration is affine whether or not the stored 1/w is in the
object, so the missing 1/w costs the iteration nothing; whether the stored 1/w feeds a perspective-
correct iteration the probe did not ask for (the DOUTI word's perspective flag was not set) is not
shown. OUTSEL bit 13 does nothing with two coordinate sets, as with zero, one (E286) and now a pixel
program that iterates the second.

**What it does not show.** Bit 13 with point sprites or the vertex colour, which the tool cannot
draw; the presence bits 16 to 31 with appended words (the tool grows the block only for presence
bits 2 to 5 and 7).
