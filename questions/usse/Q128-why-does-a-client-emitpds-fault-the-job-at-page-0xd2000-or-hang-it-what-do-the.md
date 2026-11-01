+++
id = "Q128"
question = "why does a client emitpds fault the job at page 0xd2000 or hang it, what do the s0, s1 and s2 operands of the started PDS program become (it saw ir0.0 2 or 3 whatever s2 was), and whether the addend matters (the addend 0x1000 once left the no-emit value)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E488"]
terms = []
+++

E488: in 24 of 24 client fills that executed an emitpds (a copy's shader, one instance emitting),
the PDS program the emit named ran (18 of 19 ir0.0 probes) and the job then faulted with `BIF fault
0xd2000` (22 times), 0x92000 once (sideband 0x1) or hung (two emits in a row). The started
program's ir0.0 was 3 (16 probes) or 2 (2), ir0.1 2, ir1.0 and ir1.1 0, and none of s2 = 0, 1,
0xFFFFFFFF, 0xE17D0001 appeared in ir0 or ir1; E146's reading of s2 as ir0 is not supported.

What is open: where the fault's page (0xd2000) comes from (the emitted program's data fetch, its
doutu, or a PDS state a client task lacks), what ir0 of a started program is (a task counter?), what
s2 becomes (none of ir0.0, ir0.1, ir1.0, ir1.1 of the program), and what in the control word's low
bits (0x100 started the program; 0x1000 once left the no-emit value, one probe and one repeat
outside the data, in faulting jobs) the PDS uses. To settle it: an emitted program that stores more
than one input word (not 2 to 4 dwords: E144; 5 or more, or one store per word) and the other PDS
registers, with s0 varied bit by bit and a program placed where page 0xd2000 is mapped; for the
EDM's own use of the operands, phase 12's firmware.
