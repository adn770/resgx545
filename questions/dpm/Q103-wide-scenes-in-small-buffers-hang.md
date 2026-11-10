+++
id = "Q103"
question = "why does a scene of 100 to 500 triangles take 35 or more partial renders where the one-triangle scene overflows the parameter buffer and recovers, at 4096x4096 in 0x40 or 0x23 pages from 300 vertices and in 0x100 pages from 900 (the stop E438 called a hang is the kernel's recovery, Q278 decided)?"
unit = "dpm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E310", "E312", "E438", "E630", "E706"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++
 E438 ran the triangle and copies of it (3 to 1500 vertices) on a 4096x4096 and a 1024x768 target
in 0x422 to 0x23 pages, three runs of each case. At 4096x4096 the 3-vertex scene in 0x100, 0x40 and
0x23 pages overflows and the job fails with its context kept (-ENOSPC, 9 of 9), as E311 found;
scenes of 300, 900 and 1500 vertices in 0x40 and 0x23 pages hang (18 of 18 jobs), and in 0x100
pages 300 vertices overflow (3 of 3) and 900 and 1500 hang (6 of 6). At 1024x768 in 0x23 pages 3,
300 and 1500 vertices overflow and recover (9 of 9), and 4096x4096 in 0x422 pages overflows at 900
and 1500 and recovers. So the hang depends on the scene's size and the buffer's together, and the
registers read 0 after it. Whether the TA, the DPM's partial render or the final render hangs, and
whether the pages run out before the first partial render can free any, is not read: E186 found
that a hung job's memory does not show how far it got.

To settle it: the render memory of the hung jobs against the overflowing ones (the runs' dumps are
in the dpm-partial-wide data), the free list's head and tail registers through a hung job with a
timeline (regtimeline), and the hang with the TA's page threshold raised (kpoke pb).

Narrowed in 11.38 (E630). With `hold_recovery` armed, 2 of the 3 cases that E438 saw hang (300
vertices at 4096x4096 in 0x40 and 0x23 pages; 900 vertices in 0x100 pages was the third) logged
`*ERROR* job hung, recovering` and `recovery held (debugfs hold_recovery)` in the kernel journal
about 2 s after the case began, and ended as overflows with the context kept (-ENOSPC) after 47
and 92 partial renders; the 900-vertex case (33 partial renders, last register change at 1.85 s)
logged nothing and no other wide-scene job of the 28 logged a hung, fault or reset line. So E438's
hang is reproduced in 2 of 3 cases, and with the recovery held the job ran on, with very many
partial renders, to its -ENOSPC. E438's hang is read as the kernel watchdog's recovery, a reset,
after which the registers read 0 [infer; not run: the same cases without `hold_recovery`]. What
differs from E438's batch is the module (F156823E there, B21FDA82 here), the tool, regtimeline
polling during the job, and the hold. Open: is it the watchdog (settle it with no `hold_recovery`,
one run, the same three cases, and the watchdog's period in the kernel), why the 900-vertex case
did not log the line while E438 saw it hang, and the partial-render count at which the watchdog
fires.

Narrowed in 11.39 (E706). Without hold_recovery the 300-vertex scene at 4096x4096 in 0x40 pages
(2 of 2) logs `job N hung, recovering` and ends `job hung, context lost` after 35 partial
renders, with the registers 0 after the reset; with it (2 of 2) the line and `recovery held`
are logged and the job ends as an overflow after 47 partial renders; 450 vertices in 0x100
pages (2 of 2, with and without) overflow after 16 partial renders with no line. E438's hang is
a driver-side recovery that the hold does not cause, as E630 read, not a hardware stop; the model
in which the line needs the hold was wrong in the no-hold condition (2 jobs, a run and its
repeat). The length alone does not separate the logged jobs from the others (1.03 and 1.38 s
against 0.50 s here and up to 1.40 s in E630), and the partial render counts (35 and 47, and 92,
against 16 and 22 to 33) are where the jobs ended, not thresholds, with the time confound not
separated: no rule follows. Open: what triggers the recovery (a kernel question, parked), 900 and
1500 vertices in 0x100 pages, and why a scene takes 35 or more partial renders.

The premise "a scene size hangs" is not retired here: that needs the user's acceptance, and
E438's cells at 900 and 1500 vertices in 0x100 pages were not run without the hold. What triggers
the kernel's recovery is a kernel-kind part, moved to Q278 (parked); the hardware part that stays
is why a scene takes 35 or more partial renders.

**Correction 2026-11-10:** the premise "a scene size hangs" is retired, and the question is narrowed
to why a scene takes 35 or more partial renders. The stop E438 called a hang is the driver's
recovery (E706, E630), and our kernel source says when it fires: `sgxfive_sched.c` (linux fork
branch resgx545, tip 3702e0aa3e827) declares `SGXFIVE_JOB_TIMEOUT_MS` as 500 (line 25) and its timeout
handler (`sgxfive_timedout_job`, lines 107 to 120) recovers when the oldest unfinished job is the same at two
consecutive timeouts, so after about 1.0 to 1.5 s without progress in the queue, not on a count of
partial renders nor on a register. That fits the logged jobs (1.03 and 1.38 s) and E630's 1.40 s job
without the line if a completion re-armed the timeout [infer]. Q278, which asked for that trigger,
is decided in doc/specs/3d.md. Not run, still the evidence for the narrowed question: 900 and 1500
vertices in 0x100 pages without the hold, and a timeline of the partial render count against the
registers below and above 35.
