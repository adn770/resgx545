+++
id = "Q065"
question = "why does render flag bit 0 hang a kernel-built triangle job when the firmware completes a NO_RENDER render without rendering, and does one command with FIRST_KICK and LAST_KICK act as two?"
unit = "render"
phase = 11
evidence = ["E050", "E156", "E164", "E165", "E184"]
terms = [
    "FRAG_FLAGS.NO_RENDER", "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK",
    "ta3d_ctl.cmd_ta_dev_vaddr",
]
+++

The TA finish queues a render only for a LAST_KICK command (E156), and a render reaches the 3D queue
only that way (E165); with NO_RENDER the finish frees the scene's memory first. On the hardware
render flag bit 0 hangs the job (E050). TA3DCtl dword 24 moves by 0x2c0 from a one-render to a
two-render job (E184), which reads as the CCB's read address advancing by a command [infer].

What is open (3d.md §4.5 and §4.6): why bit 0 hangs, whether nothing compares the two kick flags
or a command's place in the CCB, and whether dword 24 is the command's address.

To settle it: on the laptop, render flag bit 0 with the kernel's wait extended and the context's CCB
and status words dumped after the time-out; a job of one command with both kick flags against two
commands, the render memory compared; TA3DCtl dword 24 read after jobs of one to four renders.
