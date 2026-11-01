+++
id = "Q057"
question = "what do doutc, douts, slc, mr and ir0 do as move destinations, and movsa on ports other than doutd, and does an enabled small count in tim hang the job, and why?"
unit = "pds"
phase = 11
evidence = ["E127", "E128", "E264", "E421"]
terms = ["PORT.DOUTC"]
+++

In a fill's secondary program moves to mr, tim, ir0, slc and douts, and a movsa on douta, complete
the job and write nothing the attributes read back show (E127); tim loads the counter the ALU reads
(pds_isa.md §7, item 1). That an enabled small count in tim hangs the job was seen only in runs by
hand, which no table or record holds.

In the primary pixel program of a 64x64 triangle (E264): a movs to mr, slc, douts or ir0 leaves
every pixel as the control's and the render completes; mr01 still reads 0 after the movs to mr and
ir0 still the tile position after the movs to ir0; a movs to doutc faults the job, with a BIF status
(0xd0400) that is not the PDS's own (0x92000, 0xd2000), which suggests that doutc starts work in
another unit that reads unmapped memory [infer]. In a fill the same write made the USE task fault on
page 0 (E127).

What is open (pds_isa.md §7, item 1): what doutc starts and what its words address, what mr, slc,
douts and ir0 are for (no effect seen in either task), what movsa does on the other ports, and
whether and why an enabled small count in tim hangs the job.

To settle it: doutc with its four words varied (a mapped address in each in turn, the scratch at
0x10000) in a fill, the faults and the scratch read back; the tim counts from 1 up, timed, ten runs
each, kept for a session that may hang jobs.

Narrowed in 11.15 (E421, two runs): a movs to doutc in the primary pixel program faults the job in 8
of 8 with BIF status 0xd0400 at 0x1f031 (once 0x1f034), whichever of its four words holds the
scratch placeholder 0x5CAF0000, so the address does not follow the placeholder (the placeholder's
patch in this template is unconfirmed). Not run: the tim counts from 1 (they may hang the job and
freeze the counter until a reset) and a fill's doutc with a patched address. Status: narrowed, not
answered; missing: a PDS template whose data words are patched with the scratch address.
