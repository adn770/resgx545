+++
id = "Q082"
question = "what do CR_EVENT_STATUS2 bits 6 and 7 mean, bit 6 set while a job hangs in its pixel task and bit 7 while a TA job hangs or faults?"
unit = "edm"
phase = 11
evidence = ["E317", "E318", "E319"]
terms = ["CR_EVENT_STATUS2"]
+++

`CR_EVENT_STATUS2` reads 0x400 when the GPU is idle. With recovery held it reads 0x480 after a
render faulted reading its stream page (E317) and after the VDM state word 1 bits 15:13 = 0 job
hung in its TA (E318), 0x440 while the job hung in its pixel task is held (E318, twice), and 0x400
while the EDM's own write to a read-only control block faults (E319). Every reset puts it back to
0x400. The bits are read once per held job, 2 s in; when they rise is not shown, and the kernel
does not enable or acknowledge them.

To settle it: sample the register through a normal render with the register timeline (TA, then 3D)
and through each held hang, from the kick on.
