+++
id = "Q197"
question = "what is the pass count of the tick-driven slot against the tick counter while the EDM is held by a task of 0.7 to 6.5 ms (and above), and is a tick that falls inside a long task lost, queued or delayed"
unit = "edm"
kind = "fw"
phase = 11
evidence = ["E539", "E605"]
terms = []
+++
E539 (tick only, slot 0, up to 6.9 ms) saw the counter 1.9 to 2.2 behind the expected ticks. E605
(all four slots armed, tick only, 0.7 and 6.5 ms) kept the overlap flags at 0 and slots 1 to 3 at 0
passes, but its comparison of the pass count with the tick count is not decided: the tick counter
is read through the `regs` dump before the command and after the job and the page after that (the
dump's duration is not measured), so passes (17 to 21) and ticks (10 to 13) both carry an offset
of about 10 against the expected 0.8 to 6.2 from the job's wall time. The difference between the
two task lengths (2.3 ticks and 3.3 passes against 5.2 expected) is consistent with E539's lag,
from five jobs.

To settle it: an instrument that stamps the job inside the task (the task reads the tick counter
register at entry and at exit, through a register read it may do, and stores both, so the host
reads only the page), and a table of task lengths from 0.3 ms to 20 ms (the E539 lag grows with
the task, Q033's follow-up needs more than 7 ms). f14b (a host kick) and f14c (a client triangle
during the task, hold_recovery as q033q2) were not run and stay prepared.
