+++
id = "Q230"
question = "what does the TA write in the cases of the clip, the target's edge and the numeric formats that E776 to E783 and E795 to E798 left open: the stored order of a clipped polygon of 3 or of more than 4 vertices and of a cut by a guard-band plane (E777), the limit of the region lists in y and at the left edge of other targets (E776), the tie of the rounding of the 1/1024 grid to 1/256 (E778), the depth word of a vertex with w other than 1 (no formula: every frozen rule refuted, words recorded, E783, E795 to E797), the rule of the 1/w word of a vertex with w other than 1 (RZ of 1/w or one ulp above it in 196 of 196 words of kept vertices, w from 3e-5 to 31; which of the two follows the mantissa of w alone, held out 42 of 42 at other exponents, E859; which of the 130 mantissas read store RZ + 1, 23 of them, has no rule: 0 of 512703 declared table-plus-Newton and binary32 models fit the 99 FIT mantissas, and a mantissa whose exact 1/w lies less than half an ulp above RZ stored RZ in 64 of 64, 13 of 13 on the dense table's HELD OUT half, SEMI, E872; exponents outside -2 to 4 were read at two w only) and of a clip-made vertex (0 to 3 ulp above RZ of 1/w_made, no rule, E782, E798), the depth of a made vertex (1.0 / 0.0 in 11 of 12, E782, E798), the 1/w word under a clamp (within 1 ulp of 1/clamp, no rule, E781), and the size at which a sub-pixel triangle is no longer written (E780)?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E063", "E182", "E194", "E287", "E307", "E651", "E650", "E736", "E754", "E776", "E777", "E778", "E780", "E781", "E782", "E783", "E795", "E796", "E797", "E798", "E842", "E851", "E859", "E872"]
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

Narrowed 2026-11-10 (R2-geo, E782 and E783; the question line is reworded again, the question stays
open). T3 and T4, the stages that did not run in R1, ran with every control passing.
- Clip at w other than 1 (E782, held out). Two cut objects (w = 0.5x + 1.25 and -0.5x + 1.25, z =
  2x + 1) were the Sutherland-Hodgman polygon in (x, y, z, w) against z <= w and z >= -w, 4 vertices
  in the strip zigzag order with the prim words of E777, the window position 32 + 32 x / w at every
  vertex, made ones included (2 of 2 each); an uncut one with three different w kept the input
  order, the window 32 + 32 x / w per vertex and depth 0.5 at z = 0 (1 of 1).
- 1/w (E782, E783). The 1/w of a kept vertex is RZ of 1/w exactly: 7 of 7 words at differing w
  (E782) and 6 of 6 pairs with z other than 0 (E783; round to nearest refuted 5 of 5), as E754. The
  1/w of a clip-made vertex is within 1 ulp of RZ of the reciprocal of the made w in 4 of 4 and
  exact in 1 of 4 (offsets +1, 0, -1, +1; the frozen exact rows refuted 2 of 2); the hypothesis that
  it is interpolated along the edge is refuted 2 of 2.
- Depth (E782, E783). The depth word of a vertex at w other than 1 was recorded at six (z, w)
  pairs, all above the exact 0.5 + 0.5 z / w; each of six frozen formulas was refuted by at least
  one pair (D1 and D2 fit 5 of 6 each, D6 0 of 6), and a post hoc search over 768 rounding
  combinations found none for 6 of 6. A made vertex's depth was 1.0 in 3 of 4 and 0x3f7fffff at one
  (HDP-made refuted 1 of 2 jobs).
Open (the reworded line): as above, with the depth formula at w other than 1 (words in E783, a fit
needs pairs near w = 1 and z of both signs), the made vertex's 1/w and depth rule (a made vertex on
the -w plane at w other than 1 was not run), and polygons of 3 or 5 vertices at w other than 1.

Note 2026-11-10 (an offline fit on E783's six words, made before the round 3 runs; post hoc fit, not
a measurement; see the notes of E783). One family reproduces all six words: the product z * RZ(1/w)
rounded away from zero to a float32 when its fraction in its ulp exceeds t, with t in (0.3655,
0.4667); round to nearest is that family with t = 0.5 and misses the pair (-2.6, 3) by 0.033 ulp. Of
257 models declared in five families before the fit, 13 fit 6 of 6 (one family) and 69 fit 5 of 6.
The fit rests on one word (t4-m2p6-3), six words carry at most 6 bits, and about 4 of 257 models fit
by chance alone, so the threshold is a hypothesis for a held-out run and no depth rule is adopted. A
repeat of t4-m2p6-3 is its first control. E783's offsets for that pair are corrected there (0.17 of
2^-24, 0.33 ulp of q).

Narrowed 2026-11-10 (R3-geo, E795 to E798; the question line is reworded, the question stays
open). The four depth stages of round 3 ran with every control passing.
- Depth at w other than 1 (E795, E796, held out). The post hoc threshold fit of the note above
  (H-thr) is refuted: 5 of 11 outside cells off its frozen direction, while the word it rested on
  (t4-m2p6-3, 0x3d88888c) repeated. D1, D2, D5, T26, T27 and K23 are refuted on g-da's 21 cells,
  and every product rule with every rounding of the sum on g-db's z > 0 and q cells; D1 held on
  the four cells next to w = 1 only. No depth rule is adopted; the simulator keeps refusing.
- Viewport z words (E797, held out). Word 10 of the state block is the z offset and word 11 the z
  scale (the swap refuted 9 of 9); at w = 1 the cell that separates the roundings stored the sum
  rounded once (one cell). At w = 3 every frozen viewport rule was refuted (their product rule was
  D1, refuted in g-da).
- Cuts at w other than 1 (E798, held out). The polygon, zigzag order, window rule and prim words
  held on four cuts, two of them on the -w plane, and the made vertex's depth was exactly 1.0 /
  0.0 at all eight made vertices (11 of 12 with E782); the made 1/w is not RZ of 1/w_made (0 of 8
  words, 1 to 3 ulp above).
- 1/w [HW, read after the run, no frozen row]. The 1/w of a vertex is not RZ of 1/w at every w:
  one ulp above at w = 9 and 0.7 (one w at all three vertices, E795, E796) and at 1.40625, 1.59375
  and 1.6875 (kept vertices of cut objects, E798), RZ at the other w run.
Open (the reworded line): as above, with the 1/w rule at w other than 1 (which w store one ulp
above RZ), the depth formula, the made vertex's 1/w, and polygons of 3 or 5 vertices at w other
than 1.

Note 2026-11-11 (round 4, an offline reading of the 23 w with a recorded 1/w word, E754, E795, E796
and E798; [data]). The fraction of the exact 1/w in the last place does not separate "RZ" from "one
ulp above" (1.0625 is RZ at 0.94, 1.59375 is above at 0.63), and neither does the mantissa of w
(1.375 RZ, 1.40625 above, 1.4375 RZ). So the word is not a directed or nearest rounding of the exact
quotient at any threshold; [infer] it is an iterative or table reciprocal with an error of 0 or +1
ulp. Five "above" words carry too few bits to fit an algorithm (E783's lesson: 4 of 257 models fit
six words by chance); a table of about 60 w, with a frozen FIT and HELD OUT split, is the smallest
run that can fit and hold out (planned stage g4-rw). The depth formula stays parked behind it and
very likely uses the same reciprocal [infer].

Narrowed 2026-11-11 (R4-pixel g4-rw, E842; the question line's 1/w clause is reworded, the question
stays open). The clause read "the 1/w word of a vertex with w other than 1 (RZ of 1/w at most w, one
ulp above it at w = 9, 0.7, 1.40625, 1.59375 and 1.6875, E795, E798)". The table of 60 w ran with
its controls passing: 42 words of kept vertices were read, 31 RZ of 1/w and 11 RZ + 1 (w 1.125,
1.40625 again, 1.49219, 1.75638, 4.2782, 4.67374, 6.375, 6.75, 7.125, 7.375, 7.83901), 19 of the 30
FIT and 23 of the 30 HELD OUT words, so the frozen assertion (RZ or RZ + 1) holds on 65 of 65 words
with the earlier 23 and the frozen family fit, which needs all 60, did not run. The 18 words not
read are the third of the table scaled by 1/4 (w 0.254 to 0.443): their window coordinates 32 + 32 x
/ w fell beyond the guard band, and the TA stored polygons of 5 to 7 vertices all made on its edges
(-16 and 80), read post hoc at the fold. Open: the rule of the RZ + 1 words (a table whose every
vertex stays inside the band, the FIT and HELD OUT split frozen again; fitting the 42 words now
would be post hoc), w below 1, and the rest of the line as before.

Note 2026-11-12 (E851, an offline reading of E842's kept words; the question stays open, the line
unchanged). The frozen analysis of g4-rw is decided without its 18 unread words: none of the 225
frozen models reproduces all 19 FIT words that were read (best 16), so none can reach the 30 of 30
its rule needs, and its verdict is "no rule adopted"; the HELD OUT words were not used. Read post
hoc over the 65 known words (not held out) [infer]: H-MANT, whether the word is RZ or RZ + 1
follows the mantissa of w alone, fits the 6 of 6 mantissas read at two or three exponents (1.0625,
1.125, 1.5, 1.59375, 1.6875, 1.75), and a wider declared family of table-plus-Newton models fits
none. Open: H-MANT held out (E842's mantissas at other exponents of w, every window coordinate
inside the viewport), w below 1, then a rule for the RZ + 1 mantissas.

Narrowed 2026-11-12 (R5-pixel g5-rwa and g5-rw, E859; the question line's 1/w clause is reworded,
the question stays open). The clause read "the rule of the 1/w word of a vertex with w other than
1 (RZ of 1/w or one ulp above it in 65 of 65 words of kept vertices, E795, E798, E842; which w
store RZ + 1 is not placed: E842's frozen fit of a table of 60 w did not run, 18 of the w having
been cut at the guard band)". With every vertex inside the viewport, H-MANT held out: E842's 14
triangles with every w halved or multiplied by four stored R4's delta at 42 of 42 vertices (11 RZ
+ 1), the replicates repeated R4's six words, E842's six lost jobs wrote 3-vertex objects whose
18 words at w 0.254 to 0.443 are RZ or RZ + 1, and 60 new mantissas (w 0.254 to 7.54) are RZ or
RZ + 1 with a frozen FIT / HELD OUT split; 126 of 126 words, every control exact. Post hoc over
the 196 words now known: 47 mantissas read at two or more exponents, none with both deltas. "w
below 1" (E851's note) is answered for the RZ or RZ + 1 assertion. sgx-pipe gives the word for
the 130 mantissas read at exponents -2 to 4 and refuses the rest. Open: which mantissas store RZ +
1 (a family declared before it is fitted on the dense table's FIT half and scored on its HELD OUT
half), exponents outside -2 to 4, and the rest of the line as before.

Narrowed 2026-11-12 (E872, an offline fit and a SEMI test on E859's kept words; the question line's
1/w clause is reworded, the question stays open). The clause read "which of the 130 mantissas read
store RZ + 1, 23 of them, has no rule, and exponents outside -2 to 4 were read at two w only)". The
fit E859 left undone ran on the FIT mantissas only (99, w = 1 left out, 15 RZ + 1): 0 of 512703
models declared before the run fit them (tables plus Newton steps with truncated products, binary32
compositions, RZ of a cut w), so the HELD OUT half was not used for a fit. H-FRAC, read on FIT (with
frac the fraction of 2^47 / M, no mantissa with frac below 0.5 stores RZ + 1: 0 of 51), was frozen
with a hash and held on the HELD OUT half by counts: 13 mantissas below 0.5, all RZ, 8 RZ + 1 above
(chance 0.0042). SEMI, not held out: the planner had read the 130 deltas unlabelled in E859's fold
output before the freeze. Read [infer]: the word is floor(1/w + e) with 0 <= e < 0.5 ulp, e not
smooth in the mantissa. Open: which mantissas with frac of 0.5 or more store RZ + 1 (how e varies
between neighbouring mantissas: windows of 36 at three strides, the plan's stage g6-rw,
closing6/pixel/exp-pixel-r6.md section 4), exponents outside -2 to 4, and the rest of the line as
before. sgx-pipe keeps the table of read mantissas; H-FRAC is not a rule there yet.
