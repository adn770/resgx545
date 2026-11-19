+++
id = "Q128"
question = "why does a client emitpds fault the job at page 0xd2000 or hang it, what do the s0, s1 and s2 operands of the started PDS program become (it saw ir0.0 2 or 3 whatever s2 was), and what in the control word's addend the PDS uses (0xFFF to 0x2000 left the fill's own value, 0x100 did not): why does the addend, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where 0x100 gives 3 or 2, and what does 0x800 do"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E488", "E513", "E520", "E1148", "E1149", "E1150", "E1151", "E1152", "E1153", "E1154", "E1155", "E1156"]
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

Narrowed 2026-11-19 (E1149, E1150, r37-n3b-a and r37-n3b-b, flagged, N3b of
closing29/n3b/design.md): the same form from our task emitsb (E1148's emitsa with a store right
after the emitpds and one as entry 1's first work), one job with each image. Measured [HW]: the
issuing task went on past the emitpds in both (X0 written), the started entry 1 never made its first
store in both, and the EDM's tick stopped within 10 ticks of the command write in both, with no BIF
fault; the reset recovered. With the crumb image (E1150), whose first instruction writes a stopped 0
to `tim`, CR_EVENT_TIMER (0x0acc) still counted after the stop. Inferred from that [infer]: the
emitpds issued by our task stops the EDM's tick with the emitted PDS program never executing its
first instruction, so E1148's causes (2), the program ran and its doutu did not start our task, and
(3), entry 1 started and stopped before its first store, are excluded. The inference is that a `movs
tim` from an emitted program writes the 0x0acc the host reads: `movs tim` was measured only from a
client fill's PDS program, read back through the PDS (doc/isa/content/pds/probe/inputs.md), and the
host's 0x0acc only as the firmware's running timer (E1131, E1133); if it is false, E1150 cannot tell
whether the program ran, (1) from (2), and only E1149's readings stand. Open: why the emitted
program does not start from an EDM task (the PDS, an emit queue the stopped EDM no longer serves, or
the form), what stops the tick, and where an emitted douta lands (pa or sa), never reached.

Narrowed 2026-11-19 (E1151, E1152, r38-n3c-s1, flagged, session S1 of closing29/n3c/design.md):
two rows, one job each. R1 (E1151): our task emitsn, emitsb with the emitpds taken out, ran the
same command to done (X0, M4 and state 2 written, 40 ticks in 38.1 ms, the tick going after it),
so the stop of E1148-E1150 needs the emit [HW]. R2 (E1152): a client fill's PDS `movs tim` of
0x00abcde0 showed in the host's 0x0acc at once and held there to the reset [HW], so E1150's
instrument holds for a client program: the 0x0acc the host reads is the register a PDS `tim`
write loads. E1150's reading that the emitted program never executed its first instruction now
rests only on an emitted program's `tim` write landing as a client's does [infer]. Open: what in
the emit (the program, its page or flags, the control word's rows, the operands or the issuing
pass) stops the tick, why the emitted program does not start from an EDM task, and where an
emitted douta lands (pa or sa), never reached.

Narrowed 2026-11-19 (E1153, E1154, r38-n3c-s4 and r38-n3c-s3, flagged, sessions S4 and S3 of
closing29/n3c/design.md, one boot of module 88ADCEB5): E1149's job with the image changed at the
arm, one job each. R5 (E1153): the halt image, v1's two data rows and a lone `halt`, in the
kernel's own page, stopped the tick within 9 ticks as v1 and crumb did, the issuer going on past
the emit [HW]: the stop needs the emit (E1151) but no instruction of the program. R4 (E1154):
crumb's program with 3 data rows and #14's control word 0x01800100, placed at 0x30011100 in the
firmware's own PDS #14 page with that page's flags, never showed its first `tim` marker and
stopped the tick within 9 ticks [HW; that it never started is inferred as in E1150]: our page,
its flags, the rows and the control word are not the cause. R6 and R7 (sessions s5 and s6) were
not run: the design runs them only after a start (M-T1 to M-DONE). Remaining candidates for why
an emitted program does not start from an EDM task and the tick stops: our `emitpds`'s `s2`
operand or its encoding form, or emitting from our task's timer pass where the firmware emits
from its kick pass. The next step is a user decision (closing29/n3c/design.md, after M-NEVER),
after a facts-only fwsim read of what the stock kick pass does after its #14 emit. Where an
emitted douta lands (pa or sa) stays open, never reached.

Narrowed 2026-11-19 (E1155, E1156, r39-n3d-k and r39-n3d-z, flagged, sessions S1 and S3 of
closing29/n3d/design.md): E1154's job with crumb3 in #14's page, each emit issued on the pass of
a host GETMISCINFO kick. K (E1155: our word, sideband 0, `s2` 0, module 88ADCEB5) scored CANNOT
TELL: the readings were K-NEVER's (T running, entry 1 never stored, the tick stopped) but Δtick
from the kick was 7, outside the frozen band 8-11; read informally [infer], the kick pass alone
did not start the program. Z was then refrozen before it ran, at the user's choice, without the
band. Z (E1156: our word with the firmware's 14-bit sideband 0x843 and `s2` 0x00020000, the
request bit #14 emits with, module 0CDFCDB7) ran: crumb3 reached its last `tim` marker at
0x0acc, its `doutu` started our entry 1 and entry 1 ran to done [HW], the first program emitted
from our task that ran; an emitted program's `tim` lands at 0x0acc as a client's does. So an
emitted program does start from an EDM task when the emit carries #14's sideband and `s2` and
comes from a kick pass. Open: which of the sideband, `s2` and the kick pass decides, alone or
together (row S of the design and the rows that split the sideband from `s2`), and so what
stopped the tick after our other emits; where an emitted `douta` lands (Z: not `pa0` or `pa2`;
`sa0`-`sa3` read the values they hold anyway, so not told); and the client-side parts above.
