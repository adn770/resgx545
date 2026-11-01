+++
id = "E630"
claim = "Of the 3 wide-scene cases that E438 saw hang (300 vertices at 4096x4096 in 0x40 and 0x23 pages, 900 in 0x100 pages) the 2 of 300 vertices logged, about 2 s after the case start in the kernel journal, `*ERROR* sgxfive: job hung, recovering` and `recovery held (debugfs hold_recovery)`, and still ended as overflows with the context kept (-ENOSPC) after 47 and 92 partial renders counted by the 0x0658 stretches (the 900-vertex case, 33 partial renders, ended its timeline at 1.85 s and logged nothing): E438's hang is reproduced in 2 of 3 cases and the held recovery let the job run on, so that reading it as a hardware stop is not supported (infer: a kernel watchdog on a long job with many partial renders, delayed here by hold_recovery); the other 25 jobs of the 28 (among them 600, 750, 801 and 849 vertices at 0x100 pages, with 22 to 32 partial renders) logged no hung, fault or reset line; the global list is 4 pages (list entry 16: count 4, head 1, tail 0x35c) and TA3DCtl dword 36 is 2 at 900, 1050, 1200 and 1350 vertices in 0x422 pages (1 partial render) and 5 pages and 3 at 1500 (2 partial renders): a step between 1350 and 1500 vertices, E438's two cells fitting and no rule for dword 36 (E438 read 1 with a one-page list and 0 with one or two pages elsewhere); the high halves of STATUS2 (0x0710, 0x071c) read 0 in every line of the 65 timelines that kept 0x0748 and the STATUS2 registers (21 of 21 scores); 0x0748 bit 2 clear (the values 0xb and 0x1b) in a line of 23 of those 65 jobs, 66 lines in all, each of one reading, and in 10 of the 16 `wd-bit2` runs (300 vertices 5 of 8, 450 vertices 5 of 8; after a reset 4 of 8, without one 6 of 8)"
unit = "dpm"
method = "probe --tri pixel with the plain green pixel program and --vertices N (300 to 1500 vertices, 4096x4096, 0x422 to 0x23 pages) on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...), regtimeline over 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x0724 and 0x0748 (read-only) during each job, the risky script with debugfs hold_recovery armed on the first three hang cases (the held copies of regs, the control block and the render memory read after the tool's timeout), the kernel journal cut per case by a marker; the 28 jobs of table wide and 2 reruns"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_TASK_STATE", "ta3d_ctl"]
+++

**What ran.** Table `wide` (28 jobs that ran): 5 `wd-glist-*` (probe `--tri pixel` with the plain
green pixel program, 4096x4096, 900 to 1500 vertices in steps of 150, 0x422 pages), 16 `wd-bit2-*`
(300 and 450 vertices, 0x100 pages, eight runs of each alternately after a reset and without one:
the `noreset` jobs), 5 `wd-hang-*` accepted by the tool (the risky script, `hold_recovery` on the
first three: after the tool's timeout the script copies `regs`, the control block and the render
memory before the reset), and a rerun of the two that the tool refused (800 and 850 vertices are
not whole triangles: rc 2 with the usage text, kept; 801 and 849 vertices under new names). Same
laptop, kernel, module, firmware and tool as E625; regtimeline over 0x0654-0x0660, 0x0700-0x0710,
0x0720-0x0724, 0x0748 (read-only). The kernel journal is cut into one file per range of cases with
a marker line per case (`kernel.log`).

**Results [HW].** The journal: `wd-hang-300-0x40` has `*ERROR* sgxfive: job 5766 hung, recovering`
and `job 5766 hung, recovery held (debugfs hold_recovery)` about 2 s after its marker, and
`wd-hang-300-0x23` the same two lines for job 5767; `wd-hang-900-0x100` has none (the last
register change of its timeline came at 1.85 s, against 2.21 s and 3.45 s for the other two). All
7 accepted jobs of the risky script and its rerun (300 vertices in 0x40 and 0x23 pages, 900, 600,
750, 801, 849 vertices in 0x100 pages) failed with "scene overflowed the parameter buffer, context
kept (No space left on device)" (probe rc 3), the two that logged a hung line after 47 and 92
partial renders (the last register changes of their timelines come at 2.21 s and 3.45 s, and the
jobs with 22 to 33 partial renders logged nothing). The held copies are read after the tool's
timeout, from a job that had finished. No other journal in the batch holds a hung line, and none
of the 28 jobs logged a fault or reset line. So E438's hangs (24 of 24 at 300 or more vertices in
0x40 or 0x23 pages and at 900 and 1500 in 0x100) are reproduced in 2 of the 3 cases run here; E574
also saw 450 and 600 vertices in 0x100 pages overflow without a hang. What differs from E438's
batch: the module (srcversion F156823E6F1F976458D94BF of fork f1fad0ed9d0e with the debug option
there, against B21FDA82BD5E5CB5A627E3B of 1dd291a61499), the tool (sha256 92b82d27... there,
7732b945... here), regtimeline polling the registers during the job (E438 read them after it), and
`hold_recovery`, which is the variable that changed the outcome of the two jobs that logged the
line (without it the recovery is a reset, after which the registers read 0 as E438 saw).

The number of partial renders grows with the scene: with the model of E625 (1 + floor((U + k -
thr0) / (thr0 + 0x1f))) the counts need U + k in 2836 to 2896 at 0x40 and 2913 to 2944 at 0x23 for
300 vertices (the two ranges do not meet with the spacing 0x1f; with `thr0 + 0x1e` they overlap in
2822 to 2849, so the data do not separate a constant need per scene from the failure of one
spacing), and from 5535 (600), 7053 (750), 7559 (801), 8065 (849) and 8318 (900) up by 253 at
0x100: 9.2 to 9.8 pages a vertex, roughly linear. These ranges are lower bounds of a model that
does not close on scenes it was not fitted to (the pair of 300-vertex ranges shows it), not
measures of a need. Global list: 900, 1050, 1200, 1350 vertices (0x422): count 4, dword 36 = 2, 1
partial render; 1500: count 5, dword 36 = 3, 2 partial renders (E438: 2 and 3 at 900 and 1500).
Dword 36 is a two-point fit with the page count less 2 (4 pages 2, 5 pages 3) and fails at E438's
1-page list, where it read 1, and at its 1 or 2 pages with 0. STATUS2's high halves: 0 in every
line. 0x0748: the values seen are 0x6, 0x7, 0xb, 0xc, 0xd, 0xe, 0xf, 0x1b, 0x1d and 0x1f; the
`wd-bit2` runs: 10 of 16 with a clear line (E574's 5 of 36 and E443's 4 of 12), 12 lines, one
reading each (the shortest gap 28.8 us); outside table `wd-bit2` 13 of 49 jobs, the jobs with many
partial renders (300 vertices in 0x23 and 0x40 pages: 18 and 9 lines) having the most; the gap
between lines is 28.8 us in the `wd-bit2` jobs (12 registers) and 7.2 us elsewhere.

**Reading [infer].** The hang of E438 is, on this evidence, the kernel's watchdog firing on a job
with very many partial renders (the two jobs that logged the line ran 2.2 s and 3.5 s, the
900-vertex job, with 33 partial renders, 1.85 s), and its recovery, a reset, being what left the
registers at 0; this batch held the recovery, so the job ran on to its -ENOSPC. That is the
simplest reading and not shown: the watchdog's period and the effect of no `hold_recovery` on the
same cases were not run. A scene's need is about 9 pages a vertex at 4096x4096, and the model's
count is approximate for wide scenes. The bit-2 pulse is a sparse event; whether its rate rises
with the number of partial renders is not separated from the job's length (the jobs with the most
lines are the longest, and the same ones the watchdog saw) and whether a reset before the job
matters is not separated either (4 of 8 against 6 of 8 is within what 8 runs give).

**Not shown.** What the pulse is (a reading shorter than 29 us would be missed); the global list
above 5 pages (1500 vertices is the tool's limit); the same cases without `hold_recovery`.
