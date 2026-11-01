+++
id = "E161"
claim = "The EDM's TA pick (0x6f5-0x7b0) takes a context's next TA command from its CCB only when the context has a counted kick and is not suspended, the command's READY bit is set, its transfer-queue sync is complete, its RT data is free when the kick is a first kick or has flag 0x4, and (when another context is queued) its destination and source syncs are complete; it applies a PB threshold update on the way and starts the kick only when no TA is running"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the pick from 0x6f5 to 0x7b0 and the abort path it enters at 0x80c; fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CONTEXT_FLAGS.SUSPEND", "GEOM_FLAGS.TA3D_DEPENDENCY", "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.PB_THRESHOLD_UPDATE", "PB_FLAGS.THRESHOLD_UPDATE", "cmd_ta.ta_threshold", "cmd_ta.global_threshold", "cmd_ta.shared", "cmd_ta.hw_rt_data_dev_vaddr", "hw_rt_data.state", "FRAG_FLAGS.ABORT", "hw_render_context.submitted_commands"]
+++

**What was read.** Instruction numbers are indices in hex. The pick runs for request `0x20000`
(E154); the command words are the TA command's (`r1` below is the command).

**Results.**

- *Gates.* It returns at once if `sa8` bit 2 or bit 18 is set (bit 18 is cleared by the
  render-context cleanup, E167), or if `sa10` bits 1:0 are set (a cleanup is pending).
- *Walk.* It goes through the TA queue from the head (`sa15`), one queue index at a time, context
  by context (links in context dwords 12 and 13). While a TA runs (bit 0 of `sa8`) it still looks
  at the queue, but only the contexts of an index below the running one (`sa4`).
- *Per context.* Each condition failing moves it to the next context:
  1. context dword 5 (`submitted_commands`) is not 0, and bit 4 of the context's flags (dword 0,
     `CONTEXT_FLAGS.SUSPEND`) is clear;
  2. the command is at the context's CCB base (dword 3) plus the read offset held in the CCB
     control (dword 4 points at it; offset in bytes);
  3. bit 0 of command dword 22 (`cmd_ta.shared`, READY) is set;
  4. the transfer-queue sync of the command (dwords 25 to 28) is complete: the word its dword 26
     points at equals dword 25 and the one dword 28 points at equals dword 27, unless the first
     pointer is zero;
  5. with command flag `0x400` (`GEOM_FLAGS.TA3D_DEPENDENCY`), the write-complete word the TA to
     3D dependency (dwords 68 and 69) names equals its pending value;
  6. with command flags `0x5` (first kick, or flag `0x4`), the RT data (command dword 17) has bit
     4 of its dword 13 set, that is, no render on it is outstanding;
  7. the destination sync (command dword 15, if not zero) and every source sync (the count in
     dword 33, 4 dwords each from dword 34) are complete. These two checks (`0x760`-`0x78e`) are
     skipped when the TA queue holds no context other than this one (the loop at `0x744` looks
     for a second context) **[as read]**;
  8. with command flag `0x2000` (`GEOM_FLAGS.PB_THRESHOLD_UPDATE`): if the 3D is running (bit 0
     of `sa9`) the pick ends without kicking; otherwise it copies command dwords 10 to 13
     (`ta_threshold`, the ZLS threshold, `global_threshold`, the PDS threshold) to dwords 10 to
     13 of the context's PB descriptor and sets bit 1 of the PB's flags
     (`PB_FLAGS.THRESHOLD_UPDATE`); the TA kick applies it (E159, step 4).
- *Kick.* If a TA is running (bit 0 of `sa8`) it ends. Otherwise, if bit 6 of the RT data's
  dword 13 (`hw_rt_data.state`, aborted) is set, or render flag `0x2` (command dword 7, abort)
  is set, it takes the abort path at `0x80c`: the command completes (the transfer-queue
  read-ops sync, the TA status pairs, `SW_EVENT`, the CCB advance) without running. Else it
  enters the TA kick at `0x8e9` with the context and the queue index.

**Not shown.** Why the syncs are tested only when a second context is queued; what the
bit-4 and bit-18 gates mean beyond their setting sites; what happens to a command whose
conditions never come true (the context stays on the queue). Nothing here runs the firmware.
