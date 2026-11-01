+++
id = "Q067"
question = "how does the EDM's page-table builder (PB_FLAGS.INIT_PAGE_TABLE) scale its store offset, and does the settle routine wait for the other pipe to go idle?"
unit = "dpm"
phase = 11
evidence = ["E153", "E200", "E201", "E309", "E362"]
terms = ["hw_pb_desc.page_table_base", "CR_DMS_CTRL", "hw_pb_desc.pb_flags"]
+++

The EDM loads a PB descriptor into the TA or 3D DPM registers, stores the free-list status back and,
with flag bit 0, rebuilds the page table from the block list, one entry per page (E200); the
registers read back as these loads leave them (E201). Before a PB swap on a running pipe the routine
at 0x15bc sets CR_DMS_CTRL bits 2:0 and polls the other pipe's signature and settle registers
(E153). How a host lays out a table it builds itself is answered (E309): one 32-bit entry per page
at the base plus four times the page number, previous page in the high half, next in the low half.

Narrowed by E362 (two runs): with flag bit 0 set at the first kick (kernel poke pb:0), the EDM's
write to the render context's page (where the PB descriptor sits, at +0x380) faults under the
client's directory, in which the kernel's memory is read-only, so the builder cannot run on our
kernel's mappings and its stride is still not measured.

What is open: the builder's stride; whether the other pipe is idle once the registers the settle
routine polls stop changing (E153).

To settle it: a kernel switch that maps the context page writable in the client directory for one
job (as alias_ta3d_ro does for the control block), then flag bit 0 with the kernel's table zeroed,
the dump compared; the settle registers sampled around a PB swap on a running TA (two contexts).

Not run in 11.16: the builder needs the render context's page writable in the client directory for
one job. Kernel need: a debugfs switch that maps that page writable (as alias_ta3d_ro does for the
control block) for the next job, then kpoke pb:0 with the table zeroed and the dump compared; the
settle sampling needs two contexts. Status: narrowed, not answered.
