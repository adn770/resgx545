+++
id = "Q029"
question = "what do the EDM's render target and render context cleanups wait for, and which of them releases the parameter buffer in the TA/3D control block?"
unit = "render"
phase = 9
evidence = ["E148", "E023", "E289"]
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES"]
+++

The first half is answered (E289): with bit 8 of `CR_ISP_CTL` (the render context's isp_ipfmisc
word) clear, every 32x16 region the TA left without a control stream, except the scene's last
region, is skipped and left unwritten: 1 region at 96x64, 12 at 128x128, 33 at 256x128 and none
at 64x64, where the only empty region is the last one (one run).

What stays open: what the EDM's cleanups of the render target data set and of the render
context wait for before they complete, and which of them releases the parameter buffer in the
TA/3D control block.

To settle it: the EDM's state (the debugfs `kreg` file and `miscinfo`) at a job that a cleanup
holds, by withholding the pending count the render target data set keeps.
