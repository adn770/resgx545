+++
id = "E605"
claim = "In a firmware (EDM) task of ours (stage f14a, p1137_slow4, all four slots armed with slots=0xf entry=0,1,2,3, ticks only, no job and no host event), with slot 0 held in the slow loop for n = 10000 (2 jobs) and n = 100000 (3 jobs) iterations, the overlap flag of every slot stayed 0 and slots 1 to 3 counted 0 passes in 5 of 5 jobs, the task finished (done) inside the 400 ms window each time, no fault and one reset only; these two clauses could not have failed in this run (no event but the tick reaches slots 1 to 3, E538), so they show no more than that the tick reaches slot 0 only. The count clause of the prediction is not decided: slot 0's pass counter read 17, 17 (n = 10000) and 20, 20, 21 (n = 100000) against 0.8 to 1.3 and 6.2 ticks expected from the wall time of the job, and the tick counter's delta read 10, 10, 13, 12, 12; both carry an offset of about 10 ticks that the instrument (the tick counter read through the `regs` debugfs dump before the command and after the job, and the page after that) adds, and the difference between the two n, 2.3 ticks and 3.3 passes against 5.2 expected, is about half the wall time, as the lag of E539 (1.9 to 2.2 ticks behind) would give [infer]"
unit = "edm"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), stock firmware, kernel 7.3.0-resgx545, our firmware task p1137_slow4 armed with slots=0xf entry=0,1,2,3 (probes/p1136/asm/p1137_slow4.blob sha256 6401568edbb152593c7e6173cbac85156ad6f07980352b714c593341e8805698, 1080 bytes, accepted by the verifier), probes/p1136/run_1137.py through probes/p1136/run_1137_logged.py (one run), the remote command slowevent of probes/p1136/fwext1137.py with trigger none, after the frozen predictions (probes/p1136/predictions-1137.toml sha256 17f6cc52...) and manifest were verified; per job the page's pass counts, overlap flags and arrival logs (pa0 to pa2 of the first busy arrival of each slot), the HostCtl tick counter delta, the wall time and the expected ticks (997 per second); verdicts-f14a.json, the arm and reset records, env.toml and the journalctl -k of the stage are in the dataset"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-p1137-f14a"]
terms = []
+++

**What ran.** One arm with all four slots armed, five jobs: the task of slot 0 holds the EDM in a
slow loop of n iterations (10000 is about 0.7 ms, 100000 about 6.5 ms, E539), while slots 1 to 3
each run a counting handler that increments its pass counter and flags a pass that finds its state
busy, logging pa0 to pa2 of the arrival. No host event: the passes of the slots come from the tick
only (E538: a kick reaches slot 0 only). Slot 0's own loop counts its passes in the same way. The
seeds of the jobs repeat (1141 + k), so the arrival logs of jobs 0 and 2 and of jobs 1 and 3 are
identical.

**Results.** [HW] Overlap flags 0, 0, 0, 0 in all five jobs; slots 1 to 3 counted 0 passes and
their arrival logs equal the seeded sentinels (no arrival while busy) in all five; the arm's tick
rate was 969 Hz, after the final reset and gate 996 Hz and the gate's fill exact (0 of 2048; no
fill ran in this stage). Slot 0's pass counter and the tick-counter delta of each job:

| n | passes (slot 0) | tick delta | expected from wall time |
|---|-----------------|------------|-------------------------|
| 10000 | 17 | 10 | 0.8 |
| 10000 | 17 | 10 | 1.3 |
| 100000 | 20 | 13 | 6.2 |
| 100000 | 20 | 12 | 6.2 |
| 100000 | 21 | 12 | 6.2 |

**Against the predictions.** P37_F14a: the overlap and slots-1-to-3 clauses held (5 of 5) and could
not fail here: only the tick reaches slots 1 to 3, so nothing could make a slot find its state
busy; f14c (a client triangle during the task) could provoke it and was not run. The count clause
("passes at least 2 fewer than the expected ticks at n = 100000 in 2 of 3 jobs; none missing within
1 at n = 10000") is not met: passes are 14 to 15 above the expected ticks at n = 100000 and 16
above at n = 10000, and the falsifier ("passes equal to the expected in 2 of 3") does not trigger
either. The row is not confirmed and not falsified as to ticks: the quantity compared is not what
the prediction assumed.

**Why [infer].** The counters sit 7 to 9 passes above the ticks and 7 to 11 ticks above the wall
time of the job: the start tick is read before the command is written through the `regs` debugfs
dump and the end tick after the job, and the page after that; a dump of that file takes a time that
was not measured (the miscinfo debugfs read of the reset record took 3.6 ms), and slot 0 keeps
passing in the tick-driven idle during the reads. The offset is constant if the latency of the
dumps is, and the difference between the two n cancels it: from n = 10000 (mean wall time 1.1 ms)
to n = 100000 (6.2 ms) the expected tick gain is 5.2, the tick counter gained 2.3 (10, 10 to 13,
12, 12) and slot 0's pass count 3.3 (17, 17 to 20, 20, 21), that is 1.8 to 2.8 behind, the size of
the lag of E539 (1.9 to 2.2). That is a reading of five numbers, two jobs at one n and three at the
other, and not a measurement: no run reads the counter inside the task, so the offset, the slope
and the tick lag are not separated.

**What it shows.** [HW] With all four slots armed and a task of 0.7 or 6.5 ms in slot 0 and no
event but the tick, no slot found its state busy and none of slots 1 to 3 ran a pass, which is what
the stage was bound to give, as it provoked no arrival at them. [infer] So the tick reaches slot 0
only (consistent with E538 and E539). Whether a tick falling inside a long task is lost, queued or
delayed is not decided by this run; the differential reading above is consistent with E539's lag
and is a hint only.

**What it does not show.** The tick lag of E539 as a measurement (the instrument's reads are of the
order of the job), any overlap of slots (the stage could not provoke one), and f14b and f14c (a
kick and a client triangle during the task), which were not run in this phase: the follow-up stages
are run separately. A task whose pass counter is read from a window inside the job (the page read
with a short job time, or the tick counter read through a mapped register) would decide it
(answered by E752).
