+++
id = "E135"
claim = "With DOUTI word 1 bit 6 set, the shade model of DOUTI0 (bits 26:25) 0, 1 and 2 gives every one of the 1062 pixels the x of vertex 0, 1 and 2 (-0.75, 0.75, -0.375), as DOUTI0 bit 21 does, but shade model 3 hangs the job where bit 21 iterates smoothly; word 1 at 0x60 and 0xc0 gives vertex 0's value as bit 6 alone does, and with word 1 at 0 all four shade models iterate smoothly"
unit = "pds"
method = "probe pds-iteration-sources-douti1-bit6 of probes/pds/iteration-sources.toml (pds_tex_iter.s with vtx_persp.s: source 1 with the fetch wait, DOUTU1 0x02000004, DOUTI0 0x40000801 | shade model << 25, DOUTI word 1 0, 64, 96 or 192) on the laptop, linux fork with the debug option on: 64x64 triangle job whose vertex shader gives x as coordinate set 1, one run of each of the 10 cases, fresh context each; the table ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-iteration-sources", "pds-iteration-sources-followup"]
terms = ["DOUTI1.FLAT", "DOUTI0.FLAT", "DOUTI0.SHADEMODEL", "DOUTI.SHADEMODEL"]
+++

**What runs.** The triangle's x at the three vertices is -0.75, 0.75 and -0.375, given as coordinate
set 1, with w = x + 2 (1.25, 2.75, 1.625), and DOUTI0 bit 24 (perspective) is clear, so a smooth
iteration returns each pixel's own x. The primary pixel program issues a `douti` of source 1 with
the fetch and its `doutt`, and the shader writes `pa0` out. The 10 cases are the four shade models
with the second DOUTI word 0, the four with word 1 = 64 (bit 6), and the shade model 0 with word 1 =
96 (bits 6 and 5) and 192 (bits 7 and 6). DOUTI0 bit 21 is clear in all of them. The triangle covers
1062 pixels.

**Results.**

| shade model | word 1 = 0 | word 1 = 64 |
|---|---|---|
| 0 | x, smooth (1062 pixels) | -0.75 (0xbf400000) at all 1062 |
| 1 | x, smooth (1062) | 0.75 (0x3f400000) at all 1062 |
| 2 | x, smooth (1062) | -0.375 (0xbec00000) at all 1062 |
| 3 | x, smooth (1062) | the job hangs, context lost (Connection timed out) |

Word 1 = 96 and 192 with shade model 0 give -0.75 at all 1062 pixels, as word 1 = 64 does. In the
smooth cases the value is each pixel's own x, (px + 0.5) / 32 - 1, within 1e-5.

**Second run.** The follow-up run gives the same table: the same values at all 1062 pixels in every
case and the same hang with shade model 3.

**Not shown.** That bit 6 does what DOUTI0 bit 21 does with a shade model of 0 to 2 follows from
comparing with E048, where bit 21 with the same shade models gives the values of the same three
vertices and shade model 3 iterates smoothly; the cases here have bit 21 clear and no case
has both. The hang with shade model 3 is the only result that is not a value: what hangs
(the iteration, the task or the wait) is not told. Bits other than 6, 5 and 7 of word 1 are in
E048. One run of each case in each run.
