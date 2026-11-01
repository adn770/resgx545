+++
id = "E346"
claim = "Every one of the 1888 index lists in the closed driver's captured VDM streams is six words: a header with bits 31:30 = 2, the topology in 29:26 (0 triangles, 1 lines, 2 points, 3 strip, 4 fan, a line strip arriving as lines), bits 25:24 clear, both trailing-word bits 23:22 set and the index count in 21:0; the index base in the GENERAL heap; the trailing words 0xf0000000 and 0x003fffff (0xf4000000 once under GLES1 flat shading, 0xd0000000 once with eight vertex attributes); then the vertex task, whose word 0 holds VDM_TASK0.MAX_VERTICES (15 for most GLES2 draws, 9 for GLES1's and a point-size shader's, 7 for the screen-space draws, 13 with eight attributes, 2 with nine output rows) and the vertex PDS program's address >> 4 in 27:0 (PDSVERTEX_CODEDATA), and whose word 1 holds the output rows in 31:24 (1 to 4, and 9), 3 in 23:22 (2 once, with nine output rows), one attribute row per vertex attribute in 14:7 and the PDS data rows in 6:0"
unit = "vdm"
method = "the thirteen 3D capture tables of 11.11 (604 runs, 1263 kicks of the closed GLES1 and GLES2 stacks under the harness on the laptop): every kick's whole VDM control stream, from CR_VDM_CTRL_STREAM_BASE to its terminate word, decoded with kickwalk.decode_vdm over the 64 KiB state3d.py reads from the stream's base (VDM_READ; decode_vdm stops at 4096 blocks, never reached), the addresses resolved in the kick's snapshot"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "VDM_INDEX0.PRIMITIVE_TOPOLOGY", "VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX2.WORD",
    "VDM_INDEX3.INDEX_WRAP", "VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE",
    "CR_VDM_CTRL_STREAM_BASE",
]
+++

**What runs.** 1263 kicks; 1888 index lists, 1863 of them triangles.

**Results.**

| header topology | count field | where |
|---|---|---|
| 0 triangles | 3, 6 | one or two triangles, the clear's triangle |
| 1 lines | 4 or 2 | prim=lines (four vertices), prim=linestrip (three), the line tables |
| 2 points | 3 | prim=points, points in GLES1 and the point-size shader |
| 3 strip | 4 | prim=strip; the clear's pieces when a scissor or viewport splits it |
| 4 fan | 4 | prim=fan |

- Bits 25:24 of the header are 0 and bits 23:22 are 3 in all 1888; every list is six words.
- The first trailing word (`VDM_INDEX2.WORD`) is `0xf0000000` in 1886 lists, `0xf4000000` in
  GLES1's vcolor_flat (flat shading of a vertex colour) and `0xd0000000` in vs_many_attrs (eight
  vertex attributes); the second (`VDM_INDEX3.INDEX_WRAP`) is `0x003fffff` in all.
- The index base points into a GENERAL object of 16-bit indices; the indices of a draw of one
  triangle read 0, 1, 2.

Vertex task words:

| word 1 | output rows | attribute rows | data rows | with |
|---|---|---|---|---|
| 0x01c00082 | 1 | 1 | 2 | a GLES2 position (1045) |
| 0x02c00082 | 2 | 1 | 2 | the clear (position and colour), points (708) |
| 0x03c00082, 0x04c00082 | 3, 4 | 1 | 2 | a point size; the shader corpus's four outputs (95) |
| 0x02c00103 | 2 | 2 | 3 | a varying colour (two attributes) |
| 0x02c00184, 0x03c00103 | 2, 3 | 3, 2 | 4, 3 | GLES1 with a texture or a colour |
| 0x03c00184, 0x03c00205 | 3 | 3, 4 | 4, 5 | GLES1 texture, two textures |
| 0x02c00409 | 2 | 8 | 9 | eight vertex attributes |
| 0x09800082 | 9 | 1 | 2 | nine output rows; bits 23:22 = 2 |

- Word 0's bits 31:28 are 15 in 1159 lists (GLES2 draws), 7 in 704 (the clears, the screen-space
  pieces), 9 in 23 (GLES1 draws and vs_pointsize), 13 in vs_many_attrs and 2 in
  vs_many_varyings; bits 27:0, times 16, are a PDSVERTEX_CODEDATA object holding the task's PDS
  program (E344).

**What it shows.**

- The index-list layout the earlier readings gave holds over every captured list: topology,
  presence bits and count in the header, base, two trailing words, two task words [CAP]. The
  closed driver always writes both trailing words, the same values but in two draws (Q092).
- The vertices per task are the closed driver's choice per draw: 16 for most, 10 for GLES1, 8
  for screen-space draws, fewer with many attributes (14) or many outputs (3) [CAP]; a budget
  over input and output rows reads well for the last two, but the GLES1 value with three output
  rows against 16 with four in the shader corpus does not fit one [infer, Q094].
- A line strip of three vertices reaches the VDM as two lines (four indices) [CAP].
- The data rows of the task count the vertex program's data: two rows for one attribute, one
  row more per further attribute; the attribute rows are the attribute count [CAP].
