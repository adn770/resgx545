+++
id = "Q195"
question = "what do the narrow memory forms do that the 11.36 fills did not run: a register or negative offset, the pre- and post-increment forms, .fetchN and .repeatN, staw at an odd address, other banks and flags, and in a firmware task"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E598", "E599"]
terms = []
+++
E598 and E599 (a client pixel task, 48 jobs): `ldab` and `ldaw` with an immediate offset read
zero-extended elements of their size, an unaligned address reads the bytes there, `stab` changes
only its own byte at any address, `staw` only its own halfword at an even one. Not run:
`ldab`/`ldaw`/`stab`/`staw` with a register offset (the stride times index rule of usse_isa 7.10 for
`ldad` is not shown for them), a negative offset, the pre- and post-increment forms (what is written
back), `.fetchN` and `.repeatN` on a narrow access, `staw` at an odd address (does it split, land at
the aligned halfword or nowhere, as the plain `stad` lands nowhere), a destination in `pa` or a
source in another bank, the flags `.bpcache` and `.bypassl1`, and every one of these in a firmware
task, where the verifier refuses the four forms (unknown form) so a verifier row comes first.

To settle it: the same table over each of those forms, one probe each, in the fill as E598 and E599
and then as firmware tasks of ours once the loader accepts the rows.
