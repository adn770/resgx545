+++
id = "E602"
claim = "In a firmware (EDM) task of ours armed with trc=31 (stage f12, p1137_wdf, the landed verifier unchanged), one `wdf drc0` after N `ldad.bypassl1` (N = 2, 4, 8, 16, 32, 64 and 100, from two page bases, offsets in a permutation of 0 to 127, every 11th load repeating the address of load 0) left every destination holding its own load: 21 of 21 jobs (7 N x 3 repeats, every destination equal to the dword the host stored there for that job), which shows that loads, one `wdf` and then the stores is sufficient for these sequences and not that the `wdf` waits or is needed; and the control prediction failed: 32 `ldad.bypassl1` followed by 32 `stad` of their destinations with NO `wdf` between stored the NEW value in 32 of 32 stores in 3 of 3 jobs (96 of 96), where P37_F12b predicted at least 28 of 32 old in every job, so a load that was not waited for had landed within 32 instruction slots in a firmware task, in every job and for every register; in the 21 jobs the stores follow the loads by N + 1 slots (3 to 101), so the jobs with N = 32, 64 and 100 pass whether or not the `wdf` waits, and N = 2 to 16 were not run without it [HW]; whether a `wdf` is needed at a shorter distance or for loads from other memory was not run"
unit = "edm"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, our firmware tasks armed in the general slot (own_arm 'slots=0x1 entry=0 trc=31', one arm per task), the landed verifier unchanged, the landed tools/fwtask runner (fwtask_run.py, run_stage.py) driven by probes/p1136/run_1137.py through probes/p1136/run_1137_logged.py (which also keeps every job's record and whole results page), sources probes/p1136/asm/p1137_wdf.s made by probes/p1136/gen_1137.py (blob sha256 in env.toml), jobs and expected readbacks by probes/p1136/judge1137.py with markers of their own in every job (never the page's initial fill 0xdeadc0de), results pre-filled with sentinels of their own; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, row P37_F12a and P37_F12b (failed)) were written and hashed before the first run; a reset to stock and the gate (fill and triangle exact) after each arm. Run p1137-f12 (one run of 24 jobs). Firmware (EDM) tasks, not client pixel tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-p1137-f12", "vectors-firmware-tasks-p1137"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** One arm of `p1137_wdf` (624 instructions, `trc=31`: 124 temporaries) and 24 jobs: cmd
1 to 7 load N = 2, 4, 8, 16, 32, 64 and 100 dwords into r20 upward from the two input blocks of the
page (`ldad.bypassl1 r(20 + i), [r6 or r7, +#offset], drc0`, the block alternating, the offset (37 i
+ 5) mod 128, the repeat of load 0's address at every 11th), then one `wdf drc0`, then N `stad` to
the output block; three repeats of each. The inputs are 256 dwords of the job's own values (distinct
over the plan) and the 128 output dwords are pre-filled with their own sentinels. The control (cmd
9, three jobs, last): `ldad` of 32 destinations from the second block with a `wdf`, then 32 `ldad`
from the first block into the same registers with no `wdf`, then 32 `stad` of the destinations, then
a `wdf`: the stores read either the old (second block) or the new (first block) values.

**Results.** [HW] The 21 jobs with the `wdf`: 21 of 21, all destinations (2 + 4 + 8 + 16 + 32 + 64 +
100 = 226 per repeat, 678 in all) equal to their own load. The control: new 32, old 0, other 0 in
each of the 3 jobs. Job times 0.09 to 0.99 ms. The arm: tick 982.0 Hz, accepted, no log line; after
the reset the gate was exact and the tick 964.0 Hz. The kernel log of the stage (76 lines) shows one
debugfs reset at BIF_FAULT 0x0 and no fault.

**Against the predictions.** P37_F12a held (21 of 21). P37_F12b FAILED: the frozen falsifier says
"28 or more of 32 new in any of the 3 jobs (the loads landed by themselves within the distance)",
and all three jobs read 32 of 32 new. The prediction is kept as written; no row was refit.

**What it shows.** [HW] After N = 2 to 100 loads from two bases at mixed offsets in a firmware task,
the repeated address too, and one `wdf`, every destination held its own load (N up to 100): the
sequence is sufficient. The `wdf` was not shown to wait or to be needed: the control, with no `wdf`,
had every load in place 32 slots after it (the first store reads a load issued 32 slots before, the
last one 32 as well), so the jobs with N = 32, 64 and 100 (every distance 33 or more) cannot tell,
and N = 2 to 16 (3 to 17 slots) had no job without the `wdf`. That is a measurement of one distance
in one task: E517 saw, in a fill, a load not waited for landing after 40, 100 and 128 `nop` and not
after 48 and 64, so the landing is not a function of the distance in a fill, and nothing here shows
it is in a firmware task. [infer] A backend must keep the `wdf` (the hardware makes no promise), and
the missing-`wdf` hazard cannot be demonstrated with this distance (Q194).

**What it does not show.** A `wdf` over a load of a repeated address mixed with stores to it; that
the `wdf` waits for anything or is needed at any distance; `.fetchN`, `.bpcache`, `drc1` and a
computed base (the verifier refuses them); loads from memory other than the page; the control at
other distances (fewer than 32 instructions) or after a long `nop` run.
