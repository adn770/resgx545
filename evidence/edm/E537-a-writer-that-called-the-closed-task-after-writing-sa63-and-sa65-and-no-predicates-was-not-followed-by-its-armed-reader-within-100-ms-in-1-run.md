+++
id = "E537"
claim = "A firmware task of ours (state3.s, cmd 4) that wrote sa64, sa100, sa127, sa20, sa24, sa65, sa63, r20, r21, i0 and i1 and set no predicate, stored its done flag with the reader armed (cmd = 9) and tail-called the closed general task was not followed by the reader it had armed for the next event within 100 ms (1 of 1 run of this writer); HostCtl dword 12 advanced 6 in that 100.3 ms window (ticks_during = 6) and then did not move: it read 0x9db and USE0_SERV_EVENT 0x9e0 in both dumps taken seconds later (the status dump and the register dump, so no event ran between them); EVENT_STATUS2 0x400, BIF_INT_STAT 0x00080000, BIF_FAULT 0, no log line, and one debugfs reset restored the stock firmware (ticks 999 Hz, GETMISCINFO answered, fill and triangle diff 0 of 2048 and 0 of 4096); the writer of E536 (state2.s cmd 1, with p0 to p3 set to 0, 0, 1, 1 and without sa63 and sa65) did not stop the tick in 3 of 3 rounds"
unit = "edm"
method = "as E536 with asm/fwtask/state3.s (119 instructions, blob sha256 4465620910e7...c7480; writers cmd 1 all, 2 arm only, 3 p0 to p3 only, 4 sa, r and i only, and the reader cmd 9), run by tools/fwtask/run_stage.py stage b2, tool sha256 54eb8909...e56e; the predictions of its six rows (predictions-1130-b2.toml, sha256 35b326d7a56799c18c164e13f519f7e8402f02c49d9ee9832f562f666e743c58) were frozen after stage B's results were read and before this run, so they are not blind to them; the plan was 3 writers of each of the 4 commands in a seeded shuffle (4, 2, 1, 3, 3, 4, 3, 1, 4, 2, 2, 1), each preceded by a control reader; the first writer in that order was cmd 4, and the stage stopped on its own trigger (the next event did not run the reader within 100 ms) after 1 control and 1 writer; the tool then saved the register dump, the status, the results page and the log (on the laptop; they were copied into the data directory by hand, the stray copy removed), one debugfs reset, one stock check. Run p1130-b2-variants (one run, stopped; kept). The other 11 writers of the plan did not run and none of the six rows was evaluated. A firmware task, not a client pixel task. The module and its verifier as E536 (bypasses, fixed later; the fixed verifier was not used; it accepts state3.s)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-writer-variants"]
terms = ["Event Data Master (EDM)"]
+++
 **What ran.** The first control reader read the state E536 left (3 minutes before, with a firmware
reload at this run's arming): sa100 = 0xb949ab07, sa127 = 0xfc1e4a1a, i0 = 0xbf9be0f7 (the values of
E536's third round), r21 = 0x3000 ([infer] the fills' counter), sa20 = sa24 = 0, sa63 = 0, sa64 = 2
and sa65 = 0x02000000. The writer (cmd 4) then ran: its flag was set 0.19 ms after the command, the
page showed cmd = 9, state = done, and the echo of its run id (101), and the reader it had armed did
not run within the 100.3 ms the tool waited, in which HostCtl dword 12 advanced 6 (the healthy
rounds of E536 give 9, 7 and 7 over their windows, which include the host's register-read time). The
two dumps taken seconds later both read 0x9db in that dword and 0x9e0 in USE0_SERV_EVENT, so no
event ran between them either; whether the tick stopped within a few milliseconds of the command or
the counter kept advancing for part of the window is not told apart by a count over the window
alone.

**What was different from E536's writer.** It is another blob (state3.s, the same code with three
more commands and two more sa writes) and a different command. It wrote two more sa, sa63 and
sa65, and the predicates at its tail call were p0 = 1 and p1 = 1 (the command tests of its
dispatch) with p2 and p3 as at entry, against 0, 0, 1, 1 set by the writer of E536. The one
wrapper of 11.29 whose predicates at the tail call are readable from its source (mem.s, E532, 2
runs) also called the closed task with p0 = p1 = 1 and wrote no sa, r or i, and it did not stop the
tick. So the stop follows one of the differences or their combination [infer: the sa63 or sa65
write, the p0 and p1 values, or sa, r and i written with those predicates]; the writers that would
have told them apart (cmd 2 arm only, cmd 3 predicates only, cmd 1 with the sa written) did not
run, because the plan's stop rule ends the stage at a stop.

**Prediction.** The rows of this run's file were frozen for the 12 writers; none was evaluated:
one writer ran and the tool's stage stopped.

**E533's confound.** This is a task that called the closed task and still did not run its armed
reader within 100 ms (and no event ran between two dumps seconds later), so the stop of E533 cannot
be assigned to the missing closed task alone. With E536 the two runs show: the list of writes of
E536 plus the closed task keeps the tick (3 of 3); a writer with sa63, sa65 and p0 = p1 = 1 plus the
closed task does not (1 of 1). The pclink write of E533 (an arbitrary value; E536's writer wrote
only the tail triple's pclink) is not tested by either.

**Not shown.** Which of the differences stops the tick (Q152), whether the closed task or the
event path stops it, what the closed task did on the tick before the stop, and whether the stop
repeats (one run).
