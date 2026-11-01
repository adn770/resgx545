+++
id = "Q067"
question = "how does the EDM's page-table builder (PB_FLAGS.INIT_PAGE_TABLE) scale its store offset, and does the settle routine wait for the other pipe to go idle?"
unit = "dpm"
phase = 11
evidence = ["E153", "E200", "E201", "E309"]
terms = ["hw_pb_desc.page_table_base", "CR_DMS_CTRL"]
+++

The EDM loads a PB descriptor into the TA or 3D DPM registers, stores the free-list status back and,
with flag bit 0, rebuilds the page table from the block list, one entry per page (E200); the
registers read back as these loads leave them (E201). Before a PB swap on a running pipe the routine
at 0x15bc sets CR_DMS_CTRL bits 2:0 and polls the other pipe's signature and settle registers
(E153).

How a host lays out a table it builds itself is answered (E309): the DPM rewrites our kernel's
table in place, one 32-bit entry per page at the base plus four times the page number, the
previous page in the high half and the next in the low half, and the free list it chains agrees
with the status registers after every job tried.

What is open: the EDM's own builder is never run (our kernel never sets the flag, and no poke
reaches the PB descriptor), so its stride is not measured; and whether the other pipe is idle once
the registers the settle routine polls stop changing, which is all the routine waits for (E153).

To settle it: a kernel poke target on the PB descriptor (11.10), then a job with flag bit 0 set
and the kernel's table zeroed, the dump's table compared with the kernel's; the settle registers
sampled with regtimeline around a PB swap on a running TA (two contexts with their own PBs).
