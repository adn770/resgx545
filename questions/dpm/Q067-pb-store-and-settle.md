+++
id = "Q067"
question = "does the settle routine wait for the other pipe to go idle (the page-table builder's store offset is answered: E446, E453)?"
unit = "dpm"
phase = 11
evidence = ["E153", "E200", "E201", "E309", "E362", "E446", "E448", "E453"]
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

Answered in the other half by E453 (a table the host filled, flag bit 0 clear): with the base at
scratch pages holding the table the kernel builds before a job, the render completes exactly (6 of 6
runs) and changes 4 scratch dwords (the ends of the list), not 1058, so the render itself does not
write the table; with the flag set over the same table the scratch changes by the same 4 (6 of 6),
and over zeros by 1058, so the flag's action is what stores them [HW]. The table a finished job
leaves is not a valid pre-job table (3 of 3 faults).

What is open: whether the other pipe is idle once the registers the settle routine polls stop
changing (E153), and whether the builder's result depends on the block list; why a flagged build
over a zero table rendered exactly after a run that had not faulted and faulted after one that had
(Q105).

To settle it: the settle registers sampled around a PB swap on a running TA with two contexts on
PBs of their own, overlapping (`tri --ctx2 --overlap`; E448 kept five timelines of the DPM registers
that no one has read for it), the dump compared with a PB block list that is not the kernel's.
