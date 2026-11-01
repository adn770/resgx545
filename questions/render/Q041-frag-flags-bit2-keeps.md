+++
id = "Q041"
question = "what does a later job on a context at another address do with the DPM slot word that FRAG_FLAGS.BIT2 or NO_DEALLOCATE leaves set after a render?"
unit = "render"
phase = 11
evidence = ["E164", "E158", "E051", "E052", "E053", "E303", "E316", "E451"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "hw_render_details.access_dev_vaddr"]
+++

Which bit the completion's mask 0xc needs is answered (E303): either is enough. Read while the
context lives (E316, one run), render flag bit 2 keeps TA3DCtl dword 20 (the first DPM slot's RT
data) after the render and leaves dword 25 clear; bit 3 (`NO_DEALLOCATE`) or both keep both. A
later render on the context with the bits clear clears both, and so does a new context whose RT
data lands at the kept address, which renders exactly; of the DPM registers after it only
`CR_DPM_PAGE_STATUS` differs from a control (0x8 against 0x6). The kernel's rewrite of the RT data
set before each job is not what clears the words: with debugfs `rtds_keep` set the second render
clears them as before. The access word render details word 52 points at reads 0 before and after
every render, kept or not.

Narrowed by E451 (two contexts in one VM, both alive, two runs of each case): a later job on a
second context whose RT data is at another address (0x32423300 against 0x32411300), with the bits
clear, leaves the dword 20 that bit 2 alone kept as it is; a second context that keeps too takes
dword 21 after a first kept by bit 2 alone, and the words 20 and 25 after one kept by 0xc. That
the same job clears the words that bit 3 keeps is [infer]: the words were read once, after the pair
of renders, not between them.

What is open: the kept owner through a context that is gone. The slot step of the TA kick
(3d.md section 4.4) would store the kept owner for a later job on a context whose RT data is at
another address; E451 read the words while both contexts were alive and does not show it. Whether
the kept words are cleared by the second render or only seen as 0 after it is open with it.

To settle it: close the first context after its flagged render, render on the second, and read
the words after each step, then compare the DPM registers beside the words.
