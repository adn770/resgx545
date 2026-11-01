+++
id = "Q038"
question = "what does the final render read back of a partial render's depth (a depth buffer stored by ZLS, the 3D kick's RT status bit 1), now that a background object that reloads the target's colour gives an overflowing scene's whole image?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 10
evidence = ["E160", "E202", "E204", "E310", "E311", "E312", "E442", "E461", "E465", "E467", "E468", "E625", "E628", "E629"]
terms = ["Parameter Buffer (PB)", "Dynamic Parameter Management (DPM)"]
+++
What the missing pixels are is answered (E311): with `CR_ISP_CTL.PROCESS_EMPTY_TILES` clear every
overflowing job draws the whole triangle (207456 pixels at 1024x768, 4422528 at 4096x4096) at every
buffer size, so no geometry is discarded. With the kernel's value the missing pixels are whole
regions of the macrotiles that held geometry at a partial render, painted with the background by
the final render, whose streams hold only what the TA tiled after the last partial render. A
partial render frees every macrotile's pages, not only the aborted one's (E312), and stores a page
list per macrotile in the RT data's state page (E310). The amount drawn is the geometry tiled after
the last partial render, so it does not follow the buffer size; at 1024x768 in 0x23 pages the image
is exact, and the job's TA3DCtl words put its last abort at the first page (the ZLS threshold is 1,
E310) [infer].

The colour remedy is answered (E442): a background object whose pixel shader fetches the render
target at the pixel's position (the position from a douti of source 0 with two components, E437)
gives the whole triangle, 4422528 of 4422528 pixels, of the 4096x4096 job in 0x100 pages that the
library's background leaves with 987008 (three runs each).

Narrowed by E461 (`tri --depth`, a depth buffer for the ZLS flag, base, control and bases, the
triangle at z 0.5 under test less, two runs of every 1024x768 case, identical). The ZLS store of a
job writes a window of the buffer (64512 dwords at 1024x768, 326656 at 4096x4096) whatever the
parameter buffer, for a job that holds its scene too (Q107). In a job that overflows, the window's
first 15104 dwords (80640) read 0.0 and, from 0x28 pages down at 1024x768 and at 0x40 and 0x23 at
4096x4096, the rest hold the depth with its sign bit set: -1.0 where the whole-buffer job holds 1.0
and -0.5 where it holds 0.5; at 0x30 and 0x100 pages, taken as the one-partial-render case [infer],
it keeps the whole-buffer values behind the zeros. A load-only control (0x0011700a) stores nothing
in a whole-buffer job and the loaded 0.25f negated over the whole window in an overflowing one. So
the depth the partial renders keep is what the window holds at the end of the job, sign-flipped
[infer]; whether the final render loads it is not separated from the final render storing the same
window negated. A depth buffer also changes what the overflowing job draws: 0, 27408, 31629 and
31629 triangle pixels at 0x30, 0x28, 0x24 and 0x23 pages against 51408, 162544, 205061 and 207456
without it.

Narrowed again by E465 to E468 (11.22). The window E461 saw is the tile arithmetic of the store
(E465: tile (tx, ty) at dword 512 * (ty * (G + 1) + tx), G = control bits 11:3 = 1 in the
library's setup, so the tiles of a row overlap); what the overflowed job stores, seen with no
overlap (G = 33), is zeros for tile rows 0 to 11 (the first row of macrotiles) and the ramp with
its sign bit set for the rest (E468, 0x28, 0x23 and 0x30 pages, the printed counts identical). The
controls of those jobs have bit 19 (the store of the negated float, E466) clear and bit 1 clear
(no load, and a load clears the sign, E467), so the sign bit is set by something the control does
not show, probably the partial-render path [infer]; whether the final render loads at all is still
not separated. At 0x30 pages the ramp job of E468 is negated, unlike E461's z = 0.5 job at 0x30,
which keeps the positive whole-buffer values behind its zeros: the two disagree and it is not
explained (Q107).

What is open: whether the final render loads the partial renders' depth (what sets the sign bit of
the stored depth is not shown, E468), why the first row of macrotiles stores zeros and why 0x30
pages negate in one job and not in the other (Q107), why the depth buffer makes the overflowing
job draw less, and the depth test across partial renders with overlapping triangles whose order
the depth decides. The colour reload (E442) has not been run with a depth buffer. What the partial
render's reload reads from the render details' word is Q088's (fw).

To settle it: two overlapping triangles (probe --tri --obj2) in a depth-buffered job that overflows
the 0x23-page buffer, with the colour-reload background, the near triangle drawn first and last in
separate runs, the image against the whole-buffer one, read with the ramp job of E468 (the layout
of the stored buffer is known since E465).

Status: narrowed to the depth readback of the final render and the depth test across partial
renders.

Narrowed in 11.38 (E628, E629; 74 `depth` jobs and 10 of follow-up a). The final render's depth
after partial renders: in 8 of 8 overflowing jobs with a load buffer of ascending indices (z = 0.5
and ramp scenes, 0x28 and 0x30 pages) the store holds the load buffer's dword at every address
outside the first row of macrotiles, with the load bits 1 and 14 in the control (0x0017510e) and
without (0x0017110c) alike, while the same job in 0x422 pages stores the scene's depth without the
bits (0 of 2) and the loaded buffer with them (2 of 2): the loaded buffer reaches the store of a
job that overflows whatever the control says [infer: what loads is the partial-render path, not
the host's bits]. The load buffer itself comes back from those 8 jobs with 195583 dwords changed
to zero, all in tile rows 0 to 11 and none elsewhere, and unchanged from the 4 jobs that complete:
a store reaches the load address, so either a partial render stores zeros at the load base or the
load buffer is cleared as it is read [infer], and the zero region of the store is that region
(E628). The depth test across the partial render: two overlapping triangles, the first in a
geometry kick and the second in the final render with the overflow while the second is tiled (0x38
pages, 4 jobs), store the nearer triangle at 142323 and 141579 overlap pixels outside the zero
region (13510 more lie in it and are not seen), 0 mixed, with the bits and without (the cases at
0x3c to 0x48 completed, 12 jobs, and test the minimum only). So the depth the partial renders keep
is loaded by the final render and the test runs against it [infer]. The sign that E461 and E468
disagreed on is the raise of E625 (E629). Open: which of the two readings of the zeroed load
buffer holds, the colour reload with a depth buffer (the probe's depth scratch, a tool change of
the batch's plan, was not implemented), what the load reads when its base differs from the
store's, and the tile order of the store (Q107).
