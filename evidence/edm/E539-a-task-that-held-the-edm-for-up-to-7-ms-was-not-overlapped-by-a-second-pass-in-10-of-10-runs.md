+++
id = "E539"
claim = "A firmware task of ours that sets its state flag to busy, spins n iterations of a three-instruction loop (ima32, a test, a branch) and sets the flag to done, with every wrapper pass that finds the flag busy storing an overlap flag, ran 10 times (n = 10000 four times, 30000 and 100000 three times each) with the overlap flag 0 in 10 of 10 runs, taking 0.73 to 0.97 ms (n = 10000), 2.07 to 2.43 ms (30000) and 6.21 to 6.92 ms (100000) from command to done as the host saw it, and HostCtl dword 12 counted 38 to 42 ticks in the 38.2 to 44.3 ms windows: within 2.2 of the 0.997 ticks per ms expected in all 10 runs (none more than 3 behind, the run's limit), +1.7 to -0.7 in the seven runs of n = 10000 and 30000 and 1.9 to 2.2 behind in the three of 100000"
unit = "edm"
method = "as E531: asm/fwtask/slow.s (39 instructions, blob sha256 683dd70ddf06...a7a1b, the 11.29 source unchanged); the host cleared the state flag and the overlap flag, wrote n and the command last, polled the state flag for done, then 30 ms later compared HostCtl dword 12 with its value at the command; prediction I11_overlap (overlap_runs == 0 and lost_ticks == 0, lost meaning more than 3 ticks behind) frozen before stage B (predictions-1130.toml sha256 d8c677cd...27197). Run p1130-d-slow, tool sha256 54eb8909...e56e, one run of 10 jobs in the order 10000 x 4, 30000 x 3, 100000 x 3, timeouts 100 and 300 ms, no stop trigger. A firmware task, not a client pixel task; no fill or triangle gate ran in it. The module and its verifier as E536 (the fixed verifier was not used; it accepts slow.s)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["firmware-tasks-slow-task", "vectors-usse-fwtask-p1130"]
terms = ["Event Data Master (EDM)"]
+++

**Results.** [HW] Command to done, as a poll of the page saw it: 0.73, 0.81, 0.79 and 0.97 ms
(n = 10000), 2.43, 2.19 and 2.07 ms (30000), 6.28, 6.92 and 6.21 ms (100000): 62 to 69 ns per
iteration at 100000 (three instructions, about 21 to 23 ns each), more at the smaller n because the
polling latency is spread over fewer iterations. The overlap flag stayed 0 in all 10 and the state
flag read done at the end. Ticks counted in each window: 40, 38, 38 and 39 (n = 10000; expected
38.3, 38.4, 38.7 and 38.1), 39, 39 and 39 (30000; 39.6, 39.6 and 39.4), 42, 42 and 42 (100000;
43.9, 44.2 and 43.9).

**Prediction.** I11_overlap held: overlap_runs 0 and no run more than 3 ticks behind.

**Reading.** [HW] No wrapper pass found the state busy: no second pass of the wrapper started in the
EDM while a task of ours ran, up to 6.9 ms (about six tick periods, ticks only: no TA or 3D event
ran, one slot, no job). The flag sees a pass that starts after the task's busy store and before its
done store and finds busy; it cannot see a pass that starts before the busy store, a pass of another
slot with its own stub, or an event that is queued or dropped, so "no overlap" holds for a
tick-only, slot-0 stream and for nothing wider. [infer, not decided by this run] The three runs of
100000 counted 1.9 to 2.2 ticks fewer than expected while the task blocked the EDM for about six
periods, against +1.7 to -0.7 in the other seven: at most two of the six ticks of the busy window
were lost and the others were served after the task, or the counter is not the tick handler's alone;
the run's limit of 3 could not tell one from the other, and a design that counts the handler's runs
in the window (a flag per tick, not a counter) is the follow-up.

**Not shown.** A pass that starts before the busy store, overlap of tasks of different slots, or of
a tick with a TA or 3D event (no job ran), whether events that arrive meanwhile are queued or
dropped (Q131), and any task longer than 7 ms.
