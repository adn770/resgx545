+++
id = "E349"
claim = "The closed driver's 1263 captured VDM streams use three block types only, state (bits 31:30 = 1), index list (2) and terminate (3), and no link (0), each stream one GENERAL object from CR_VDM_CTRL_STREAM_BASE to a lone terminate word 0xc0000000; every stream ends with a state block whose second word is 0x0400e100, the end-of-scene state block (first word bit 29 set, second word 0x0e022401) and the terminate; a draw adds its MTE state block (second word 0x0e0224nn, bits 25 and 17 set) and, before its index list, a block that loads the vertex program's constants (0x0800e1nn or 0x0c00e1nn, bit 8 set) when its state changed, and only an index list when nothing changed; state blocks' first words point into PDSVERTEX_CODEDATA, bit 28 is never set"
unit = "vdm"
method = "the thirteen 3D capture tables of 11.11 (604 runs, 1263 kicks of the closed GLES1 and GLES2 stacks under the harness on the laptop): every kick's whole VDM control stream decoded with kickwalk.decode_vdm over the 64 KiB state3d.py reads from the stream's base (VDM_READ; decode_vdm stops at 4096 blocks, never reached), block by block, the PDS addresses resolved in the kick's snapshot"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "VDM_BLOCK.TERMINATE", "VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13",
    "VDM_STATE1.BIT25", "VDM_STATE1.BIT18", "CR_VDM_CTRL_STREAM_BASE", "control stream",
]
+++

**What runs.** 1263 kicks over thirteen tables: 4404 state blocks, 1888 index lists, 1263
terminate words, no link block.

**Results.**

- Every stream lies in one GENERAL object (`0x5000` bytes), starts at
  `CR_VDM_CTRL_STREAM_BASE` and ends at its first terminate, a single word `0xc0000000`.
- The first kick of a one-triangle frame (base):

  | block | second word | what its PDS program does |
  |---|---|---|
  | state | 0x0e022403 | copies the clear's MTE state block (12 dwords) |
  | index list | | the clear's triangle |
  | state | 0x0e022405 | copies the triangle's MTE state block (18 dwords) |
  | state | 0x0800e103 | copies the vertex program's constants (10 dwords) |
  | index list | | the triangle |
  | state | 0x0400e100 | starts a USSE task only |
  | state | 0x0e022401 | writes the end-of-scene state (presence 0x2000) by douta |
  | terminate | | |

  The second kick of every frame is the last two state blocks and the terminate alone.
- Draws with unchanged state add one index list each: draws=2, 4, 64 and 256 give 2, 4, 64 and
  256 index lists after one triangle state block. With a flush between two draws the second kick
  starts with the triangle's state block and the constants block again.
- Second words seen: 0x0e0224nn (nn 01 and 03 to 07) on MTE state blocks; 0x0800e1nn (nn 03,
  04, 06, 07, 0b, 13) and 0x0c00e1nn (nn 06, 0c, 23, 43: GLES1 lighting and points, a matrix
  palette, skinning) on constant blocks; 0x0400e100 on the closing USSE-only block. Bits 31:26
  are the block's PDS data in rows (3, 2 or 1), bits 7:0 the rows of attributes its USSE program
  writes.
- First words: bits 31:28 are 4, or 6 on the end-of-scene block (bit 29); bit 28 never; bits
  27:0, times 16, land in a PDSVERTEX_CODEDATA object.

**What it shows.**

- In the closed driver's streams the block type is bits 31:30 and only three of the four types
  occur; a stream is never split across objects, so the link type has no captured instance
  [CAP]. The terminate word is a single word with no address [CAP].
- The MTE state blocks carry bits 25 and 17 (SD and MTE emit in kickwalk's names) and use pipe 1,
  two partitions; the constant and USSE-only blocks carry bit 8 (`VDM_STATE1.BIT8`, the
  secondary) and use pipe 7 with no partitions [CAP]. Bits 18 and 12 are clear in every block.
- A state change, not a draw, is what costs a state block: the closed driver re-sends state only
  after a change or a flush [CAP].
