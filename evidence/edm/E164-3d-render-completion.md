+++
id = "E164"
claim = "A render completes only when both the end of render (request 0x2, handler at 0xebb) and the 3D deallocation (request 0x1, handler at 0xeb4) have arrived, in either order; the completion (0xfd1) then writes the RT index's destination sync, steps to the next render target or, on the last, completes the TA to 3D dependency, the 3D transfer-queue sync, the source syncs and the 3D status pairs, marks the RT data free and raises SW_EVENT; a partial render instead posts request 0x80000"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the end-of-render and memory-free handlers (0xeb4-0xecc), the completion (0xfd1-0x1034) and its two routines (0xf45 and 0xf9d); fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset, a post-increment fetch starts at the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_EVENT_STATUS.PIXELBE_END_RENDER", "CR_EVENT_STATUS.DPM_3D_MEM_FREE", "FRAG_FLAGS.GET_VIS_RESULTS", "FRAG_FLAGS.TA3D_DEPENDENCY", "hw_rt_data.rt_status_dev_vaddr", "hw_rt_data.state", "FRAG_FLAGS.BIT10", "hw_rt_data_set.executed_count", "hw_rt_data.hw_render_details_dev_vaddr", "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "CR_EVENT_STATUS.SW_EVENT", "hw_render_details.access_dev_vaddr"]
+++

**What was read.** Instruction numbers are indices in hex. `sa9` is the 3D state word (E154): bit
4 is a render in flight and bit 5 a deallocation pending, set by the 3D kick (E163). The render
details are `rd` and the render flags `rd` dword 53.

**Results.**

- *End of render (`0xebb`).* Request `0x2` is acknowledged with `0x40000` (`PIXELBE_END_RENDER`).
  If bit 2 of `sa9` is set the job is a transfer and the handler goes to the transfer's own
  completion. Otherwise it waits until `CR_CLKGATECTL` (`0x0000`) & 3 is not 2 or bit 0 of
  `CR_CLKGATESTATUS` (`0x0008`) is clear, clears bit 4 of `sa9`, and, if bit 5 is still set,
  stores the word and returns: the deallocation has not arrived. If bit 5 is clear it completes.
- *Memory free (`0xeb4`).* Request `0x1` is acknowledged with `0x1` (`DPM_3D_MEM_FREE`). It clears
  bit 5 of `sa9`; if bit 4 is clear it completes, else it stores the word and returns. So the
  second of the two events completes the render, whichever it is.
- *Completion (`0xfd1`).* It clears bits 0, 3, 6, 7, 10, 11, 12 and 13 of `sa9`. If bit 6 of the
  old value (out-of-memory waiting for the 3D) was set it writes `CR_DPM_OUTOFMEM` = 1 and
  clears bit 14 (`0x157f`). A partial render (bit 1 of the old value) posts request `0x80000`
  (E160) and ends. For a render:
  1. with render flag `0x20` (`GET_VIS_RESULTS`) it accumulates the visibility counters
     (`0xecd`);
  2. `0xf45`, the syncs: the destination sync list is render details dword 56; the entry for the
     render-target index (list plus 8 plus 16 times the index) has its write-complete word set to
     write-pending plus 1. If render details dword 65 (the RT count) is not index plus 1, dword
     66 (the next index) becomes index plus 1 and nothing else of this list is done. On the
     last index it sets dword 66 to 0; with render flag `0x200` (`FRAG_FLAGS.TA3D_DEPENDENCY`)
     the dependency's write-complete word is set to its pending value plus 1 (dwords 63 and
     64); the 3D transfer-queue sync's read-complete word to its pending plus 1 (dwords 59 and
     60); each source sync's read-complete word likewise (dword 90 entries from dword 91); and
     the pairs counted by dword 81 and listed from dword 82 are stored (value at address,
     `ctl_status_info_3d`). Whatever the index, bit 0 of the RT status word of that index
     (RT data dword 12 plus 4 times the index) is then set;
  3. the context leaves the 3D queue (context dwords 14 and 15) and the render details leave the
     ready list (context dwords 10 and 11, linked through render details dwords 74 and 75) unless
     dword 66 is not zero, that is, unless more render targets remain; the context is appended
     to the 3D queue again if its ready list is not empty;
  4. `0xf9d`, the scene: for a non-last index it only raises `SW_EVENT` (a write of `0x4000` to
     `CR_EVENT_STATUS`). For the last it sets the RT data's dword 13 to (old with bits 6:5
     cleared) | `0x10` | ((render flags >> 14) << 12), that is, free again with the high
     flags copied up; with render flag `0x400` (`BIT10`) it adds 1 to dword 1 of the RT data
     set; it clears RT data dword 1; unless render flags `0xc` are set it clears the word render
     details dword 52 points at (`access_dev_vaddr`) and the RT data's slot (TA3DCtl dwords 20 and
     21); it clears the word that the first dword of the destination sync list points at; and
     raises `SW_EVENT`;
  5. the TA and 3D schedulers run again: request `0x40` is posted if bit 17 of `sa8` is set
     (E160), else `0x20000` if the TA queue is not empty, and the 3D schedule (`0x1035`) runs.

The HWPerf records in these handlers use type 2 for a transfer, 3 for the TA, 4 for a render and
8 for a partial render, with bit 28 set in the end record.

**Not shown.** What the clock-gating wait guards; what the visibility accumulation does; what the
high flags copied into the RT data word mean (E050 to E053 show the effect of the render flags on
images, not this word). Nothing here runs the firmware.
