+++
id = "E413"
claim = "Jobs of the one-triangle library job with VDM state word 1 bits 11:9 = 7 hang exactly when the previous such job completed and complete when it hung: 55 of 55 consecutive such jobs alternate, with or without the pixel readback, with the unpoked control between them, in series of ten and in mixed series; the control itself never hangs (0 of 35), bits 11:9 = 3 and 5 hang 3 of 20 and 5 of 20 jobs"
unit = "vdm"
method = "probes/vdm/state1-hang.toml (state1-hang.sh: 7 with and without readback alternating, ten of each; 3, 5 and the control ten times each with readback, 50 jobs) and probes/vdm/state1-hang-seq.toml (state1-hang-seq.sh: ten 7 without readback in a row, ten with readback in a row, 7 and the control alternating ten times, ten 3 and ten 5 in a row, the control three times before 7, five times over: 20 jobs; 80 jobs in all) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on; each job one tool process, the driver's hang and reset lines of its case kept (kernel.log)"
tiers = ["HW"]
date = "2026-11-07"
data = ["vdm-state1-hang", "vdm-state1-hang-seq"]
terms = ["VDM_STATE1.BITS11_9"]
+++

**The pattern.** Marking each job of bits 11:9 = 7 as ok (.) or hung (H), in the order run: the
first table (without readback, with readback, alternating) gave .H .H .H ... for its 20 jobs: every
job without readback completed and every job with readback hung. In that table the readback
alternated job by job with the hang, so the table alone cannot tell the one from the other (the
confound the second table removes). The second table (each series run
in a row) gave .H.H.H.H.H for ten jobs without readback, .H.H.H.H.H for ten with readback,
.H.H.H.H.H for the ten jobs that alternate with an unpoked control, and .H.H. for the five that
follow three control jobs: 35 more jobs, so 55 of 55 jobs of 7 alternate, the first of each series
completing (the job before it, the last of the series before, a hang whose reset cleared the state,
or a control). Every hang is a hung job with a reset (14 + 21 hung-job lines in the kernel logs).

**Not the readback, not the controls.** The hung jobs are the same ones whether the pixels are read
back or not (series A and B), and a control job in between neither prevents the hang nor starts the
sequence again (series C: ten alternating pairs, the 7 hanging every second time; series E: 7
completes after three controls, hangs the next time). The control hangs in none of the 35 jobs run
with the same options (0 of 35).

**Bits 11:9 = 3 and 5.** With readback, 3 hung 2 of 10 jobs in the first table (the 3rd and 8th) and
1 of 10 in the second (the 9th); 5 hung 2 of 10 (the 5th and 10th) and 3 of 10 (the 3rd, 6th and
9th): sometimes, not in a fixed pattern.

**What it shows.** What decides whether a job of bits 11:9 = 7 hangs is the state the previous such
job left: a job that completes leaves the next one to hang, and the reset that follows a hang leaves
the next one to complete. The earlier tables' "some hang, some complete" (E299, E060, E185) is this
alternation seen through their order. A job in between that does not use the value leaves the state
alone [infer: the state sits in the VDM or the TA, not in the context].

**What it does not show.** What the state is; whether jobs of 3 and 5 follow a longer cycle (the
counts of hangs fit a period of about 5 to 10 jobs, not tested); a fresh boot, which this session
could not do.
