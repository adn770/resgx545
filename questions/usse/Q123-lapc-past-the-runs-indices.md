+++
id = "Q123"
question = "does lapc reach instruction indices past the first 65536 words of a code base and the 18th bit of the program counter, and every index from 256 to 8191 in a fill?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E475", "E476", "E492", "E1098", "E1102"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E476: lapc lands exactly on each index that was run (a fill: 30, 31, 32, 34, 37, 45, 69 and 129,
backward targets and the call returns; placed programs: 0x2081, 0x20c8, 0x20fa, and the link plus 8
at five heap offsets: 0x200a, 0xa, 0xfe0a, 0xa, 0xa). E492 adds five placements, 0x2ff000,
0x1a0000, 0x3a8000, 0x4ff000 and 0x300008, whose links (0xfe02, 0x4002, 0x5002, 0xfe02 and 0x3) and
lapc landings fit the code base moving in steps of 0x80000 bytes (65536 instructions) with the
program at its offset inside the step: of the ten placements seven are not multiples of the step,
and no other power of two from 0x1000 to 0x1000000 fits all ten. A fill program is at most 256
words by sgxfive-test's check, and a placed program one page, 256 words by the same check, so an
index of 256 to 8191 in a fill, and a jump that crosses a 65536-word step (bits 16 and 17 of the
18-bit program counter, pclink keeps 18 bits: E475), were not run.

What is open: whether the counter carries into bits 16 and 17 as a plain 18-bit counter would, and
whether a long program is reached the same way; every index not listed above; and whether a step
that is not a power of two could fit the ten links (a power of two was fitted, nothing else was
tried). The second non-aligned placement that this question asked for is answered (E492). To settle
it: a program of two code bases' worth of nops across a 65536-word step, built in the code heap by
the host (not through sgxfive-test's 256-word check), with a lapc at its start to the last words,
and the same with a straight run across the step.

Narrowed 2026-11-15 by E1098 and E1102: the counter carries into bits 16 and 17 (E1098, held out
7 of 7) and a run reaches word 8100 of an 8192-word program; the 0x80000 step holds out at four new
placements where every other candidate step fails (E1102, 8 of 8), and a lapc and a ba land on ten
words drawn from 256 to 8191 (E1102, 10 of 10).
