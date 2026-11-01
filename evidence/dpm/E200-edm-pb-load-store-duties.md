+++
id = "E200"
claim = "The EDM loads a parameter-buffer descriptor into the TA-side or the 3D-side DPM registers (0x0618-0x0668 and 0x0600-0x0664), stores the free-list status registers back into it, reloads the thresholds when the descriptor's flags have bit 1 set, and rebuilds the page table from the descriptor's block list when they have bit 0 set, one 32-bit entry per page holding the previous page in the high half and the next in the low half"
unit = "dpm"
method = "the cut ukernel image (firmware-images) disassembled with usse-dis, the routines 0x1665-0x170d and their callers read by hand against the register table of firmware-edm-dataflow, and the DPM registers read back after the successful jobs of probes/dpm/parameter-buffer.toml; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "HW"]
date = "2026-11-01"
data = ["firmware-edm-dataflow", "firmware-images", "dpm-parameter-buffer"]
terms = ["ta3d_ctl.hw_pb_desc_ta", "ta3d_ctl.hw_pb_desc_3d", "CR_DPM_TA_ALLOC_PAGE_TABLE_BASE", "CR_DPM_TA_ALLOC_FREE_LIST", "CR_DPM_TA_ALLOC", "CR_DPM_TA_PAGE_COUNTS", "CR_DPM_TA_PAGE_THRESHOLD", "CR_DPM_PDS_THRESHOLD", "CR_DPM_TA_GLOBAL_LIST", "CR_DPM_TASK_TA_FREE", "CR_DPM_3D_PAGE_TABLE_BASE", "CR_DPM_3D_FREE_LIST", "CR_DPM_3D", "CR_DPM_3D_PAGE_COUNTS", "CR_DPM_TASK_3D_FREE", "PB_FLAGS.THRESHOLD_UPDATE", "PB_FLAGS.INIT_PAGE_TABLE", "pb_block.page_count", "pb_block.next_block_dev_vaddr", "CR_DPM_3D_DEALLOCATE"]
+++

**What was read.** The routines are at 0x1665-0x170d, called from the TA kick (0x8e9-0xacd), the
general event routine (0x1c4-0x599), the partial-render routine (0xc23-0xdbe) and the 3D kick
(0x112b-0x12db). Each takes a pointer to a parameter-buffer descriptor from the TA3D control
structure (dword 46 for the TA side, 47 for the 3D side; the dataflow lists them as the structure's
words at 0xb8 and 0xbc) and moves dwords between it and DPM registers. Dword numbers below are
indices into the descriptor, counting the one-element offset of multi-dword fetches (E093).

**Results.**

- Load into the TA (0x16a2): descriptor dword 4 with its low 4 bits cleared goes to 0x0618, dword 6
  to 0x061c, dword 7 to 0x0648, dwords 8 and 9 (the second shifted up 16 bits) to 0x0638, dword 10
  to 0x0620, dword 13 to 0x0668, dword 11 to 0x0624, and the low 16 bits of dword 12 with bit 16 set
  to 0x0628. A word that records which of the three PB slots of the TA3D control structure (words
  46, 47, 48) differ goes to 0x0664 (bit 0: first and third, bit 1: first and second, bit 2: second
  and third). Then 0x0684 is set to 1 and the routine waits for bit 0 of the event status register
  0x0118 and clears it by writing 1 to 0x0114.
- Load into the 3D (0x16e9): the same fields go to 0x0600 (dword 4), 0x0604 (6), 0x064c (7), 0x0660
  (dwords 8 and 9), then 0x0664 as above, then 0x0680 is set to 1 and the routine waits for bit 1 of
  0x0118.
- Store (0x168d TA side, 0x16d4 3D side): the free-list status registers (0x0700, 0x0710, 0x0724,
  0x072c on the TA side; 0x070c, 0x071c, 0x0728, 0x0730 on the 3D side) go back to dwords 6, 7
  (second register shifted up 16 bits), 8 and 9 of the descriptor, the high half of the page-count
  status for the TA side and the low half for the 3D side. When both sides share a descriptor the
  other side's state is stored first, with that pipe paused (0x15bc pauses it, 0x15ad resumes).
- Thresholds (0x1665): a four-dword fetch from the descriptor's dwords 10 to 13 sets 0x0620 (dword
  10), 0x0624 (11), 0x0628 (the low 16 bits of dword 12 with bit 16 set) and 0x0668 (13), the
  registers the TA load sets from the same dwords; the routine also clears bits 1:0 of dword 0. In
  the TA kick the call is made when the descriptor the TA already holds has bit 1 of dword 0 set; a
  second call, from the same kick under another condition, is not examined.
- Page table (0x170d): when bit 0 of dword 0 is set the routine clears bits 1:0 of it, copies dwords
  2 and 3 over dwords 6 and 7, zeroes dwords 8 and 9, and walks the block list from dword 14: for
  each block it writes one entry per page at the page-table base of dword 4, each holding the
  previous page's number in the high half and the next in the low half, with 0xffff in the missing
  neighbour at both ends of the list. The store address is the base plus a register offset whose
  word has bit 18 set; how that offset scales is not measured here.

**Hardware.** In the successful jobs of the parameter-buffer table (0x422, 0x200, 0x100, 0x80, 0x62
and 0x40 pages at 1024x768, 0x422 and 0x200 at 4096x4096) the registers read back as the loads leave
them: 0x0618 and 0x0600 both 0x10423000, 0x0648 and 0x064c both the page count less one in the high
half (0x04210000 at 0x422 pages), 0x0620 the page count plus 0x10, 0x0624 the page count less 0x22,
0x0628 that with bit 16, 0x0668 the page count less 0x122 (zero when negative), and 0x0664 equal to
5 (the first two slots equal, the third different) in every one.

**Not shown.** The conditions of the other calls; the DPM contexts, out-of-memory handling and
deallocation duties that the routines around these perform; the stride of the page-table store. The
register values above are the host's descriptor read back, not a test of the loads one by one.
