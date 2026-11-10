+++
id = "E818"
claim = "R3k stage t (K1, 5 jobs of ring_timer.s, stops 1): a task of ours that stored the tick handler's own word 0x01061a80 to CR_EVENT_TIMER (str #691, the verifier's new row, the first str of the timer by a task of ours) and then called the closed task kept the tick in 2 of 2 jobs (T1) with the next entry 25114 units after the acted pass in both, outside the frozen 25000 +- 50; the same str followed by our own idf, wdf, nop.end stopped it in the one job run (T2: 4 ring entries, E537's busy signature, the miscinfo of P3 not answered, not replicated); frozen verdict 'H-NOTIMER (the timer write does not make our own end enough)', H-TIMER refuted by the held-out row, H-TIMERW-HARMLESS and H-TIMERW-STOPS refuted by the control"
unit = "edm"
method = "R3k session K1 (stage t; decision R3-K10), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run in one driver call from 19:30:07 Mac time (out/r3-kev.log), gated on stage f's kept stage.json (exit 0, run 1794335393-2512); the task ring_timer (sha256 8f1536f18a831f41..., 672 instructions, our own source, the stored word pinned by the guard to 0x01061a80 = 0x01000000 | HostCtl dword 6, the closed handler's own reload word, DEVIATION 1 of PREFLIGHT.md: the brief's 0x01061a70 is pa2, sixteen units later) armed once at the stage start; jobs E0, T1 x2 (ACT 7: str, then the closed task), T2 (ACT 8: str, then idf, wdf, nop.end; run only if T1 kept; its replicate not run after the stop); stop budget 1, stop signed before the reset as in stage f; exit 0, 1 stop, 4 of 5 jobs run, health ok; scored by the frozen score/score_r3.py t (out/score-t.txt). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file. The 25114 gap was read from the ring with the frozen reader (the scorer's own line)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/t/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER", "CR_CLKGATESTATUS", "CR_USE0_SERV_EVENT"]
+++
**What ran.** The closed tick handler stores `0x01000000 | HostCtl dword 6` to `CR_EVENT_TIMER`
(E155) before it ends a pass, and E793's task ended a pass without it. Stage t asks whether that
store is what the pass needs: T1 stores it and then calls the closed task (a control: the store is
harmless or not), T2 stores it and ends our own way.

**Frozen verdict (as printed).** `SUMMARY: t: E0 held; T1 kept; T2 stopped: H-NOTIMER (the timer
write does not make our own end enough); stops 1 [t2: busy (E537), read-write 0, dword 14 0x0]; P3
answered in 0 of 1 stops; Q152 rows: held out: 5 held, 1 FAILED, 0 cannot tell/void; refuted
['H-TIMER (the timer write is what an ended tick pass needs)']; control: 9 held, 4 FAILED, 0
cannot tell/void; refuted ['H-TIMERW-HARMLESS (the closed handler stores the same word)',
'H-TIMERW-STOPS (a str of the timer by our pass stops the tick)']`.

**Results [HW].**

| job | the pass | entries (acted, flags) | next entry after the acted pass | CCB write, read | dword 14 | class |
|---|---|---|---|---|---|---|
| e0 | nothing acted | 14 (0, [1]) | on the grid | - | - | ok |
| t1, t1-r2 | str #691 of 0x01061a80, then the closed task | 13, 14 (1, [1, 4]) | +25114, +25114 | 2, 2 | 0 | ok |
| t2 | str #691, then idf, wdf, nop.end | 4 (1, [1, 3]) | none | 2, 2 | 0 | stop |
| t2-r2 | - | - | - | - | - | not run |

T2's signature: CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0xc10, EVENT_TIMER 0x105978c,
EVENT_STATUS 0x20000000; P3 not answered (505 ms).

**The control's four FAILED rows.** T1 is the control of two hypotheses about the store itself.
H-TIMERW-STOPS (the store stops the tick) predicted a stop and was refuted (T1 kept the tick, 2 of
2). H-TIMERW-HARMLESS (the closed handler stores the same word, so the store changes nothing)
predicted the next gap on the grid, 25000 +- 50, and was refuted too: the gap after the acted pass
was 25114 units in both jobs, 114 units (4.6 microseconds at 25 MHz) longer. So the store is not
invisible: it moves the next tick by about 114 units [infer: the write reloads the timer, the
closed task then reloads it again at its end, so the pass's remaining time counts twice; not
tested].

**What it shows and does not.** The EVENT_TIMER store alone does not make our own end enough (T2
stopped, 1 job, not replicated), and it does not stop the tick when the closed task follows (T1 2
of 2). With E817 the picture for a pass that ends our way is: the `phas ... end` is the part of
the exit that matters, the timer store is not. It does not show what the closed task does at the
end of a tick pass besides the exit (the tick handler's other stores were not tried), and a stop
is one job.
