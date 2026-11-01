+++
id = "Q029"
question = "does clearing bit 8 of the render context's isp_ipfmisc word skip untouched tiles above 64x64, and what do the EDM's render target and render context cleanups wait for?"
unit = "render"
phase = 9
evidence = ["E148", "E023"]
terms = []
+++

Targets from 64x64 to 256x256, up to sixteen tile rows, render exactly with bit 8 of the render
context's isp_ipfmisc word set (E148; the bit has no name of its own here). Two things stay open.

First, whether clearing that bit skips tiles that no geometry touches once the target is
larger than 64x64, and which tiles. Second, what the EDM's cleanups of the render target data
set and of the render context wait for before they complete, and which of them releases the
parameter buffer in the TA/3D control block.

To settle it: sgxfive-test tri at 96x64, 128x128 and 256x128 with a poke that clears the bit
(the debugfs `kpoke` file on the `isp_ipfmisc` word of the render details), counting unwritten
tiles; then the EDM's state (the debugfs `kreg` file and `miscinfo`) at a job that a cleanup holds,
by withholding the pending count the render target data set keeps.
