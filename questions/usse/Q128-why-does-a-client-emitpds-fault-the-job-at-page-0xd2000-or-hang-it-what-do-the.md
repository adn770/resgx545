+++
id = "Q128"
question = "why does a client emitpds fault the job at page 0xd2000 or hang it, what do the s0, s1 and s2 operands of the started PDS program become (it saw ir0.0 2 or 3 whatever s2 was), and what in the control word's addend the PDS uses (0xFFF to 0x2000 left the fill's own value, 0x100 did not)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E488", "E513", "E520"]
terms = []
+++

E488: in 24 of 24 client fills that executed an emitpds (a copy's shader, one instance emitting),
the PDS program the emit named ran (18 of 19 ir0.0 probes) and the job then faulted with `BIF fault
0xd2000` (22 times), 0x92000 once (sideband 0x1) or hung (two emits in a row). The started
program's ir0.0 was 3 (16 probes) or 2 (2), ir0.1 2, ir1.0 and ir1.1 0, and none of s2 = 0, 1,
0xFFFFFFFF, 0xE17D0001 appeared in ir0 or ir1; E146's reading of s2 as ir0 is not supported.

Narrowed in 11.27: the emit was executed by a quad of four lanes, not one instance (E513: a test of
`pa0` selects a whole 2 x 2 quad). The addend matters (E520, 39 probes, all faulted (37) or hung
(2)): 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 left the fill's own 0x403 in 12 of 12 probes,
in two orders, where 0x100 read 3 or 2 (11 of 11), 0x800 read 0x401 and 0x400, and 0x10 read 3 once
and 0x400 once; Q145 asks why.

What is open: where the fault's page (0xd2000) comes from (the emitted program's data fetch, its
doutu, or a PDS state a client task lacks), what ir0 of a started program is (a task counter?), what
s2 becomes (none of ir0.0, ir0.1, ir1.0, ir1.1 of the program), and what the control word's low bits
are for beyond the window of E520 (0x100 started the program; the PDS uses the addend). To settle
it: an emitted program that stores more than one input word (not 2 to 4 dwords: E144; 5 or more, or
one store per word) and the other PDS registers, with s0 varied bit by bit and a program placed
where page 0xd2000 is mapped; for the EDM's own use of the operands, phase 12's firmware.
