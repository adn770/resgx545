+++
id = "E181"
claim = "The TA object holds a primitive list of 16-bit entries of three 5-bit vertex numbers counted from 16, two entries to a dword with the last repeated for an odd count, and the primitive word's bits 30:29 are 2 for triangles and lines and 3 for points; the object word's bits 31:26 fit twice the primitives less one in these dumps"
unit = "ta"
method = "the triangle, points and lines probes of probes/ta/objects.toml (one line, two lines, three points) and the scene probes of probes/ta/regions.toml (two to five copies of the triangle, with the plain triangle ta-objects-fbf-opaque of objects.toml as the single copy), the parameter buffer saved after the render, the object's list and the streams' words decoded; the w clamp and viewport z probes as controls, on the laptop, linux fork with the debug option on; one run each"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-objects", "ta-regions"]
terms = ["PB_OBJ.PRIM_LIST", "PB_OBJ.LINE_WIDTHS", "CSTREAM.PRIM_POINTS", "CSTREAM.PRIM_VERTICES", "CSTREAM.OBJ_PRIMS", "ISP0.OBJ_TYPE", "VDM_INDEX0.PRIMITIVE_TOPOLOGY"]
+++

**What runs.** The probes save the parameter buffer after the render. The object's primitive list
sits between ISP word 1 and the line-width dword (E176, E178); the streams are those of E177.

**Results.**

- *The list.* One 16-bit entry per primitive, two to a dword with the first entry in the low half,
  the last entry repeated to fill an odd count. An entry is three 5-bit vertex numbers, the first
  in bits 4:0. The triangles: 0x4a30 is (16, 17, 18) for the first, then 0x5693 (19, 20, 21),
  0x62f6 (22, 23, 24), 0x6f59 (25, 26, 27) and 0x7bbc (28, 29, 30) for copies two to five, giving
  the dwords 0x4a304a30 (one), 0x56934a30 (two), 0x56934a30 and 0x62f662f6 (three), 0x56934a30
  and 0x6f5962f6 (four), and these two and 0x7bbc7bbc (five). The object's vertices are therefore
  numbered from 16.
- *Points.* Three points, index list type 2: ISP word 0 is 0x01d18200 (the triangle's with 0x18000
  added) and the list is 0x46314210 and 0x4a524a52, that is (16, 16, 16), (17, 17, 17),
  (18, 18, 18): each point repeats its vertex.
- *Lines.* One line (index list type 1, two indices): ISP word 0 is 0x01d08200 (the triangle's
  with 0x8000 added), the object has 2 vertices and the entry is 0x4630 = (16, 17, 17), the
  second vertex repeated, as the list 0x46304630. Two lines over four vertices: the entries are
  0x4630 and 0x4e72 = (18, 19, 19), the dword 0x4e724630.
- *The primitive word.* Bits 30:29 are 2 for the triangles and lines (0x4490ffff, 0x4290ffff for
  the line, 0x4688000f for two lines) and 3 for points (0x64800101); bits 28:25 are the vertices
  less one (2, 5, 8, 11, 14 for 3, 6, 9, 12, 15 vertices; 1 for the line's 2; 2 for the
  points' 3). So bit 29 marks points. ISP word 0 is what tells lines from triangles in the
  object (the added 0x8000 or 0x18000 above). Two lines add a further dword to some streams
  (0x00010003, 0x00010001, 0x00020002).
- *The object word.* Its bits 31:26 are 1, 3, 5, 7 and 9 for one to five triangles; 1 and 3 for
  one and two lines; 5 for three points: twice the primitives less one in every dump.
- *Controls.* The w clamp at 1e-3 leaves the object word for word as the plain triangle's. The
  viewport z probe (offset 0.75, scale 0.25) changes the stored depths (0x3f40 in the packed
  vertex words) and nothing else.

**Not shown.** The meaning of the vertex numbering from 16. Lines with an odd count of indices
hang in the vdm/state1 table's lines3 job (E186) and are not drawn here. The reading that the
list entry is a vertex triple, bit 29 a points marker and the object word's bits 31:26 twice the
primitives less one, is the pattern of these dumps [infer].
One run each.

**Correction 2026-11-10:** A post hoc reading of the objects of S1 and S1b's g-e3 (41 dumped objects of 3,
4 and 5 vertices; a fit on data measured before the reading, not a test), made before the round 2
runs; the entries above stand as measured. [infer] The primitive list is a triangle strip: the
entries of a 4-vertex object are (0, 1, 2) and (2, 1, 3), and of a 5-vertex object (0, 1, 2), (2,
1, 3), (2, 3, 4) over the stored vertices (41 of 41 objects). Each 5-bit field is a bit 4 flag plus
a 4-bit stored vertex index in bits 3:0: the flag says that the edge from this vertex to the next
vertex of the triangle is a boundary edge of the polygon (0 for an internal diagonal), and it is set
on every edge of a lone triangle, which is why the fields read as "16 to 31" above (the flag plus
the index 0 to 15) and not as numbers counted from 16 (the object's vertices are numbered from 0).
The stored vertex order is the strip's zigzag p1, p2, p0, p3, ... of the clipped polygon's boundary
(41 of 41 are a zigzag of their convex hull); for the two z cuts the polygon is Sutherland-Hodgman
over the input edges A to B, B to C and C to A, whose zigzag is exactly the stored order (2 of 2
each, repeats included). The "meaning of the vertex numbering from 16" left open above is thus
read as an index plus an edge flag; this is not tested by a frozen run. Q070 and E546 (whose
primitive list equals the control's in 9 of 9 jobs, so its measurements are unaffected) refer to
this re-reading.
