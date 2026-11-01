+++
id = "Q052"
question = "what do .skipinv, .syncs, .nosched and the other scheduling flags change, and how many instructions after a write can a dependent instruction read the result, with or without an interlock?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E100", "E104", "E111", "E113", "E124", "E371", "E470", "E472", "E475", "E478"]
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

Narrowed in 11.23, for `ima32` only in part: four dependent `ima32` in a row, each reading the one
before it in the next instruction, give the exact chain (10 of 10: E470), and the compare formula
reads an `ima32`'s result two and three instructions later, with and without three `nop`s after it
(64 of 64 pairs, and 16 of 16 for the unsigned compare with the `nop`s: E472). A `mov pclink, rN` is
seen by a `lapc` in the very next instruction, with or without `.nosched` on either (19 of 19:
E475). Not run for `ima32`: `.nosched` on the writer, and any distance beyond three.

Narrowed in 11.24, for loads read by a `stad`: the register of a `ldad` still holds its old value
when a `stad` reads it with no `wdf` after 0, 1, 2, 4, 8, 16 or 32 `nop`s (one load) and after 0 or
16 (four loads), 9 of 9 cases (E478), so no interlock was seen for that reader and the result was
seen only after the `wdf` that counts it; a `stad` and a later `ldad` of the same dword, all
instances storing the same value to it, return the stored value with no `idf` (16 cases, E481;
Q134). Not run: a load read by an ALU instruction (the interlock of that reader might differ), a
load read more than 32 instructions on with no `wdf`, a load overwritten by a later write to its
register, and the time a load takes.

What is open (usse_isa.md §8, items 3 and 7): what `.syncs` and `.nosched` change (timing, with
the reads correct either way), whether the hardware stalls a reader or the result is ready, loads
read by readers other than `stad`, and the other writers (the texture unit, dual issue).

To settle it: the loop of probes/usse/loop-short.toml with a dependent chain against an
independent one, with and without `.nosched`, timed; `.syncs` on a multi-task fill with the tasks'
stores compared.
