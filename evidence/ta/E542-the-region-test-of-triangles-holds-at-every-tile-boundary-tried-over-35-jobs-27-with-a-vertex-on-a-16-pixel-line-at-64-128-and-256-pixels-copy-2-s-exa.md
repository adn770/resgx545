+++
id = "E542"
claim = "The region test of triangles holds at every tile boundary tried: over 35 jobs (27 with a vertex on a 16-pixel line at 64, 128 and 256 pixels, copy 2's exactly on it in 24 five-copy jobs, the first triangle's in the 3 single-triangle fit jobs, and 8 with an edge exactly through a tile corner), 14656 (primitive, tile) pairs, a 16 x 16 tile is met iff the bounding box meets it (high sides open, low sides closed) and no edge has the four corners strictly outside: 0 mismatches, where the landed fit (half-open only between a region's tiles) is wrong in 11 of 23 held-out jobs and in 4 of 4 fit jobs, by listing tiles the TA does not list (27 pairs, none the other way)"
unit = "ta"
method = "script tables ta-tri-boundary (27 jobs) and ta-tri-corner (8 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: `probe --tri pixel` with the viewport words (blk:6-9) placing the triangle and its copies (`--vertices 15`: the copy c moved c/16 pixel right and down, so the apex of copy 2 lies on the line) at 64, 128 and 256 pixels; tri-corner: `--vertices 6`, v0 = C - (48, 12) and v1 = v0 + (96, 24) so the edge v0 v1 passes exactly through the tile corner C (16, 32, 48, 64 by 16, 32), the second copy missing it by 0.047 pixel; every region's control stream decoded by recompute_p1131.py; H70-T1 declared before the runs"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-tri-region"]
terms = ["CSTREAM.PRIM_TILES", "CSTREAM.PRIM_VERTICES", "CSTREAM.OBJ_PRIMS", "REGION_HDR.POS", "REGION_HDR.STREAM"]
+++

**The rule (H70-T1).** [HW] A tile [x0, x0 + 16) x [y0, y0 + 16) of a 32 x 16 region lists a
primitive iff the primitive's bounding box has max x >= x0 and max y >= y0 and min x < x0 + 16 and
min y < y0 + 16, and none of the primitive's three edge lines has all four tile corners strictly
outside it (a corner on the line counts). It was fitted post hoc to E180's 472 regions (plan.md
section 2) and declared as a prediction: the four fit jobs (E180's geometry twice, one shift, one
five-copy job) 4 of 4 jobs, the 23 held-out five-copy jobs 23 of 23, the 8 corner jobs 8 of 8; 14656
(primitive, tile) pairs (13632 + 1024), 0 mismatching. Every one of the 35 jobs has a vertex exactly
on a 16-pixel line: a vertex of copy 2 (the third triangle) in the 24 five-copy jobs, of the first
triangle in the 3 single-triangle fit jobs and in the 8 corner jobs. The triangle geometry (the NDC
constants and the c / 16 pixel shift of copy c) is an assumption of the recompute, not read from the
packed vertices; the 0 mismatches over 14656 pairs are the evidence for it. The landed text's rule
(H70-T0: closed tiles, half-open only on the line between a region's two tiles) is right in 0 of 4
fit and 12 of 23 held-out jobs (27 pairs wrong over the 15 jobs it misses, 0 in the corner jobs);
every one of the 27 is a tile the rule lists and the TA does not (21 right tiles, 6 left), none the
other way. E180's 472 of 472 (region_tiles.py) counts only the regions that have a stream, so it
never saw a listed tile with no stream: the two statements do not conflict. The corner jobs separate
the closed edge test from an open one (8 pairs wrong with the edge test open, 0 closed) and do not
separate T0 from T1.

**What a primitive word and its stream say (read in this batch).** [HW] The control stream's
per-tile masks: in the forms 0x80 (left tile) and 0x98 (right tile) of the primitive word, bits 7:0
are the primitive mask of that one tile (5 primitives, 39 of 39 single-tile regions of the first
batch agree with H70-T1) and bits 15:8 the low byte of the vertex mask (3 bits for each listed
primitive, 81 of 81 single-tile regions of the 35 jobs); in 0x90 every primitive is in both tiles
(bits 15:0 0xffff, no mask); in the form 0x88 the third dword is the masks, the low 16 bits the left
tile's and the high 16 bits the right tile's primitive mask, and in 0x8a and 0x8c (left only, right
only) the low 16 bits. So 0x88 is "both tiles, with a mask each": the landed glossary row says
"which tiles 0x88 means is not shown". [infer] That reading of 0x88 was made from these jobs and
checked by H70-T1's agreement, so the 27 + 8 jobs test the rule and the decode together. Bit 21 of
the primitive word (forms 0xa0 to 0xbf) adds one dword after the object word (0x00000400 in 336 and
0x00001000 in 30 of the 366 words that have it, in the vertex-task jobs of E546): Q164.

**What it does not show.** A vertex exactly on a tile line of the first triangle's own tiles beyond
the five-copy apex (ta-tri-edges, 24 jobs, was not run: the tool has no option to place such
vertices); a vertex or edge on the boundary of the 32 x 16 region itself is covered through the
tiles only; objects of more than 8 primitives (the masks are 8 bits wide in the
primitive word); lines and points are E543 and E544.
