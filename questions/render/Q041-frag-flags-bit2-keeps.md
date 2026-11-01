+++
id = "Q041"
question = "what does a later job do with the DPM slot word that FRAG_FLAGS.BIT2 or NO_DEALLOCATE leaves set after a render, when no image changes with either bit?"
unit = "render"
phase = 11
evidence = ["E164", "E158", "E051", "E052", "E053", "E303"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "hw_render_details.access_dev_vaddr"]
+++

Which bit the completion's mask 0xc needs is answered (E303): either is enough. Read after the
context's cleanup, TA3DCtl dword 20 (the first DPM slot's RT data) keeps the RT data after a
render with render flag bit 2 (0x4), bit 3 (`NO_DEALLOCATE`, 0x8) or both, and is 0 without them;
`NO_DEALLOCATE` also keeps dword 25, the TA's RT data, which the TA finish clears for a last kick
without it. A second render on the same context with the bits clear clears dword 20 again. The
context's cleanup clears neither word, so they outlive the context. Both runs agree, and no image
changes (E051-E053).

What is open: what a later job does with the slot so kept (a reload skipped, or the stale RT data
of a context that is gone); the access word (render details dword 52), which the dumps here do not
read; whether the kernel's rewrite of the RT data before each job (E052) undoes what the bits
keep.

To settle it: two contexts, the first rendering with 0xc, the second's first kick with
`NO_DPM_CONTEXT_LOAD` clear, its image and the DPM registers compared with a control; the access
word dumped through a debugfs view of the context's kernel words (11.10); then the kernel's RT
data rewrite switched off between two renders of one scene (11.10).
