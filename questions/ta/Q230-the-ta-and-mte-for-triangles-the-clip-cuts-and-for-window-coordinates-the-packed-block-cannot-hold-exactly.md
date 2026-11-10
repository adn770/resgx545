+++
id = "Q230"
question = "what does the TA write in the cases of the clip, the target's edge and the numeric formats that E776 to E781 left open: the stored order of a clipped polygon of 3 or of more than 4 vertices and of a cut by a guard-band plane (E777), the limit of the region lists in y and at the left edge of other targets (E776), the tie of the rounding of the 1/1024 grid to 1/256 (E778), the depth and the 1/w of a vertex with w other than 1 and of a clip-made vertex, the 1/w word under a clamp (within 1 ulp of 1/clamp, no rule, E781), and the size at which a sub-pixel triangle is no longer written (E780)?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E063", "E182", "E194", "E287", "E307", "E651", "E650", "E736", "E754", "E776", "E777", "E778", "E780", "E781"]
terms = ["PB_OBJ.RHW", "PB_OBJ.ISP_WORDS", "VIEWPORT.X_OFFSET", "WCLAMP"]
+++

The pipeline simulator's vertex side and TA (E650) compute an object only for whole triangles whose
three vertices have w = 1, window coordinates that are multiples of 1/256 pixel, and that at least
one region of the target lists. Everything else refuses here:

- a triangle with a vertex beyond z = -w or z = w, whether all three are (the clip removes it from
  the image: E287 measured flat triangles at -1.01 and 1.01 removed, by pixels) or one is and
  another inside (E287 measured sloped ones cut along the line where z reaches the plane); nothing
  dumped says whether the TA writes an object for the removed triangle, as for the one no region
  lists below, or what it writes for the cut one;
- a 1/w equal to the minimum of the command (E197's three values were all clear of it: whether the
  replacement applies on the boundary is open);
- a triangle no target region lists: the zero-words baseline (viewport x offset 1000) gives no
  object and empty headers, and the object of every dumped triangle that reaches the target is
  written, so the limit is open: a rule "an object is written when some region lists a primitive"
  and a rule "an object is not written beyond a guard band" both fit the data;
- window coordinates with more than 8 fraction bits: the packed block holds 24 bits of
  (v + 4096) * 256, and every coordinate dumped so far is a multiple of 1/16 pixel, so truncation,
  rounding and the viewport's own arithmetic (a multiply then an add, or a fused one) are not told
  apart;
- the depth and 1/w of a vertex with w other than 1 (E063, E194 measured the pixels), and a w
  below 1e-3.

What would settle it: a triangle wholly beyond z = w and one beyond z = -w, dumped; a table of
triangles with window coordinates on a 1/1024 grid and with w of 0.5, 2 and 4, their objects
dumped; triangles moved across the target's edge by 8, 64, 128, 512 and 1000 pixels; a triangle
with one vertex beyond z = w, dumped.

Status: open.

Post hoc 2026-11-09 (S1, E736; the frozen verdict was cannot tell, because the control of the
WCLAMP group failed; nothing here is held out or an answer). The WCLAMP control, w = 1e-5 under a
clamp of 1e-3, wrote an object (4 vertices, a 0.96 pixel square at the target's centre covering no
pixel centre, 1/w 0x4479ffff), not "no object" as E194's image had been read: the 35 dumped objects
are in E736. Read per group after the run: triangles wholly beyond z = w or z = -w leave no object;
cut and w-clipped triangles are stored as clipped polygons of 3 to 5 vertices; a viewport offset of
8 and 64 pixels keeps the object and 128, 512 and 1000 leave none; 1/1024 coordinates are packed
rounded to 1/256; x and y are divided by w exactly at w = 2 and 0.5; a clamp one ulp above w = 1e-3
stores the clamp's reciprocal as 1/w. Each needs a frozen run with the group's control gating that
group alone.

Narrowed 2026-11-10 (S1b, E754; the rounding of 1/w inside the guard band only). With x and y scaled
by w so that the stored x and y equal the original triangle's, the stored 1/w of a vertex with w =
3, 7, 0.003 and 3e-5 is the float32 reciprocal truncated toward zero (4 of 4: 0x3eaaaaaa,
0x3e124924, 0x43a6aaaa, 0x47023555 at every vertex; round-to-nearest refuted in 4 of 8 checks; the w
= 1 control passing; frozen, held out), so inside the band the object holds the truncated reciprocal
and the original x and y; the depth at w other than 1 was not scored. Under a clamp (block word 14)
of 3e-5 to 1e-3 with w = 1e-5 the object had the original's x and y shrunk by w over the clamp and
1/w = 1/clamp in 4 of 5 jobs (the clamp of 1e-3 wrote no object where E736's control wrote a 0.96
pixel square), that 1/w truncated at 3e-5 and rounded at 3e-4: every frozen clamp model is refuted
at least once and none is consistent. The z cuts repeat as clipped polygons (4 and 3 vertices, 2 of
2, repeat only). Open: the clamp's rule, the depth at w other than 1, the vertex rules of the clip
cuts, the limit of the region lists and coordinates finer than 1/256.

Note 2026-11-10 (a post hoc reading of E736's viewport-offset cells, a fit and not a test, made
before the round 2 runs; see the note of E736). [infer] The viewport's word 6 is an absolute x
offset (default 32.0), so the window x is X + 32 x_clip: e3o-x64 put the triangle at x 40 to 88 and
e3o-x128 at 104 to 152, inside macrotile 0's 128-wide region grid and yet with no object. The
reading that the limit of the region lists is the macrotile grid is therefore refuted on existing
data; E542's tile rule applied to the target's regions only (low side closed, high side open) fits
all the cells, with the object's minimum x going out of reach in (64, 104]. The clause "the limit
of the region lists" is narrowed to that interval and that candidate; the boundary itself has not
been run.

Narrowed 2026-11-10 (R1-pixgeo, E776 to E781; the question line is reworded to what stays open, the
question stays open). Each group was gated by its own control and every control passed. T3 and T4
(the 1/w of a clip-made vertex and the depth at w other than 1) did not run.
- Clip cuts (E777, held out). Five new clipped objects of 4 and 3 vertices, cut in x and y by one
  and two planes: the vertex set is the Sutherland-Hodgman polygon over A to B, B to C, C to A (5
  of 5), the prim entries the strip triangles with the boundary flag in bit 4 (5 of 5, the
  re-reading of E181 and Q070's primitive list held out), the depth at a clip-made vertex 0 or 1
  exactly, and for a polygon that both planes cut the -w plane acts first (2 of 2: order and
  depth words; +w first refuted 2 of 2). The 3-vertex polygon was stored in the Sutherland-Hodgman
  order, one place from the zigzag the frozen rule gave (post hoc: n = 4 zigzags, n = 3 does not).
- Off-target (E776, held out). At the right edge a triangle with min x 63.5 is written and listed,
  at 64.0 and beyond nothing is written; at y 63.5 listed, at 64.0 written and unlisted; at the left
  edge max x 0.0 and below gives nothing. E542's tile rule as frozen failed 1 of 9 (the -24.0 cell)
  and the band reading 3 of 6. A rule fitting every cell (an object is listed iff the extent
  overlaps the target with positive width and height) was read after the run and has no held-out
  cell.
- Fine grid (E778, held out). Coordinates on the 1/1024 grid are packed rounded to nearest 1/256 in
  18 of 18 coordinates of three triangles (truncation refuted 3 of 3), no ties; the answer to that
  clause except for ties and finer grids.
- Clamp (E781, held out). Under a clamp above w the stored 1/w is one of the two floats next to
  1/clamp (RZ in 2 cells, RN in 3 of the 5 where they differ), within 1 ulp and no rounding rule,
  and the position is x, y divided by the clamp in 6 of 6.
- Sub-pixel cull (E780). No object for any triangle about a pixel corner from a bounding box of
  0.30 to 0.98 pixel (area 0.042 to 0.451), where the 0.96-pixel square control is written: the
  frozen HS-ext (an object from a box of at most 0.96) is refuted by the 0.98 cell although the
  scorer printed consistent; the threshold is not between the ladder's cells, and the box is not
  the criterion (an area between 0.45 and 0.92 is a post hoc reading across two routes).
Open (the reworded line): the plane order and the stored order beyond 4 vertices and for a
guard-band cut, the y and left-edge limits and other targets, the tie rule of the grid, the depth
and 1/w of clip-made and perspective vertices, a rule for the clamp's 1/w word, and the cull's
threshold.
