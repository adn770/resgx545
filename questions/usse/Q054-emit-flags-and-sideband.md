+++
id = "Q054"
question = "what do #incp, .cut and .tasks/.taske do on the emits?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E030", "E102", "E106", "E239", "E269", "E376", "E488"]
terms = ["SIDEBAND.PACKMODE", "SIDEBAND.BIT9", "SIDEBAND.BITS8_6", "SIDEBAND.DITHER"]
+++

Bit 42 (.twopart) is needed on emitvcbvtx and not on emitmtevtx (E102), and on the state task's
emits it changes nothing (E106). In the end-of-tile emit's sideband the pack mode selects the
stored format (E030), bit 9 (`TILERELATIVE` in the specs) clear hangs the job, on a one-tile
target too (E239), bits 8:6 select the channel of a one-channel mode, bit 10 dithers the modes
that drop colour bits, bit 11 faults the job and bit 12 stores values of no colour (E269). The
emitpix2 instruction carries sideband bits 13:0 only.

Narrowed by E376: on the triangle's vertex program, incp 1 to 3 on emitvcbvtx or emitmtevtx draws
the triangle as with 0, and .cut on emitmtevtx hangs the job (two runs).

Narrowed in 11.24 (E488), for `emitpds` in a client fill shader: `.tasks`, `.taske`, both, neither,
`.freep`, `.nosched`, `#incp` 1 to 3 and the sideband 0x1, 0x200 and 0x2000 each changed nothing
seen of whether the PDS program the emit names ran (the 19 probes that store `ir0.0`: it ran in 18,
and with the addend 0x1000 the dword held the no-emit value once: one probe, twice with a repeat
outside the data, in jobs that faulted), and every job with an emit then faulted at page 0xd2000 (22
of 24; 0x92000 once) or hung (once, two emits in a row), 24 of 24 (Q128). The flags were run one at
a time, each on one probe, and the fault may hide an effect after the emit.

What is open (usse_isa.md §8, item 5): what incp counts, .cut on a program that emits more than
one primitive, .tasks/.taske (emitpds: what they do once the emit does not end the job in a
fault). Sideband bits 11 and 12 are Q046's and bit 9 is Q074.

To settle it: a vertex program that emits two primitives with .cut between them, and emitpds with
.tasks/.taske in the state task, the parameter buffer dumped.

Narrowed 2026-11-12 (round 6 housekeeping, decision R6-1 a): the clause on sideband bits 11 and
12 (bit 11 faults the job, bit 12 stores values of no colour, E269, E383) was in this question and
in Q046; it stays in Q046, which sweeps the pack modes, and leaves this one, which asks about the
emit flags. What the end-of-tile emit's sideband pack mode and bits 8:6, 9, 10 and 13 do is in the
paragraphs above.
