+++
id = "E133"
claim = "With state word 13 at 0x83800 and state word 16 at 5, iteration source 32 gives a vertex colour packed as ARGB8888, the colour of vertex 0, 1 or 2 for shade models 0, 1 and 2 on 753, 751 and 723 of the 1062 triangle pixels and a varying colour for 3, while with word 13 left at the harness's default and word 16 at 4 it gives 0xff000000 under every shade model, and either word alone gives no colour (word 13 alone faults the job)"
unit = "pds"
method = "the two probes of probes/pds/iteration-sources.toml that set state words 13 and 16 to 0x83800 and 5 (one reads pa0, the other pa1), and pds-iteration-sources-color-ours, -color-outsel11 and -color-coordsize5 of the same table (pds_iter_nofetch.s: DOUTU1 0x01000004, one douti of DOUTI0 0x21c10000 plus the shade model in bits 26:25 or the source in bits 16:11, DOUTI0 bit 29 set, no fetch; vtx_color.s writes o4 to o7 as x, y, 0.25, 1.0) on the laptop, linux fork with the debug option on: 64x64 triangle job, state words 13 and 16 as the case says, one run of each case, fresh context each; the tables ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-iteration-sources", "pds-iteration-sources-followup"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTI0.SHADEMODEL", "DOUTI0.FLAT", "DOUTU1.WAIT_ITER", "DOUTI0.LAST_ITER"]
+++

**What runs.** The vertex shader writes `o4` to `o7` as the vertex's clip x and y, 0.25 and 1.0 (x =
-0.75, 0.75, -0.375; y = -0.75, -0.375, 0.75 at the three vertices), after the position. The primary
pixel program starts the shader with DOUTU1 0x01000004 (waits for the iterations) and issues one
`douti` with DOUTI0 bit 29 set, the shade model (bits 26:25) 0, 1, 2 or 3 and source 32, or with the
shade model 3 and source 33, 34, 35, 1 or 2; the shader writes `pa0` out. Four state settings were
run: words 13 and 16 of the job's state block at 0x83800 and 5 (the two probes that set them, one
reading `pa0` and the other `pa1`; the pair is a trial pair of ours), word 13 left at the harness's
default and word 16 at 4 (`color-ours`), 0x83800 and 4 (`color-outsel11`), and the default word 13
with 5 (`color-coordsize5`). A vertex colour of vertex 0, 1, 2 packs as 0xff000040, 0xffbf0040,
0xff00bf40 (R and G clamped to [0, 1], B 0.25, A 1.0).

**Results.** Pixels counted of the 1062 in the triangle.

- Words 13 = 0x83800 and 16 = 5. Source 32, shade model 0: vertex 0's colour on 753 pixels, 0 on
  293, the value 2 on 13, 3 others. Shade model 1: vertex 1's colour on 751, vertex 0's on 299.
  Shade model 2: vertex 2's on 723, vertex 1's on 310. About 300 pixels in each of these cases do
  not hold the case's colour; in the first three cases they lie in the second row of tiles (rows 16
  to 31, columns 16 to 63, a few elsewhere), and they hold what the previous case gave most of its
  pixels (0 for case 0). Shade model 3: 759 pixels with alpha 0xff and blue 0x40 and a varying red
  and green, 297 with vertex 2's colour and 6 with the value 2. Source 33: 0xff000000 on 755, other
  values on 302. Source 34: 0 on 729, 0xff000000 on 320. Source 35: the job hangs (context lost).
  Sources 1 and 2: 0 on all 1062. `pa1` holds 0 on 1051 to 1062 pixels in every case (the other
  pixels hold a few stale values): source 32 delivers one dword.
- Word 13 at the default and word 16 = 4: source 32 under each of the shade models 0 to 3 and source
  33 give 0xff000000 on all 1062 pixels, source 34 gives 0, source 35 hangs, source 1 gives x (the
  iteration of `o4`) on all 1062 and source 2 gives 1.0 on all 1062.
- Word 13 = 0x83800 with word 16 = 4: all 4 cases (source 32 flat, source 32 smooth, 1 and 2) fault
  the job ("job faulted, context lost (Input/output error)").
- Default word 13 with word 16 = 5: source 32, flat and smooth, give 0xff000000 on all 1062; source
  1 gives x on all 1062; source 2 gives 0 on all 1062 (it was 1.0 with word 16 = 4).

**Second run.** The follow-up run repeats the picture with other counts. Words 0x83800 and 5: shade
model 0 gives vertex 0's colour on 736 pixels (0 on 314), model 1 vertex 1's on 757 (vertex 0's on
286), model 2 vertex 2's on 746 (vertex 1's on 310), and model 3 has vertex 2's colour on 294
pixels; source 33 gives 0xff000000 on 744, source 34 0 on 714 and 0xff000000 on 338, source 35
hangs. The setting with the default word 13 and word 16 at 4, word 13 alone and word 16 alone give
the same results as in the first run. The group of about 300 pixels is there again.

**Not shown.** The group of about 300 pixels per case that do not hold the case's value is not
explained: why it is those tiles, and whether it depends on the order of the cases, was not tested.
Because of it the figures 753, 751 and 723 are the pixels that took the colour in this run; the data
does not show a case where every pixel does. The packed colour rests on the three flat colours and
on alpha 0xff and blue 0x40 at the 759 pixels of the smooth case; the red and green of the smooth
case were not fitted. What word 16 counts (5 in the trial pair, 4 in the other settings) and why
word 13 alone faults while word 16 alone does not are not known. One run of each case in each run.
