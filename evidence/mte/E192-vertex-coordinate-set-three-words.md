+++
id = "E192"
claim = "A coordinate set on the vertices needs three words changed together, which the probe tool's vertex-coordinates option does: OUTSEL's vertex size (blk:13 bits 19:16) 4 to 6 dwords, the coordsize word (blk:16) 0 to 2 and the vertex task's output size (vdm:7 bits 31:24) 1 to 2 rows; with the size alone at 5 or 6 the triangle keeps 490 of its 1062 pixels, and the output size alone at 0, 3, 5 or 9 removes it"
unit = "mte"
method = "the pds-iteration-sources probe iter-coords (tri host, vtx_coords 2, 64 cases) and the vdm-stream-words sweep (blk:13, blk:16 and vdm:7 flips) on the laptop with the linux fork and the debug option on; the sweep ran twice, the second run being the follow-up run"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-iteration-sources", "vdm-stream-words", "vdm-stream-words-followup"]
terms = ["OUTSEL.VTX_SIZE", "PRESENCE.COORD", "VDM_TASK1.OUTPUT_SIZE"]
+++

**What runs.** The probe tool's `--vtx-coords N` (userspace/libsgxfive, `tri_probe.c`) gives each
vertex N more output dwords. It sets the three words named above together: the vertex size to 4 + N
dwords, the coordsize word to N coordinate dwords, and the vertex task's output size to (4 + N + 3)
/ 4 rows of four dwords. The triangle job holds 4 dwords, coordsize 0 and 1 row. The table
`pds-iteration-sources` runs its `iter-coords` probe with N = 2 (a vertex program writing the
position's x and y as a coordinate set) over 64 pixel-program cases. The sweep flips every bit of
`blk:13`, `blk:16` and `vdm:7` of the triangle job, one word at a time.

**Results.**

- Three words together (N = 2, vertex size 6): in all 64 cases the image holds 3034 background
  pixels and 1062 others, the triangle's area, so the triangle is drawn whole.
- Vertex size alone (`blk:13` ^= 0x10000 and ^= 0x20000, size 5 and 6): 490 triangle pixels, 1379
  pixels away from the baseline, the same image hash for both, in both runs. Bit 18 (size 0) and bit
  19 (size 12) remove the triangle (936 pixels away).
- Coordsize alone (`blk:16`, each of bits 0-3, and the values 0 and 0xffffffff): the baseline image
  (1062 triangle pixels, 0 away), in both runs.
- Output size alone (`vdm:7` ^= 0x1000000, 0x2000000, 0x4000000, 0x8000000, rows 0, 3, 5 and 9): the
  triangle is removed (936 pixels away), in both runs.

**Not shown.** No case changes the size and the coordsize word without the output size, nor the size
and the output size without the coordsize word, so what the 490-pixel image of the size alone owes
to each missing word is not separated. Coordsize alone showing no change does not say the word is
unused; it is read when the vertex has coordinates. The triangle's 64 cases of `iter-coords` ran
once.
