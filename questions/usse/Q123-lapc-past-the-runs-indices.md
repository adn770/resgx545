+++
id = "Q123"
question = "does lapc reach instruction indices past the first 65536 words of a code base and the 18th bit of the program counter, and every index from 256 to 8191 in a fill?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E475", "E476"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E476: lapc lands exactly on each index that was run (a fill: 30, 31, 32, 34, 37, 45, 69 and 129,
backward targets and the call returns; placed programs: 0x2081, 0x20c8, 0x20fa, and the link plus 8
at five heap offsets: 0x200a, 0xa, 0xfe0a, 0xa, 0xa), and the code base moves in steps of 0x80000
bytes (65536 instructions) with the program at its offset inside the step, which five placements
show with one non-aligned offset (0x1ff000) besides 0x10000. A fill
program is at most 256 words by sgxfive-test's check, and a placed program one page, 256 words by
the same check, so an index of 256 to 8191 in a fill, and a jump that crosses a 65536-word step
(bits 16 and 17 of the 18-bit program counter, pclink keeps 18 bits: E475), were not run.

What is open: whether the counter carries into bits 16 and 17 as a plain 18-bit counter would, and
whether a long program is reached the same way; every index not listed above; and whether the
step is 0x80000 for a second non-aligned placement (0x2ff000 or 0x1a0000, not run). To settle it:
a program of two code bases' worth of nops across a 65536-word step, built in the code heap by the
host (not through sgxfive-test's 256-word check), with a lapc at its start to the last words, and
the same with a straight run across the step.
