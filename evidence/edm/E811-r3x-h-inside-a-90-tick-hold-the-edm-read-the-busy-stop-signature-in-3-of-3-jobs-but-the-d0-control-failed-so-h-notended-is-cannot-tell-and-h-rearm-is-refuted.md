+++
id = "E811"
claim = "R3x-events stage h (6 jobs of ring_hold.blob, S2b's task byte for byte, a reset and an arm before each: H0 x3, no hold, the register signature at 20 and 60 ms after the window opened; H1 x3, the signature at 20 and 60 ms inside a hold of one pass of 2262434 timer units, about 90.5 ms): H0 read the idle signature in 3 of 3 (CR_CLKGATESTATUS 0x20, USE0_SERV_EVENT with bit 16 set and its count moving), and the hold of H1 was in its band (2262433, 2262434, 2262433 units); inside the hold all four samples of each H1 job read the busy signature of E537 and E793's stops (CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x3ed, 0x3ea and 0x415 with bit 16 clear and its count frozen, EVENT_TIMER moving, CCB offsets 2 and 2, HostCtl dword 14 0), all elements as a running task in 3 of 3 jobs, so H-REARM (a stop that differs from a running task in some element) is REFUTED, 3 of 3; the control 'D0 one modal value' FAILED in 3 of 3 (no valid D0 read: in every triple the page's pass count moved between its two reads), so D in the hold could not be read and the frozen verdict for H-NOTENDED (the stopped pass never ended) is cannot tell"
unit = "edm"
method = "R3x-events stage h of the question-closing pass, round 3 (session L3, decisions R3-E1 to R3-E9), dataset edm-closing-r3x-events, on the laptop (host cedar, direct cable), 2026-11-10, stages h, c, e and d in one driver call from 16:37:55 Mac time (out-l3.log), each gated on the previous stage's kept stage.json, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded, checked at each preflight), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), health tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); the tasks accepted by the landed tools/fwtask verifier at 927bea4 and at 7aaa017 to the frozen bytes (the lead's refreeze before the first job, PREFLIGHT.md); per job a baseline D0 of 20 triples (page pass count, HostCtl dword 12, page pass count), the row, the tick bracket (dword 12 and USE0_SERV_EVENT advancing), the CCB offsets and HostCtl dword 14 after it; a stop signed before anything else (P1: the signature twice 30 ms apart with dword 14, the CCB offsets and the pass count; the landed dumps; P3: one miscinfo into the stopped EDM, not in B3), then a debugfs reset, the gate and health; health ok after every stage; stage h with a stop budget of 0 (DEVIATION 1); H1's two samples 10 ms apart at each time (DEVIATION 7), the page's STATE read around each sample; scored by the frozen score/score_r3.py h (out/score-h.txt); the D0 triples quoted were read after the run from the kept job records out/h/NAME.json"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3x-events:out/h/"]
terms = ["Event Data Master (EDM)", "CR_CLKGATESTATUS", "CR_EVENT_TIMER", "CR_USE0_SERV_EVENT"]
+++
**What ran.** E793 read E537's busy signature at the stops where a pass of ours ended without the
closed task, and asked whether the EDM is still waiting for that pass (H-NOTENDED) or the pass
ended and delivery is not re-armed (H-REARM). A task of ours that holds one pass for about 90 ms
(S2b) shows what a pass still running looks like; H0 is the same task between passes. D (the page's
pass count less dword 12) was a new instrument meant to tell whether a stopped pass was counted.

**Frozen verdict (as printed).** `SUMMARY: h: H0 DIFFERS; H1 reads H-NOTENDED (3 of 3 jobs look
exactly like a running task), D offsets [()]; stops 0 []; Q152 rows: held out: 1 held, 1 FAILED, 1
cannot tell/void; refuted ['H-REARM']; cannot tell ['H-NOTENDED']; replicate: 2 held, 2 FAILED, 2
cannot tell/void; ...; control: 6 held, 3 FAILED, 0 cannot tell/void; refuted ['control (D0 one
modal value)']`.

**Results [HW].**

| job | 0x0008 | USE0_SERV_EVENT | CCB write, read | dword 14 | hold (units) |
|---|---|---|---|---|---|
| h0, h0-r2, h0-r3 | 0x20 (4 of 4 samples each) | bit 16 set, moving | 2, 2 | 0 | - |
| h1 | 0x000ccfa0 (4 of 4) | 0x3ed, frozen | 2, 2 | 0 | 2262433 |
| h1-r2 | 0x000ccfa0 (4 of 4) | 0x3ea, frozen | 2, 2 | 0 | 2262434 |
| h1-r3 | 0x000ccfa0 (4 of 4) | 0x415, frozen | 2, 2 | 0 | 2262433 |

EVENT_STATUS read 0x20000000 and STATUS2 0x400 in every sample. No stop: every job kept the tick.

**Read after the run [HW, no frozen row].** D0 needs a triple whose two page reads agree; in all 20
triples of every job of the session (29 jobs, 580 triples) the pass count moved between them, by 1
to 4 in H0 and 6 to 12 elsewhere, so D was never measured and every D row of the session is cannot
tell.

**What it shows and does not.** A pass of ours that is still running reads exactly E537's and
E793's stop signature in every element sampled, so that signature cannot tell a stop from a pass
in progress; what it does not show is whether the EDM counted the stopped pass, which D was to
read. H-NOTENDED is not claimed.
