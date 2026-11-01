+++
id = "Q106"
question = "why does a render on a second context at another RT data address fault at page 0x20003000 after the first context, which kept the DPM owner with render flag bit 3, is closed (E458)?"
unit = "render"
phase = 11
evidence = ["E458", "E451", "E316", "E310"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE"]
+++

E458: with both contexts alive, a render on a second context clears the words render flag bit 3
(NO_DEALLOCATE, alone or with bit 2) keeps and is exact (4 of 4 runs); with the first context
closed after its render, the same render faults (6 of 6 runs: INT_STAT `0x90004`, BIF_FAULT
`0x200030c1`, page 0x20003000 through list 1) and the close leaves the kept words in place (TA3DCtl
dwords 20 and 25 both the first context's RT data + 0x18). With bit 2 alone the second render is
exact in both cases and dword 20 stays.

Open: what accesses page 0x20003000 (for a context of up to 64x64 the TA data's DPM state page,
E310), whether it is the slot step storing the kept owner's state through the second context's
directory or reading the first's, and whether the fault needs the closed context's memory to be
freed or only the context to be gone.

To settle it: the same case with the first context's memory kept (a kernel switch that does not
free it, or a third context holding the VM), with the second context's TA data page 0x20003000
poked or filled (tadata_fill) before the render, and the DPM registers sampled by regtimeline
through the faulting render. Also compare the DPM registers (0x0600 to 0x0750) beside the slot
words in the exact cases, against the control: bit 2 alone with the first context closed, and bit 3
(0xc) with it open, which E458 read after the second render only.
