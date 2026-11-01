+++
id = "Q065"
question = "why does render flag bit 0 hang a kernel-built triangle job when the firmware completes a NO_RENDER render without rendering, and does one command with FIRST_KICK and LAST_KICK act as two?"
unit = "render"
phase = 11
evidence = ["E050", "E156", "E164", "E165", "E184", "E303", "E304", "E361"]
terms = [
    "FRAG_FLAGS.NO_RENDER", "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK",
    "ta3d_ctl.cmd_ta_dev_vaddr",
]
+++

The TA finish queues a render only for a LAST_KICK command (E156); with NO_RENDER the finish frees
the scene's memory first. On the hardware render flag bit 0 hangs the job (E050). A render without
render flag bit 10 adds nothing to the executed count, and the kernel's count follows (E314).

Narrowed by E361 (one run, held): with render flag bit 0 the TA finishes (the PB descriptor holds
its two pages, both frame numbers read 1) and the 3D takes the render (`hw_render_details_3d`
names it), but the render never completes: the executed count stays 0 against the kernel's pending
1, the RT data state reads 0x20, the context's pending list keeps the render details. So the bit
hangs the render in the 3D, not its cleanup.

What is open: what the 3D waits for with bit 0; and whether one command with both kick flags acts as
two (our tool's scenes always put the geometry in every kick).

To settle it: the same job with the 3D's registers sampled from the kick (regtimeline), and a
library job whose closing kick holds no geometry against a single command, the render memory
compared.
