+++
id = "E347"
claim = "The closed driver's MTE state blocks take eight presence words, 0x2000 (2 dwords), 0xd485 (9), 0xd4c3 (12), 0xd4c7 (13), 0xdf43 (18), 0xdf47 (19), 0xdfc3 (20) and 0xdfc7 (21), each block exactly the presence word plus the words its set bits add in bit order (isp0, isp1, isp2 one each, the pixel programs three, the region clip two, the viewport six, then one each for bits 9 to 15); the VDM state block's PDS program copies it with doutd, whose second word gives the dwords of a line less one in bits 3:0, the lines less one in 7:4, the destination dword offset in 19:8 and the line stride less one in 29:22, equal to the line length in every copy, a block over 16 dwords going as two or three lines (18 as 2 x 9, 20 as 2 x 10, 21 as 3 x 7) or as a 16-dword line and a second doutd of 3 dwords at offset 16; the end-of-scene block is written by douta instead; the VDM state word's bits 7:0 are at least the block's dwords in rows of four"
unit = "mte"
method = "the thirteen 3D capture tables of 11.11 (the closed GLES1 and GLES2 stacks under the harness on the laptop): the PDS program of every VDM state block whose USSE task emits MTE state (state3d.py's vdm.b<i>.pds and mte.* paths), its dout writes decoded, the copied words named by the presence word"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "PRESENCE", "PRESENCE.WCLAMP", "PRESENCE.COORD", "ISP0.ISP2_PRESENT", "OUTSEL",
    "MTECTL.CULL_MODE", "VIEWPORT.X_OFFSET", "COORDSIZE.SET_LAYOUT", "COORDFMT.SET_F16", "WCLAMP",
    "TERM.CLIP_RIGHT", "TERM.CLIP_BOTTOM", "DOUTD1", "DOUTD1.BURST", "DOUTD1.LINES",
    "DOUTD1.OFFSET", "DOUTD1.STRIDE",
]
+++

**What runs.** 2507 MTE state blocks over thirteen tables: 1263 end-of-scene blocks and 1244
blocks of draws and clears.

**Results.**

| presence | dwords | words, in order | doutd word 1 (and a second) | blocks |
|---|---|---|---|---|
| 0x2000 | 2 | term | none: four douta | 1263 |
| 0xd485 | 9 | isp0, isp2, clip0-1, outsel, mtectl, coordsize, coordfmt | 0x02000008 | 12 |
| 0xd4c3 | 12 | isp0-1, pds x3, clip0-1, outsel, mtectl, coordsize, coordfmt | 0x02c0000b | 588 |
| 0xd4c7 | 13 | the same with isp2 | 0x0300000c | 10 |
| 0xdf43 | 18 | isp0-1, pds x3, vp0-5, bit 9, outsel, wclamp, mtectl, coord x2 | 0x02000018 | 583 |
| 0xdf47 | 19 | the same with isp2 | 0x03c0000f and 0x00801002 | 10 |
| 0xdfc3 | 20 | 0xdf43's with clip0-1 | 0x02400019 | 39 |
| 0xdfc7 | 21 | 0xdfc3's with isp2 | 0x01800026 | 2 |

- The doutd's first operand is the block's address in PDSVERTEX_CODEDATA; the program's data
  holds a second doutd slot, address and control 0, used only by 0xdf47 (3 dwords at offset 16).
- The copies' dwords, (bits 3:0 + 1) x (bits 7:4 + 1) plus the second doutd's, equal the block
  length the presence word gives in all 1244 blocks, and bits 29:22 equal bits 3:0 in each.
- The VDM state block's second word, bits 7:0, against the block: 3 for 9 and 12 dwords, 4 for
  13, 5 for 18 to 20, 6 for 21, 1 for the end-of-scene block; and 7 for 41 of the 18- and
  20-dword blocks: the triangle blocks of the scissor and viewport runs (after a clear split
  into mask fills) and of later kicks of flushed, multi-frame and render-to-texture scenes.
- The end-of-scene program writes the presence word to attribute 0 and the term word to
  attribute 1 by douta, then starts its USSE task.
- Bits 3 to 5 and 16 to 31 of the presence word are never set.

**What it shows.**

- The presence word's layout holds for every block the closed driver builds: the block has
  exactly the words its bits announce, in bit order, with the word counts state3d.py's PRESENCE
  table gives [CAP]. Bit 2 (isp2, the stencil word) is set whenever stencil is enabled and in the
  mask fills (0xd485, with no isp1 or pixel programs), and the screen-space blocks of a clear or
  a mask fill carry no viewport, wclamp or bit 9 word [CAP].
- doutd's second word is a 2D copy: line length less one, lines less one, a destination offset in
  attribute dwords and a line stride less one; the closed driver's copies always have stride equal
  to length [CAP]. Where a block needs more than 16 dwords it is cut into equal lines or, once,
  a 16-dword line and a remainder at offset 16 [CAP].
- The USE attribute rows the VDM state word asks for cover the copied block; what the 7 rows of
  some blocks are for is not shown [CAP].
