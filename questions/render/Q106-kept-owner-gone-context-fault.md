+++
id = "Q106"
question = "why does a render on a second context at another RT data address fault at page 0x20003000 after the first context, which kept the DPM owner with render flag bit 3, is closed (E458)?"
unit = "render"
phase = 11
evidence = ["E458", "E451", "E316", "E310", "E462"]
terms = ["FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE"]
+++

E458: with both contexts alive, a render on a second context clears the words render flag bit 3
(NO_DEALLOCATE, alone or with bit 2) keeps and is exact (4 of 4 runs); with the first context closed
after its render, the same render faults (6 of 6 runs: BIF fault status `0x90004` at `0x200030c1`,
page 0x20003000 through list 1) and the close leaves the kept words in place (TA3DCtl dwords 20 and
25 both the first context's RT data + 0x18). With bit 2 alone the second render is exact in both
cases and dword 20 stays.

Narrowed by E462 (the DPM registers 0x0600 to 0x0750 beside the words at every snapshot, and
regtimeline): after a render that keeps the owner with bit 3 the DPM status registers read 0x0700
and 0x070c = 0x04220003, 0x0710 and 0x071c = 0x421, 0x0724 = 0x00020002 and 0x0728 = 2, where bit 2
alone and no flag leave 0x00020003, 1, 0 and 0 (6 of 6 runs each); the close changes none of the 85
registers (4 of 4 runs with bit 3, and none in the 4 runs with the control and bit 2 alone) and the
second render then faults (9 of 9 runs) with none of the 85 changing before the recovery (3 of 3
runs that sampled them all); with the first context open the second render takes the registers back
to 0x00020003, 1, 2 and 0 (5 of 5).

Open: what accesses page 0x20003000 (for a context of up to 64x64 the TA data's DPM state page,
E310), whether it is the slot step storing the kept owner's state through the second context's
directory or reading the first's, and whether the fault needs the closed context's memory to be
freed or only the context to be gone.

To settle it: the same case with the first context's memory kept (a kernel switch that does not
free it, or a third context holding the VM), with the second context's TA data page 0x20003000
poked or filled (tadata_fill) before the render. (The DPM registers beside the slot words in the
exact cases, and regtimeline through the faulting render, were read in E462.)
