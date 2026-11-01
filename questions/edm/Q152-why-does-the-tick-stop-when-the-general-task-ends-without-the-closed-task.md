+++
id = "Q152"
question = "what stopped the 1 kHz tick after the task of E533 (nop.end instead of the closed general task, after writes of sa, r, i, p and pclink: every later event stopped until a reset), when a writer that calls the closed task after the same writes but pclink keeps it (E536, 3 of 3 rounds) and another that called it after also writing sa63 and sa65 did not (E537, 1 of 1)"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E533", "E155", "E536", "E537"]
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
differences inside E537 are Q156.
