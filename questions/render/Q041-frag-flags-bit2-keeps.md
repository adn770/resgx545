+++
id = "Q041"
question = "what does a later job on a context at another address do with the DPM slot word that FRAG_FLAGS.BIT2 or NO_DEALLOCATE leaves set after a render?"
unit = "render"
phase = 11
evidence = ["E164", "E158", "E051", "E052", "E053", "E303", "E316"]
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

What is open: a later job on a context whose RT data is at another address, which the slot step
of the TA kick (3d.md §4.4) would store the kept owner for, through a context that is gone. Every
context sgxfive-test creates lands at the same addresses, so this needs a test that holds one
context while it renders on another.
