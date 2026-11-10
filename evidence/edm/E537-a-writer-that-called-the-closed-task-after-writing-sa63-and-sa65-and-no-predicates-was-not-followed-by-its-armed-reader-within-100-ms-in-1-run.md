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

**Correction 2026-11-10:** A reading of this run's own dumps, made before the round 2 runs and not a new
measurement; the measurements above stand. [data] The register dump taken after the stop
(p1130-b2-variants/tailpair-stop1-regs.txt) reads `CR_CLKGATESTATUS` 0x000ccfa0 (the busy pattern
the idle value 0x20 does not have), `USE0_SERV_EVENT` 0x9e0 and `EVENT_TIMER` (0x0acc) 0x01038ec3,
and `EVENT_STATUS` 0x20000000. [infer] So the timer was running and events were queued, bit 16 of
`USE0_SERV_EVENT` (empty) read clear and its count did not move, and a USSE task stayed resident:
the closed task did not end (E154: its waits are polls), which reads as a hang inside the closed
task and not as the EDM having stopped dispatching. [data] The writer's sa65 (the 10th marker of
the first writer in b2-markers.json, stored by the `mov sa65, r19` of state3.s) was 0xb009c5dc and
its sa64 0xb0150d9d. [infer] Read as `pa1` by E155's layout, the low bits of the sa65 word are 2,
3, 4, 6, 7, 8, 10, 14, 15, 16 and 19 under a count byte of 0xb0: of the bits whose handler E155
names these include 4 (`PIXELBE_END_RENDER`), 7 (`BREAKPOINT`), 8 (the kernel CCB reader), 10
(`TA_TERMINATE`) and 19 (tested with the out-of-memory bits, posting nothing), with no job in flight
to cause them; the sa64 word has bit 1 clear, so it is not a tick's. The closed task dispatches on
the event words it finds, and the sa65 write is the leading candidate for this run's stop, with a
mechanism (a word that asks for handlers no event raised); it is a candidate, not established: the
p0 = p1 = 1 predicates and the sa, r and i writes remain the other differences from E536's writer
(Q152). The register values above were read from the dump; the reading of sa65 as `pa1` is E155's
[infer] reading, which no run has fed to the firmware.

**Correction 2026-11-10:** (R3-events, E791 and E793) the reading above that a task stayed
resident and "the closed task did not end", read as a hang inside the closed task and not as the
EDM having stopped dispatching, is not supported. [data] A task of ours that never called the
closed task (E793, ring_skip.s: the pass logged itself and ended with `nop.end`, no sa, r, i, p or
pclink write) stopped the tick in 2 of 2 runs with the same signature this dump has:
`CR_CLKGATESTATUS` 0x000ccfa0, `EVENT_STATUS` 0x20000000, `EVENT_TIMER` counting,
`USE0_SERV_EVENT` with bit 16 clear and its count frozen (0x8ad and 0x33b there, 0x9e0 here, the
count depending on the time since the load). [infer] So this signature does not by itself mean that
the closed task hung: it is what the EDM looks like when the tick stops after a task that ended
without the closed task's end-of-pass work, whatever that work is, and E537's stop may have the same
cause or another. The note's other readings were tested by single writes in E791: no write of sa63
alone, of sa64 or of sa65 with the value the closed task found, nor the tail call with p0 = p1 = 1
and r and i written stopped the tick (19 of 19 jobs); the sa65 word E537's writer left (0xb009c5dc)
was not written by any of those rows, so the note's leading candidate, the word the closed task
dispatched on, is neither confirmed nor refuted.

**Correction 2026-11-10:** (offline readings of this run's own status dump and of our disassembly of the
closed firmware, made before the round 3 runs; not new measurements; the readings are in the note of
Q152). [HW] Besides the busy signature, this stop's dump differs from E793's two stops: `ccbctl[0]`
reads write offset 2 and read offset 3 (E793: 2 and 2, in both stops), and HostCtl dword 14 reads
0xad002600 (E793: 0). [RE] The only code that writes that word is at instructions 0x0 to 0x5 (`mov
r16, #0xAD002600` at 0x0, the store to dword 14 at 0x1; the constant of the other site, 0x55c, is
0xad001a07); after the store the code fences and branches to 0x173f, it neither loops nor ends. No
run of ours has entered 0x0 (E014). [infer] The sa65 word E537's writer left, 0xb009c5dc, has bit 8
set, the bit that starts the kernel CCB reader (E155), which takes the command at the read offset,
advances it and branches to the address in the command's first dword; a command slot never written
reads 0 (the buffer pages are zeroed), which would branch to 0x0 and leave exactly the two marks
above. That chain is a reading of the code and the dump, not shown by a run; the E793 stops, which
have neither mark, were a different stop.

**Correction 2026-11-10:** (R3x-events, E814 and E812, held out) The note above's chain from bit 8
is borne out in its outcome: a writer that left only the count byte and bit 8 in sa65 (0x02000100)
stopped the tick with both of this record's marks, read offset 3 against write offset 2 and HostCtl
dword 14 0xad002600, with the busy signature (1 job); the chain itself is not traced by a run. Bit 8
is not the only cause in this record's word: 0xb009c4dc, the word without bit 8, also stopped the
tick, busy and with neither mark (read = write, dword 14 0; 1 job), while sa65 words with the count
byte 0xb0 alone, with bit 23, bit 19 or bits 2, 3, 6, 14, 15 and 16 kept it (E812, 11 jobs), which
leaves bits 4, 7 and 10 of this word untried alone. The word 0xb009c5dc itself was not run again
(D3, ended by the stop budget). The busy signature is also what a pass of ours still running reads
(E811), so it does not mark a stop by itself.
