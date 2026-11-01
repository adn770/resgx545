+++
id = "Q038"
question = "what does the final render read back of a partial render's depth (a depth buffer stored by ZLS, the 3D kick's RT status bit 1), now that a background object that reloads the target's colour gives an overflowing scene's whole image?"
unit = "dpm"
phase = 10
evidence = ["E202", "E204", "E160", "E310", "E311", "E312", "E442"]
terms = ["Parameter Buffer (PB)", "Dynamic Parameter Management (DPM)"]
+++
What the missing pixels are is answered (E311): with `CR_ISP_CTL.PROCESS_EMPTY_TILES` clear every
overflowing job draws the whole triangle (207456 pixels at 1024x768, 4422528 at 4096x4096) at every
buffer size, so no geometry is discarded. With the kernel's value the missing pixels are whole
regions of the macrotiles that held geometry at a partial render, painted with the background by the
final render, whose streams hold only what the TA tiled after the last partial render. A partial
render frees every macrotile's pages, not only the aborted one's (E312), and stores a page list per
macrotile in the RT data's state page (E310). The amount drawn is the geometry tiled after the last
partial render, so it does not follow the buffer size; at 1024x768 in 0x23 pages the image is exact,
and the job's TA3DCtl words put its last abort at the first page (the ZLS threshold is 1, E310)
[infer].

The colour remedy is answered (E442): a background object whose pixel shader fetches the render
target at the pixel's position (the position from a douti of source 0 with two components, E437)
gives the whole triangle, 4422528 of 4422528 pixels, of the 4096x4096 job in 0x100 pages that the
library's background leaves with 987008 (three runs each).

What is open: what the final render reads back of a partial render's depth, which a colour reload
does not say: whether the 3D kick's RT status bit 1 makes the final render load a partial render's
depth (3d.md §6.4), and whether a depth buffer stored by ZLS (and loaded by it in the final
render) keeps the depth test's result across partial renders. The tool has no depth buffer, and a
PB dump at each partial render waits for a kernel hook (11.10).

To settle it: a depth buffer for the render (ZLS stored and loaded, the ISP's depth test with
overlapping triangles whose order the depth decides) on the overflowing 4096x4096 scene with the
colour reload, the image compared with the whole-buffer one.

Not run in 11.16: no tool option sets up a depth buffer or the ZLS words. Status: narrowed to the
depth readback.
