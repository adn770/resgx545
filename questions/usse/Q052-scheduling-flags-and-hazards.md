+++
id = "Q052"
question = "what do .skipinv, .syncs, .nosched and the other scheduling flags change, and how many instructions after a write can a dependent instruction read the result, with or without an interlock?"
unit = "usse"
phase = 11
evidence = ["E100", "E104", "E111", "E113", "E124"]
terms = []
+++

An instruction with .skipinv reaches exactly the covered pixels of a triangle, one without it also
some uncovered ones (E104), and every instance of a touched quad runs such an instruction (E111);
how many helper pixels' o0 lands follows the shader's length (E113). bexception hangs a fill's pixel
task with or without .nosched (E100). A counted loop's time is linear in its count modulo 65536
(E124). usse_isa.md §8 records that .syncs hangs a fill's task.

What is open (usse_isa.md §8, items 3 and 7): what .syncs and .nosched change when set or clear,
whether the flags matter for correctness or only for performance, how many instructions a result
takes to become readable and whether the hardware interlocks a read that comes too early.

To settle it: on the laptop, a fill whose shader writes a register and reads it back 0 to 8
instructions later, each read stored to memory, with and without .nosched on the writer, ten runs;
the same writer timed over a long loop; .syncs on a multi-task fill with the tasks' stores compared.
