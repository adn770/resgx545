+++
id = "E165"
claim = "There is no 3D command: the kernel CCB's kick table (E012) has no render handler, the render details reach the 3D queue only through the render-queue routine (called from the TA-finished handler on a last kick, the abort path of the TA pick and two cleanup sites), and the 3D schedule (request 0x40000, routine 0x1035) tries the transfer queue first and then the 3D queue, checks the ready render details' syncs before kicking, and returns to its caller after the first kick"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the schedule at 0x1035-0x105c, the 3D pick at 0x105d-0x112a, the head of the transfer pick at 0x12dc, the render-queue routine at 0x1942 and every instruction that writes the 3D queue heads; fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset, a post-increment fetch starts at the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["hw_render_context.ready_renders_head", "CONTEXT_FLAGS.SUSPEND", "FRAG_FLAGS.NO_RENDER", "FRAG_FLAGS.ABORT"]
+++

**What was read.** Instruction numbers are indices in hex. The 3D queue is `sa17` (head) and `sa18`
(tail), one list per queue index, linked through context dwords 14 and 15 (E154); a context's ready
list starts at its dword 10 (E156). The render details are `rd`.

**Results.**

- *No command.* The kernel CCB's kick table (E012) names handlers for the TA, the transfer,
  POWER, CONTEXTSUSPEND, CLEANUP, GETMISCINFO, PROCESS_QUEUES and SETHWPERFSTATUS, none for a
  render. The only code that writes a 3D queue head or tail is the render-queue routine at `0x1942`
  (which also moves the render details from the pending list to the ready list, E156), the
  schedule's own unlinking and relinking when it kicks or completes a render (`0x10eb`-`0x1110`,
  `0x12b0`-`0x12c7`) and the completion (`0xfed`-`0x1016`, E164). The render-queue routine is
  called from the TA-finished handler (`0x6b9`, last kick only, E156), the abort path of the TA
  pick (`0x8a1`) and two sites of the cleanup code (`0x3d7`, `0x434`). So a render is queued by
  the EDM, at the end of a scene's last TA kick, and by nothing the host sends.
- *Schedule (`0x1035`, request `0x40000`).* It returns at once if `sa10` bits 1:0 are set (a
  cleanup is pending), or `sa9` has bit 1 (partial render) or bit 3 set, or the 3D is running
  (bit 0) and a transfer is the job (bit 2). While a render runs it considers only queue indices
  below the running one (`sa6`). For each index it calls the transfer pick (`0x12dc`, E015)
  and then the 3D pick (`0x105d`). The kick routines of both replace the link register by the
  schedule's caller, so the first kick ends the whole schedule, and the 3D pick is not
  reached after a transfer kick.
- *3D pick (`0x105d`).* It takes the head of the queue for the index (`sa17`) and walks the
  contexts through context dword 15. For each context:
  1. a context whose flags have bit 4 set (`CONTEXT_FLAGS.SUSPEND`) is skipped, unless it is
     the TA's current context (TA3DCtl dword 27) and bit 11 of `sa8` (out-of-memory pending) is set;
     then its render may free memory;
  2. the render details are the first of the ready list (context dword 10), the RT data is
     render details dword 55 and the render-target index dword 66;
  3. the destination sync list (dword 56) entry for the index, at the list plus 8 plus 16
     times the index, must be complete in both words, unless the list address is 0;
  4. the 3D transfer-queue sync (dwords 57 to 60) must be complete, unless its first pointer is 0;
  5. every source sync (the count in dword 90, 4 dwords each from dword 91) must be complete.
  If one is not, it goes on to the next context.
- *Kick or complete.* With the checks passed, if bit 6 of the RT data's dword 13 (aborted) is set
  or render flags `0x3` (`NO_RENDER` or `ABORT`, render details dword 53) are set, the render
  details are completed without rendering: the HWPerf record, the removal from the ready list
  and the 3D queue (as in E164), the syncs and the scene routines (`0xf45`, `0xf9d`), the
  scheduler requests, then the schedule runs again. Otherwise the 3D kick (E163) starts.

**Not shown.** The path at `0x10be`-`0x10d6`, which, when `sa9` bits 6 and 14 are set (an
out-of-memory waiting for the 3D), may choose the TA's own context and its ready render
details instead of the one found; the transfer pick's conditions; that nothing outside the
firmware queues a render (the host never writes the queues, but no run tests it).
