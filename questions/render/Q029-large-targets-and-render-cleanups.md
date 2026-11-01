+++
id = "Q029"
question = "what does the render context's own cleanup wait for once its RT data set is cleaned up (the PB is released by the PB step of the donor's cleanup: E449)?"
unit = "render"
kind = "fw"
phase = 9
evidence = [
    "E148", "E023", "E156", "E164", "E289", "E303", "E304", "E314", "E315", "E318", "E354",
    "E355", "E449",
]
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES", "hw_rt_data_set.executed_count", "hw_rt_data_set.pending_count_dev_vaddr"]
+++

The first half is answered (E289): with bit 8 of `CR_ISP_CTL` (the render context's isp_ipfmisc
word) clear, every 32x16 region the TA left without a control stream, except the scene's last
region, is skipped and left unwritten: 1 region at 96x64, 12 at 128x128, 33 at 256x128 and none
at 64x64, where the only empty region is the last one (one run).

What the RT data set's cleanup waits for is answered (E314, E315, one run each). The counts read
while the context lives: the executed count (set word 1) rises by one at every kick of a scene,
the geometry kicks included, and not for a render without render flag bit 10; with the kernel
raising its pending count by the same rule the two are equal after every job of scenes of one to
four kicks, and every cleanup completes (E314). The cleanup compares the executed count with the
word the set's word 0 points at and waits for them to be equal: with the pending count one above
or one below, the cleanup fails; with it one above but word 0 pointed at the executed count
itself, it completes (E315). Render details word 54 names the set counted in, the count landing
one word past the address it holds (E315, restating E304's reading with the counts read). The
cleanup failures of E303 and E304 were the kernel's pending count of one per scene.

Narrowed by E449 (two render contexts on one PB, closed in both orders, 8 shared-PB runs): the PB
is released by the PB step of the donor's cleanup. The context that shares the PB sends only the RT
data and context steps (its PB descriptor is passed as 0) and leaves the loaded-PB slots at the
donor's descriptor; the donor's cleanup, with its PB step, clears them, and runs after the sharing
context's release whichever is closed first. TA3DCtl dword 32 holds the operand of the last CLEANUP
sent [infer].

What stays open: what the render context's own cleanup waits for once its RT data set is gone. The
cleanups of E318's held jobs failed after blame-free resets that ran the held job again; with a
reset that blames the held job, the held context's cleanup completes (E354, E355; linux fork
commit 31).

To settle it: the cleanup of a context with a job in flight or its PB loaded by a running TA (a
close during a long render), and the firmware's wait on the context's own cleanup read from a
trace of its commands.
