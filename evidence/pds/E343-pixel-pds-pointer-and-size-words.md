+++
id = "E343"
claim = "Every pixel PDS pointer the closed driver writes (an MTE state block's secondary and primary words, the TA command's special object words 0 and 2) holds the program's offset from PDS_EXEC_BASE in 16-byte units in bits 23:0 and its data size in 16-byte rows in bits 31:26, bits 25:24 clear; each resolves into a PDSPIXEL_CODEDATA object holding the whole data, and the highest data dword the program's dout operands read lies in the last row the pointer counts in 4978 of the 4990 programs (the other 12, all GLES1, also read registers above their data); of the size word between them, bits 17:16 are 3 in every block, bits 24:18 at least the secondary's constant dwords in rows of four (0 to 6), bits 6:0 1 except with three or more iterated sets (2 and 4), and bits 31:25 0 on the clear's blocks and otherwise 12, or 11 when bits 24:18 are not 0, divided by bits 6:0 and rounded down; the special object's size word is 0x00030001 in all 1263 kicks"
unit = "pds"
method = "the thirteen 3D capture tables of 11.11 on the laptop's GLES1 and GLES2 stacks (604 runs, 1263 kicks): state3d.py's MTE state words (mte.pds_sec, pds_size, pds_pri) and TA command words (cmd.pds_bgnd), each pointer resolved in the kick's snapshot (kickwalk.Snapshot) and its program's dout operands decoded (state3d.pds_outputs)"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "PDS_SIZE.BITS17_16", "PDS_SIZE.BITS24_18", "PDS_PRIMARY.USE_KICK",
    "PDS_SECONDARY.USE_KICK", "PRESENCE", "CR_PDS_EXEC_BASE",
]
+++

**What runs.** Every kick of thirteen capture tables: 2464 pointers in MTE state blocks (1232
secondary, 1232 primary) and 2526 in the TA command's special object words.

**Results.**

- Bits 23:0 of a pointer, times 16, plus `PDS_EXEC_BASE` (`0xe4000000` in the harness) lands in
  a `PDSPIXEL_CODEDATA` object in every case, and the object holds the data the pointer counts.
  Bits 25:24 are 0 in all of them.
- Bits 31:26 give 1 to 5 and 7 rows for primaries, 1 to 3 for secondaries, 3 and 1 for the
  special object's primary and secondary. Decoding each program's movs to its output ports, the
  highest data dword an operand reads is within the last row the pointer counts in 4978 of the
  4990 programs; the other 12, all GLES1, also read registers above their data (a second douti, the
  douta of the secondaries), as temporaries would be [infer].
- The rows follow the outputs: a primary with one doutu has 1 row, with one douti 2, with a
  douti and a doutt 3, more with more (the float RGBA texture's four pairs 7, eight iterated
  sets 5); a secondary with only a doutu 1, with a doutd of constants and a doutu 2, with two
  doutd 3.
- The size word: bits 17:16 are 3 in all 1232 blocks.

  | size word | bits 6:0 | 24:18 | 31:25 | blocks |
  |---|---|---|---|---|
  | 0x00030001 | 1 | 0 | 0 | 598, the clear's screen-space blocks |
  | 0x18030001 | 1 | 0 | 12 | 144, no secondary constants |
  | 0x16070001 | 1 | 1 | 11 | 11, GLES1 douta secondaries |
  | 0x160f0001 | 1 | 3 | 11 | 434, 10 to 12 constant dwords |
  | 0x16130001 | 1 | 4 | 11 | 34, 11 to 15 |
  | 0x16170001 | 1 | 5 | 11 | 5, 17 and 18 |
  | 0x161b0001 | 1 | 6 | 11 | 1, fs_mat4_mat4 |
  | 0x0c030002 | 2 | 0 | 6 | 1, five iterated sets |
  | 0x0a0f0002 | 2 | 3 | 5 | 3, three iterated sets (discard) |
  | 0x06030004 | 4 | 0 | 3 | 1, eight iterated sets |

  Bits 24:18 are the secondary's constant dwords in rows of four, rounded up, in 1225 of the
  1232 blocks, and more in the seven others: color_red, color_green and color_white (3 rows,
  the doutd's operands not data words), fs_div and fs_mod (4 rows for 11 dwords), fs_radians (4
  for 12) and fs_mat4_mat4 (6 for 17).

**What it shows.**

- The pixel PDS pointer's layout (offset in 23:0, data rows in 31:26) holds for every pointer of
  the closed driver, and the data size it gives is exact in 4978 of the 4990 programs: the
  program reads its last row and nothing past it (the 12 GLES1 exceptions also read registers
  above their data) [CAP].
- `PDS_SIZE.BITS24_18` counts the secondary program's attribute rows, the constants it loads
  [CAP: equal in 1225 of 1232 blocks, never fewer]. Bits 6:0 grow with the primary's iterated
  sets, and bits 31:25 fit floor(12 / bits 6:0), or floor(11 / bits 6:0) when bits 24:18 are
  not 0, in all 634 draw blocks, which reads as a count the attribute space allows per task
  [infer: five distinct values; the clear's 0 does not fit it].
