+++
id = "E188"
claim = "Setting the index list's word 4 to 0, 0x10000000 or 0x70000000 leaves the TA's output of five copies of the triangle byte for byte the same; word 5 at 0 does too, at 1 the TA writes no object, at 5 it writes five primitives over 10 vertices whose list entries fit the indices taken modulo 5 (a reading), and at 8 the job hangs"
unit = "vdm"
method = "the seven probes of probes/vdm/index-list.toml (five copies of the triangle, 15 vertices, indices 0 to 14, 64x64, one VDM stream word set per probe), the parameter buffer and TA data saved after the job, compared byte for byte with the plain five-copy scene of probes/ta/regions.toml, on the laptop, linux fork with the debug option on; one run each"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["vdm-index-list", "ta-regions"]
terms = ["VDM_INDEX0.WORDS_PRESENT", "VDM_INDEX2.WORD", "VDM_INDEX3.INDEX_WRAP"]
+++

**What runs.** The VDM stream of the five-copy job holds an index list: a header word, then the
base and two further words, called words 4 and 5 here (the stream's dwords 4 and 5); the table
sets one of them per probe and leaves the other as the job writes it. The job's own values of the
two words are not read here, so which probe is the unchanged job is shown only by the comparison
below. After each job the parameter buffer and the TA data are saved.

**Results.**

- *Word 4* at 0x0, 0x10000000 and 0x70000000: all three dumps are byte-identical, both files,
  to each other and to the dump of the plain five-copy scene of probes/ta/regions.toml (one
  object of 15 vertices with 5 primitives, and 7 streams).
- *Word 5.* At 0x0 the dump is byte-identical to that plain scene as well. At 0x1 the job completes
  with every pixel the background (0xff203040 in all 4096) and the TA writes no object and no
  stream; the dump is byte-identical to the culled triangle's (E185). At 0x5 the object has 10
  vertices (ten 1/w words) and five primitives, whose list entries are (16, 17, 18), (19, 20, 16),
  (17, 18, 19), (21, 22, 23) and (24, 25, 21): the five triangles' indices, if the job lists 0 to 14
  in order, (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), taken modulo 5 [infer], the
  first three over vertices 16 to 20 and the last two over the second run 21 to 25 (the second of
  them reusing vertex 21). The streams are 7, with primitive words such as 0x5290ffff and the object
  word 0x2400040d (bits 28:25 of the primitive word are 9, the vertices of the object less one; bits
  31:26 of the object word are 9, twice the 5 primitives less one). At 0x8 the job fails: "job hung,
  context lost (Connection timed out)"; the saved parameter buffer has no object and the TA data is
  zero.

**What it shows.** Word 4 does not reach what the TA writes at any of the three values. Word 5 acts
on the indices: 0 leaves them alone, 5 wraps the vertex indices by 5 [infer: only 0, 1, 5 and 8 were
tried, and the wrap by 5 is a fit to the five list entries above]. At 1 every triangle disappears;
that every triangle becomes degenerate (the same vertex three times) is a reading, not a
measurement.

**Not shown.** The values the unchanged job writes for the two words and what the first word
(word 4) is for: no value made a difference here. Values of word 5 between 1 and 8, or above.
Whether the hang at 8 stops before the TA writes an object: the saved memory of a hung job is not a
reliable witness (E186). Clearing the bits that announce the words was not tried here. The list
dword 0xc2934a30 of the 0x5 dump has bit 15 set in its upper entry (0xc293), which three 5-bit
vertex numbers (E181) do not account for; what that bit is, is not shown. One run each.
