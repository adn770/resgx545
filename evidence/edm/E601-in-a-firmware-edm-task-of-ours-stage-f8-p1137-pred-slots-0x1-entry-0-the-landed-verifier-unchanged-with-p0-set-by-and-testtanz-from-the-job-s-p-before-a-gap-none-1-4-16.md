+++
id = "E601"
claim = "In a firmware (EDM) task of ours (stage f8, p1137_pred, slots=0x1 entry=0, the landed verifier unchanged), with p0 set by `and.testtanz` from the job's P before a gap (none; 1, 4, 16 or 64 `mov` limm; 1, 4, 16 or 32 `ldad.bypassl1` and one `wdf`; a mix of mov, ldad and a `mov` from a loaded register; `wdf`, `idf`, `wdf`; a taken `br` hop), `p0 mov r20, #A` wrote iff P was not 0 (else r20 kept the job's marker), `!p0 mov r21, #B` wrote iff P was 0, `p0 br` was taken iff P was not 0 and `!p0 br` iff P was 0: 72 of 72 jobs (12 gaps, P = 0 and 1, 3 repeats, shuffled, a pair of markers of its own per job), so p0 survived every gap and the four forms the verifier accepts follow it [HW]; the verifier refuses `p0 mov r, r`, `!p0 mov r, r` (unknown form) and `p0 ba`, `!p0 ba` (form not allowed), so those were not run in a firmware task"
unit = "edm"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, our firmware tasks armed in the general slot (own_arm 'slots=0x1 entry=0 (stock temporaries)', one arm per task), the landed verifier unchanged, the landed tools/fwtask runner (fwtask_run.py, run_stage.py) driven by probes/p1136/run_1137.py through probes/p1136/run_1137_logged.py (which also keeps every job's record and whole results page), sources probes/p1136/asm/p1137_pred.s made by probes/p1136/gen_1137.py (blob sha256 in env.toml), jobs and expected readbacks by probes/p1136/judge1137.py with markers of their own in every job (never the page's initial fill 0xdeadc0de), results pre-filled with sentinels of their own; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, row P37_F8) were written and hashed before the first run; a reset to stock and the gate (fill and triangle exact) after each arm. Run p1137-f8 (one run of 72 jobs). Firmware (EDM) tasks, not client pixel tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-p1137-f8", "vectors-firmware-tasks-p1137"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** One arm of `p1137_pred` (457 instructions) and 72 jobs, one command per gap:
`ldad.bypassl1` of P and the two markers from the page, `and.testtanz.chan0 !c0, p0, r10, r10` (p0 =
P != 0), the gap, then `p0 mov r20, #0x0a11ce11`, `!p0 mov r21, #0x0b22ce22`, `p0 br`, `!p0 br` (the
two branches set r22 and r23 to a hit or a miss value), and the four registers stored to the
command's result slot. The jobs came shuffled (seed 1137), each with two markers of its own (r20 and
r21 preset from the page) so that a stale register shows.

**Results.** [HW] 72 of 72 jobs: r20 = A and r21 = M2 for P != 0, r20 = M1 and r21 = B for P = 0;
the branches taken as p0 said in all of them. Job times 0.13 to 1.06 ms. The arm: tick 984.2 Hz,
accepted by the verifier, no log line; after the reset the gate was exact and the tick 965.5 Hz. The
kernel log of the stage (75 lines) shows one debugfs reset at BIF_FAULT 0x0, EVENT_STATUS
0x20000000/0x400, no fault.

**Against the predictions.** P37_F8 held: 72 of 72.

**What it shows.** [HW] In a firmware task p0 is kept over up to 64 `mov` limm, over 32 `ldad` with
a `wdf`, over `wdf` and `idf`, and over a taken branch, and `p0 mov r, #n`, `!p0 mov r, #n`, `p0
br`, `!p0 br` follow it. [infer] The register-move forms and a not-taken `!p0 ba` behave alike (E596
shows the register moves and a not-taken `ba` in a fill, 74 of 74); a taken `!p0 ba` was run
nowhere.

**What it does not show.** `p0 mov r, r`, `!p0 mov r, r` and every `ba` in a firmware task (the
verifier refuses them), a taken `!p0 ba`, p0 across a task boundary (Q124).

**Correction 2026-11-11:** "No log line" for the arm was the tool's report, not the kernel's:
`cmd_arm` of tools/fwtask/fwtask_run.py slices dmesg by a line count and read an empty list on a
full ring buffer (`"log": []` in f8-arm.json). The stage's kernel.log (dataset
firmware-tasks-p1137-f8) has the kernel's `own_code: 3786 bytes accepted` and `own task armed:
slots 0x1, trc 0 (0: stock)` lines for the arm and no fault, hang or recovering line; no other
statement here depends on it.
