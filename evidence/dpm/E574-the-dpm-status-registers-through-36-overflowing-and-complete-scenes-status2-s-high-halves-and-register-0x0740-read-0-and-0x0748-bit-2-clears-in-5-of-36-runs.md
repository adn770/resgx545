+++
id = "E574"
claim = "Through 36 jobs of triangles of 3 to 900 vertices at 4096x4096 in 0x100 to 0x422 parameter-buffer pages (3 runs of 12 cells; 6 completed and 30 overflowed into partial renders, none hung or faulted), the high halves of STATUS2 (0x0710, 0x071c) and the register 0x0740 read 0 in every timeline line of all 36 jobs (30 to 1066 lines a job, the readings about 29 microseconds apart); 0x0748 bit 2 cleared in 5 of the 36 jobs, in 6 lines of one reading each (300 vertices in 0x100 pages 1 of 3, 150 in 0x100 1 of 3, 450 in 0x100 1 of 3, 600 in 0x100 2 of 3, none of the other cells; 5 of 15 jobs at 0x100 pages, 0 of 21 elsewhere), against 3 of 3 for 300 in 0x100 in E443: across the two batches the clearing is not a function of the scene's vertices and pages alone, and 29 of this batch's 36 jobs ran after a reset (a reset follows each failed job), which E443's record does not say of its own; 450 and 600 vertices in 0x100 pages overflowed without a hang (6 of 6)"
unit = "dpm"
method = "script dpm-bit2 (safe 30 jobs, risky 6), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed equal to loaded at the start of every script, never reloaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written: probe --tri pixel with the plain green shader, 4096x4096, --vertices N, debugfs render_pb_pages set before each job and put back at the end, regtimeline 10 s, 0.2 s lead over 0x0600-0x0750 (a line at every change; 365512 to 376525 readings a job), 3 runs of each of 12 cells; the script reset the GPU after every job whose text named a failure, which the tool prints for an overflowing scene (30 of 36 jobs), so each of those jobs started after a reset"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-bit2-grid"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_3D_PAGE_COUNTS"]
+++

**What ran.** 36 jobs, declared in 12 cells before the first run (plan.md section 1): (vertices,
pages) (3, 0x422), (300, 0x100), (900, 0x422) as fit cells (E443's), and (150, 0x100), (225,
0x100), (300, 0x180), (300, 0x200), (450, 0x200), (600, 0x300), (600, 0x422), (450, 0x100), (600,
0x100) held out, the last two as the risky script. 6 jobs (3 at 0x422 and 600 at 0x422) completed;
30 overflowed the buffer, which the tool reports as failed with the partial renders done ("context
kept"), and none hung or faulted: the kernel journal holds no fault line. That includes (450, 0x100)
and (600, 0x100), which the plan expected to run beside the 900-vertex hang: they overflowed like
the cells beside them (E438 saw 900 and 1500 vertices hang in 0x100 pages, this batch did not run
them).

**Results.** [HW] The high halves of 0x0710 and 0x071c: 0 in every line of all 36 jobs (H36-Z:
36 of 36 scores). 0x0740: 0 in every line (36 of 36 jobs; E256 and E312 read it the same).
0x0748: the values seen are 0x6, 0x7, 0xb, 0xd, 0xe, 0xf, 0x1b, 0x1d and 0x1f; the value with bit
2 clear (0xb or 0x1b) appears in 5 jobs: (300, 0x100) run 2, (150, 0x100) run 3, (450, 0x100) run
2, (600, 0x100) runs 1 and 3 (the last twice: 6 lines in all). H36-DET (the same scene gives the
same outcome in all three runs, with (300, 0x100) clearing in 3 of 3 as E443 saw) was a miss: 1 of
3 here, and the 3 runs of (900, 0x422) 0 of 3 (E443 saw 1 of 3). Both E443's 4 of 12 and these 5
of 36 are runs of the same sparse event: it appears only at the 0x100-page cells here (5 of 15 jobs
there against 0 of 21 at the other cells).

**The sampling.** [HW] The timeline's readings are about 29 microseconds apart (the shortest gap
between two lines of any job is 28.6 us and the median of the 8732 gaps under 100 us is 28.8 us;
365512 to 376525 readings in a 10 s job, a mean of 26.6 to 27.4 us; the time column is read as
nanoseconds [infer: the header does not give the unit]). Each of the 6 clearings lasts 28.8 to
29.0 us, one reading: the lines before and after it have the bit set. So the clearing is not
seen longer than one reading, and nothing shorter than about 29 us would be seen at all. The lines
a job holds are changes, 30 (3 vertices, 0x422) to 1066.

**The reset confound.** [HW] The script reset the GPU after every job whose text named a failure,
which the tool prints for an overflowing scene (30 of 36 jobs), so 29 of the 36 jobs started after
a reset (the other 7 were the first of a script or followed a completed job); E443's record does not
say whether its jobs followed a reset. History is a second variable besides
the scene, and the two batches may differ in it: what was found is "not a function of (vertices,
pages) alone across the two batches", not "not a function of the scene". A short pulse that the
sampling catches by chance [infer] fits the sparse and unrepeatable appearance.

**Not shown.** What makes the pulse (readings 29 us apart miss events shorter than that);
STATUS2's high half after a scene of more than five global-list pages (the global lists here are
those of E438; no page count is read in this batch).
