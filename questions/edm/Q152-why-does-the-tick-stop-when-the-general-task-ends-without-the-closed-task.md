+++
id = "Q152"
question = "what does the EDM need from the closed general task's end of a pass so that the next event is delivered and the 1 kHz tick continues (E793: a task of ours that ended a tick pass with `nop.end` and did not call it stopped the tick, 2 of 2, while E791's single writes of sa63, sa64 or sa65 and the tail call with p0 = p1 = 1 did not, 19 of 19), and what in E537's writer (sa63 and sa65 written with the words it left, p0 = p1 = 1: the armed reader did not run, 1 run) stopped it, E536's writer (3 of 3 rounds kept the tick) not, and does the closed task use p0 to p3, sa63 or sa65"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E533", "E155", "E536", "E537", "E791", "E792", "E793"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER"]
+++

E533: `HostCtl` dword 12 and `USE0_SERV_EVENT` stopped after a task of ours that ended with
`nop.end` for one tick (one run, the stage's own trigger), and a debugfs reset recovered. That task
did two things in the same run: it skipped the closed general task, and it wrote `sa64`, `sa100`,
`sa127`, `sa20`, `sa24`, `r20`, `r21`, `i0`, `i1`, `p0` to `p3` and `pclink`, then stored a command
for the next event. The cause is confounded: skipping the closed task, clobbering state the closed
task or the PDS needs, the `EVENT_TIMER` write of the tick handler (E155) that the closed task would
have made [infer], or something our command-1 path left undone are all consistent with the run.

Narrowed in 11.30 (not retired). The second half of the question is answered for one writer: a task
of ours that wrote sa100, sa127, sa20, sa24, r20, r21, i0, i1 and set p0 to p3, and then called the
closed general task, kept the tick (E536, 3 of 3 rounds, tick 910.8 to 1005.4 Hz) and what it wrote
to sa100, sa127, sa20, sa24, r20, r21, i0 and i1 was read by the next task, after 1200 ms and (not
r20 and r21) after a client fill. The first half is not answered, and E537 makes it wider: a writer
that wrote two more sa (sa63 and sa65), set no predicate and called the closed task was not followed
by its armed reader within 100 ms (1 run, HostCtl dword 12 frozen in the dumps after it). Against
E533's task (which wrote an arbitrary pclink, p0 to p3 = 1, 0, 1, 0, and ended with `nop.end`),
E536's writer differs by no arbitrary pclink write (the tail triple's own write only, which every
pass makes), the tail call, and the p values (0, 0, 1, 1), so it shows the sa, r, i and p writes of
its list are not enough to stop the tick when the closed task follows; it does not separate skipping
the closed task from the arbitrary pclink write, nor from the p values. The pclink write cannot be
repeated with the fixed verifier of the fork (it refuses `mov pclink` outside the patched triple);
E533's task and E536's ran with the earlier one. To settle what remains of E533: `nop.end` after
E536's writes, with no arbitrary pclink write and no closed task (the control that separates the
missing closed task from the pclink write and the p values), predictions frozen first; the
differences inside E537 are the second half of this question, folded in below from the question that
asked them.

Reworded in 11.39 (merge 3: Q152, Q155 and Q156 in one question; the wording is drafted from the
three
landed texts and no new run bears on it). The known parts: E536's writer kept the tick and what it
wrote to sa100, sa127, sa20, sa24, r20, r21, i0 and i1 was read by the next task; E533 and E537
stopped it; sa65 held 0x02000000, the value of a tick's pa1, before any writer of E537; E536's
reader found p = 1, 0, 1, 1 and pclink 6 after the writer, pclink 0x98 and p1 = 1 after the
controls. Q156's candidates are one list: the predicates at the closed task's entry, the sa63 or
sa65 write, the sa64 write, the missing closed task, the arbitrary pclink write (not repeatable
with the fixed verifier of the fork). To settle it: the state3.s variants of Q155 and Q156 and the
control of this question (`nop.end` after E536's writes, no arbitrary pclink write), predictions
frozen first. The experiments wait for the `nop.end` stub.

Folded in 11.39 from Q155 (retired into this question; a fold is not an answer). Its question was:
why do p1 and pclink at the entry of the event after a writer of ours hold the writer's values (p1 =
0 and pclink = 6, the continue index of its tail call, in 3 of 3 rounds) when after an ordinary tick
they hold 1 and 0x98 (8 of 8 readings), and is the closed general task's path on that tick different
from its path on a tick that follows no task of ours

E536: after the writer of the state2 wrapper (sa, r and i written, p0 to p3 set to 0, 0, 1, 1,
a tail call to the closed task) the reader at the next event read p = 1, 0, 1, 1 and pclink 6,
while the two controls, the reader after 1200 ms and the reader after a fill read pclink 0x98 and
p1 = 1. p0 read 1 although the writer set 0, and p2 and p3 equal the writer's flags but also occur
in the other readings, so p1 and pclink are the registers that differ. Either the closed task
leaves pclink and p1 alone on the tick after our writer (it takes a path it does not take
otherwise, which would then depend on something we wrote, such as the flags or the stored command)
or the registers at the entry of a task are not what the previous task, the closed one, left. The
pclink value 6 is the one the writer's own tail triple wrote (`mov r30, #cont0; mov pclink, r30;
lapc`, which every pass of the wrapper executes, ours in command 0 too), and after a normal tick the
next entry reads 0x98, so the closed task rewrites it on a normal pass and did not after the writer
[infer]. That favours "the closed task took another path" over "the entry registers are not what
the previous task left", which would not explain the 0x98 after normal passes; neither is shown.

To settle it: the writer variants of state3.s (cmd 2 arm only, cmd 3 predicates only, cmd 1 with
the flags all 1), each three times, with cmd 4 (the writer whose armed reader did not run, E537)
last and a second stop ending the stage; Q156 asks what that stop depends on.

Folded in 11.39 from Q156 (retired into this question; a fold is not an answer). Its question was:
which of the differences between the writer whose armed reader did not run within 100 ms (E537: sa
and r and i written with sa63 and sa65, p0 = p1 = 1 at the tail call, 1 run) and the writer that was
not (E536: no sa63 and sa65, p0 to p3 = 0, 0, 1, 1, 3 of 3 rounds) stops the tick after the closed
task is called, and does the closed task use p0 to p3, sa63 or sa65 at all

Narrows Q152. E533's task skipped the closed task, E536's called it and kept the tick, and E537's
called it and did not. Candidates: the predicates the closed task finds at its entry (p0 = p1 = 1
against 0, 0, 1, 1), the write of sa63 or sa65 (sa65 held 0x02000000, the value of a tick's `pa1`),
the sa64 write (in both writers), and a first stop after a command that E536's rounds did not
see (E536 was 3 of 3, E537 1 of 1, and the two are different blobs). The writer of E533 and the
earlier wrappers (E532) are not controls: they differ in more than one of these.

To settle it: state3.s cmd 2, 3 and 1, each three times, then cmd 4 last, one reset at most per
stop, the stop rule first (a second stop ends the stage), predictions frozen after E537 and before
the first run. A repeat of cmd 4 alone would say whether the stop repeats.

Note 2026-11-10 (offline readings of E536's and E537's own data, made before the round 2 runs so
that their predictions are fixed against them; not new measurements; see the notes of E537 and
E536). E537's stop signature, from its register dump: `CR_CLKGATESTATUS` 0x000ccfa0 (busy, the
idle value is 0x20), `USE0_SERV_EVENT` 0x9e0 (bit 16 empty clear, the count not moving),
`EVENT_TIMER` 0x01038ec3 and `EVENT_STATUS` 0x20000000 [data]. [infer] The timer ran, events were
queued, and a USSE task stayed resident, so the closed task did not end (E154: its waits are
polls); a reset should be preceded by this dump on every stop. The sa65 the cmd-4 writer wrote,
0xb009c5dc, read as `pa1` (E155's layout) sets bits 4, 7, 8, 10 and 19 among others with no job in
flight, under a count byte of 0xb0, and its sa64 0xb0150d9d has bit 1 clear (not a tick) [data for
the words, infer for the reading]. The closed task dispatched on that word: the sa65 write is the
leading candidate for E537's stop, with a mechanism (a word asking for handlers no event raised);
it is not established, and the p0 = p1 = 1 predicates and the sa, r and i writes with them are not
excluded. Of E536's three sa64 markers all have bit 1 clear [data], so on those passes the closed
task may have skipped the tick handler, the reading that would leave pclink 6 and p1 as left at
the next entry (Q124) [infer, untested]. Hypotheses named for the next runs, to be frozen before
them: the alias hypothesis (all the closed task sees passes through sa64 and sa65), sa63 alone,
and p0 = p1 = 1 at the tail call with sa, r and i written.

Narrowed 2026-11-10 (R3-events stages a and b, E791 to E793; not retired). Two halves ran, with
their controls passing.
- No single write stops the tick (E791, 19 of 19 jobs kept it, no stop). sa63 alone, left at a
  marker (3 of 3, still read 1200 ms later), sa64 with the tick bit set or clear (3 and 3), sa65
  written with the value it held (3) or with a marker restored before the tail call (3), and the
  tail call with p0 = p1 = 1 and r20, r21, i0 and i1 written (2): H-63 and H-P11 are refuted.
  The sa65 word E537's writer left in place (0xb009c5dc) was not written by any row, so what stopped
  E537's writer (that word, the combination, or a stop that does not repeat: 1 run) is open; the
  rows that would leave such a word (A7, A8) were not run.
- Ending a tick pass without the closed task stops the tick (E793, 2 of 2): a task that logged its
  pass and ended with `nop.end`, with no sa, r, i, p or pclink write, was followed by no event, with
  E537's signature (busy `CR_CLKGATESTATUS` 0x000ccfa0, `EVENT_STATUS` 0x20000000, the timer
  counting, `USE0_SERV_EVENT` frozen): H-FREE (the hardware dispatches the next event after any
  task end) is refuted. A reset recovered both, as in E533. So skipping the closed task is enough
  for E533's stop, and the arbitrary pclink write, the p values and E533's sa, r and i writes are
  not needed for it (that they are harmless is not shown). The B2 rows (a skip of five ticks) did
  not run: the stage ended at its second stop.

**Correction 2026-11-10:** the inference of the note above, that the stop signature
(`USE0_SERV_EVENT` count frozen, a USSE task resident) means that the closed task did not end, is
withdrawn: the signature also follows a task that never called the closed task (E793), so it does
not locate the hang in it. The EDM appears to need something the closed task does at the end of a
pass (E155's tick handler does several things, among them the `EVENT_TIMER` write) [infer]; which
of them, and whether E537's writer stopped the tick for the same reason, is not shown.

Open: what the closed task does at the end of a pass that the EDM needs (candidates: the
`EVENT_TIMER` write of E155's tick handler, an acknowledge, a state store: a task of ours that
repeats one of them after its own `nop.end` pass, run only after the register-write limits allow
it, would separate them); what E537's stop depends on; whether the closed task reads sa63 at all
(sa63 is read back by the next task, E791 A1); p2 and p3 (Q124); the B1 control for a skip on a
kick pass (B3, not run).

Note 2026-11-10 (offline readings of kept data, of our disassembly and of the landed verifier, made
before the round 3 runs; not new measurements; see the notes of E537, E793 and E155). [HW, E792 and
E791] With sa64 = pa0 & ~2 the closed task left `pclink` at 6 (no call returned to 0x98) and the
tick was kept in 3 of 3, and no single write kept in E791 stopped it: the tick handler at 0x486 is
not what the EDM needs [infer: the dword 12 instrument said "cannot tell" within a bracket of +-8].
What remains common to every kept pass is the general task's entry code and the shared exit 0x1974
to 0x1978 (E793: `cfi.global` and a `phas` with `end` among its five instructions). [RE] The landed
verifier lets a continue patch name any slot 0 to 3 from any entry (`contK`), so entry 0 may
tail-call the closed task of slot 1, 2 or 3 (the fast paths at 0x59a, 0xace and 0xe0a) with no
kernel change; `br` cannot leave the blob, loads and stores cannot leave the results page, `nop` has
only bit 50 free, so a jump to 0x1974 or an exit form outside the 15 rows needs a kernel row. [RE]
The path of each fast path to the shared exit with no group bit of its own set (none reads `pa0`;
each starts `smlsi`, `mov r15, #0`, `mov r22, #0`), with `sa19` bit 3 clear: slot 2 (0xace) 12
instructions then the exit's 5, 17 in all, with no `sa19` test and no write beyond r0, r15, r16,
r22, r23 and `pclink`; slot 1 (0x59a) 20 (two `sa19` tests); slot 3 (0xe0a) 26 (two `sa19` tests,
three `pa1` tests). With `sa19` bit 3 set, slots 1 and 3 call the routine at 0x1979, which stores a
record to memory (a HWPerf record [infer]); no run of ours has read `sa19` there.
