+++
id = "Q029"
question = "what does the EDM's render context cleanup wait for, and which cleanup releases the parameter buffer in the TA/3D control block?"
unit = "render"
phase = 9
evidence = ["E148", "E023", "E156", "E164", "E289", "E303", "E304"]
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES", "hw_rt_data_set.executed_count"]
+++

The first half is answered (E289): with bit 8 of `CR_ISP_CTL` (the render context's isp_ipfmisc
word) clear, every 32x16 region the TA left without a control stream, except the scene's last
region, is skipped and left unwritten: 1 region at 96x64, 12 at 128x128, 33 at 256x128 and none
at 64x64, where the only empty region is the last one (one run).

What the RT data set's cleanup waits for is answered in part. On the hardware a scene of two kicks
fails the set's cleanup in every run that tried one (E303 in both its runs, E304 in one; the
kick-objects table of E288 reset the GPU four times for this), as does a render without render flag
bit 10 (E303, two runs), and the kernel times out and resets the GPU; one render's cleanup
completes. Render details dword 54 is the set the firmware counts in: moved by 0xc it makes the
kernel report an overflow after a render and after a geometry kick (E304, one run). The reading that
fits every outcome is a cleanup that waits for the set's executed count to equal the pending count
the host keeps [infer]. Our kernel adds one to that count per scene [DDK: linux fork,
sgxfive_render.c], while a kick that is not the scene's last adds one to the executed count, and so
does a render with bit 10 [RE: E156, E164]. No case read the counts: no case dumped the set's dword
1.

What stays open: whether the set's cleanup compares the two counts, which no case read; what the
render context's own cleanup waits for once its RT data set is gone, and which of the cleanups
releases the parameter buffer in the TA/3D control block (the trace shows dwords 46 and 47 cleared
at the PB step, and dword 32 holding the cleaned-up descriptor).

To settle it: the RT data set's dwords 0 to 4 dumped after each job and before the cleanup (a
debugfs view of the context's kernel words, 11.10), for one render, two kicks and the rd:54 flips,
to read the counts; the cleanup trace (debugfs `render_cleanup`) of a context whose pending count
the host sets to the scene's kicks; then of one whose PB descriptor another context shares, which
tells the context's PB descriptor from the one the cleanup names in `TA3DCtl` dword 32.
