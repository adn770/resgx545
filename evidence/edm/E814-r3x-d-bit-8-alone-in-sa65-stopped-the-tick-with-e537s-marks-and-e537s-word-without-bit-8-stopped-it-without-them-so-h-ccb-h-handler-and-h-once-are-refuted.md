+++
id = "E814"
claim = "R3x-events stage d (alias2.s with a reset and an arm before each job; D0 the reader alone, D1 a writer leaving sa65 = 0xb009c4dc, E537's word with bit 8 clear, D2 one leaving sa65 = 0x02000100, the count byte with bit 8 alone; each then calling the closed task): D0 held (pclink 0x98, p1 1, sa64 2, sa65 0x02000000, sa63 0); D1 stopped the tick after the writer's pass with the busy signature of E537 (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x3f3 frozen, EVENT_TIMER moving), the CCB write and read offsets 2 and 2 (read = write) and HostCtl dword 14 0; D2 stopped it with the same signature (USE0_SERV_EVENT 0x3ee) and E537's two marks, read offset 3 against write offset 2 (read = write + 1) and dword 14 0xad002600; P3 (one miscinfo into the stopped EDM) was not answered in either stop; so H-CCB (bit 8 alone stops it with E537's marks and D1 keeps the tick) is REFUTED by D1, H-HANDLER (a job bit with no job stops it, no mark, D2 keeps it) by D2, H-ONCE (E537 does not repeat) by both, and H-REARM (P3 answered) by both; D2 held every frozen row of H-CCB's own (stop, read = write + 1, dword 14, busy); the stage ended by its stop budget at D2 by design (the second stop), so D1's replicates, D3 (E537's own word, A8) and D4 were not run"
unit = "edm"
method = "R3x-events stage d of the question-closing pass, round 3 (session L3, decisions R3-E1 to R3-E9), dataset edm-closing-r3x-events, on the laptop (host cedar, direct cable), 2026-11-10, stages h, c, e and d in one driver call from 16:37:55 Mac time (out-l3.log), each gated on the previous stage's kept stage.json, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded, checked at each preflight), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), health tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); the tasks accepted by the landed tools/fwtask verifier at 927bea4 and at 7aaa017 to the frozen bytes (the lead's refreeze before the first job, PREFLIGHT.md); per job a baseline D0 of 20 triples (page pass count, HostCtl dword 12, page pass count), the row, the tick bracket (dword 12 and USE0_SERV_EVENT advancing), the CCB offsets and HostCtl dword 14 after it; a stop signed before anything else (P1: the signature twice 30 ms apart with dword 14, the CCB offsets and the pass count; the landed dumps; P3: one miscinfo into the stopped EDM, not in B3), then a debugfs reset, the gate and health; health ok after every stage; stage d with a reset and an arm before every job (own_arm slots=0x1 entry=0, blob alias2 sha256 c41bd078cd42eb33..., cmd 10: sa65 = the host word, left in place), stop budget 1 (the second stop ends the stage, exit 8, reset and gate exact); the stop records P1 (stop-NAME-status.txt, stop-NAME-regs.txt), P2 and P3 kept in the job records; scored by the frozen score/score_r3.py d (out/score-d.txt); the offsets and registers after P3 quoted in the body were read after the run from the kept job records out/d/NAME.json"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3x-events:out/d/"]
terms = ["Event Data Master (EDM)", "CR_CLKGATESTATUS", "CR_EVENT_TIMER", "CR_USE0_SERV_EVENT"]
+++
**What ran.** E537's writer left sa65 = 0xb009c5dc and the tick stopped with two marks no other stop
showed (read offset 3, dword 14 0xad002600). The note of 2026-11-10 on E537 read a chain from bit 8,
the bit that starts the kernel CCB reader, through a never-written command slot to the code at 0x0
that stores 0xad002600 [infer]. D1 removes bit 8 from E537's word, D2 keeps bit 8 alone.

**Frozen verdict (as printed).** `SUMMARY: d: D0 held; D1 and D2 both stop it: neither H-CCB nor
H-HANDLER alone (the stage ended before D3); kept 1 of 3 read jobs, stops 2 ['d1', 'd2'] [d1: busy
(E537), read-write 0, dword 14 0x0; d2: busy (E537), read-write 1, dword 14 0xad002600]; P3 answered
in 0 of 2 stops; Q152 rows: fit: 0 held, 0 FAILED, 7 cannot tell/void; cannot tell ['H-CCB',
'H-HANDLER', 'H-ONCE']; held out: 9 held, 6 FAILED, 1 cannot tell/void; refuted ['H-CCB',
'H-HANDLER', 'H-ONCE', 'H-REARM']; control: 6 held, 0 FAILED, 0 cannot tell/void; stage exit 8`.

**Results [HW].**

| job | sa65 left | tick | 0x0008 | USE0_SERV_EVENT | CCB write, read | dword 14 | P3 |
|---|---|---|---|---|---|---|---|
| d0 | none | kept | - | - | 2, 2 | 0 | - |
| d1 | 0xb009c4dc | stopped | 0x000ccfa0 | 0x3f3, frozen | 2, 2 | 0 | not answered (504 ms) |
| d2 | 0x02000100 | stopped | 0x000ccfa0 | 0x3ee, frozen | 2, 3 | 0xad002600 | not answered (3 ms) |

EVENT_STATUS 0x20000000 in both stops. Both resets recovered the tick (gates exact, health ok).

**Read after the run [HW, no frozen row].** After P3 in d1 the CCB write offset had moved to 3
(the kernel's command written, not read) and BIF_INT_STAT read 0x000d0400 with 0x0c08 = 15,
against 0x00080000 and 0 before it; in d2 the offsets stayed 2 and 3 and BIF_INT_STAT 0x00080000.

**What it shows and does not.** Bit 8 alone in the word the closed task reads reproduces E537's
stop with both of its marks, as the note's chain predicted [infer for the chain itself: the code
path is not traced by a run]; E537's word without bit 8 also stops the tick, without the marks, so
another bit of that word stops it by another path. Its bits below the count byte are 2, 3, 4, 6, 7,
10, 14, 15, 16 and 19 [arithmetic]; C3 and C4 of E812 kept the tick with 2, 3, 6, 14, 15, 16 and 19
and with 0xb0 as the count byte, which leaves 4, 7 and 10, the job bits H-HANDLER named, untested
one by one. One job each.
