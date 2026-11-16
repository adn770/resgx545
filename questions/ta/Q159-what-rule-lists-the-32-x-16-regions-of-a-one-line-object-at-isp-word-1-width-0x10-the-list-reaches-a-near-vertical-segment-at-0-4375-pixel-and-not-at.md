+++
id = "Q159"
question = "what rule lists the 32 x 16 regions of a one-line object: at ISP word 1 width 0x10 the list reaches a near-vertical segment at 0.4375 pixel and not at 0.5, a near-horizontal one at 0.5 and 0.625 pixel at two regions of one job, and at the widths 0x20 to 0xf0 a near-vertical one up to 0 (the own regions), 1.497, 3.493 and 6.487 pixel and not at 1.0, 2.0, 4.0 and 8.0, and (folded from Q160) how does the TA split an index list of several lines into objects and regions: two lines at 128 x 128 give two objects of 2 vertices (the second the segment from vertex 2 to vertex 0) or, in the shifted job, one of 4, three lines give 2 and 4 vertices, and at 64 x 64 one object of 4 or 6, with four regions more than its segment in the first object"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E543"]
terms = ["ISP1.LINE_WIDTH", "PB_OBJ.LINE_WIDTHS", "CSTREAM.PRIM_TILES", "PB_OBJ.PRIM_LIST", "CSTREAM.OBJ_PRIMS", "VDM_INDEX0.PRIMITIVE_TOPOLOGY"]
+++

A line written with ISP word 0 + 0x8000 and index list topology 1 runs through the TA (E543). Its
regions are not those the exact segment meets (right in 4 of 23 held-out jobs): the list reaches
further, by 0.5 pixel at the width 0x10 and, at the widths 0x20 to 0xf0, by a distance the 28
near-vertical jobs bracket without fixing it: listed up to 1.497 pixel at 0x40, 3.493 at 0x80 and
6.487 at 0xf0 and not at 2.0, 4.0 and 8.0 (at 0x20 only the line's own regions are listed and 1.0 is
not). The declared w / 32 pixel fits, as does any reach inside the brackets; the max(w / 32, 0.5) of
the declaration never acted, since w / 32 is at least 0.5 at every width run, and no width under
0x10 was run on a line. The reach is not one distance at width 0x10: with a segment rising 0.1875
pixel over 48, the region whose nearest point is 0.5625 pixel away is listed and the next, 0.6875,
is not, while the near-vertical segment is listed at 0.4375 and not at 0.5; a flat-ended or
square-ended rectangle of half-width hw is inconsistent with the two (hw < 0.5 against hw >= 0.625),
and a bounding box expanded by 0.5 lists regions of a diagonal line (8, 8) to (56, 20) that are not
listed. So the test is between a distance to the segment and a test on the line's extreme point in
y.

Open: the rule for any orientation and width: the exact reach at a diagonal (45 degrees) line and
at a near-horizontal line at the wide widths, the reach beyond the end points (a cap), widths under
0x10, between 0x10 and 0x20 and above 0xf0, the reach at 0xf0 within 6.49 to 8.0, and the half-open
or closed edge of the reach.

To settle it: `probe --tri` with ISP word 0 0x01d08200, single lines at angles of 0, 15, 30, 45, 60,
75 and 90 degrees (the viewport words set the end points; sx and sy are free) at distances from a
region edge of 0.25 to 1.0 pixel in sixteenths, ISP word 1 widths 0x10, 0x18, 0x20; the reach read
from which regions have a stream (`ta_words.py`-style region lists, recompute_p1131.py). No kernel
change.

**Correction 2026-11-16 (round 31, with the user):** Q160 is folded into this question (retired as
folded into Q159 after E1125; a fold is not an answer): both ask which regions and objects the TA
lists for line objects, from the same record (E543). Its clauses are appended to the line above,
its evidence (E543) was already in this list, and its terms (`PB_OBJ.PRIM_LIST`,
`CSTREAM.OBJ_PRIMS`, `VDM_INDEX0.PRIMITIVE_TOPOLOGY`) are added. Its text, kept here: with the
index list's count at 4 and 6 the tool's index buffer wraps, so the second line of two is vertex 2
to vertex 0 (E543: 12 regions listed against 10 for that segment) and the third of three is
probably vertex 4 to vertex 0 or 2 (not read). Of the six multi-line jobs, at 128 x 128 ln-two128
and ln-two128-w40 wrote two objects of 2 vertices (0x405 and 0x805, each a line), ln-two128-shift
one object of 4 vertices and two primitives (0x407) and ln-three128 two objects (0x405 of 2
vertices and 0x807 of 4); at 64 x 64 ln-ctl64-two wrote one object of 4 vertices (0x407) and
ln-three64 one of six vertices and three primitives (0x409). The first object of ln-two128 lists
10 regions where its segment (v0 to v1) gives 6, and the exact-segment rule is right on 1 of 6
multi-line jobs.

Open from Q160: what the vertex pairs of each object are (the primitive list entries (16, 17, 17)
and (18, 19, 19) with the object's own vertices, E308's layout), why an object of two lines is not
the union of its segments' regions, and what decides one object or several (the size of the target,
the number of indices, and the viewport x offset, 80 in ln-two128-shift and 64 in ln-two128, that
makes one object of two lines where the other makes two). To settle it (Q160's plan): single and
multiple lines with an index buffer the tool writes by `--blk`/`--vdm` (index words 1: the base;
the buffer's contents are the tool's default 0, 1, 2, ...), the objects' vertices read from the
dumps (the packed block), at 64, 128 and 256 pixels. No kernel change.
