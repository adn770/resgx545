+++
id = "E812"
claim = "R3x-events stage c (13 jobs of alias2.s, one entry: C0 x2 the reader alone; C1 to C4 a writer leaving one sa65 word in place before calling the closed task, C1 x3 count byte K = 2 in bits 31:24 with bit 23, C2 x2 0xb0000000, C3 x2 K with bits 2, 3, 6, 14, 15 and 16, C4 x2 K with bit 19; C5 x2 sa64 = pa0 & ~2 written on 50 consecutive passes): the tick was kept in 13 of 13 jobs; C0 read pclink 0x98, p1 1, sa64 2, sa65 0x02000000 and sa63 0 as E791's A0 (2 of 2); after each C1 to C4 writer the next entry read pclink 0x98 and sa65 0x02000000 (K << 24), the CCB write and read offsets 2 and 2 and HostCtl dword 14 0 (9 of 9); after C5's 50 passes pclink read 6 and HostCtl dword 12 less the passes counted was in (-57, -43) and (-58, -43) against the frozen -50 +- 8 (2 of 2: dword 12 did not advance on those passes); the frozen scorer: held out 17 held, 0 FAILED, 1 cannot tell (C5's D row, D0 never measured, E811)"
unit = "edm"
method = "R3x-events stage c of the question-closing pass, round 3 (session L3, decisions R3-E1 to R3-E9), dataset edm-closing-r3x-events, on the laptop (host cedar, direct cable), 2026-11-10, stages h, c, e and d in one driver call from 16:37:55 Mac time (out-l3.log), each gated on the previous stage's kept stage.json, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded, checked at each preflight), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), health tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); the tasks accepted by the landed tools/fwtask verifier at 927bea4 and at 7aaa017 to the frozen bytes (the lead's refreeze before the first job, PREFLIGHT.md); per job a baseline D0 of 20 triples (page pass count, HostCtl dword 12, page pass count), the row, the tick bracket (dword 12 and USE0_SERV_EVENT advancing), the CCB offsets and HostCtl dword 14 after it; a stop signed before anything else (P1: the signature twice 30 ms apart with dword 14, the CCB offsets and the pass count; the landed dumps; P3: one miscinfo into the stopped EDM, not in B3), then a debugfs reset, the gate and health; health ok after every stage; stage c with the task armed once at the stage start (own_arm slots=0x1 entry=0, blob alias2 sha256 c41bd078cd42eb33..., 301 instructions: alias.s of round 2 plus cmd 10, sa65 = a host word left in place, cmd 12, sa64 = pa0 & ~2 for N passes with the reader armed on the last); K read by the host from ccbctl[0] before each job, the writer's own read-back of the word checked; scored by the frozen score/score_r3.py c (out/score-c.txt)"
tiers = ["HW"]
date = "2026-11-10"
data = ["edm-closing-r3x-events:out/c/"]
terms = ["Event Data Master (EDM)", "CR_USE0_SERV_EVENT"]
+++
**What ran.** E537's writer left sa65 = 0xb009c5dc and the tick stopped; E791 kept the tick with
single sa63, sa64 and sa65 writes but never wrote that word. The note of 2026-11-10 on E537 read
bit 8 (the CCB reader's bit of the event word) as the likely cause. Stage c leaves words without
bit 8 in sa65, each with bits of the event word that have no handler (C3, outside the tested mask
0x780790) or a handler that posts nothing (C1 bit 23 beside the count, C4 bit 19), and C5 repeats
E792's A4 (the tick bit of sa64 clear) on 50 passes so that the dword 12 count can see it.

**Frozen verdict (as printed).** `SUMMARY: c: C0 held; C1 kept 3 of 3; C2 kept 2 of 2; C3 kept 2 of
2; C4 kept 2 of 2; C5 kept 2 of 2; stops 0 []; Q152 rows: fit: 12 held, 0 FAILED, 0 cannot
tell/void; held out: 17 held, 0 FAILED, 1 cannot tell/void; cannot tell ['E792 A4']; replicate: 22
held, 0 FAILED, 1 cannot tell/void; cannot tell ['E792 A4']`.

**Results [HW].**

| row | word left | jobs kept | next entry pclink, sa65 | CCB write, read | dword 14 |
|---|---|---|---|---|---|
| C0 | none | 2 of 2 | 0x98, 0x02000000 | 2, 2 | 0 |
| C1 | sa65 = 0x02800000 | 3 of 3 | 0x98, 0x02000000 | 2, 2 | 0 |
| C2 | sa65 = 0xb0000000 | 2 of 2 | 0x98, 0x02000000 | 2, 2 | 0 |
| C3 | sa65 = 0x0201c04c | 2 of 2 | 0x98, 0x02000000 | 2, 2 | 0 |
| C4 | sa65 = 0x02080000 | 2 of 2 | 0x98, 0x02000000 | 2, 2 | 0 |
| C5 | sa64 = pa0 & ~2, 50 passes | 2 of 2 | 6 (after the last) | 2, 2 | 0 |

**What it shows and does not.** None of these words stops the tick, so E537's stop does not come
from the count byte 0xb0 alone, bit 23, bit 19 or the six handlerless bits of C3. The closed task's
pass with the tick bit of sa64 clear leaves pclink at 6 (E792) and does not advance HostCtl dword
12, which the tick handler counts [infer: the handler at 0x486 is skipped on those passes], 2 of 2
over 50 passes each.
