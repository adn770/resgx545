+++
id = "E651"
claim = "The object's packed vertex block (E176's 8 dwords for 3 vertices) is a bit stream, least significant bit first, of 80 bits for each vertex: the window y as a 24-bit field of (y + 4096) * 256, the window x the same way, then the 32-bit depth float; E176's 8 dwords for the plain probe decode to (8, 8), (56, 20), (20, 56) at depth 0.5, and 89 of 89 dumped jobs (up to 15 vertices, 38 packed dwords) hold the packed block this rule writes from the vertices the vertex program gave and the viewport, with every window coordinate a multiple of 1/16 pixel"
unit = "ta"
method = "offline decode: E176's listing 0x00100800, 0x00001008, 0x14003f00, 0x10380010, 0x3f000000, 0x00103800, 0x00001014, 0x00003f00 read as one bit stream gives 24, 24 and 32 bit fields at bits 0, 24 and 48 of the first vertex and the next vertex at bit 80; written as a rule (sgx-pipe ta::object_words, first as a unit test of the record's listing) and checked in the replay of E650 on 89 dumps (ta-tri-region, ta-regions, ta-objects, ta-object-words, vdm-vtask-capacity); one run each"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["ta-objects", "ta-tri-region", "ta-regions", "scene-vectors-12-2"]
terms = ["PB_OBJ.ISP_WORDS", "PB_OBJ.SET_MASKS", "VIEWPORT.X_OFFSET"]
+++

**Results.** [HW] The first vertex of the plain probe, (8, 8): y = 0x100800 = (8 + 4096) * 256 in
bits 23:0 of the first dword, x the same in bits 47:24, the depth 0x3f000000 in bits 79:48. Vertex
1, (56, 20), starts at bit 80: y = 0x101400 and x = 0x103800. The viewport z offset of 0.75 changes
the depth bytes of the three vertices and nothing else (E176). In the dumps of E650 the window
coordinates are the viewport offset plus scale times the clip coordinate, for example 63.875 + 64 *
-0.75 = 15.875, and every packed field equals (v + 4096) * 256 exactly: the block is the vertex
program's output through the viewport and nothing else. A block of n vertices takes ceil(80 n / 32)
dwords: 8 for 3, 38 for 15.

**Not shown.** How a coordinate with more than 8 fraction bits is rounded, whether the product and
the sum of the viewport are fused, and what the depth is for a vertex with w other than 1 (Q230).
