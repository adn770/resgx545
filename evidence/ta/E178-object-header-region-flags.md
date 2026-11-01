+++
id = "E178"
claim = "The TA's object carries ISP words 0 and 1 exactly as the job gives them (11 values tried), then the primitive list and the line width in both bytes of one dword; the region headers list every 32x16 region of the macrotiles, the ones outside the target included, with flags for outside, first of a macrotile, empty inside the target, last of a macrotile and last of the scene"
unit = "ta"
method = "the ISP-word probes of probes/ta/objects.toml (ISP word 0 with five pass and depth settings and a stencil reference, ISP word 1 with polygon offset, visibility test, line widths 0x20 and 0x35, and bit 12 clear) and the target-size scenes of probes/ta/regions.toml (64x32, 32x64, 64x192, 192x64, 128x128, 256x256) with the 64x64 headers from the dumps of probes/ta/objects.toml and of the regions.toml scenes of two to five copies, the parameter buffer and TA data saved after the render, on the laptop, linux fork with the debug option on; one run each"
tiers = ["HW"]
date = "2026-11-02"
data = ["ta-objects", "ta-regions"]
terms = ["PB_OBJ.PDS_WORDS", "PB_OBJ.ISP_WORDS", "PB_OBJ.LINE_WIDTHS", "PB_OBJ.PRIM_LIST", "REGION_HDR.FLAGS", "REGION_HDR.POS", "ISP1.LINE_WIDTH", "macro tile"]
+++

**What runs.** The ISP probes change one of the job's two ISP words and save the parameter
buffer; the scene probes draw the triangle on several targets and save the TA data. The object
is the dwords of the first page (E176); the headers are those of E177.

**Results.**

*The object.* Its dwords 6 and 7 (after three header words and three 1/w) are ISP word 0 and ISP
word 1, and each value tried lands there unchanged:

- ISP word 0: 0x01d00200 (the plain job), 0x00400200, 0x02400200, 0x03d00200, 0x08400200 and
  0x01d00255 (a stencil reference of 0x55). Nothing else in the object changes.
- ISP word 1: 0x000010f0 (plain), 0x008010f0 (bit 23, polygon offset), 0x000010f8 (bit 3, the
  visibility test), 0x000020f0 and 0x000035f0 (line widths 0x20 and 0x35 in bits 15:8), and
  0x000000f0 (line width 0).
- The dword after the primitive list (E181) is **the line width in both bytes**: 0x1010 at width
  0x10, 0x2020, 0x3535, and 0 when the width is 0. The word equals ISP word 1's bits 15:8 in
  both bytes; the format word, the masks and the vertices follow (E176).
- The word the object also holds, 0x4a304a30 for the plain triangle, does not stay constant: it
  is the primitive list of E181 (it is 0x46304630 for a line and 0x46314210 for points).

*The region headers.* In all seven target sizes the headers list the regions of every macrotile
the target needs, the ones past the target's edge included: 64 for 64x64, 64x32, 32x64, 192x64
and 128x128, and 128 for 64x192 and 256x256. Word 0's flags in bits 31:24:

- bit 25 (0x02): the region lies outside the target: 56 of the 64 headers on 64x64, 60 on 64x32
  and 32x64, 104 of 128 on 64x192, 40 of 64 on 192x64, 32 on 128x128, none on 256x256;
- bit 26 (0x04): the first header of a macrotile that holds regions of the target: 1 header on
  64x64, 64x32 and 32x64, 2 on 192x64, 64x192 and 128x128, 4 on 256x256;
- bit 27 (0x08): a region inside the target with no stream;
- bit 28 (0x10): the last header of such a macrotile (the same counts as bit 26: 0x10, 0x18, 0x18
  and 0x98 on 256x256);
- bit 31 (0x80): the last region of the scene (0x98 on an empty one, 0x90 with a stream).

Bits 15:12 of word 0's row field number the macrotile (0 to 3).

**Not shown.** What the object's first three words are made from (E176). The role of the
visibility and polygon-offset bits is not read here, only that they pass through. Targets above
256x256 and sizes that are not multiples of 32x16. One run each.
