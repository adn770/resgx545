+++
id = "Q160"
question = "how does the TA split an index list of several lines into objects and regions: two lines at 128 x 128 give two objects of 2 vertices (the second the segment from vertex 2 to vertex 0) or, in the shifted job, one of 4, three lines give 2 and 4 vertices, and at 64 x 64 one object of 4 or 6, with four regions more than its segment in the first object"
unit = "ta"
kind = "hw"
value = "low"
phase = 11
evidence = ["E543"]
terms = ["PB_OBJ.PRIM_LIST", "CSTREAM.OBJ_PRIMS", "VDM_INDEX0.PRIMITIVE_TOPOLOGY"]
+++

With the index list's count at 4 and 6 the tool's index buffer wraps, so the second line of two is
vertex 2 to vertex 0 (E543: 12 regions listed against 10 for that segment) and the third of three is
probably vertex 4 to vertex 0 or 2 (not read). Of the six multi-line jobs, at 128 x 128 ln-two128
and ln-two128-w40 wrote two objects of 2 vertices (0x405 and 0x805, each a line), ln-two128-shift
one object of 4 vertices and two primitives (0x407) and ln-three128 two objects (0x405 of 2 vertices
and 0x807 of 4); at 64 x 64 ln-ctl64-two wrote one object of 4 vertices (0x407) and ln-three64 one
of six vertices and three primitives (0x409). The first object of ln-two128 lists 10 regions where
its segment (v0 to v1) gives 6, and the exact-segment rule is right on 1 of 6 multi-line jobs.

Open: what the vertex pairs of each object are (the primitive list entries (16, 17, 17) and (18, 19,
19) with the object's own vertices, E308's layout), why an object of two lines is not the union of
its segments' regions, and what decides one object or several (the size of the target, the number of
indices, and the viewport x offset, 80 in ln-two128-shift and 64 in ln-two128, that makes one object
of two lines where the other makes two).

To settle it: single and multiple lines with an index buffer the tool writes by `--blk`/`--vdm`
(index words 1: the base; the buffer's contents are the tool's default 0, 1, 2, ...), the objects'
vertices read from the dumps (the packed block), at 64, 128 and 256 pixels. No kernel change.
