+++
id = "E750"
claim = "A GETMISCINFO kick issued 3.4 to 3.6 ms after the command of a 90-period hold of the EDM by a task of ours (the hold's state read busy before the kick, 3 of 3) was not lost: the debugfs read was answered after 86.7 to 87.5 ms and the ring logged exactly one kick entry (pa0 0, pa1 bits 23:0 0x100, count byte 2, 3 and 4) 328 to 552 CR_TIMER units after the hold's exit in 3 of 3 jobs, scored QUEUED by the frozen classifier (the other discriminant, LOST, was no kick entry and no answer); the stage's gate stayed closed because its control, the same hold without a kick, which had to reproduce e4l's shape class, had no told shape on either side (every shape 'cannot tell', E749), so the held triangle stage e5t did not run in this session; the kick entries' pa2 (age 283.8 and 287.5 units for the first two, 22415 for the third) was read after the run"
unit = "edm"
method = "S2 stage e5c of the question-closing pass (ctl100 x2: n = 1500000, window 2, no trigger; kick100 x3: n = 1500000, window 1, GETMISCINFO through the debugfs 3 ms after the command, the hold's state read once before it), run 3, paths relative to edm/closing-s2/ of the dataset, run 1794265199-19105, on the laptop (direct cable), 2026-11-10 00:00, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1; ring_hold as E749, one arm; the hold is 2250015 CR_TIMER units (90.2 ms); the job is void unless the state reads busy once before the trigger; the frozen discriminants QUEUED (one kick entry within 5000 units after the exit) and LOST (no kick entry, no MISCINFO_READY), no favourite; the control compared with e4l by shape class, 'cannot tell' shapes dropped from both sides; scored by the frozen score/score_s2.py e5c; the kick's pa2 age and its place against the controls' bursts were read after the run"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-s2:out/e5c/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_KICK", "CR_EVENT_TIMER"]
+++
**What ran.** The same question asked what the EDM does with an event that arrives while a task of
ours holds it. Three GETMISCINFO kicks were sent during a 90-period hold, after two controls of the
same hold with no kick.

**Frozen verdict.** `GATE e5c CLOSED`: `control NOT reproduced {'reference': [], 'control': [],
'mismatch': []}; kick ['QUEUED', 'QUEUED', 'QUEUED']` (out/score-e5c.txt). The comparison had
nothing to compare: e4l's two shapes and the two controls' were all 'cannot tell' (E749). The
gate rule therefore closed the stage; e5t was not run. The kicks' own verdict does not depend on
the control comparison but, by the frozen rule, a closed gate means the session did not treat it
as established.

**Results [HW].** kick100, kick100-r2 and -r3: the kick at +3.41, +3.61 and +3.40 ms after the
window opened, the state busy each time; `GETMISCINFO answered after 87344, 86703 and 87460 us`
(E538's kick with no hold: 211 to 214 us); one kick entry in each ring, at +552, +551 and +328
units after the exit (the hold lasted 2250015 units, 90.2 ms), pa1 0x02000100, 0x03000100 and
0x04000100 (the count byte 2, 3 and 4 of E746, since the arm was one for the stage); no other
entry (window 1 does not log plain ticks), drops 0, busy flags 0. The controls' stamps are e4l's:
the four entries after the exit at +103 to +585 units, then the grid, window counts 74 and 74.

**Post hoc [infer; read after the run, not held out].** A host kick that arrives while a task of
ours holds the EDM is delivered once after the task ends and not lost, and the host's read waits
out the hold (0.2 ms became 87 ms). The kick's pa2 is not the time its pass ran: (400000 - pa2
bits 23:0) / 16 is 283.8 and 287.5 units for the first two (two arrival phases this close are
unlikely for a kick that arrived at random, so these were latched at a fixed point of the drain,
about 200 units after the exit) and 22415 units for the third, which was delivered earlier (+328);
with the queue of E749 that reads as the third kick latched on arrival into a free place and the
other two arriving with the queue full. Where the kick fell among the drained ticks is not visible
in window 1 (E752 logs it in window 2).

**Not shown.** Two kicks in one hold (merged or not), the kick's place in the drain order (E752),
a client job's events in a hold (E752), holds of another length, and a kick whose answer the host
does not wait for.
