+++
id = "E201"
claim = "The descriptor the host gives the EDM holds a flags dword, the initial and current free-list head/tail and previous-page words, a page-table base address, the local and global page counts, four thresholds (TA, ZLS, global, PDS), and a pointer to a list of blocks; with the host's values (0x422 pages) the DPM registers read back a free list from page 1 to the last page, a previous-page word one before it, thresholds of pages + 0x10, pages - 0x22, the same with bit 16 set, and pages - 0x122, and the same fields at every smaller size"
unit = "dpm"
method = "the descriptor fields read by the load, store and page-table routines of the cut ukernel image (firmware-images; the routines of E200), and the DPM registers read back after the successful jobs of probes/dpm/parameter-buffer.toml; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "HW"]
date = "2026-11-01"
data = ["firmware-edm-dataflow", "firmware-images", "dpm-parameter-buffer"]
terms = ["hw_pb_desc", "hw_pb_desc.initial_stack_top", "hw_pb_desc.current_stack_top", "hw_pb_desc.initial_dpm_ta_alloc", "hw_pb_desc.dpm_ta_alloc", "CR_DPM_TA_ALLOC", "hw_pb_desc.ta_threshold", "hw_pb_desc.zls_threshold", "hw_pb_desc.global_threshold", "hw_pb_desc.pds_threshold", "pb_block", "PB_FLAGS.INIT_PAGE_TABLE"]
+++

**What was read.** The same routines as E200, from the descriptor's side: which dword each one reads
or writes. The firmware's multi-dword fetches and stores start one element after their address
(E093), and the indices below count that.

- dword 0: flags. Bit 0 asks for the page table to be rebuilt and bit 1 for the thresholds to be
  reloaded; the routines clear both.
- dwords 2 and 3: the initial free list (head/tail and previous page), copied to dwords 6 and 7 when
  the table is rebuilt.
- dword 4: the page-table base, low 4 bits ignored; it goes to 0x0618 (TA) or 0x0600 (3D) and is the
  base of the builder's stores.
- dwords 6 and 7: the current free list; they go to 0x061c and 0x0648 (TA) or 0x0604 and 0x064c (3D)
  and are stored back from the status registers.
- dwords 8 and 9: the local and global page counts; they go to 0x0638 (TA, dword 8 low, dword 9
  high) or 0x0660 (3D), are stored back from the status registers, and are zeroed when the table is
  rebuilt.
- dwords 10 to 13: the TA, ZLS, global and PDS thresholds, in 0x0620, 0x0624, 0x0628 (low 16 bits,
  bit 16 set) and 0x0668.
- dword 14: a pointer to the first block of the block list, walked by the page-table builder.

A block, as the builder reads it, has a page count in its first dword, a first-page field in its
third and a pointer to the next block in its fourth; the builder fills the page table block by block
(E200).

**Hardware.** The host (our kernel) fills the descriptor for the sizes of the parameter-buffer
table, and after the successful jobs the registers hold: free-list status 0x04220001 at 0x422 pages
(tail 0x422 in the high half, head 1), 0x02000001 at 0x200 (0x01ff0000 at 0x0648 and 0x064c), and so
on down to 0x00400001 at 0x40; thresholds of pages + 0x10 (0x0620), pages - 0x22 (0x0624), 0x0628
holding the value of 0x0624 with bit 16 set, and pages - 0x122 (0x0668, 0 below 0x122); 0x0664 at 5.
The page-table base register 0x0618 reads 0x10423000 at every size.

**Not shown.** That the host builds the page table itself (the flag that asks the EDM to build it is
a firmware path not run here), the page contents and the 4 KiB stride of one entry per page, which
need a read of the page table in memory. The host in these jobs is our kernel.
