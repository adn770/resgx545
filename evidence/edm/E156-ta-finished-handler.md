+++
id = "E156"
claim = "At TA_FINISHED (request 0x80, handler at 0x606) the EDM completes the TA command's sync and status words, raises SW_EVENT, and, when the kick carries LAST_KICK, flushes the tail pointer cache (unless render flag 0x8 is set) and queues the render details on the context's ready list and the 3D queue; a kick without LAST_KICK instead saves the tiling engine state and counts itself in the RT data set"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the handler at 0x606-0x6f4, the routines it calls (0x187c, 0x1942, 0x7fc, 0x1592, 0x159e, 0x1756), and the other callers of the render-queue routine; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_EVENT_STATUS.TA_FINISHED", "CR_EVENT_STATUS.SW_EVENT", "hw_pb_desc.allocated_page_count", "CR_DPM_PAGE_STATUS", "GEOM_FLAGS.LAST_KICK", "FRAG_FLAGS.NO_DEALLOCATE", "FRAG_FLAGS.NO_RENDER", "CR_TE_TPCCONTROL", "CR_TE_CONTEXT_STATE", "hw_render_context.pending_renders_head", "hw_render_context.pending_renders_tail", "hw_render_details.render_list_next_dev_vaddr", "hw_render_details.render_list_prev_dev_vaddr", "hw_render_details.te_context_state", "hw_rt_data_set.executed_count", "hw_render_context.ready_renders_head", "hw_render_context.ready_renders_tail", "hw_render_context.run_node_next_3d", "hw_render_context.run_node_prev_3d", "hw_render_context.submitted_commands", "cmd_ta.shared", "CR_DPM_FREE_CONTEXT"]
+++

**What was read.** Instruction numbers are indices in hex; `r0` is the TA command (TA3DCtl
dword 24), `r14` its RT data and `r6` its render details; `cmd_ta` dwords are the command's.
PDS #14's task `0x5d4` acknowledges `TA_FINISHED` (`0x2000`) and enters the handler (E154).

**Results.** The handler first looks at bits 9 and 10 of `sa8`, the TA state word. With both
clear (the normal case) it goes to `0x643`. With bit 9 set and bit 10 clear it sets bits 1, 5
and 10 of `sa8`, clears TA3DCtl dword 55, sets bit 0 of dword 54, posts request `0x40` and ends
(the terminate handler of E160 takes over). With bit 10 set (the TA was stopped by an
out-of-memory) it first runs a path of the partial-render sequence (E160: it sets bit 8 of
the RT data's dword 13 (bit 6 for a last kick), clears the DPM control state, flushes the tail
pointer cache and restores the thresholds), then falls into `0x643`.
From `0x643`:

1. It clears `sa8` bits 0, 2, 3, 4, 7, 8, 9 and 10 (the TA is idle).
2. It clears bit 0 of command dword 22 (`cmd_ta.shared`'s control flags); the TA pick (E161)
   tests that bit.
3. It reads command dwords 27 and 28 and, if dword 28 is not zero, stores dword 27 plus 1 at the
   address in dword 28 (the transfer-queue sync's read-ops-complete word).
4. It stores the upper half of `CR_DPM_PAGE_STATUS` (`0x0724`) in dword 5 of the structure that
   command dword 9 points at (`hw_pb_desc.allocated_page_count`).
5. It stores, for each of the pairs counted by command dword 23 and listed from command
   dword 70, the value at the address.
6. It writes `0x4000` (`SW_EVENT`) to `CR_EVENT_STATUS`.
7. With `GEOM_FLAGS.LAST_KICK` (command dword 1, bit 1), it sets bit 5 of the RT data's dword 13
   (`hw_rt_data.state`). If render flag `0x8` (`FRAG_FLAGS.NO_DEALLOCATE`, command dword 7)
   is clear, it also clears TA3DCtl dword 25 and writes `CR_TE_TPCCONTROL` (`0x0224`) =
   `0x40000000`, then polls bit 10 of `CR_EVENT_STATUS` and acknowledges it with `0x400`.
8. With command flags `0x5` (the first-kick flag `0x1` or flag `0x4`) it appends the render details
   to the context's pending-render list (context dwords 8 and 9, linked through render details
   dwords 74 and 75).
9. Unless the kick is a last kick with render flag `0x8` clear, it saves `CR_TE_CONTEXT_STATE`
   (`0x0274`) in render details dword 73. Unless the kick is a last kick, it also adds 1 to
   dword 1 of the RT data set (`hw_rt_data_set.executed_count`), and that is all it does for a
   kick without LAST_KICK, which goes straight to step 11.
10. For a last kick: with render flag `0x1` (`FRAG_FLAGS.NO_RENDER`) it first frees the scene's
    memory at `0x187c` (the routine releases the RT data's DPM slot and the loaded PB, writes
    `CR_DPM_FREE_CONTEXT` = 1 and `CR_TE_TPCCONTROL` = `0x80000000`, and waits for bits 24 and
    11 of `CR_EVENT_STATUS`). Then, whether or not it freed, it calls the render-queue routine
    at `0x1942` with the context and the render details. That routine takes the render details
    off the pending list, appends them to the context's ready list (context dwords 10 and
    11) and, only if that list was empty, appends the context to the 3D queue (`sa17`, `sa18`,
    linked through context dwords 14 and 15). With command flag `0x1000` (command dword 1) it
    also clears HostCtl dword 16 before this.
11. It posts the 3D scheduler request (`0x40000`) if the transfer or 3D queue holds a context,
    then runs the TA queue step at `0x7fc`: it adds command dword 0 (the command size) to the
    context's CCB read offset, modulo 64 KiB (`0xffff` mask, so a 64 KiB TA CCB), and subtracts
    1 from context dword 5 (`hw_render_context.submitted_commands`). The context leaves the
    TA queue, is put back at its tail if it has more kicks or pending renders, and the TA
    scheduler request (`0x20000`) is posted if the queue is not empty. Last, if `sa9` has bit 12
    set and bit 13 clear, it sets bit 13.

The render-queue routine has four callers: this handler (`0x6b9`), the abort path of the TA pick
(`0x8a1`) and two places in the cleanup code (`0x3d7`, `0x434`).

**Not shown.** That the writes of step 7 mean "scene closed" and "tail pointer cache flushed" is a
reading of the names; the bits and registers are given as the code shows them. Which of these
steps a run of the hardware needs is not shown; E051 to E053 show the effect of LAST_KICK and
of the flags on rendered images, not these writes.
