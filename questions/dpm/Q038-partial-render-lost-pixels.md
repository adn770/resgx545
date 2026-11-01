+++
id = "Q038"
question = "does a background object with a colour reload, or a host that renders the scene's partial renders into a stored target, give the whole image of an overflowing scene, and what does the final render read back of a partial render's depth?"
unit = "dpm"
phase = 10
evidence = ["E202", "E204", "E160", "E310", "E311", "E312"]
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

What is open: the remedy is not run. A background object that reloads the target's colour (or
depth through ZLS) in the final render and in each partial render should give the whole image; no
run has built one. Whether the 3D kick's RT status bit 1 makes the final render load a partial
render's depth (3d.md §6.4) is also not run, and a PB dump at each partial render waits for a
kernel hook (11.10).

To settle it: a background object whose pixel program reads the target (a texture fetch of the
colour buffer at the pixel's position) for the overflowing 1024x768 and 4096x4096 scenes, the image
compared with the whole-buffer one; then with a depth test and a depth buffer stored by ZLS.
