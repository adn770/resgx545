+++
id = "Q152"
question = "what stopped the 1 kHz tick after a firmware task of ours that wrote sa, r, i, p and pclink state and ended with nop.end for one tick (E533: every later event stopped until a reset), and can a firmware task of ours leave state for the next task (items 12 and Q124) in a way that keeps the tick, for example by jumping to the closed general task after its writes"
unit = "edm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E533", "E155"]
terms = ["Event Data Master (EDM)", "CR_EVENT_TIMER"]
+++

E533: `HostCtl` dword 12 and `USE0_SERV_EVENT` stopped after a task of ours that ended with
`nop.end` for one tick (one run, the stage's own trigger), and a debugfs reset recovered. That task
did two things in the same run: it skipped the closed general task, and it wrote `sa64`, `sa100`,
`sa127`, `sa20`, `sa24`, `r20`, `r21`, `i0`, `i1`, `p0` to `p3` and `pclink`, then stored a command
for the next event. The cause is confounded: skipping the closed task, clobbering state the closed
task or the PDS needs, the `EVENT_TIMER` write of the tick handler (E155) that the closed task would
have made [infer], or something our command-1 path left undone are all consistent with the run.
Open: what exactly stopped the tick; whether a writer that jumps to the closed task after its writes
leaves its `sa`, `r`, `i` and `p` state to the next task (the closed task's own effects are then in
what a reader sees); and so item 12 and Q124 for a firmware task. To settle it: the controls that
separate them (the same writes then a jump to the closed task; `nop.end` without the writes), with
predictions frozen before their first run, and one task of ours reading `sa64`, `sa100`, `sa127`,
`sa20` and `sa24` after the closed task ran between.