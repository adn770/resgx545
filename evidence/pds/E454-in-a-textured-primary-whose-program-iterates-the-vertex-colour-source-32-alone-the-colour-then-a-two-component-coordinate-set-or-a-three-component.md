+++
id = "E454"
claim = "In a textured primary whose program iterates the vertex colour (source 32) alone, the colour then a two-component coordinate set, or a three-component coordinate set before the fetch, pa0 to pa3 and the image are the same (the coordinate registers reading 0 in every pixel throughout) in every run that completed (29 of 29 with bits 24 and 25, 30 of 30 with bit 25 alone, 30 of 30 with bit 25 alone and no completion bit) with the fetch wait (DOUTU1 bit 25) set, whether DOUTU1 bit 24 is set or clear, and change from run to run without bit 25 (in 9 of 10 probes with bit 24 alone, in 10 of 10 with neither bit); 1 of 30 jobs with bits 24 and 25 hung (0 of 30 with bit 25 alone)"
unit = "pds"
method = "probes/pds/iter-wait-colour.toml on the laptop (direct cable), linux fork 01cff214d7d2 with the debug option on, module srcversion FC6EB50DEF21E3A6249727F (read by the campaign with modinfo from the installed module file; the loaded module was not read, and no output.txt exists: the data are the campaign's reports and kernel log, and only the second run, the first having been overwritten), the triangle's primary pixel PDS program (--tri pixpds, --vtx-coords 4, state words 13 = 0x83800 and 16 = 5 as the closed driver's colour state in pds/iteration-sources, vtx_color.s): shape P douti source 32 (0x27c10000 with the completion bit, 0x07c10000 without) then the fetch's douti 0x46012201 and a doutt on the 16x16 RGBA8888 scratch texture (dword i = 0xD0000000 | i); shape Q the colour douti (0x07c10000) then a two-component source 1 douti (0x20400800 or 0x00400800); shape R one three-component source 1 douti (0x20800800 or 0x00800800); the shader's U1 at 0x03000004 (bits 24 and 25), 0x02000004, 0x01000004 and 0x00000004 (bit 24 only with the completion bit, which it needs: E436) and a shader that writes pa0, pa1, pa2 or pa3 out as the colour (10 probes of 18 cases: shape P pa0 and pa1, Q and R pa0 to pa3; three runs; 180 jobs); every pixel compared by its value"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["pds-iter-wait-colour"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH", "DOUTI0.LAST_ITER", "DOUTI0.ATTR_SOURCE"]
+++

**What runs.** E436 tried one program shape (one douti of source 1 with one component, one
fetch). 18 of the closed driver's 21 captured programs with bit 24 iterate the vertex colour
(source 32), and 5 read pa0 to pa2 (E364). The colour is iterated here with the state words the
closed driver sets, as the colour of o4 to o7 (with our word 16 = 4 the colour is absent and pa0
reads 0xff000000).

**Results** (per probe, the three runs of each U1 compared pixel by pixel):

| U1 bits | completion bit | runs identical across the three | what pa0 to pa3 hold |
|---|---|---|---|
| 24 and 25 | set | 9 of 10 probes (1 job hung, below) | the same image as bit 25 alone, 29 of 29 completed jobs |
| 25 only | set or clear | 10 of 10 probes, each | the same image, with or without the completion bit |
| 24 only | set | 1 of 10 (shape R pa1) | in the other 9 probes at least one run differs from the stable image |
| neither | set or clear | 0 of 10, either | every probe differs from the stable image in at least one run |

Under the fetch wait the images with bit 24 set and clear are equal: 10 of 10 probes, 3 runs
each, 29 of 30 with bits 24 and 25 (shape P pa0 pa1, shape Q pa0 to pa3, shape R pa0 to pa3).
The colour reads as the ARGB8888 of the vertex values (pa0 of shapes P and Q equal, 0xff020240
and so on) and the texel (0xd0000000 | i) in the register after the iterated ones (pa1 of P, pa3
of Q and R). The coordinate registers read 0x00000000 in all 1062 triangle pixels of every
stable image, with bit 24 set or clear: pa1 and pa2 of Q, pa0 to pa2 of R. One job with bits 24
and 25 and the completion bit hung (the first run of shape Q pa0), 1 of 30 against 0 of 30 with
bit 25 alone; the same program completed in its other two runs, so the hang is not shown to be
caused by the bits.

**What it shows.**

- In the shapes that iterate the vertex colour, or two or three attribute registers, bit 24 adds
  no image or register difference under the fetch wait: the image and every register read are the
  same with it set and clear in 10 of 10 probes (3 runs each; 29 of 30 jobs with both bits, one
  hung) [HW]. For the colour and the texel registers this is a comparison of real values; for the
  coordinate registers (Q pa1 and pa2, R pa0 to pa2) it is a comparison against a constant zero,
  so those shapes show nothing about what the iteration delivers [HW].
- Without bit 25 the values are unstable whether bit 24 is set or not (9 of 10 probes with bit
  24 alone; one, R pa1, was stable) [HW].
- So bit 24 is redundant under bit 25 for the colour in the shapes tried (E436 and these)
  [infer]; why the closed driver sets both is not shown.

**What it does not show.** A primary with no fetch (no bit 25) that iterates; programs of the closed
driver other than these shapes (18 of E364's 21 programs were not run themselves); a coordinate
register that reads other than 0 (Q093); whether the one hang recurs; the hang's cause.

**Provenance.** The sgxfive-test binary of these runs is the one whose sha256 env.toml names
(83318889...); it was built from source not yet committed, which was later committed in f63c7d19.
