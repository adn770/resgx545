+++
id = "E414"
claim = "With the index list's first trailing word at 0xf0000000 | k on the five-copy job (15 indices), the TA's object keeps floor((16 - k) / 3) of the five triangles, the leading ones, for k = 0 to 6 and none for k = 16, 256 and 4096, in two runs each; bit 24 alone or with 0xf0000000 keeps three and sets bit 15 in the first two primitive-list entries; bits 25 to 27 alone or with 0xf0000000, and bits 31:28 at 0xf, 0xd and 0x7 with a vertex task of 16 and of 14 vertices, change nothing; topology 1 (line) hangs the job and 2 (point) writes no object"
unit = "vdm"
method = "probes/vdm/index-trailing.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: five copies of the triangle at distinct depths (--vertices 15 --copy-depth) with the index list's word 4 (vdm:4) at the values above, twice; the same with 12 vertices and vdm:4 top nibble 0xf, 0xd, 0x7 against the vertex task's maximum (vdm:6 bits 31:28 15 and 13); the index list's topology (vdm:2 bits 29:26, 1 to 4) on 3 and 15 vertices; the state word's bit 8, bits 11:9 and bits 15:13 (vdm:1) on the five copies; each case's render memory dumped and read with ta_words.py object (71 cases)"
tiers = ["HW"]
date = "2026-11-07"
data = ["vdm-index-trailing"]
terms = ["VDM_INDEX2.WORD", "VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX3.INDEX_WRAP", "VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13", "MTECTL.FLAT_VERTEX"]
+++

**The low bits.** The primitive list of the object after the job lists, for the word 0xf0000000 | k:
five triangles (16, 17, 18) to (28, 29, 30) for k = 0 and 1; four for k = 2, 3 and 4; three for k =
5 and 6; and no object, every pixel the background, for k = 0x10, 0x100 and 0x1000. The retained
triangles are the leading ones. The counts fit floor((16 - k) / 3) at all ten values, in both runs,
which reads k as an offset in indices into the 15 of the list and the object as the triangles that
whole read of three indices starting at k reaches, counting one index past the list [infer].

**Bits 27:24.** 0x01000000 alone, and 0xf1000000, keep three triangles and set bit 15 in the first
two entries of the primitive list; the image is the same 1098 pixels as with five. 0x02000000,
0x04000000, 0x08000000 and 0xf2000000, 0xf4000000, 0xf8000000 give the object of 0xf0000000. So the
drop of two triangles that E300 saw at 0x0f000000 is bit 24, and bit 26, the bit the flat-shaded
draw of the closed driver sets (0xf4000000, E348), changes nothing in our job.

**Bits 31:28.** At 0xf, 0xd and 0x7 against a vertex task whose maximum is 16 and 14 vertices (vdm:6
bits 31:28 15 and 13), with 15 and with 12 vertices, all 12 cases give the object and the image of
the control; the counts of E346 and E348 are not tied to anything our job shows. The attribute count
was not varied.

**Topology.** Bits 29:26 of the index list's header at 3 (strip) and 4 (fan) give the triangles of a
strip (16, 17, 18), (17, 19, 18) and of a fan (16, 17, 18), (16, 18, 19) with 15 vertices, and (16,
17, 18) with 3, drawing 1098 and 1062 pixels. At 1 (line) the job hangs, with 3 and with 15
vertices; at 2 (point) the job completes with no object and every pixel the background.

**The state word.** On the five copies, bit 8 flipped, bits 11:9 at 3, 4, 5 and 7 and bits 15:13 at
2, 3, 4 and 7 give the control's object and image; bits 11:9 at 0 give no object, at 1 and 6 the job
hangs; bits 15:13 at 0, 5 and 6 hang it: as on the one-triangle job (E060, E185). One run each.
Bits 11:9 at 3, 5 and 7 hang some jobs and not others (E413: 7 every second job), so these runs
show what the job did the once it was run, with the state the preceding job left: they give the
control's object when the job completes, not that the value always does.

**What it does not show.** What bit 24 does besides the drop (the winding mark on two entries
[infer]); the offset's width beyond 4096; the lines and points the region test would be run on; what
bits 31:28 count.
