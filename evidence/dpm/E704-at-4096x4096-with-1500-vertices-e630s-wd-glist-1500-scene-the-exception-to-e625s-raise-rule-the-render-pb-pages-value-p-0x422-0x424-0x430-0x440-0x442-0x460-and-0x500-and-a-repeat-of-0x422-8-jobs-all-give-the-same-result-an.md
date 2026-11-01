+++
id = "E704"
claim = "At 4096x4096 with 1500 vertices (E630's wd-glist-1500 scene, the exception to E625's raise rule), the render_pb_pages value P = 0x422, 0x424, 0x430, 0x440, 0x442, 0x460 and 0x500 and a repeat of 0x422 (8 jobs) all give the same result: an overflow (-ENOSPC, context kept) after 2 partial renders, the first at status 0x400, identical status peaks (0x400, 0x400, 0x11c) and identical control block dwords 34 to 40 (dword 35 0x3fe, 36 = 3, 37 = 0, 38 = 0, 39 = 6), no raise; but P above 0x422 did not reach the TA (its threshold register 0x0624 reads 0x400 at the first sample of every job, where P - 0x22 would be 0x4de at P = 0x500, and the parameter-buffer dumps are byte-identical), so the 8 jobs are one condition and 7 repeats if the debugfs knob or the page buffer clamps P at 0x422, which this table cannot exclude, and the threshold is held at 0x3fe only for P in 0x422 to 0x500; of the frozen models HA (a non-zero dword 36 blocks the raise) was right in 8 of 8 on that condition and its repeats, and HP (the raise needs the pages) is untested above 0x422, not refuted; the jobs at 1400 and 1300 vertices did not run"
unit = "dpm"
method = "table dpm-oom (10 jobs: 8 ran, safe; probe --tri pixel --width 4096 --height 4096 --vertices N with the plain green pixel program, regtimeline over 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x0724 and 0x0748, read-only), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl"]
+++
**What ran.** E625 and E630 left one job against the rule 'the threshold is raised by 0x20 iff the
run after the first partial render reaches the status of the first (R2)': wd-glist-1500 (1500
vertices at 4096x4096, 0x422 pages, dword 36 = 3), where R2 predicts a raise and none was seen. This
table ran it at P = 0x422 (fit, and a repeat as control), 0x424, 0x430, 0x440, 0x442, 0x460 and
0x500 (held out), and planned 1400 and 1300 vertices at 0x422 as controls below the step of dword 36
(E630: 2 at 1350 vertices and below, 3 at 1500). Frozen: HA (a non-zero dword 36 blocks the raise at
any P: no raise anywhere), HP (the raise needs the pages for the first threshold plus 0x20: raised
from P = 0x442, which is 0x400 + 0x20 + 0x22) and H2 (the raise is the second out-of-memory event;
not predicted, since it is the rule that failed on this job).

**Void jobs.** [HW] The jobs at 1400 and 1300 vertices did not run: the tool refused them with its
usage text (rc 2): a vertex count that is not a multiple of 3 is rejected (tri_probe.c, vertices %
3), the same refusal that E630 recorded for 800 and 850. Their frozen predictions (no raise) are
void, not right: the frozen recompute scores them as passes (it sees a zero control block).

**Results.** [HW] The 8 jobs that ran are the same: rc 3 `scene overflowed the parameter buffer,
context kept (No space left on device)`, 2 partial renders (0x0658 stretches), the status at the
first partial render 0x400 (thr0 = 0x400 in every job), peaks 0x400, 0x400 and 0x11c, control block
dwords 34 to 40 = 0, 0x3fe, 3, 0, 0, 6, 0 (so dwords 37 and 38, the raise, are 0), no hung or fault
line. The 0x422 job and its repeat equal E630's wd-glist-1500 word for word (timeline peaks and the
control block). The parameter-buffer memory the tool dumps is 4603904 bytes (0x464 pages), so P =
0x500 is beyond it; whether the debugfs knob or the page buffer clamps there was not read.

**What the registers say about P.** [HW] The first sample of the TA threshold register 0x0624 is
0x400 in every one of the 8 jobs (the first line of each timeline: 0x400, 0x10400, ...), and the
control block's dword 35 is 0x3fe at P = 0x424, 0x430, 0x440, 0x442, 0x460 and 0x500 as at 0x422
(dwords 34 to 40 identical in all 8). In E705's dpm-stack jobs the same register reads P - 0x22
(6 at P = 0x28, 0xe at 0x30), which at P = 0x500 would be 0x4de. The parameter-buffer dumps of the 8
jobs are byte-identical (raw sha256 09f75435...) and so are the tadata dumps (4dbecfff...). The high
half of register 0x0700 reads 0x0422 in 421 to 442 samples of every job, the 0x500 one included
(its meaning is not established here). The knob was written before each job with tee and no output
reads it back. These are the facts a clamp would leave; nothing here shows that a pages value
above 0x422 reached the TA.

**Scores.** HA 8 of 8 on the jobs that ran (10 of 10 as the frozen recompute counts, with the two
void jobs as passes), which is one condition and its repeats if P is clamped at 0x422, not 8
independent observations. HP 5 of 8 (7 of 10 by the frozen recompute): the three held-out jobs at P
= 0x442, 0x460 and 0x500, where it predicted a raise, did not raise, but if P did not reach the TA
they did not test HP: the score is not a refutation. R2 itself predicts a raise in all 8 (the run
after the first partial render reaches 0x400, its thr0) and none occurred: one scene, one
condition at least, eight runs.

**What it shows.** [HW] P above 0x422 changed nothing the TA or the DPM does here: the threshold
register read 0x400 and dword 35 was 0x3fe for every P set from 0x422 to 0x500, and no job raised.
The exception to R2 stays an exception (R2: 109 of 110 timeline jobs in E625's data). Two readings
fit and are not separated. [infer] (a) The threshold has a ceiling at 0x3fe (status 0x400): from P -
0x22 = 0x400 up the first partial render starts at the ceiling and a raise by 0x20 has nowhere to
go, which would explain why P above 0x422 is without effect and why E625's raises (thresholds below
0x100) happen. [infer] (b) The debugfs knob or the page buffer clamps P at 0x422, so the jobs at
0x424 to 0x500 were the same experiment as 0x422 (the registers and the dumps above are what that
leaves). Under (b) HP was not tested above 0x422; under (a) pages did not matter. 'Not the pages'
is therefore not shown. The first run is the knob check and P below 0x420 (Q273).

**Not shown.** Whether the knob takes effect at any P (no read-back), the threshold for P below
0x422 (nothing was run below it), whether dword 36 (3 at 1500, 2 at 1350 and below, from E630
alone) blocks the raise (HA is not separated from a scene effect by this batch: the controls below
the step did not run), and whether the raise appears when the first threshold is below the ceiling.
