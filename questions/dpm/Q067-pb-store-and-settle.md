+++
id = "Q067"
question = "how does the EDM's page-table builder (PB_FLAGS.INIT_PAGE_TABLE) scale its store offset (first half answered, with one inference: E446), and does the settle routine wait for the other pipe to go idle?"
unit = "dpm"
phase = 11
evidence = ["E153", "E200", "E201", "E309", "E362", "E446", "E448"]
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

Answered in its first half by E446 (the render context's page mapped writable for one context,
debugfs alias_ctx_rw, flag bit 0 set), with one inference: the stores into the table named by the
base are four bytes a page from the base, one dword for each of the 1058 pages of the descriptor,
none past them, and the render is exact with flag bit 0 set on the kernel's own table too, whose
result equals the kernel's [HW]. A control with the base at the scratch and flag bit 0 clear (six
runs, the flag word left alone or poked to 0) faults the render on the empty table and changes 0
to 2 scratch dwords, not 1058, so the stores need the flag [HW]; that the page-table builder (the
flag's action, E200) makes them is [infer], and it no longer rests on the render rewriting the
table alone.

What is open: whether a render with the table at the scratch and flag bit 0 clear that does not
fault (a table the host filled) leaves the scratch as it is, which would close the inference; what
the 2 scratch dwords of the control are; whether the other pipe is idle once the registers the
settle routine polls stop changing (E153), and whether the builder's result depends on the block
list.

To settle it: a render with the descriptor's page-table base at scratch pages the host filled with
the table and flag bit 0 clear, the scratch dwords changed counted; the settle registers sampled
around a PB swap on a running TA with two contexts on PBs of their own, overlapping (`tri --ctx2
--overlap`; E448 kept five timelines of the DPM registers that no one has read for it), the dump
compared with a PB block list that is not the kernel's.
