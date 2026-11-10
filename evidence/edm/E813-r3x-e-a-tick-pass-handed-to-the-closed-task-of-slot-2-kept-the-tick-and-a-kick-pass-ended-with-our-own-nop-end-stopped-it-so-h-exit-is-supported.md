+++
id = "E813"
claim = "R3x-events stage e (7 jobs of ring_end.s, which logs every pass of its four PDS #13 slots in a ring and acts on the passes of one kind in window 2: E0 x2 no act; X1 x2 one plain tick pass handed by a second continue patch, cont2, to the closed task of slot 2 at 0xace instead of the general task; X20 x2 twenty such passes; B3 x1, last, a kick pass made by one miscinfo and ended with our own idf, wdf, nop.end without the closed task): E0 held (13 and 14 entries on the 25000-unit grid, nothing acted); X1 kept the tick in 2 of 2 jobs, the acted pass logged with its flag and the next entry 24995 units after it in both (frozen 25000 +- 50), the CCB offsets 2 and 2 and HostCtl dword 14 0; X20 kept it in 2 of 2 with 20 of 20 passes acted (the ring of 16 rungs dropped 8 and 7 entries) and dword 12 less the passes in (-27, -14) and (-27, -13) against the frozen -20 +- 8; B3 stopped the tick: one kick entry with flag 3 and nothing after it, the miscinfo not answered, the CCB write offset 3 and read offset 2 (read = write - 1), dword 14 0, the busy signature of E537 (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x1365 frozen, EVENT_TIMER moving); so H-EXIT (any closed path that reaches the shared exit keeps the tick, a pass ended without it stops it) is supported, H-BODY (the general task's own path is needed: X1 stops) is REFUTED, 2 of 2, and H-TICKONLY (only tick passes need the closed task: B3 keeps the tick) is REFUTED, 1 of 1"
unit = "edm"
method = "R3x-events stage e of the question-closing pass, round 3 (session L3, decisions R3-E1 to R3-E9), dataset edm-closing-r3x-events, on the laptop (host cedar, direct cable), 2026-11-10, stages h, c, e and d in one driver call from 16:37:55 Mac time (out-l3.log), each gated on the previous stage's kept stage.json, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded, checked at each preflight), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), health tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); the tasks accepted by the landed tools/fwtask verifier at 927bea4 and at 7aaa017 to the frozen bytes (the lead's refreeze before the first job, PREFLIGHT.md); per job a baseline D0 of 20 triples (page pass count, HostCtl dword 12, page pass count), the row, the tick bracket (dword 12 and USE0_SERV_EVENT advancing), the CCB offsets and HostCtl dword 14 after it; a stop signed before anything else (P1: the signature twice 30 ms apart with dword 14, the CCB offsets and the pass count; the landed dumps; P3: one miscinfo into the stopped EDM, not in B3), then a debugfs reset, the gate and health; health ok after every stage; stage e with the task armed at the stage start (own_arm slots=0xf entry=0,1,2,3, blob ring_end sha256 0dd75bc9102981ed..., 678 instructions: round 2's ring_skip.s with the host words KIND, ACT and COUNT and the continue triple cont2 in entry 0, overlaid by the kernel at the arm as the landed fwtask.apply_patches does; the arm record kept, arm.json) and again after B3's stop (rearm1.json); the slot of cont2 fixed by the offline reading R-2 of closing3/events/readings/readings-r3.md (slot 2's fast path: 12 instructions then the shared exit's 5, no group bit, no state word); B3 last and without P3 (its own miscinfo is the probe); stop budget 1, not reached; scored by the frozen score/score_r3.py e (out/score-e.txt)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3x-events:out/e/"]
terms = ["Event Data Master (EDM)", "CR_CLKGATESTATUS", "CR_EVENT_TIMER", "CR_USE0_SERV_EVENT"]
+++
**What ran.** E793's tasks ended a tick pass with `nop.end` instead of calling the closed general
task and the tick stopped. The note of 2026-11-10 on E793 found the shared exit (0x1974 to 0x1978:
`cfi.global`, `idf`, `wdf`, `phas ... end`, `nop.end`) as the only difference the code shows
between the closed end and ours. Stage e asks whether any closed path through that exit keeps the
tick (X1: slot 2's short fast path, which reads no group bit and no state word) and whether a kick
pass ended our way stops it as a tick pass does (B3).

**Frozen verdict (as printed).** `SUMMARY: e: E0 held; H-EXIT (a tick pass handed to a fast-path
task keeps the tick, a skipped kick pass stops it); stops 1 [b3: busy (E537), read-write -1, dword
14 0x0]; Q152 rows: held out: 21 held, 2 FAILED, 0 cannot tell/void; refuted ['H-BODY',
'H-TICKONLY']; replicate: 8 held, 1 FAILED, 0 cannot tell/void; refuted ['H-BODY']; control: 6
held, 0 FAILED, 0 cannot tell/void`.

**Results [HW].**

| job | entries in the window | acted | after the acted pass | CCB write, read | dword 14 | class |
|---|---|---|---|---|---|---|
| e0, e0-r2 | 13, 14 | 0 | - | 2, 2 | 0 | kept |
| x1, x1-r2 | 14, 13 | 1 (flag 4) | next entry +24995 units | 2, 2 | 0 | kept |
| x20, x20-r2 | 16, 16 (8, 7 dropped) | 20 | dword 12 - passes in (-27, -14), (-27, -13) | 2, 2 | 0 | kept |
| b3 | 7 | 1 (flag 3, the kick) | nothing logged after it, miscinfo not answered | 3, 2 | 0 | stop |

B3's signature, read twice before the reset: 0x0008 0x000ccfa0, USE0_SERV_EVENT 0x1365 (bit 16
clear, frozen), EVENT_TIMER 0x1029647 moving, EVENT_STATUS 0x20000000, HostCtl dword 12 frozen at
4918; the tick gaps before the kick were on the grid. The reset recovered it; the stage re-armed
and ended with health ok.

**What it shows and does not.** Handing a tick pass to the closed task of slot 2, which runs 12
instructions and the shared exit and nothing of the general task, keeps the tick, in 42 of 42 such
passes (X1 2, X20 40), and the 20 a job of X20 do not advance dword 12 [infer: the tick handler is the general task's].
Ending a kick pass our way stops the EDM as ending a tick pass did (E793), with the kick's CCB
command written and not read. So what a pass needs at its end is in the closed tasks' common path
to the exit, not in the general task's body nor only on tick passes [infer]; whether the exit's
five instructions alone are enough is stage f's (the kernel batch), not run here.
