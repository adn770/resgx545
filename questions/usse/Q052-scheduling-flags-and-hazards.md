+++
id = "Q052"
question = "what do .skipinv, .syncs, .nosched and the other scheduling flags change, and how many instructions after a write can a dependent instruction read the result, with or without an interlock?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E100", "E104", "E111", "E113", "E124", "E371"]
terms = []
+++

An instruction with .skipinv reaches exactly the covered pixels of a triangle, one without it also
some uncovered ones (E104), and every instance of a touched quad runs such an instruction (E111);
how many helper pixels' o0 lands follows the shader's length (E113). bexception hangs a fill's pixel
task with or without .nosched (E100). A counted loop's time is linear in its count modulo 65536
(E124). usse_isa.md §8 records that .syncs hangs a fill's task.

Narrowed by E371: a register written by `mov`, `or`, `fmad`, `frcp` or `fexp` reads as the result
in the very next instruction and at every distance to 8, with or without `.nosched` on the writer
(230 cases, every pixel), so for these writers the flag does not change correctness.

What is open (usse_isa.md §8, items 3 and 7): what `.syncs` and `.nosched` change (timing, with
the reads correct either way), whether the hardware stalls a reader or the result is ready, and
the other writers (loads, the texture unit, dual issue).

To settle it: the loop of probes/usse/loop-short.toml with a dependent chain against an
independent one, with and without `.nosched`, timed; `.syncs` on a multi-task fill with the tasks'
stores compared.
