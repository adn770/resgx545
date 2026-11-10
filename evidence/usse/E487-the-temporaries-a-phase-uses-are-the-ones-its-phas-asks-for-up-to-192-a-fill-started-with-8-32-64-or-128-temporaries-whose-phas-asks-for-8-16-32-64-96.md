+++
id = "E487"
claim = "The temporaries a phase uses are the ones its phas asks for, up to 192: a fill started with 8, 32, 64 or 128 temporaries whose phas asks for 8, 16, 32, 64, 96, 124, 128, 132, 136, 144, 160 or 192 for phase 1 (the 12 values run, all started with 8; 192 also started with 32, 64 and 128) reads back the marker it wrote to its highest register (r123 from 124 up) in all 15 jobs, and a request of 196, 200, 204, 208, 212, 216, 220, 224, 252, 256, 508 or 1020 hangs the job in all 15 jobs (196 also when started with 32, 64 and 128), each recovered with no reload, in a client pixel task (196 is the lowest request that hung and 192 the highest that ran, among the values run: every request run was a multiple of four, as the field counts in fours, and 100 to 120, 148 to 156, 164 to 188, 228 to 248, 260 to 504 and 512 to 1016 were not run; the 12 and 12 values are not an interval), whatever the task was started with (8, 32, 64 or 128 for 192 and 196); every request from 124 up wrote r123 only, r124 and up cannot be named by usse-asm, so a request above 124 exercised r123 and not the registers past it; the 15 jobs that ran took 420 to 583 microseconds, single samples, with no trend seen in the request"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/temps-past.toml probe phas-request (10 cases), probes/usse/temps-bound.toml (7 cases: 132, 136, 144, 160, 192, 224, 252), temps-bound2.toml (7 cases: 196, 200, 204, 208, 212, 216, 220) and temps-bound3.toml (3 probes started with 32, 64 and 128 temporaries, 192 and 196); the risky probes one at a time, probe.py first (outside the data) and then the campaign (the dataset; the same outcome in 10 + 7 + 7 + 6 = 30 of 30 cases of the four tables, 15 ran and 15 hung), a health triangle after each (clean in all)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-temps-past", "usse-temps-bound", "usse-temps-bound2", "usse-temps-bound3"]
terms = []
+++

**What runs.** A two-phase fill: phase 0 (the run's --temps, 8, 32, 64 or 128) does nothing, `phas
#2, #T, pixel, none, parallel` asks for T temporaries for phase 1 (the field counts in fours up to
1020), and phase 1 writes 0x7E57007B to r123 (r(T - 1) for T of 124 or less), reads it back and
stores it. T = 8, 16, 32, 64, 96, 124, 128, 256, 508 and 1020 in temps-past, 132, 136, 144, 160,
192, 224, 252 in temps-bound, 196, 200, 204, 208, 212, 216, 220 in temps-bound2.

**Results.** Requests of 8 to 192: the marker back in all 15 jobs (T = 192 also when started with
32, 64 and 128). Requests of 196 and up: the job hung (15 of 15: 196, 200, 204, 208, 212, 216 and
220 seven, 224, 252, 256, 508, 1020, and 196 started with 32, 64 and 128); each hang was reported
as `job hung, context lost`, the GPU was reset by the driver and the next health triangle was
clean, with the module unchanged. The job times of the 15 jobs that ran (wall time from the kick to
the wait): 420 to 583 microseconds, median 491, with no trend in the request (192: 568, 549, 517,
491; 8: 468).

**What it shows.** [HW] A phas request is the task's allocation for the phase: registers past a
phase's request read back wrapped (E486), and a request of up to 192 runs and r123 works in a job
started with 8; registers 124 to 191 were never addressed (r124 and up are not encodable by
usse-asm as ALU operands), so the data show that the job runs and that r123 is real storage, not
that 192 temporaries are usable. The bound that matters to a toolchain, the register numbers a
program can name, is 123. [HW] The 12 requests 196 to 224 (in fours), 252, 256, 508 and 1020 hung
the job, and 192 was the highest value run that did not; 228 to 248 and 260 to 504 were not run, so
this is the 12 values, not an interval, with no dependence seen on the allocation the task started
with (8 to 128, for 192 and 196). [infer] The first request that hangs is probably the one that
does not fit the register file for all the instances the phase runs (192 x the instances in
flight), not a field limit (the field takes 1020). The job times show no cost in single samples
(420 to 583 microseconds; 192 gave 568, 549, 517 and 491 against 433 to 496 for the requests up to
128), which is not a trend test.

**What it does not show.** The exact limit between 193 and 195 (the field counts in fours: 192
passes, 196 hangs); the other multiples of four from 8 to 192, 228 to 248, 260 to 504 and 512 to
1016 (not run); a request of more than 124 as anything but r123 (r124 and up are refused as ALU
operands by usse-asm [infer], E485); the same limit for a firmware (EDM) task, whose temporaries
the microkernel requests itself (Q133).

**Correction, 2026-11-08 (11.27).** The measurements above are unchanged. E519 shows that the 12
values that ran and the 12 that hung are not an interval: a request T ran when T mod 256 was 4 to
192 and hung the job when it was 0 or 196 to 252, in every request run since: 100 to 120, 148 to
156, 164 to 188 and 260 to 448 (every multiple of four there, 64 requests) ran, 228 to 248 and 452
to 504 (20 requests) hung, and of 15 requests from 512 to 1016 chosen by that rule 8 ran and 7 hung
as predicted (15 of 15; the rule was written after the 64 + 20 and tested on these 15). So 'the
highest value that did not hang is 192' holds below 256 only, 'not run: 228 to 248, 260 to 504 and
512 to 1016' is mostly run, and the 196 to 256 hang is part of the rule E519 fitted (84 requests)
and tested (15 of 15); what a request above 256 allocates is not measured (E519 does not show
whether a write reaches a register under a small allocation: Q132, Q133), and r123 is still the only
register above 124 any of these jobs wrote. Q133 is narrowed and Q133 asks the rest.

**Correction, 2026-11-09 (11.35).** The measurements above are unchanged. The sentence that the job
reads back "the marker it wrote ... in all 15 jobs" did not tell a write that landed from a stale
read for every job (E484): the jobs T = 8, 16, 32, 64 and 96 wrote r7, r15, r31, r63 and r95
(registers no earlier job of the campaign's table order had written, but probe.py had run the same
table on the same boot first, with the same marker, so that is not a separation either; E535's
controls T = 8, 32 and 64 with r3, r31 and r63 and its negative at T <= 100 cover part of them); T =
124 and 128 are shown by E535 with a marker of its own; the jobs T = 132, 136, 144 and 160 (started
with 8) and T = 192 (started with 8, 32, 64 and 128) wrote r123 after the T = 124 job had left the
same value there, so their read-back could have been a leftover. E594 reran those 8 jobs with a
marker of its own in each: 8 of 8 read their own marker in 2048 of 2048 pixels, none hung. The
reading holds for them, on E594's evidence and no longer on this record's alone.
