+++
id = "E177"
claim = "The TA writes for the triangle one region header per 32x16-pixel region of the target's macrotiles and, for the regions it bins the triangle into, a 128-byte-step control-stream block of a primitive word and an object word (a third dword with more than 6 vertices of the object) pointing at the object; 64x64 gives 7 streams, 128x128 19 against 17 regions with a pixel centre covered"
unit = "ta"
method = "the scene probes of probes/ta/regions.toml (the triangle at 64x64, 64x32, 32x64, 192x64, 64x192, 128x128, 256x256, and two to five copies at 64x64), the parameter buffer and TA data saved after the render and read as dwords, on the laptop, linux fork with the debug option on; one run each"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-regions", "ta-objects"]
terms = ["REGION_HDR.POS", "REGION_HDR.STREAM", "REGION_HDR.FLAGS", "CSTREAM.PRIM_VERTICES", "CSTREAM.OBJ_ISP_ADDR", "CSTREAM.OBJ_PRIMS", "region header", "control stream", "tile", "macro tile"]
+++

**What runs.** The scene probes render the 64x64 triangle (and copies of it) or the triangle on
other target sizes, and save the parameter buffer and the TA data. The TA data's first non-empty
page holds the region headers, three dwords each; the parameter buffer's object is on its first
page and the stream blocks from byte 0x1000 on.

**Results.**

- *Headers.* Word 1 is the address of the region's stream block (a multiple of 0x80, relative to
  the slot, 0x2000 on) or 0, and word 2 is 0 in every header. Word 0 places the region: bits 23:16
  step by 2 per 32-pixel column, bits 15:0 by 2 per 16-pixel row, with bits 15:12 the macrotile
  number (0 to 3 in all the dumps). A region is therefore 32x16 pixels. The number of headers
  written follows the macrotiles: 64 for 64x64, 64x32, 32x64, 192x64, 128x128 and the copies, 128
  for 64x192 and 256x256.
- *Streams.* Every one of the 824 stream blocks in the dumps of the objects and regions tables is 2
  words (the primitive word, then the object word) or 3 (one more dword, a vertex or primitive mask)
  followed by 0xc0000000 filler up to 8 dwords; the rest of the 128-byte step is zero. The blocks
  are distinct and 128 bytes apart (0x2000 to 0x2300 for 64x64; two pages, 0x2000 to 0x3380, for
  128x128; four, 0x2000 to 0x5280, for 256x256).
- *How many regions get a stream.* The triangle covers 7 regions at 64x64 and the TA writes 7
  streams (also 7 for two to five copies of it). On 128x128 it writes 19 streams, with a pixel
  centre of the triangle in 17 regions; on 256x256, 56 against 46. The TA's region test is wider
  than the pixels.
- *Object word.* Its low bits are the dword address, in the slot, of the object's ISP words:
  0x406 for the object of one triangle (the ISP words are its 7th dword, at slot byte 0x1018),
  0x409, 0x40c, 0x40f and 0x412 for two to five copies (ISP words after 3 header words and 3
  dwords of 1/w per triangle). Its bits 31:26 are 1, 3, 5, 7 and 9 for one to five triangles:
  twice the primitives less one.
- *Primitive word.* Bits 30:29 are 2 for triangles; bits 28:25 are the object's vertices less one
  (2, 5, 8, 11, 14 for 3, 6, 9, 12, 15). With bits 23:16 at 0x90 (both of the region's
  16x16 tiles, E180) the region takes all the object's primitives (0x4490ffff, 0x5c90ffff);
  otherwise the word carries masks in bits 15:0 (E180).
- *Nothing drawn.* Where the triangle is culled the TA writes no stream and every header reads
  empty (E185).

**What it shows [infer].** The TA bins each object into 32x16 regions and writes, for each region
it meets, a stream entry pointing at the object with the subset of its primitives in the region
(all of them, or a mask). The region headers are the list of regions the ISP walks; that they are
so is a reading, nothing here runs the ISP over them.

**Not shown.** The meaning of bits 19:16 and bit 24 of the primitive word beyond the tile bits of
E180, and of the object word's bits 31:26 beyond the count above. Larger objects than five
triangles. The reason the region test is wider than the pixels. One run each.
