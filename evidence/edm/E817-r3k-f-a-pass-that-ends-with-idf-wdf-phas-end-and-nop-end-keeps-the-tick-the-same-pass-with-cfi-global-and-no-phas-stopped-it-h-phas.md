+++
id = "E817"
claim = "R3k stage f (K1, 9 jobs of ring_exit.s, which logs every pass of its four PDS #13 slots in a ring and ends a tick pass of window 2 as ACT says; stops 1): the closed exit reached by a tail call from our page (cont4, to exit index 0x1974, the first run of the kernel's new patch kind) kept the tick in 2 of 2 jobs (FC4); our own replica of the exit, cfi.global, idf, wdf, phas ... end, nop.end, kept it in 2 of 2 (FB); cfi.global, idf, wdf, nop.end stopped it in the one job run (FCF: 4 ring entries, busy signature of E537 with CR_CLKGATESTATUS 0x000ccfa0, the miscinfo of P3 not answered in 505 ms, CCB offsets 2 and 2, dword 14 0, not replicated by the stop rule); idf, wdf, phas ... end, nop.end kept it in 2 of 2 (FPH); frozen verdict 'H-PHAS (the phase end is what the EDM needs)', H-ANY, H-BOTH, H-CFI and H-PLACE refuted by the held-out rows and H-BEFORE refuted by the control"
unit = "edm"
method = "R3k session K1 (stage f; decisions R3-K8 and R3-K9, R3-E1 to R3-E9), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run in one driver call from 19:29:52 Mac time (out/r3-kev.log), gated on k0h's kept stage.json (run 1794334355-1828); the task ring_exit (sha256 3c031d998489f1699d53b469d5aae6403dd0beec2fc51e35ddb29556955a19cb, 686 instructions, built and verified with the landed tools/fwtask at 7aaa017, the verifier rows for the exit's cfi.global and phas words and for cont4) armed once at the stage start (own_arm slots=0xf entry=0,1,2,3, the arm line of the kernel 'exit 0x1974', exit_index 6516 in arm.json) and again after the stop (rearm1.json); per job a ring of the passes, one acted tick pass in window 2 with ACT 6 (FC4: tail call to the exit by cont4), 5 (FB: our cfi, idf, wdf, phas, nop.end), 3 (FCF: cfi, idf, wdf, nop.end) or 4 (FPH: idf, wdf, phas, nop.end), the next entry's gap against the 25000-unit grid (+- 50), CCB offsets and HostCtl dword 14; gating by run_if (FB only if FC4 kept, FCF and FPH only if FB kept), a stopped row is never replicated, stop budget 1 (the second stop ends the stage), a stop signed before the reset (signature twice, P3 one miscinfo, dumps, then debugfs reset, gate, health); stage exit 0, 1 stop, 8 of 9 jobs run, health ok; scored by the frozen score/score_r3.py f (out/score-f.txt). Failed attempt before any row of this stage, kept in the dataset: K1 attempt 1 (19:13, out/kev-attempt1-armlog): stage f stopped (4) after the arm and before any row because the landed cmd_arm sliced dmesg by line count, which is constant when the ring buffer is full (1880 lines), and returned an empty log although the kernel had printed 'own task armed ... exit 0x1974'; r3_run.py arm() now reads its own kmsg marker slice (mock test first), refrozen to 1d6a3ad2. The landed tools/fwtask/fwtask_run.py itself was not changed (the session pins its hash). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file. PREFLIGHT.md of the dataset is the pre-run document (its sections 1 and 7 carry hashes older than the final freeze)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/f/", "edm-closing-r3k-events:out/kev-attempt1-armlog/"]
terms = ["Event Data Master (EDM)", "CR_CLKGATESTATUS", "CR_USE0_SERV_EVENT"]
+++
**What ran.** E813 found that a pass handed to the closed task of slot 2 keeps the tick (X1, 42 of
42 passes) and that a kick pass ended with our own `idf, wdf, nop.end` stops it (B3), so H-EXIT:
the EDM needs what the closed tasks' shared exit does. The exit is five instructions (our own
reading, facts only): `cfi.global`, `idf`, `wdf`, `phas ... end`, `nop.end`. Stage f separates
them. Each row is a plain tick pass, COUNT 1: FC4 reaches the real exit by tail call (the
control), FB ends with a replica of all five in our page, FCF without the `phas`, FPH without the
`cfi.global`.

**Frozen verdict (as printed).** `SUMMARY: f: E0 held; FC4 and FB kept; H-PHAS (the phase end is
what the EDM needs); stops 1 [fcf: busy (E537), read-write 0, dword 14 0x0]; P3 answered in 0 of 1
stops; Q152 rows: held out: 18 held, 5 FAILED, 0 cannot tell/void; refuted ['H-ANY', 'H-BOTH',
'H-CFI', 'H-PLACE']; replicate: 12 held, 3 FAILED, 0 cannot tell/void; refuted ['H-BOTH', 'H-CFI',
'H-PLACE']; control: 11 held, 2 FAILED, 0 cannot tell/void; refuted ['H-BEFORE (the need is before
the exit)']`. The FAILED counts are prediction rows of the refuted hypotheses (each case has one
row per hypothesis), not failed measurements.

**Results [HW].**

| job | the pass ends with | entries (acted, flags) | next entry after the acted pass | CCB write, read | dword 14 | class |
|---|---|---|---|---|---|---|
| e0 | nothing acted | 14 (0, [1]) | on the grid | - | - | ok |
| fc4, fc4-r2 | tail call to the closed exit (cont4) | 14, 14 (1, [1, 4]) | +24994, +24995 | 2, 2 | 0 | ok |
| fb, fb-r2 | cfi.global, idf, wdf, phas end, nop.end | 14, 14 (1, [1, 3]) | +24995, +24995 | 2, 2 | 0 | ok |
| fcf | cfi.global, idf, wdf, nop.end | 4 (1, [1, 3]) | none | 2, 2 | 0 | stop |
| fcf-r2 | - | - | - | - | - | not run (a stopped row is not replicated) |
| fph, fph-r2 | idf, wdf, phas end, nop.end | 14, 13 (1, [1, 3]) | +24994, +24995 | 2, 2 | 0 | ok |

FCF's signature, read twice before the reset: CR_CLKGATESTATUS 0x000ccfa0 (busy), USE0_SERV_EVENT
0x1149, EVENT_TIMER 0x104389b, EVENT_STATUS 0x20000000 (E537's marks); the miscinfo of P3 was not
answered (505 ms, no new ring entry). The reset recovered it, the stage re-armed and ended with
health ok.

Per hypothesis, against the frozen rows: H-PHAS (the `phas` end is needed, `cfi.global` is not)
predicted every row; H-ANY (either word is enough) failed FCF's stop, H-BOTH (both are needed)
failed FPH's keep, H-CFI (only `cfi.global` is needed) failed FPH's keep and FCF's stop, H-PLACE
(the exit must be the closed code itself) failed FB's keep, H-BEFORE (the need is before the exit)
failed FC4's keep.

**What it shows and does not.** In a plain tick pass, `idf, wdf, phas ... end, nop.end` in our own
page is enough to keep the tick and the same pass with `cfi.global` instead of the `phas` is not:
the `phas ... end` is what the pass must reach [infer: the phase end tells the EDM the task is
finished, which the signature of E811 (busy while a task runs) fits]. The exit's words in our page
do as well as the closed code (FB 2 of 2), so the need is not in the closed code's place
(H-PLACE); the tail call to the closed exit works (FC4 2 of 2), so cont4 runs. This closes E813's
open point (whether the exit's five instructions alone are enough: they are, FB). Evidence for the
`phas` being necessary is one stopping job (FCF), not replicated by the stage's rule, against two
keeping jobs each of FB and FPH; the kick pass (B3 of E813) was not run again with a `phas`, so
that a kick pass needs the same is [infer]. The P3 miscinfo was again not answered in a stop (0 of
1 here, 0 of 2 in E814).
