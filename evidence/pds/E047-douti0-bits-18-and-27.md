+++
id = "E047"
claim = "With DOUTI0 bit 18 set, the iterated x of the textured triangle is the plane (13/45) x + (8/45) y + 3/5 in clip coordinates (largest error 1e-7 over 1062 pixels), which takes 0.25, 0.75 and 0.625 at the three vertices, so each vertex's x was reduced to its fractional part before iteration (an inference from the fit); with bit 27 set each pixel's value depends on its column alone and, for 906 of the 1062 pixels, is x in fixed point with 28 fractional bits, the other 156 differing by 2^-8"
unit = "pds"
method = "probe pds-iteration-sources-douti-bits of probes/pds/iteration-sources.toml on the laptop, linux fork with the debug option on: the 64x64 textured-triangle host with the vertex shader giving its clip x and y as coordinate set 1, the pixel PDS program iterating that set into the first primary attribute with DOUTI0 0x40000801 plus one bit per case (17 cases), every pixel read back and fitted"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["pds-iteration-sources"]
terms = ["DOUTI0.VERTEX_FRAC", "DOUTI0.FIXED_OUT", "DOUTI0.F16"]
+++

**What runs.** The probe's vertex shader writes the vertex's clip x and y as coordinate set 1;
the triangle's vertices are at x = -0.75, 0.75, -0.375 and y = -0.75, -0.375, 0.75, and cover 1062
of the 4096 pixels. The pixel PDS program starts a task that iterates set 1 (source 1, with the
texture fetch) with the DOUTI0 word 0x40000801 and one more bit per case, and the pixel shader
writes the primary attribute out as the pixel. Each of the 17 cases reads the 64x64 target back
and the 1062 triangle pixels are fitted. Each case ran once.

**Results.**

- Base case (no extra bit): each pixel holds its clip x as an IEEE single, (px + 0.5) / 32 - 1,
  exactly (error 0.0) at all 1062 pixels.
- Bit 18: a least-squares plane through all 1062 values is 0.288888848 x + 0.177777749 y +
  0.599999938, against 13/45, 8/45 and 3/5 (0.288889, 0.177778, 0.6), largest error 4e-8; the
  fixed plane (13/45) x + (8/45) y + 3/5 fits every pixel within 1.0e-7 (the same plane with
  the sign of y reversed is off by 0.26). Its values at the three vertices are 0.25, 0.75 and
  0.625: the vertices' x of -0.75, 0.75 and -0.375 reduced mod 1 (0.25, 0.75, 0.625) and then
  iterated as usual. That reading, that the bit wraps the per-vertex values into [0, 1), is
  the inference.
- Bit 27: the value depends on the column only (47 columns of the triangle, one value in
  each). Read as raw bits it is x as a two's-complement fixed-point number with 28 fractional
  bits, in the low 30 bits: for example 0x34500000 in column 8. 906 of the 1062 pixels match
  that exactly; the other 156, all in columns 8 to 15 and 48 to 54 (the columns nearest the left
  and right vertices), differ by 0x100000, which is 2^-8.
- Bit 28 gives the value as half floats (for example 0x0000b5c0 where the base has 0xbeb80000).
  Bits 17, 19, 20, 22 to 26, 29 and 31 left the image as the base, and bit 21 gave 0xbf400000
  (-0.75) at every pixel.

**Not shown.** What a shader would use the two modes for (a repeating coordinate kept small, an
integer texel address) is not tested. The 156 pixels that differ by 2^-8 from the exact
fixed-point value could be a rounding of the iterator; the data only shows the size and the
columns.
