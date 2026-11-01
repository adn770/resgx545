+++
id = "Q038"
question = "what does the final render read back of a partial render's depth (a depth buffer stored by ZLS, the 3D kick's RT status bit 1), now that a background object that reloads the target's colour gives an overflowing scene's whole image?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 10
evidence = ["E202", "E204", "E160", "E310", "E311", "E312", "E442", "E461"]
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
and -0.5 where it holds 0.5; at 0x30 and 0x100 pages, taken as the one-partial-render case
[infer], it keeps the whole-buffer values behind the zeros. A load-only control (0x0011700a) stores
nothing in a whole-buffer job and the loaded 0.25f negated over the whole window in an overflowing
one. So the depth the partial renders keep is what the window holds at the end of the job,
sign-flipped [infer]; whether the final render loads it is not separated from the final render
storing the same window negated. A depth buffer also changes what the overflowing job draws: 0,
27408, 31629 and 31629 triangle pixels at 0x30, 0x28, 0x24 and 0x23 pages against 51408, 162544,
205061 and 207456 without it.

What is open: whether the final render loads the partial renders' depth (the load-only control's
negated store fits it, the store of the same window negated fits as well), what the leading zero
dwords and the sign flip are (Q107), why the depth buffer makes the overflowing job draw less, and
the depth test across partial renders with overlapping triangles whose order the depth decides. The
colour reload (E442) has not been run with a depth buffer.

To settle it: two overlapping triangles (probe --tri --obj2) in a depth-buffered job that overflows
the 0x23-page buffer, with the colour-reload background, the near triangle drawn first and last in
separate runs, the image against the whole-buffer one; and the window read with a buffer whose
layout is known (Q107).

Status: narrowed to the depth readback of the final render and the depth test across partial
renders.
