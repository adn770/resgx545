+++
id = "Q056"
question = "where does a write to destination bank 6 with value 0 (printed i.) land?"
unit = "usse"
phase = 11
evidence = ["E091", "E147", "E366"]
terms = []
+++

Answered (E366): a write to destination bank 6 with neither index bit set (numbers 0, 4, 8, 16, 64
and 124, all printed `i.`) changes no register a fill reads: r0-r25, i0-i2, i.l and i.h and the
pixel o0 read as without it (one run of each number), and pa0-pa15 and sa0-sa31 too for numbers 0,
4 and 64 (three runs each; 8, 16 and 124 had one run, with pa and sa not read), while numbers 1 to
3 write i.l, i.h and both. The marker appears in none of o0-o7. The simulator takes it as writing
nothing for those six numbers and stops on any other number with the low two bits clear.

What is left: state no form of ours reads back (the MOE state, the global bank's write path),
pa and sa for numbers 8, 16 and 124, and the numbers not run.
