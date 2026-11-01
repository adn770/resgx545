+++
id = "Q065"
question = "why does render flag bit 0 hang a kernel-built triangle job when the firmware completes a NO_RENDER render without rendering, and does one command with FIRST_KICK and LAST_KICK act as two?"
unit = "render"
phase = 11
evidence = ["E050", "E156", "E164", "E165", "E184", "E303", "E304"]
terms = [
    "FRAG_FLAGS.NO_RENDER", "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK",
    "ta3d_ctl.cmd_ta_dev_vaddr",
]
+++

The TA finish queues a render only for a LAST_KICK command (E156), and a render reaches the 3D queue
only that way (E165); with NO_RENDER the finish frees the scene's memory first. On the hardware
render flag bit 0 hangs the job (E050).

TA3DCtl dword 24 is read (E303, two runs): after one to four renders of a new context it reads the
TA client CCB's base (0x32400000) plus 0x2c0 for each render after the first, the address of the
last TA command the firmware read [infer: one to four renders]. A render without render flag bit 10
is drawn but its RT data set's cleanup then never completes (E303, two runs). That this is the
set's executed count left behind the kernel's pending count is a reading: the completion adds the
count only with bit 10 [RE: E164], and E304's outcomes (one run) fit a cleanup that waits for the
two to be equal [infer], the counts not read. A NO_RENDER render, which skips the completion, may
leave the same mismatch [infer].

What is open (3d.md §4.5 and §4.6): why bit 0 hangs the job itself rather than its cleanup;
whether nothing compares the two kick flags or a command's place in the CCB.

To settle it: render flag bit 0 with the kernel's wait extended, the context's CCB control words
and the RT data set's counts (a debugfs view, 11.10) dumped after the time-out; a job of one
command with both kick flags against two commands, the render memory compared.
