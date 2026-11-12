+++
id = "E897"
claim = "Round 7 offline reading of the kept parameter-buffer dumps (Q293; post hoc, nothing held out): in 13 of 13 kept two-object dumps of `tri --tri-full -n 2 --geometry 1` at 64 x 64 with CR_TE_AA 0x40000000 (r3k-pixel k-pb0 2, r3k-regress rg-pb 3, r4-q285 a-pb 5 and a-pb0 2, r6-render4x t7 1) render 2's own object starts at dword 27, holds a zero at its dword 11 (dump dword 38) and its format word 0x00040101 at its dword 12 (dump dword 39), the 27-dword layout with the inserted zero that render 1's object has; in the 11 of those jobs whose first object was not put in the bit-29-set layout (no poke, or 0, 1 or 0xffffffff at dword 11) render 2's image has 0 triangle and 4096 background pixels although its triangle covers the target, and the 3 kept two-object dumps at 0x60000000 (bit 29 set) have the second object at dword 26 with the format word at its dword 11"
unit = "ta"
method = "Offline, no run (round 7, decision R7-1 a: the offline items fold before any freeze; plan closing7/a/exp-pixel-r7.md section 1.1). closing7/a/q293/obj2_scan.py read every *param.bin.gz under render/closing-* of resgx545-data (1342 dumps; the first 4096 dwords each) for the objects that open as the one-triangle scene's does (0x04000004 0x00030001 0x04000000) and printed, per dump with two or more objects, each object's start, the offset of its format word 0x00040101 and the dword before it (obj2_scan.out); obj2_inserted.out is its 13 lines with a second object at dword 27 and the format word at +12 (taken with grep); obj2_images.py read each of those 13 jobs' own text (the .txt.gz beside the dump) for the kernel pokes before render 2 at dword 11 and the last render's pixel counts (obj2_images.out); t7_words.py printed the first 96 dwords of E888's t7 and t8 dumps (t7_words.out). The jobs are those of E825 (k-pb0), E827 (rg-pb), E829 (a-pb, a-pb0) and E888 (t7) (64 x 64, render_rgn_arrays 1, render 1 geometry only, render 2 drawing the same triangle (0,0) (192,0) (0,192)). In the fold (2026-11-12) each script was re-run with python -I from its published copy (resgx545-data cited/closing7/a/q293/) and printed output byte-identical to the kept .out files, and obj2_inserted.out came out identical from the same grep. No frozen verdict and no scorer: the plan's author read the dumps before writing the reading, so it is post hoc; the held-out rows the plan freezes for it (section 3.5, u1 to u4: -n 3, pokes into render 2's object only) have not run"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = [
    "render-closing-r3k-pixel:out/20261110-193547/k-pb0/",
    "render-closing-r3k-regress:out/20261110-222647/rg-pb/",
    "render-closing-r4-q285:out/20261111-081210/", "render-closing-r6-render4x:out/20261112-144822/t/",
    "cited-scratch:closing7/a/q293/",
]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What was done.** Q293 kept one bounded item after E888: what the TA writes for render 2's own
object and how the 3D reads it. The two-render rows of E825, E827, E829 and E888 (`tri --tri-full -n 2
--geometry 1`: render 1 tiles its triangle and leaves the scene open, render 2 tiles its own and
draws) kept their `--dump-render` files, so both objects are already in the data. The round 7 plan
scanned every kept dump of the closing sessions for objects that open as the one-triangle scene's
do and read the jobs' own pixel counts (`closing7/a/q293/`). Re-run from the published copies:
byte-identical.

**Results [HW, read post hoc].** From `obj2_scan.out` and `obj2_images.out`:

| dumps | `CR_TE_AA` | first object (start, format word at) | second object | render 2's image |
|---|---|---|---|---|
| 8: no poke (7) or 0 at dword 11 (1) | 0x40000000 | 0, +12, zero before it | 27, +12, zero at +11 | 0 triangle, 4096 background |
| 1: t7, 0x00000001 at dword 11 | 0x40000000 | 0, +12, 0x1 before it | 27, +12, zero at +11 | 0 triangle, 4096 background |
| 2: p4a, p4b, 0xffffffff at dword 11 | 0x40000000 | 0, +12, 0xffffffff before it | 27, +12, zero at +11 | 0 triangle, 4096 background |
| 2: p3a, p3b, the twin's words at 11 to 26 | 0x40000000 | 0, +11 (the poked layout) | 27, +12, zero at +11 | 4096 triangle, 0 wrong |
| 3: pb-p0-te60 (2), pb-n60 | 0x60000000 | 0, +11, 0x000e1010 before it | 26, +11, 0x000e1010 before it | (not read) |

So in 13 of 13 dumps at 0x40000000 render 2's object is 27 dwords from render 1's, with the zero
at its dword 11 (dump dword 38) and the format word at its dword 12 (dump dword 39); at 0x60000000
the objects are 26 dwords apart and in the plain layout. In the 11 jobs whose render 1 object
stayed displaced, render 2's image is empty although its triangle covers the 64 x 64 target.

**What it shows.** [HW, post hoc] The TA writes render 2's own object in the same displaced
layout as render 1's: one zero dword inserted right before the format word, wherever the poke
before render 2 left render 1's object. [infer] The 3D reads render 2's object as it reads
render 1's (E829), the zero at the format word's place giving no pixels: an image with no
triangle pixel in 11 of 11 jobs fits that.

**What it does not show.** That the 3D skips render 2's object for its own zero rather than
stopping at render 1's displaced object first: every empty job had both objects displaced, and
the two twin jobs, where render 1's object was put in the bit-29-set layout, drew 4096 triangle
pixels that either object could have drawn (the same triangle; the pages hold render 2's colour
by then). That is what the plan's held-out rows test (a poke into render 2's object only, with
three renders). Everything is one command shape (64 x 64, one triangle, 0x40000000); 0x80000000,
0xc0000000, lines, points and the four-array 4x layout were not read for a second object. The
reading is post hoc, not a held-out test.
