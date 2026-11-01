+++
id = "E439"
claim = "A 4x render of our stack (CR_ISP_MSAA mode 2, the closed driver's TE words) through our end-of-tile task with the PBE words and sidebands the closed driver hands it (a 64x64 rectangle, pitch 64, sideband 0x200 or 0x2200) writes all 4096 pixels of the 64x64 target with 1248 triangle and 2848 background pixels and no other colour, the same in three runs of each of the 12 probes (36 jobs), with bit 48 of either emit set giving the same image; sideband 0x2200 (bit 13) rearranges the pixels of the single-sampled and the 4x image without changing their counts; a 64x64 rectangle on a 128x128 target writes 4096 pixels and leaves 12288 unwritten"
unit = "isp"
method = "probes/isp/msaa-pbe.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: probe --tri pixel (green) with the end-of-tile slot eot_plain.s (or eot_bit48_1.s, eot_bit48_2.s) and --sideband 0x200 or 0x2200, 64x64 and 128x128 targets, single-sampled and 4x (render command words 1, 10, 13 and 16 as the closed driver's, E339, and for 64x64 the macrotile words poked: ta:143 and ta:144 = 0x802002, ta:146 = 4), --pbe 1=0x003f003f and 2=0x001f8000 in two probes (the closed driver's rectangle words for 64x64); 12 probes, three runs each (36 jobs); every pixel read, the target pre-filled with 0xdeadbeef"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["isp-msaa-pbe"]
terms = ["CR_ISP_MSAA.MODE", "EMIT1.MAXCLIP_X", "EMIT2.LINE_STRIDE", "SIDEBAND.MEMLAYOUT", "SIDEBAND.BIT9", "CR_TE_MTILE1"]
+++

**What runs.** E333 and E339 give the closed driver's PBE words for a render to a 64x64 texture
(EMIT1 0x003f003f, EMIT2 0x001f8000, a sideband of 0x2200) and its 4x words. Our end-of-tile
program for a 64x64 target already has the two EMIT words, so the runs vary what differs: the
sideband (0x200 as ours, 0x2200 as the closed driver's), the single or four samples, the target's
size, and a 64x64 rectangle on a 128x128 target. The triangle is the default's, pixels read.

**Results** (triangle G, background B, unwritten S, any other colour O; identical in the three runs
of each case):

| target | samples | sideband | rectangle | G | B | S | O |
|---|---|---|---|---|---|---|---|
| 64x64 | 1 | 0x200 | 64x64 | 1062 | 3034 | 0 | 0 |
| 64x64 | 1 | 0x2200 | 64x64 | 1062 | 3034 | 0 | 0 |
| 64x64 | 4 | 0x200 | 64x64 | 1248 | 2848 | 0 | 0 |
| 64x64 | 4 | 0x2200 | 64x64 | 1248 | 2848 | 0 | 0 |
| 64x64 | 4, bit 48 of emit 1 or 2 | 0x2200 | 64x64 | 1248 | 2848 | 0 | 0 |
| 128x128 | 1 | 0x200 or 0x2200 | 128x128 | 4284 | 12100 | 0 | 0 |
| 128x128 | 4 | 0x200 or 0x2200 | 128x128 | 4096 | 12288 | 0 | 0 |
| 128x128 | 1 | 0x2200 | 64x64 | 1728 | 2368 | 12288 | 0 |
| 128x128 | 4 | 0x2200 | 64x64 | 2272 | 1824 | 12288 | 0 |

The triangle's bounding box at 64x64 single-sampled is columns 8 to 54, rows 8 to 54 with sideband
0x200 and columns 0 to 63, rows 3 to 54 with 0x2200; the 4x image's is columns 0 to 38, rows 4 to 47
(0x200) and columns 0 to 63, rows 0 to 39 (0x2200). The 0x2200 image is not the 0x200 image
through the plain twiddle of either orientation (3052 and 3052 of 4096 pixels agree for the single
sample, 2692 and 2688 for four, about the background's count).

**What it shows.** The closed driver's end-of-tile words do not turn our 4x render into a resolved
64x64 image: every stored pixel is one of the two plain colours (no blend, in 36 of 36 jobs), so
the target holds whole samples as E281 found them stored by mode 2, cut to the rectangle [infer],
and the emit's
bit 48 is not a resolve bit in either emit (E074 found the same without the sideband). Sideband bit
13 (E333's render-to-texture bit) changes where the pixels land and not how many are triangle,
background or unwritten. The 64x64 rectangle on a larger target leaves the rest unwritten as the
single-sampled case does.

**What it does not show.** Where the closed driver resolves its 4x render (a later pass, say
[infer]), what a sample average would look like in the target, the layout bit 13 selects, and the
closed driver's coverage words (E339's capture walk).
