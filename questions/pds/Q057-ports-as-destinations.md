+++
id = "Q057"
question = "what do doutc, douts, slc, mr and ir0 do as move destinations, and movsa on ports other than doutd, and why does an enabled small count in tim hang the job?"
unit = "pds"
phase = 11
evidence = ["E127", "E128"]
terms = ["PORT.DOUTC"]
+++

In a fill's secondary program moves to mr, tim, ir0, slc and douts, and a movsa on douta, complete
the job and write nothing the attributes read back show (E127); tim loads the counter the ALU reads
(pds_isa.md §7, item 1). That an enabled small count in tim hangs the job was seen only in runs by
hand, which no table or record holds.

What is open (pds_isa.md §7, item 1): what these destinations do to anything other than the
attributes, what movsa does on the other ports, and whether and why an enabled small count in tim
hangs the job.

To settle it: on the laptop, each destination written in the primary and the secondary program of
the triangle job with the USE task's registers, the pixels and the PDS registers read back after;
tim with counts from 1 up, timed, ten runs each, recorded as a probe table.
