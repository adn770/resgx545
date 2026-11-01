+++
id = "E195"
claim = "MTECTL (blk:15) bits 8:7 choose which vertex's values the clipper gives the vertices it makes (0 interpolated values, 1, 2, 3 vertex 0's, 1's, 2's) and the 2-bit fields from bit 10 say per attribute whether that choice is dropped for interpolation again; on a triangle that is not clipped no tried value changes the image, and bit 9 and bit 26 of the index list's third word change nothing clipped or not"
unit = "mte"
method = "the 34 probes of probes/mte/mtectl.toml (pds_iter_nofetch.s with the vertex programs vtx_color.s, vtx_color_wclip.s and vtx_color_wclip0.s, blk:15 set to 14 values, vdm:4 with bit 26 in four of them, four shade selections each), 64x64 target, on the laptop with the linux fork and the debug option on, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["mte-mtectl"]
terms = ["MTECTL.FLAT_VERTEX", "MTECTL.ATTR_SMOOTH", "OUTSEL.COLOUR_PRES", "DOUTI0.SHADEMODEL"]
+++

**What runs.** The pixel program iterates the vertex colour in four ways: flat from vertex 0, 1 or 2
(the shade model's selection 0, 1, 2) and smooth. The vertices are v0 = 0xff000040, v1 = 0xffbf0040,
v2 = 0xff00bf40. The state block's `OUTSEL` and `coordsize` are set for a colour (blk:13 = 0x83800,
blk:16 = 5) or, in the `clipc` probes, for a coordinate set (blk:16 = 4). The unclipped triangle
covers 1062 pixels. `vtx_color_wclip.s` gives vertex 1 a negative w (-0.5), so the clipper cuts the
triangle (1394 pixels), `vtx_color_wclip0.s` does the same to vertex 0 (2006 pixels). MTECTL runs
over 0x01555620 (our job's), 0x15555620, 0x15555420, 0x01555420, 0x000001a0, 0x00000220, 0x000002a0,
0x000003a0, 0x00000320 and the four fields words 0x000007a0, 0x00000ba0, 0x00000fa0, 0x000013a0 and
0x155557a0.

**Results.**

- Not clipped: the images under 0x01555620, 0x15555620, 0x15555420, 0x00000220, 0x000002a0,
  0x000003a0 and 0x00000320, and under 0x01555620 and 0x000003a0 with bit 26 of the index list's
  third word (`vdm:4` = 0xf4000000), are the same: flat from vertex 0, 1, 2 gives v0, v1, v2 on all
  1062 pixels, and smooth gives the interpolated colours.
- Vertex 1 clipped, 8:7 = 0 (0x01555620, 0x15555620, 0x15555420, 0x01555420): selection 0 gives
  0xff600040 on all 1394 pixels, a colour no vertex has; selection 1 gives v2 on 1304 pixels and v0
  on 90; selection 2 gives 0xff600040 on 660, v0 on 644 and 0xff570040 on 90.
- Vertex 1 clipped, 8:7 = 3 (0x3a0, and the same with bit 9 clear, 0x1a0, and with bit 26 of the
  third word): selections 0 and 2 give v2 on all 1394 pixels, selection 1 gives v0 on 734 and v2 on
  660. With 8:7 = 1 (0x2a0) selections 0 and 2 give v0 on all 1394 and selection 1 gives v2 on 1304
  and v0 on 90. With 8:7 = 2 (0x320) selection 1 gives v1 on all 1394, selection 0 gives v0 on 734
  and v2 on 660, selection 2 v1 on 750 and v2 on 644.
- Vertex 0 clipped: 8:7 = 3 gives v2 on all 2006 pixels for selections 1 and 2 (selection 0: v1 on
  1310, v2 on 696); 8:7 = 1 gives v0 on all 2006 for selections 0 and 1 (selection 2: v1 on 1310, v0
  on 696); 8:7 = 2 gives v1 on all 2006 for every selection, smooth too; 8:7 = 0 gives colours that
  are not vertices' (0xff00a740 on 1943 pixels for selection 1).
- Fields from bit 10 with 8:7 = 3: a non-zero first field (1, 2 or 3: 0x7a0, 0xba0, 0xfa0, and the
  smooth word 0x155557a0) gives the images of 8:7 = 0 colours cut as 8:7 = 3 cuts the polygon
  (selection 0: 0xff600040 on 750 pixels and v2 on 644). The second field (0x13a0) changes nothing
  from 0x3a0. With 8:7 = 0 the fields change nothing (0x15555420 and 0x15555620 give the same
  images).
- With a coordinate set instead of the colour (the probes `clipc`): source 1 (the first coordinate,
  x) is -0.375 (v2's) on all 1394 pixels under 0x3a0, -0.75 (v0's) under 0x2a0, interpolated again
  under 0x7a0 and 0x155557a0, and -0.375 under 0x13a0.

So bits 8:7 act as the provoking vertex of flat shading for the vertices the clipper makes (0 is
none, the GL last vertex is 3), and a non-zero field returns that attribute to interpolation. The
number of regions a selection splits the clipped polygon into depends on 8:7 as well (selection 2 on
the vertex 1 clip gives three regions under 0 and two under 2).

**Not shown.** What bit 9 and the third word's bit 26 are for, as neither changes any image here.
The fields beyond the first two were tried with one value each and their attributes are not told
apart. Which attribute each field governs is read from the colour and the first coordinate only. One
run.
