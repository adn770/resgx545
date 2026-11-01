+++
id = "E286"
claim = "OUTSEL bit 12 puts each vertex's 1/w into the TA's object: with it clear the object loses the three 1/w dwords, its format word drops bit 18 and one stored and one iterated dword per vertex (0x00040303 to 0x00000202), and the image of the triangle at w 1 is unchanged; bit 13 clear changes neither object nor image; of the presence word's bits 16-31 set one at a time, 17, 18 and 22-25 remove the triangle, 27 hangs the job and the other nine change nothing (one run)"
unit = "mte"
method = "probes/mte/outsel-bits.toml and probes/mte/presence-high.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with OUTSEL (state-block word 13) bits 13:12 at 3 (the job's), 2, 1 and 0, with no coordinate set, one set of two components (vtx_zx.s, pds_iter_done.s, o0 = pa0) and two sets (vtx_xy4.s, COORDSIZE 0x12), the parameter buffer and TA data dumped after each render and read with pbdump.py --diff, twice; the presence word (state-block word 0, 0xdf43) with each of bits 16-31 set, once; every pixel read back"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["mte-outsel-bits", "mte-presence-high"]
terms = ["OUTSEL", "PB_OBJ.RHW", "PRESENCE"]
+++

**What runs.** OUTSEL is 0x43000, 0x63000 or 0x83000 (vertex size 4, 6 or 8) with bits 13 and
12 both set, as the job builds it; each probe clears bit 12, bit 13 and both. The images are the
triangle's own: 1062 pixels of one colour with no set, and the four iterated values of x the
coordinate set gives (0xbeb80000 and others, 171 of 1062 shown by the reader) with one or two.

**Results.** Both runs alike. Every image is the same within a probe. Clearing bit 13 leaves the
parameter buffer and the TA data byte for byte as built. Clearing bit 12, with or without bit 13:

| sets | object with bit 12 | without |
|---|---|---|
| none | 23 dwords: three 1.0 dwords after the PDS words, format word 0x00040101 | 20 dwords, no 1.0 dwords |
| one | 29 dwords: per vertex 1.0 then x, y; format word 0x00040303 | 26 dwords: per vertex x, y; format word 0x00000202 |
| two | 1.0 then four dwords per vertex | four dwords per vertex |

The object word's ISP address moves with the object (0x40c to 0x409 with one set).

Presence bits: set alone, bits 16, 19, 20, 21, 26 and 28 to 31 give the triangle; bits 17, 18,
22, 23, 24 and 25 give the background only; bit 27 hung the job, which the kernel recovered.

**What it shows.** OUTSEL bit 12 makes the MTE store each vertex's 1/w (`PB_OBJ.RHW`) and count
it in the vertex's stored and iterated sizes; format word bit 18 marks it. At w 1 the image cannot
show what the missing 1/w costs; a perspective triangle would [infer]. What bit 13 selects is not
shown (Q069). Six presence bits above 15 remove the triangle and one hangs; what words they
expect is not shown, and the bits ran once.
