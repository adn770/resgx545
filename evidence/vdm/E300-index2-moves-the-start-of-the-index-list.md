+++
id = "E300"
claim = "The index list's first trailing word (VDM_INDEX2) changes the TA's object of the five-copy job: at 1 the object keeps five triangles and its last vertex's 1/w reads 100000.0, at 2 and 3 four triangles (12 vertices), at 5 and 0x0f000000 three (9 vertices), but with 0x0f000000 bit 15 is set in the primitive list's entries and the packed vertices differ, at 0xff none and no pixel of them; at 0, 0x80000000 and the job's own 0xf0000000 the object is the job's; in the first run the job's own value hung (every pixel read back, no TA data saved), and the eight other cases give the same bytes in both runs; every image with triangles is the job's image"
unit = "vdm"
method = "probes/vdm/index2.toml on the laptop, linux fork with the debug option on: the probe's triangle with four copies after it (vertices 15, one index list of 15 indices), a green pixel shader, VDM stream word 4 (the index list's first trailing word, its header announcing both trailing words) at nine values, the render memory dumped after each; two runs; objects read with ta_words.py object (pbdump.py object_fields)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["vdm-index2"]
terms = ["VDM_INDEX2.WORD", "VDM_INDEX0.WORDS_PRESENT", "PB_OBJ.PRIM_LIST", "PB_OBJ.RHW"]
+++

**What runs.** The five-copy job of E188 with VDM_INDEX2 at 0xf0000000 (the value the library
writes, userspace/libsgxfive render.c), 0, 1, 2, 3, 5, 0xff, 0x0f000000 and 0x80000000.

**Results.** In the second run (in the first, the control case hung; the other eight dumps are
byte for byte those of the second run):

| VDM_INDEX2 | object vertices | primitives | image |
|---|---|---|---|
| 0xf0000000, 0, 0x80000000 | 15 | 5 | the job's: 1098 triangle pixels |
| 1 | 15, the last 1/w 100000.0 | 5 | the job's |
| 2, 3 | 12 | 4 | the job's |
| 5 | 9 | 3 | the job's |
| 0x0f000000 | 9, packed differently | 3, bit 15 set in both entries of the first dword | the job's |
| 0xff | no object, every region empty | 0 | background only |

With 0x0f000000 the object differs from that of 5 in the primitive list's first dword,
0xd693ca30 for 0x56934a30 (bit 15 set in both of its entries), and in the packed vertices
(dwords 22-43 of the parameter buffer); the region headers and control streams are the same.
The copies overlap in the target, so the image does not tell which triangles were dropped.

**What it shows.** The word's low bits act on the indices the TA reads: an offset of the first index
fits every low value [infer]. With the 15 indices moved by 1 the last triangle reads one index past
the list, whose vertex has w at the clamp (1/w 100000.0); moved by 2 or 3 the last triangle reads
past it and is dropped, by 5 the last two, by 0xff all. Bits 31:28 (0x8, 0xf) change nothing;
0x0f000000 drops two triangles and changes the object's primitive entries and packed vertices, which
an offset in bits 7:0 alone does not explain; bit 15 of an entry marks one winding in the random
triangles of E307 (E308), so a winding that 0x0f000000 flips would fit [infer]. The job's own value,
with no word changed, hung in the first run: a hang of an unpoked job with every pixel read back
(Q015). The earlier reading, an instance count or a split, fits none of these.
