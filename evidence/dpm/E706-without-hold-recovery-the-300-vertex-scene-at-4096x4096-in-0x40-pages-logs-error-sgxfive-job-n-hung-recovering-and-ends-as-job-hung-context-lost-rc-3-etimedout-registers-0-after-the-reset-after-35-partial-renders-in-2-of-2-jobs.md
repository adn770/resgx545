+++
id = "E706"
claim = "Without hold_recovery the 300-vertex scene at 4096x4096 in 0x40 pages logs `*ERROR* sgxfive: job N hung, recovering` and ends as `job hung, context lost` (rc 3, ETIMEDOUT, registers 0 after the reset) after 35 partial renders in 2 of 2 jobs (a run and its repeat), the same job with hold_recovery logs the line and `recovery held` and ends as an overflow (-ENOSPC) after 47 partial renders in 2 of 2, and 450 vertices in 0x100 pages overflow after 16 partial renders with no hung line with and without the hold (2 of 2): the line does not need hold_recovery, and E438's hang is a driver-side recovery that the hold does not cause, not a hardware stop; what triggers the recovery (a time, a count, no progress) was not read; the frozen model in which the line needs hold_recovery was wrong in the no-hold condition (2 jobs, a run and its repeat)"
unit = "dpm"
method = "table dpm-hang (6 jobs, risky: 300 vertices in 0x40 pages with and without hold_recovery, two runs each, 450 vertices in 0x100 pages with and without; probe --tri pixel --width 4096 --height 4096, regtimeline over 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x0724 and 0x0748; after every hung job a reset and a health triangle that drew), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["Dynamic Parameter Management (DPM)"]
+++
**What ran.** E630 reproduced 2 of E438's 3 hanging cases with hold_recovery armed, and ended them
as overflows after 47 and 92 partial renders; the same cases without the hold, which would show that
the line is the kernel's and not the hold's, were not run (E630's `[infer; not run]`). Here: 300
vertices in 0x40 pages without hold_recovery (and a repeat), with it (and a repeat), and 450
vertices in 0x100 pages with and without it. Frozen: HH (the line needs the hold: not logged without
it), HL (the 300-vertex case logs it, with and without the hold; 450 vertices not predicted).

**Results.** [HW] 300 vertices, 0x40, no hold (2 jobs): `job N hung, recovering` once each, no
`recovery held`; the tool ends `job hung, context lost (Connection timed out)`; the timeline ends at
status 0 (the reset, as E438 saw) after 35 partial renders, 1.03 s between the first status and the
last change (1.033 and 1.035 s). With the hold (2 jobs): the hung line and `job N hung, recovery
held (debugfs hold_recovery)`, the tool ends `scene overflowed the parameter buffer, context kept`,
47 partial renders over 1.378 and 1.375 s, the last status 0x2d. 450 vertices, 0x100, hold and no
hold: no hung line, the tool ends as an overflow, 16 partial renders over 0.50 s, threshold 0xde,
last status 0xf9. HL 4 of 4, HH 2 of 4 (both no-hold jobs of 300 vertices logged the line where HH
said no: one condition, a run and its repeat, enough to refute HH). The 300-vertex jobs repeat E438
(24 of 24 hung at 300 vertices and more in 0x40 and 0x23 pages and at 900 and 1500 in 0x100) and
E630, so HL's 4 of 4 is in sample; the held-out part is HH, refuted.

**Length.** [HW] The jobs that logged the line ran 1.03 s (no hold) and 1.38 s (hold) between the
first status and the last change; a job without a line ran 0.50 s here, and E630's table has
overflowing jobs that ran as long (up to 1.40 s) with 22 to 33 partial renders and no line (the
recompute of that table, hang_len.py). So the length of the job alone does not separate them. The
partial render counts are 35 and 47 (and 92 in E630) with the line, 16 here and 22 to 33 in E630
without; they are the counts at which the jobs ended (the no-hold job's is cut by its stop, the
others end in an overflow), not thresholds, and more renders also take longer, which this table
does not separate: no rule about a count follows.

**What it shows.** [HW] The line, the reset and the lost context at 300 vertices in 0x40 pages
happen without hold_recovery, and with it the same job logs the line and then runs on to its
overflow: the hang of E438 is a driver-side recovery that the hold does not cause, as E630 read
(infer there), now shown by the run that was missing; it is not a hardware stop. [infer] What
triggers the recovery (a period, a count of events, no progress) was not read in this batch (a
kernel question): the time between the first status and the line cannot be read as a period, since a
job starts before its first status, and 1.03 s (no hold) is shorter than overflowing jobs without a
line in E630 (up to 1.40 s).

**Not shown.** 900 and 1500 vertices in 0x100 pages (the other two of E438's cases), the trigger
of the recovery, and why this scene takes 35 or more partial renders.
