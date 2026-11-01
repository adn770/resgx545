+++
id = "E536"
claim = "A firmware task of ours (state2.s, cmd 1) that wrote sa64, sa100, sa127, sa20, sa24, r20, r21, i0 and i1 (a random value each, none equal to anything the controls read) and set p0 to p3 to 0, 0, 1, 1, armed a reader for the next event and then tail-called the closed general task, left the EDM running (tick rate 910.8 to 1005.4 Hz after each of the 9 steps, 3 writers, 3 readers after 1200 ms and 3 readers after a client fill, the 3 fills diff 0 of 2048; no stop trigger, no log line, no reset), and the reader the writer armed ran at the next event (the writer's flag 0.42, 0.47 and 0.70 ms after the command, the reader done 1.50, 1.53 and 1.74 ms after it) and read the values written for sa100, sa127, sa20 and sa24 (12 of 12 values in 3 of 3 rounds), r20 and r21 (6 of 6), i0 and i1 (6 of 6), p1 = 0 (3 of 3, against 1 in all 8 other readings) and pclink = 6 (3 of 3, against 0x98 in the 8 readings of the controls, the 1200 ms readers and the fill readers; [infer] 6 is the value the writer's own tail triple wrote, a write every pass of the wrapper makes), p2 and p3 = 1, 1 (as written, but also 1, 1 after 1200 ms, 0, 0 in the controls and 0, 1 after a fill: they move between readings with no writer in between, so they show nothing), but sa64 = 2 (3 of 3, as in both controls) and p0 = 1 (written 0); 1200 ms (1200 ticks of the closed task) later sa (12 of 12), r (6 of 6) and i (6 of 6) were still there, and a client fill between left sa (12 of 12) and i (6 of 6) and replaced r20 and r21 (r20 = 0 and r21 = 0x1000, 0x2000, 0x3000: 0 of 6 values ours)"
unit = "edm"
method = "as E531 (srcversion 7ED723C25D78D7FCB3C08C1, fork tip d614af574cc6, own_arm slots=0x1 entry=0 trc=8): asm/fwtask/state2.s (97 instructions, blob sha256 df82c85410fe...d7ebc; the entry captures pclink, p0 to p3, r20, r21, i0 and i1 before anything else, then reads cmd; cmd 1 writes the nine values from parameters and p0 to p3 from flags, stores cmd = 9, the run id, idf, wdf and the state flag and tail-calls the closed task; cmd 9 stores what was captured and reads sa64, sa100, sa127, sa20 and sa24), run by tools/fwtask/run_stage.py stage b with predictions frozen before the stage (predictions-1130.toml, sha256 d8c677cd520c8304aa60c5f10a1743cab132a032c60671d85306644836827197; its 10 stage-B rows); two controls (reader only), then 3 rounds of writer, reader at the next event, reader after 1200 ms and reader after a client fill, hold_recovery set; the host's markers are random (seed 1130) and the predicate flags the complement of the control's p. Run p1130-b-tailpair, one run, tool sha256 4a4b0330...e2fb. The tool's evaluation of the stage crashed after the hardware part (the expression evaluator lacked the builtins len and set), the data had been saved, and the evaluation was repeated offline from the saved files (tools/fwtask/rejudge_b.py, no laptop), after which the tool was fixed (the later runs have another tool hash); the kernel log of the window was saved by hand. A firmware task, not a client pixel task. The module was the one built before the verifier review: the verifier it ran had bypasses, fixed later; the fixed verifier was not used for this run (it accepts state2.s)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-tail-pair", "vectors-usse-fwtask-p1130"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++
 **Controls (no writer).** [HW] Both controls read pclink 0x98, p0 to p3 = 1, 1, 0, 0, r20 = 0, r21
= 0x1000, i0 = 0xb5000020, i1 = 0xb5000021, sa64 = 2, sa100 = 0xa5000064, sa127 = 0xa500007f, sa20 =
sa24 = 0, the same in both. The values of i0, i1, sa100 and sa127 are those that the writer of phase
11.29 (E533, state.s) wrote, 15 minutes before (E533's task ran at 22:16 and these controls at
22:32), with a debugfs reset, the stock check after it and the firmware reload of this run's arming
in between: those four survived a reset and a reload. The other values that writer wrote did not
survive: sa20 and sa24 read 0, not 0xa5000014 and 0xa5000018 [infer: the load or the closed code
writes them, not tested], sa64 reads 2, not 0xa5000040 (the one this phase's writer could not set
either, below), and r20 and r21 read 0 and 0x1000, not 0xb5000020 and 0xb5000021 (client fills
replace them, below).

**What ran.** Nine steps after the controls: three times a writer (cmd 1; the reader it armed ran at
the next event and is read in the same step), a reader after 1200 ms, a reader after a client fill
(diff 0 of 2048 each). That is 11 reader captures in all: 2 controls, 3 at the next event, 3
after 1200 ms and 3 after a fill. Writer flag at 0.42, 0.47 and 0.70 ms after the command, reader
done at 1.50, 1.53 and 1.74 ms. EVENT_STATUS2 0x400 throughout, 0 resets, tick rate (a 100 ms
window after each step) 989.1 to 1005.4 Hz except one window of 910.8 Hz (the first 1200 ms
reader); the stage's criterion was 900 to 1100 Hz.

**Readings (3 rounds each).** [HW]
- next event: sa100, sa127, sa20, sa24 = the writer's values (12 of 12); r20 and r21 (6 of 6); i0
  and i1 (6 of 6); p = 1, 0, 1, 1 (p0 is 1, not the 0 written; p1 is the 0 written; p2 and p3 are 1,
  1 as written but read 1, 1 after 1200 ms too); pclink 6 [infer: the value of the writer's own tail
  triple]; sa64 = 2.
- after 1200 ms: sa (12 of 12), r (6 of 6) and i (6 of 6) unchanged; p = 1, 1, 1, 1; pclink 0x98
  (the controls read p2, p3 = 0, 0).
- after a client fill: sa (12 of 12) and i (6 of 6) unchanged; r20 = 0 and r21 = 0x1000, 0x2000,
  0x3000 (0x1000, 0x2000 and 0x3000 in the three fills, and E537's first control read 0x3000 again:
  [infer] a counter the fills leave, +0x1000 each); p = 1, 1, 0, 1; pclink 0x98. So p2 and p3 are
  0, 0 in the controls, 1, 1 after 1200 ms and 0, 1 after a fill, with no writer in between: they
  are no baseline.

**Predictions (judged apart from the stage).** The stage passed on its own criteria (the writer and
the reader ran in every round and the tick went on). Of the 10 rows frozen for stage B, 4 held on
their claim (B_alive, B_ctl_stable, B_sa_low_next and B_i_kept), 1 formally (B_p_gone, below) and
**5 failed**: B_sa_high_next, B_sa_gap and B_sa_fill failed only through sa64 (sa100 and sa127 were
as predicted in all three rounds), **B_r_gone failed** (r20 and r21 persisted at the next event and
after 1200 ms; the row compares a tuple, so one register kept would have failed it and both were
kept), and **B_pclink_const failed** (6 at the next event, 0x98 elsewhere). B_p_gone held on its
expression only (p_vals != pattern, because p0 differs) and does not count as a pass of its claim,
that predicates are not retained, which p1 falsifies: the row's expression was too weak. p1 is 0
only at the next event (3 of 3, against 1 in the 8 other readings); p2 and p3 equal the pattern but
also occur elsewhere. A row for r20 and r21 after a client fill was not frozen.

**What it shows.** [HW] A writer that calls the closed general task after its writes leaves the
EDM running: the sa, r, i and p writes of this list do not by themselves stop the tick when the
closed task follows (3 of 3 rounds). State written by a firmware task of ours outlives the closed
task that runs after it and 1200 ticks of it: sa100, sa127, sa20, sa24, r20, r21, i0, i1; a client
fill replaces only r20 and r21. sa64 did not take the writer's marker [infer: the closed code
writes it, or it is not an ordinary sa; it reads 2 in every reading, controls included]. **[infer,
open: Q152]** At the next event p1 holds the 0 the writer set and pclink 6, while
after an ordinary tick they hold 1 and 0x98. Every pass of the wrapper, ours in command 0 included,
writes pclink in its tail triple (`mov r30, #cont0; mov pclink, r30; lapc`), and 6 is the value of
that triple [infer], so after a normal tick the closed task rewrites pclink (0x98 at the next
entry) and after the writer it did not. That favours that the closed task took another path on
that tick over the registers at a task's entry not being what the previous task left (which would
not explain 0x98 on the normal passes).

**E533's confound.** E533's task wrote the same list plus an arbitrary pclink value (and the stored
cmd) with p0 to p3 = 1, 0, 1, 0, and ended with `nop.end`, without the closed task. This run differs
in more than two things: no arbitrary pclink write (only the tail triple's own write, which every
pass makes), the closed task is called, the p values (0, 0, 1, 1 against 1, 0, 1, 0), the markers
and the stored command. It therefore shows that the sa, r, i and p writes of this list, with the
closed task after them, do not stop the tick; it does not separate skipping the closed task from the
arbitrary pclink write, nor from the p values, as E533's cause, and E537 shows that a task that
calls the closed task can stop the tick as well (Q152).

**Not shown.** What the closed task does when the writer's p, sa or r differ (E537 has one writer
that stops it), more than one instance or a second task slot, the effect of a reset on i and sa in
general (Q158), an arbitrary pclink write (the verifier of the fork as fixed refuses it), and the
tick rate after the reader at the next event (the rate window follows the step).
