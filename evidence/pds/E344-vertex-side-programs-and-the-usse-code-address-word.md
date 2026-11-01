+++
id = "E344"
claim = "In the closed driver's captured kicks every USSE code-address word a PDS program hands to doutu holds a code-base index in bits 3:0 and an instruction index in bits 23:4: the pixel-side programs (special object, MTE pixel programs, end of render) use base 0 and the vertex-side ones (VDM state-block programs, vertex tasks) base 10, and with base 0 at 0xf4000000 and base 10 at 0xfc000000 all 15071 land on an instruction inside an object of the PIXELSHADER or the VERTEXSHADER heap, as the side says; a vertex task's PDS program fetches each attribute with one doutd whose second word gives the attribute's dwords less one in bits 3:0 and its offset in the vertex's attribute rows in bits 19:8, from a data word holding the stream address and one holding the stride in bytes, and starts its USSE program with a base-10 doutu"
unit = "pds"
method = "the thirteen 3D capture tables of 11.11 (604 runs of the closed GLES1 and GLES2 stacks under the harness on the laptop): each PDS program state3d.py walks (special object, end of render, VDM state blocks, MTE pixel programs, vertex tasks), its doutu operand resolved with the code bases the harness's heap layout gives (summary3d.DEFAULT_CODE_BASES) in the kick's snapshot; the vertex tasks' data words and doutd operands over usse-inputs' attribute layouts"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "PORT.DOUTU", "DOUTU0.TEMPS", "VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE",
    "HEAP.PIXELSHADER", "CR_USE_CODE_BASE_0", "CR_USE_CODE_BASE_10",
]
+++

**What runs.** 604 runs over thirteen tables; the walker reaches 15071 doutu operands that are
data words.

**Results.**

| program | code base | heap the address lands in | doutu words |
|---|---|---|---|
| special object (secondary and primary) | 0 | PIXELSHADER | 2526 |
| end of render (three tasks each) | 0 | PIXELSHADER | 3789 |
| MTE secondary and primary pixel programs | 0 | PIXELSHADER | 2464 |
| VDM state blocks (MTE state copy, constants, end of scene) | 10 | VERTEXSHADER | 4404 |
| vertex tasks | 10 | VERTEXSHADER | 1888 |

Every address is a multiple of 8 from its object's start and below the object's size. Bits
31:24 of the word are 0 except in two of the three end-of-render tasks, which carry bit 24.

The vertex task programs, over the attribute layouts of usse-inputs (one position attribute):

| attribute | doutd word 1 | stride data word |
|---|---|---|
| float x4 (base) | 0x3 | 0x10 |
| float x3 / x2 | 0x2 / 0x1 | 0xc / 0x8 |
| short x4, normalised or not, ushort x4 | 0x1 | 0x8 |
| short x2, byte x4, ubyte x4 | 0x0 | 0x4 |
| byte x3, stride 8 | 0x0 | 0x3 |
| float x4, stride 32, client array | 0x3 | 0x10 |
| float x4, stride 32, buffer object | 0x3 | 0x20 |

- The doutd's first operand is the stream's address: the driver's copy of a client array, or the
  buffer object itself (`vbo`). A second attribute (`varying`) adds a doutd with word 1 `0x403`:
  four dwords at offset 4, the second row of the vertex's attributes.
- The data size of a vertex task (vertex-task word 1 bits 6:0) is 2 rows with one attribute and 3
  with two; its attribute rows (bits 14:7) count the attributes, one row each.
- Normalisation and the element type change no PDS word: the vertex program receives the raw
  bytes.

**What it shows.**

- `PORT.DOUTU`'s first word is a code-base index and an instruction index, and the closed driver
  keeps pixel programs under base 0 and vertex-side programs under base 10 [CAP]; that base 0 and
  base 10 are the PIXELSHADER and VERTEXSHADER heaps' starts is what every address fits, the
  registers themselves being the init script's [CAP: the bases are the harness's heap layout].
- A vertex fetch is one doutd per attribute, sized in dwords from the element size (bytes
  rounded up to dwords) and placed in rows of four dwords; the stride lives in the program's data
  for its code to use, and client arrays are repacked to their element size while buffer objects
  keep the application's stride [CAP].
