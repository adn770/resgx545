+++
id = "E157"
claim = "The EDM's TA kernel-CCB handler (kick address 0x11d, instructions 0x11d-0x139) reads only the render context named in command data dword 1: it counts the kick in the context's submitted-commands word, queues the context on the TA queue if it was idle and had no pending render, and ends in the shared tail that posts the 3D and TA scheduler requests; the command's own address is never passed"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the handler (E012 lists its kick address), the shared tail at 0x161 and the posting routines at 0x1592 and 0x159e; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["hw_render_context.submitted_commands", "hw_render_context.pending_renders_head", "hw_render_context.priority", "hw_render_context.run_node_prev_ta", "hw_render_context.run_node_next_ta", "kernel_ccb", "command.data"]
+++

**What was read.** Instruction numbers are indices in hex. A kernel CCB handler gets the command's
words in `r4` to `r11` (E013); the handler's only use of them is `r7`, command data dword 1.

**Results.**

- It takes `r7` as the render context. It adds 1 to context dword 5
  (`hw_render_context.submitted_commands`). If the old value was not zero it is done: the context
  is already queued.
- Otherwise, if context dword 8 (`hw_render_context.pending_renders_head`) is not zero, it is
  done too: the context is still on the queue for a pending render.
- Otherwise it appends the context to the TA queue of its priority (context dword 1): the
  list's tail is `sa16` indexed by the priority and the head `sa15`; the head is set only if the
  tail was empty; the links are context dwords 12 and 13
  (`hw_render_context.run_node_prev_ta`, `_next_ta`).
- It reads no other word of the command and no word of the TA command in the context's CCB. The
  TA command is found later, by the TA pick, from the context's CCB base and read offset (E161);
  the host never passes its address.
- The handler then goes to the tail that the kernel CCB handlers share (`0x161`): if `sa8` bit 6
  is set it clears the bit and writes `CR_DPM_OUTOFMEM` = 1; it posts request `0x40000` when the
  transfer or 3D queue holds a context and request `0x20000` when the TA queue holds one
  (E154), and ends the task. The TA pick runs from the `0x20000` request.

**Not shown.** What the host writes in the command's other data dwords: the handler ignores them.
That one kernel command stands for one TA command waiting in the context's CCB is a reading of
the counter (the handler adds one per command and the TA completion subtracts one, E156); no run
of the TA kick on the hardware is in this record.
