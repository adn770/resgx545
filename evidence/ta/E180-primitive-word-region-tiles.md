+++
id = "E180"
claim = "The primitive word's bits 23:16 say which of a 32x16 region's two 16x16 tiles the triangle meets: 0x80 the left tile only, 0x98 the right only, 0x90 both; over 26 viewport offsets and 472 streamed regions all three forms occur (74, 106 and 292 regions) and a bounding-box and edge test against the tiles reproduces every region's form"
unit = "ta"
method = "the 26 sweep probes of probes/ta/regions.toml (the triangle on 128x128 moved by 0 to 32 pixels in x in steps of 2 and by 0 to 16 in y), the parameter buffer and TA data saved after each render, every streamed region's primitive word read, against a tile test applied to the triangle's pixel vertices (region_tiles.py), on the laptop, linux fork with the debug option on; one run each"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-regions"]
terms = ["CSTREAM.PRIM_TILES", "control stream", "tile"]
+++

**What runs.** The triangle of the scene probes, on 128x128, is shifted by the viewport's x or y
offset: x from 0 to 32 in steps of 2 (17 dumps), y from 0 to 16 in steps of 2 (9 dumps). In each
dump every region with a stream is read: the primitive word is the first word of its stream
(E177). A 32x16 region is two 16x16 tiles side by side.

**Results.** Over the 26 dumps there are 472 regions with a stream, all with the object word
0x04000406 and a primitive word of one of three forms:

- 0x44800701, bits 23:16 = 0x80: 74 regions;
- 0x44980701, bits 23:16 = 0x98: 106 regions;
- 0x4490ffff, bits 23:16 = 0x90: 292 regions.

The one-tile forms carry masks 0x0701 in bits 15:0 and the two-tile form 0xffff. A tile test
applied to the triangle's vertices (shifted by the same offset) gives, per region, which of the
region's two tiles the triangle meets: the bounding box against the tile, closed but half-open on
the line between the region's two tiles (a triangle whose leftmost point lies on that line is the
right tile's only), then each edge's line against the tile's corners, closed (an edge through
the corner between the tiles meets the left tile too, and touching the region's outer sides
counts). With that test, left only is exactly 0x80 (74 of 74), right only exactly 0x98 (106 of
106) and both exactly 0x90 (292 of 292).

The forms also occur outside this sweep: the scene probes of two to five copies at 64x64 give,
for objects of more than 3 vertices, 0x4a803f03 and 0x4a983f03 (two copies) and 0x5c8a7fff,
0x5c8c7fff and 0x5c90ffff (five), that is bits 23:16 of 0x80, 0x98, 0x8a, 0x8c and 0x90, the
masks not fitting the word's low 16 bits for five copies (the primitive mask is in a further
dword, 0x1f).

**What it shows [infer].** The reading that bits 23:16 are a tile pair (one bit pattern per tile
combination) rests on the tile test reproducing 472 of 472 regions; the test was fitted to this
sweep's data, so it is a description of these dumps and not a prediction on new ones. The 0x8a
and 0x8c forms of the five-copy scene are not covered by it.

**Not shown.** Why the test is half-open on the line between the tiles (it is the choice that
fits). The roles of the other bits of the field, and of bit 24. Triangles other than ours, so
the bounding-box choice may be only one of several that fit this triangle. One run each.
