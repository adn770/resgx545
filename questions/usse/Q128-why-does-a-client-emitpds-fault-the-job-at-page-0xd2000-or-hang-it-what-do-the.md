+++
id = "Q128"
question = "why does a client emitpds fault the job at page 0xd2000 or hang it, what do the s0, s1 and s2 operands of the started PDS program become (it saw ir0.0 2 or 3 whatever s2 was), and what in the control word's addend the PDS uses (0xFFF to 0x2000 left the fill's own value, 0x100 did not): why does the addend, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where 0x100 gives 3 or 2, and what does 0x800 do"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E488", "E513", "E520", "E1148"]
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

Noted 2026-11-09: near duplicate of Q145, not merged (Q128's question includes what the control
word's addend of an emitpds does (E520), which is Q145's). A merge or a fold decides which text
survives.

**Correction 2026-11-11:** Q145 is merged into this question (retired as folded into Q128; a fold is
not an answer), and its question is now a clause of the one above. Its question was: why does the
control word's addend of an emitpds, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where
0x100 gives 3 or 2, and what 0x800 does.

Its text: E520: 3 or 2 at 0 to 0x400 and at 0x4000 and above (24 of 27 probes outside the window),
0x403 at 0xFFF, 0x1000, 0x1001, 0x1010, 0x1100 and 0x2000 (12 of 12), 0x401 and 0x400 at 0x800 (2
probes) and 0x400 at 0x10 in one of its two probes, the 10 base probes interleaved among them
reading 3 or 2; every job faulted or hung. What is open: what the addend is (an offset the PDS adds
to an address, [infer]), the values between those run, what the 0x400 bit of the stored dword marks
(it was also read at the addend 0x10 once), and whether the 0x800 and 0x10 readings repeat. To
settle it: the addends 0x7FF to 0x801, 0x1FFF to 0x2001, 0x3FFF; a PDS program that stores more than
one input word. Q145's evidence (E520) and terms (none) were already in this question. Both files
noted on 2026-11-09 that a merge decides which text survives; this is that merge.

Narrowed 2026-11-18 (E1148, r36-n3, flagged): the firmware's own emitpds form (`.tasks.taske`, the
kernel's control word 0x01000100, its image's address >> 4 and 0), run from an EDM task of ours with
the kernel's PDS image (douta to attributes 0 and 2 with the values sa0 and sa2 hold, doutu our
entry 1), left no write of the started entry 1 within 200 ms in its one job, and the EDM's tick
stopped within that window with no BIF fault (post hoc); the kit's reset restored exact draws. So
from an EDM task the form neither faulted the bus as a client's did (E488) nor started our task
visibly. Not shown: whether the emitted program ran at all, or ran and its doutu did not start our
task (the design's [infer] U1 = U2 = 0, TRC 8 and code index in U0), or started it and entry 1
stopped before its first store; what stopped the tick; where an emitted douta lands (pa or sa) stays
open.
