+++
id = "Q290"
question = "what advances the count byte pa1 bits 31:24 that every event handed to an EDM task carries (in E747's 14 client jobs it rose by one after each entry with pa0 = 0 and pa1 bit 8 and after nothing else, 124 of 124 successive pairs; E746: after each host kick), and why does it read 2 on the first tick after a firmware load"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E746", "E747"]
terms = ["Event Data Master (EDM)"]
+++
Split off 2026-11-10 from the questions on bits 24 and 25 of pa1 (answered by E746, which read them as
bits of a count byte). The count is 2 on every tick of a freshly armed firmware, 2, 3 and 4 on the
three host kicks of E746 (+1 after each), and rose by one after each (slot 0, pa1 bit 8, pa0 = 0)
entry of 14 client jobs, the kernel's command buffer kicks that a job causes (E747, read after the
run, not a frozen rule); it carried unchanged from the last entry of a job to the first of the next
(13 of 13 boundaries). Open: whether it counts kicks of the kernel's command buffer or something
those kicks also cause, why it is 2 after the arm (the arm's own GETMISCINFO read is one guess,
not tested), whether it wraps at 256 and whether any other event advances it.

To settle it: a stage that reads the byte at the arm, after a reset and after more than 256 kicks,
and a job type whose kernel-buffer kicks are known (a transfer, a render with a partial render),
logged in window 2 of the ring of E746.
