+++
id = "Q067"
question = "how does the PB store offset scale with the page count, how must a host lay out a page table it builds itself, and does the settle routine wait for the other pipe to go idle?"
unit = "dpm"
phase = 11
evidence = ["E153", "E200", "E201"]
terms = ["hw_pb_desc.page_table_base", "CR_DMS_CTRL"]
+++

The EDM loads a PB descriptor into the TA or 3D DPM registers, stores the free-list status back and,
with flag bit 0, rebuilds the page table from the block list, one entry per page (E200); the
registers read back as these loads leave them (E201). Before a PB swap on a running pipe the routine
at 0x15bc sets CR_DMS_CTRL bits 2:0 and polls the other pipe's signature and settle registers
(E153).

What is open (3d.md §6.1 and §6.2): how the store offset scales, the page table's layout in memory
when a host builds it, and whether the other pipe is idle once the registers the settle routine
polls stop changing, which is all the routine waits for (E153).

To settle it: on the laptop, PB dumps after loads at several page counts with flag bit 0 set and
clear; a host-built page table in the layout the EDM writes; the settle registers sampled with
regtimeline around a PB swap on a running TA.
