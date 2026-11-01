+++
id = "Q070"
question = "what do the TA object's format word bits 15:8 and above and its set masks select beyond the settings seen, and does the fitted region test hold for lines and points?"
unit = "ta"
phase = 11
evidence = ["E176", "E177", "E180", "E181", "E185", "E306", "E307", "E308", "E414"]
terms = ["PB_OBJ.PDS_WORDS", "PB_OBJ.SET_MASKS", "PB_OBJ.FORMAT", "CSTREAM.PRIM_TILES",
         "REGION_HDR.POS"]
+++

Two parts are answered. The object's three header words are the state block's words 3-5, the
pixel program's secondary pointer, size word and primary pointer, copied as given: six values set
in them appear unchanged in the object and nothing else changes (E306, one run). The region test
fitted to 26 shifts of one triangle (E180) predicts every region and every `CSTREAM.PRIM_TILES`
form of 24 fresh random triangles on 128x128, 20 of them reaching past the target: 265 regions,
none missing, none extra (E307, one run). Those triangles confirm the test as a generic overlap of
triangle and tiles, not the rules the fit decided at the tile boundaries (the bounding box half-open
between a region's two tiles, the closed corners): no vertex or edge of theirs lies on a boundary,
and only the forms 0x80, 0x90 and 0x98 occur. The boundary rules rest on E180 alone.

The layout of 3d.md §10.1 decodes the 28 object dumps it was written from and the 45 taken since
(E308), placed by the stream's object word; the new ones all have the format 0x00040101, so they
test the placement and the vertex count, not the other formats. The format word's bits 7:0 count a
vertex's dwords in the object (1, 2, 3 or 5), and the set masks of the in-sample dumps read as half
precision (mask 1) and, by the coordinate-size settings 1, 3, 4 and 5, one component (mask 2), z
(mask 3) and w (mask 4) [infer: one value per setting]. Bit 15 of a primitive list entry follows
the winding of the random triangles (E308) [infer].

What is open: the format word's other bits beyond 18 and 19; the set masks for several sets and each
coordinate format; the region test's boundary rules on triangles it was not fitted to; the region
test for lines and points; that the ISP walks the headers [infer].

To settle it: the object dumped over every coordinate size and format of two and three sets
(vtx_coords 4 to 11), read with ta_words.py object; the random-triangle probe with lines and points
(the index list's topology), compared by ta_words.py regions with a line and point test; triangles
placed on the boundaries, a vertex or an edge exactly on the line between a region's two tiles, on a
tile's corner and on the region's edges, and triangles whose primitive mask needs the forms 0x8a and
0x8c (several primitives of one object, as in the five-copy scene), to test the fitted boundary
rules.

Narrowed in 11.15 (E414): the index list's topology (bits 29:26 of its header) on our triangle job
with 3 and with 15 vertices: 3 (strip) and 4 (fan) give the triangles of a strip (16, 17, 18), (17,
19, 18), ... and a fan (16, 17, 18), (16, 18, 19), ...; 1 (line) hangs the job and 2 (point)
completes with no object and every pixel the background, so lines and points cannot be run through
this stream and the region test's line and point rules (the second part) stay untested; the format
word's other bits and the vtx_coords 4 to 11 dumps were not run. Status: narrowed, not answered.
