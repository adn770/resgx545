+++
id = "Q049"
question = "does the firmware or the hardware ever read dword 7 (offset 0x01c) of the render context, which the EDM dataflow reaches on no path?"
unit = "render"
phase = 11
evidence = ["E013", "E021", "E156", "E165"]
terms = ["hw_render_context.ready_renders_tail", "hw_render_context.run_node_prev_3d", "hw_render_context.run_node_next_3d", "hw_transfer_context.pd_dev_paddr"]
+++

The forward dataflow over the whole microkernel records every structure word it reaches through a
typed pointer, and the render context is one of the typed structures (E013). Of the context's first
seventeen dwords it reaches those at offsets 0x000, 0x004, 0x00c to 0x018, 0x020 to 0x028, 0x030,
0x034 and 0x040 (edm_dataflow.md); it reaches none at 0x008, 0x01c, 0x02c, 0x038 or 0x03c. Yet the
firmware uses 0x02c, 0x038 and 0x03c: they are the ready list's tail and the links of the 3D queue
(E156, E165), and the dataflow knows them only as pointer types it is given. The same dataflow
counts 379 memory accesses through a base of unknown origin (E013). Not being reached is therefore
no proof that the firmware never reads a word, and no record gives dword 7 a use or a meaning.

Dword 2 (0x008) is not asked here because it has a candidate: the GPL kernel writes a context's page
directory at an offset the client names, and in the transfer context that offset is 0x008, the
directory its transfers run under (E021), a word the dataflow reaches no access to either. Whether
the render context holds its page directory there is a question of its layout, not of this run.

To settle it: poison the word in a render context, with 0xdeadbeef and with the address of a page of
the job's scratch buffer, and run a first kick, a scene of several kicks, a render that overflows
its parameter buffer into partial renders, and the context's cleanup, two runs each. Compare every
image, fault and hang with the unpoisoned control, and read the scratch page after each job. In the
dataflow, list the unresolved accesses whose base could be a render context: a load at offset 0x01c
among them is where to look.
