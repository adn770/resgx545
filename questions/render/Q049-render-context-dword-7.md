+++
id = "Q049"
question = "does the firmware or the hardware ever read dword 7 (offset 0x01c) of the render context, which the EDM dataflow reaches on no path?"
unit = "render"
phase = 11
evidence = ["E013", "E021", "E156", "E165", "E361"]
terms = ["hw_render_context.ready_renders_tail", "hw_render_context.run_node_prev_3d", "hw_render_context.run_node_next_3d", "hw_transfer_context.pd_dev_paddr"]
+++

The main part is answered (E361, two runs): with render context dword 7 set to 0xdeadbeef or to
the background object's address at the first kick, a render, a scene of three kicks, a render
that overflows its parameter buffer and the context's cleanup come out as their unpoked controls,
nothing faults, the scratch primitive block the kernel points the word at reads the same, and the
word keeps its value through later kicks. Our kernel and the closed client both put the address
of a 0x40-byte parameter-heap object there (E323).

What is open: whether a path not run here reads it (a context switch, a PB swap, two contexts on
one PB), and the dataflow's 379 accesses through a base of unknown origin, none tied to the word.
