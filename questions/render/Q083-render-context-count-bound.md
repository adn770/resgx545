+++
id = "Q083"
question = "what bounds TA/3D control block dword 49 at 15 values, and is it a count of render contexts or an index the EDM gives each one?"
unit = "render"
phase = 11
evidence = ["E303", "E314", "E315", "E316", "E319"]
terms = ["ta3d_ctl.render_context_count"]
+++

Dword 49 of the TA/3D control block moves by one at each render context's first kick, whatever
its renders, and not at its later kicks or its cleanup; a first kick that faults at its PB load has
already moved it (E314, E316, E319, one run each). After a reset it reads 0, and 1 after the next
context's first kick (E303, E315). It runs from 0 to 0xe and goes from 0xe to 0 at a
context's first kick with no reset, once in each of two tables (E314, E316), never reading 0xf.
So it is a count or index modulo 15, not a count of the contexts since the boot.

What is open: what bounds it at 15 (a field of four bits whose 0xf is reserved, a table of 15
entries, or a compare in the first kick's code) and whether anything reads it, for the contexts
the EDM keeps or for the DPM.

To settle it: read the first kick's code around the word's update for the compare that wraps it,
and on the hardware read dword 49 with two contexts alive at once over a wrap, to see whether a
live context keeps or loses anything there.
