+++
id = "Q049"
question = "does the firmware or the hardware ever read dword 7 (offset 0x01c) of the render context, which the EDM dataflow reaches on no path?"
unit = "render"
phase = 11
evidence = ["E013", "E021", "E156", "E165", "E361", "E448"]
terms = ["hw_render_context.ready_renders_tail", "hw_render_context.run_node_prev_3d", "hw_render_context.run_node_next_3d", "hw_transfer_context.pd_dev_paddr"]
+++

The main part is answered (E361, two runs): with render context dword 7 set to 0xdeadbeef or to
the background object's address at the first kick, a render, a scene of three kicks, a render
that overflows its parameter buffer and the context's cleanup come out as their unpoked controls,
nothing faults, the scratch primitive block the kernel points the word at reads the same, and the
word keeps its value through later kicks. Our kernel and the closed client both put the address
of a 0x40-byte parameter-heap object there (E323).

Narrowed by E448 (a second render context in the VM, on a PB of its own or on the first's, the
second job submitted before the first was waited for, dword 7 poked in either): the word set to
0xdeadbeef or 0xffffffff in the first context, the second or both changes nothing on the paths a
second context may add (the EDM's switch between the two contexts' jobs, a PB swap and one PB
shared; none is shown to occur, the overlap in the firmware was not timed), and stays as set; 69
renders of each context were exact.

What is open: a context switch in the middle of a TA (no run interrupts one), contexts of different
VMs, and the dataflow's 379 accesses through a base of unknown origin, none tied to the word.

To settle it: a TA interrupted by a context switch (Q068's route, a path of the fork not yet
written), and the dataflow's base found.
