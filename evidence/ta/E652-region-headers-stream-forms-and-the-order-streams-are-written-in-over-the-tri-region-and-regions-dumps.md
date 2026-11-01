+++
id = "E652"
claim = "The TA's headers and streams of E177 and E180 follow these rules in 89 of 89 dumped jobs: a header's flags are 0x02 outside the target, 0x08 for a target region with no stream, 0x04 on the first and 0x10 on the last header of a macrotile with target regions and 0x80 on the last such header of the last such macrotile (headers in macrotile order, macrotile m = column * n + row of macrotiles, regions in raster order, 2 macrotiles in a row up to 256 x 256); a macrotile's streams share one page, the pages go 0x2000, 0x3000, ... to the macrotiles that have streams in raster order of the macrotiles (rows outer), and a stream block of 128 bytes goes to each region in the order of 64 x 64 pixel blocks (two regions across and four down, in raster order, regions in raster order within one); the forms of the primitive word are 0x90 with 0xffff when both tiles list every primitive, otherwise for one tile 0x80 (left) or 0x98 (right) with the primitive mask in bits 7:0 and the vertex mask (3 bits a primitive) in bits 15:8 while that mask fits a byte, else 0x8a or 0x8c with the vertex mask in bits 15:0 and the primitive mask in a further dword, and for both tiles with different masks 0x88 with the vertex mask of the union and a further dword of the right mask in bits 31:16 and the left in 15:0"
unit = "ta"
method = "offline: the stream forms and the walk order read from the 35 ta-tri-region dumps (table of forms by object size and mask counts; the 256 x 256 jobs for the page order and the block walk; one 64 x 64 and one 128 x 128 job for the flags), written as rules (sgx-pipe ta::stream_words, walk, headers, write; unit tests from the dumps' words) and replayed over ta-regions (37 dumps: the tile test and the primitive word forms 0x80, 0x98 and 0x90 are E180's and E177's, the forms 0x88, 0x8a and 0x8c, the page order and the four non-square targets are not in an earlier record), ta-objects, ta-object-words and vdm-vtask-capacity; the packed vertices are E651"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["ta-tri-region", "ta-regions", "ta-objects", "ta-object-words", "vdm-vtask-capacity", "scene-vectors-12-2"]
terms = ["CSTREAM.PRIM_TILES", "CSTREAM.OBJ_ISP_ADDR", "REGION_HDR.POS", "REGION_HDR.FLAGS", "REGION_HDR.STREAM"]
+++

**Results.** [HW] Over the 35 ta-tri-region dumps the primitive words of the 5-primitive objects
take these forms (counts of regions): 0x90 205 (both tiles, all five), 0x88 66 (both tiles, masks in
the further dword, among them left 3 right 3 and left 3 right 0x1f), 0x8a 61 and 0x8c 38 (one tile,
mask above a byte), 0x80 6 and 0x98 12 (one tile, the first two primitives, vertex mask 0x3f). The
objects of two primitives give 0x80, 0x98, 0x90 and, for a region whose tiles' masks are 3 and 1,
0x4a88003f with the further dword 0x00010003. The page of each macrotile: at 128 x 128
0x2000 and 0x3000; at 256 x 256 the macrotiles 0, 2, 1, 3 get 0x2000, 0x3000, 0x4000 and 0x5000
(macrotile 2 is the right column's first). The streams of macrotile 0 of the 128 x 128 job go to
the regions 0, 4, 5, 8, 9, 12, 13, 6, 10, 11, 14, 15 at 0x2000 + 0x80 k. Header flags at 64 x 64:
the first header 0x04, the second 0x08, the outside ones 0x02, header 13 (the last target region)
0x90.

**What it does not settle [infer].** Why the order is by 64 x 64 blocks (the four-tile blocks of
TE_MTILE, E247); whether a macrotile with more than 32 streams (several objects) continues on the
next page; the form for an object of two primitives in both tiles with the same, not all, mask
(none dumped); the forms of four macrotiles in a row. In the 35 dumps in sample the rules are fits;
what the other jobs hold that no earlier record gave (the forms 0x88, 0x8a and 0x8c, the page
order, the four non-square targets) is the check, and the tile test is E180's (E650).

The narrow form's limit "while that mask fits a byte" is the same rule as "while the mask names
primitives 0 and 1 only": the vertex mask is a sum of 7 << 3k, so the value 0xff is unreachable
and "at most 0xff" and "below 0xff" give the same forms.