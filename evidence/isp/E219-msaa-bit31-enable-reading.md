+++
id = "E219"
claim = "Reading 0x042c bit 31 as the enable of the multisampled ISP path is consistent with the data (bits 1:0 at 2: bit 31 clear draws nothing, in two multisample setups) but rests on one mode and two setups; that clear bit 31 still tiles the triangle is not shown"
unit = "isp"
method = "comparison of E211's jobs with the open descriptions of other GPUs' anti-aliasing controls (no citation record of this tree covers them, so the reading is ours), hardware run on the laptop, linux fork with the debug option on; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-msaa"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.ENABLE", "CR_ISP_MSAA.MODE", "CR_TE_AA"]
+++

**The reading.** The multisample jobs of E074 and E210 set bit 31 of 0x042c together with the mode
bits, and the TE anti-aliasing bits are a separate pair of enables, so bit 31 looked like a further
enable of the multisampled path (the reading is ours). A test would clear it under multisampling
and see what the ISP writes.

**What the data show.** E211's jobs: with bits 1:0 at 2 and the sample positions, bit 31 set
draws 896 triangle pixels and bit 31 clear draws none; with the TE bits and the macrotile words
added, 1248 against none. With the whole word at 0 the unpoked 1062-pixel image is drawn. So with
the multisample mode on, clearing bit 31 removes the triangle from the target in both setups, and
the single-sampled image needs no bit 31.

**Not shown.** That the multisampled path is "enabled" by the bit, and not, for instance, a bit
the path needs for its stores to reach the target, is a reading: the data give an effect, not a
mechanism. Mode 1 was not run with bit 31 clear, and the single-sampled path was run with bit
31 clear only in the all-zero word, so "the single-sampled path ignores it" is not shown for other
bits. That the triangle is tiled with bit 31 clear needs the parameter-buffer dumps that are not
in the data (E211). The name CR_ISP_MSAA.ENABLE rests on this one run.
