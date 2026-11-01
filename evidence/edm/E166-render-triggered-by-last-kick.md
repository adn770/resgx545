+++
id = "E166"
claim = "In the firmware the render is queued at TA_FINISHED by a TA command with flag 0x2 (command dword 1, bit 1: the last kick), not by render flag 0x400, which the only code that tests it uses for a completion count; and a command that carries both the first-kick flag 0x1 and flag 0x2 runs the first-kick actions at its TA kick and the last-kick actions at its TA finished through the same code as two commands would"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: every test of command dword 1 bit 1 on the TA-finished and abort paths, a scan for every test of bit 10 of the render flags (command dword 7, render details dword 53), and the TA kick (E158, E159) and TA-finished (E156) paths followed with flags 0x1 and 0x3; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK", "FRAG_FLAGS.BIT10", "CR_TE_CONTEXT_STATE", "hw_render_details.te_context_state", "hw_rt_data_set.executed_count"]
+++

**What was read.** Instruction numbers are indices in hex. The TA command's flags are its dword 1
(`GEOM_FLAGS`), the render flags its dword 7 (copied to render details dword 53 by the TA kick,
E158).

**Results.**

- *The trigger.* The TA-finished handler (E156) tests bit 1 of command dword 1 (`LAST_KICK`) at
  `0x676` and `0x677`. The render-queue routine (`0x1942`) runs from it only when that bit is set
  (with render flag `0x8` clear or set), at `0x6b9`. The abort path of the TA pick tests the same
  bit (`0x874` and `0x875`) and queues the render details at `0x8a1` only for a last kick. A kick
  without the bit counts itself in dword 1 of the RT data set and posts the schedule (E156); it
  queues nothing, so its render details stay on the context's pending list.
- *Render flag `0x400`.* The only test of bit 10 of the render flags that I found is at `0xfae`,
  in the scene routine of the completion (E164), where it adds 1 to dword 1 of the RT data set. No
  other instruction tests it: the TA pick, the TA kick, the TA-finished handler and the 3D kick
  copy or test other bits (`0x1`, `0x2`, `0x8`, `0x10`, `0x20`, `0x80`, `0x100`, `0x200`, `0xc`,
  and the bits from 14 up, which are copied into the RT data's state word).
- *One command with both flags.* With flags `0x3`: the TA kick does the first-kick actions
  (reset `TA_RESET`, the DPM clear and OTPM reset of E158, the RT status words zeroed); the
  TA-finished handler appends the render details to the pending list (flags `0x5` test),
  then, for the last kick, queues the render, and the queue routine takes them off the
  pending list in the same pass. It does not save the tiling engine state (E156, step 9) unless
  render flag `0x8` is set. Nothing in the path needs the first kick and the last kick to be
  separate commands **[infer]**: no test compares the two flags or the command's position in
  the CCB.

**What it shows.** A render exists in the firmware when a TA command with flag `0x2` finishes, not
because of a render flag. The hardware records E051 and E052 agree: a kick without the last-kick
flag leaves its render waiting, and a scene of several kicks is rendered by the one that ends it.
That one command with the first and last flags works on the hardware is not shown here; the
reading above is from the code.

**Not shown.** What a client's command stream does at the TA (the vertex data master's
terminate and state words are not touched by the firmware); that the firmware never queues a render
by another path, which a scan for the queue routine's callers (E165) supports for the four callers
found but does not prove for code reached by a computed branch.
