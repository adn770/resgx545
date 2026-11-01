+++
id = "E603"
claim = "In a firmware (EDM) task of ours armed with trc=31 (stage f11, p1137_regsA and p1137_regsB, one arm each, the landed verifier unchanged), every register r0 to r123 is real storage as a destination of `ldad` and a source of `stad`: a marker of its own per job, loaded from the page into each register and read back to the page, read back as written for r1 to r31 (20 of them outside the wrapper's), r32 to r63, r64 to r95 and r96 to r123 (28) one range at a time (12 jobs), for all 112 registers outside the wrapper's 11 at once (3 jobs), for the wrapper's 11 and r8 from a second wrapper that uses r12 to r22 (3 jobs), and for r0 (3 jobs, markers 0xb921ea5f, 0x8f940932 and 0xb3b031b9): 21 of 21 jobs, no register reading a stale value, another register's marker or the sentinel, the tick advancing and the gate exact after each arm [HW]; the markers differ in every job and register, which extends E540's read of the top register r123 and E550's marker to every other register"
unit = "edm"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, our firmware tasks armed in the general slot (own_arm 'slots=0x1 entry=0 trc=31', one arm per task), the landed verifier unchanged, the landed tools/fwtask runner (fwtask_run.py, run_stage.py) driven by probes/p1136/run_1137.py through probes/p1136/run_1137_logged.py (which also keeps every job's record and whole results page), sources probes/p1136/asm/p1137_regsA.s and p1137_regsB.s made by probes/p1136/gen_1137.py (blob sha256 in env.toml), jobs and expected readbacks by probes/p1136/judge1137.py with markers of their own in every job (never the page's initial fill 0xdeadc0de), results pre-filled with sentinels of their own; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, row P37_F11a, P37_F11b and P37_F11c) were written and hashed before the first run; a reset to stock and the gate (fill and triangle exact) after each arm. Run p1137-f11 (one run of 21 jobs in two arms). Firmware (EDM) tasks, not client pixel tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["firmware-tasks-p1137-f11", "vectors-firmware-tasks-p1137"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** Two arms with `trc=31`. `p1137_regsB` (49 instructions, wrapper in r12 to r22) loaded
markers into r1 to r7, r9, r10, r11, r30 and r8 from a block of the page, then stored them to the
output block: three jobs. `p1137_regsA` (515 instructions, wrapper in r1 to r7, r9 to r11, r30)
loaded a marker into each register it may use (cmd 3 to 6: r1 to r31 but the wrapper's, r32 to r63,
r64 to r95, r96 to r123, one range per job; cmd 1: all 112 at once; cmd 2: r0 alone), a `wdf` after
every 16 loads and after the last, then stored them all; three jobs of each command, in the order
regsB, cmd 3, 4, 5, 6, 1, 2. The union is r0 to r123. Every marker is a 32-bit value of the host's
own (top bit set, distinct in the whole plan, never the page's fill); the output block is pre-filled
with sentinels of its own.

**Results.** [HW] 21 of 21 jobs, 0 registers wrong: regsB 3 x 12, regsA ranges 3 x (20 + 32 + 32 +
28), all-at-once 3 x 112, r0 3 x 1 = 3 x 12 + 3 x 112 + 3 x 112 + 3 = 711 register reads, each equal
to its own job's marker. r0 reads back the marker written to it (0xb921ea5f, 0x8f940932 and
0xb3b031b9), where E540 only read r0 unwritten (0). Job times 0.18 to 1.05 ms. Arms: tick 996.4 Hz
(regsB) and 1011.2 Hz (regsA), accepted, no log line; after the resets the gate was exact and the
tick 987.5 and 1001.9 Hz (taken after the reset to stock, which restarts the EDM: they show the
restored system, not the clobbered task). What shows the closed wrapper survived a task that
overwrote its temporaries is that every job after a clobbering one completed, the wrapper running
again at a tick after the previous tail call (21 of 21 jobs, the 3 jobs of the 112-register command
among them). The kernel log (150 lines) shows two debugfs resets at BIF_FAULT 0x0 and no fault.

**Against the predictions.** P37_F11a (15 of 15 jobs, 112 of 112 registers), P37_F11b (3 of 3 jobs)
and P37_F11c (3 of 3 jobs) held; the 15 jobs of P37_F11a are the 12 range jobs and the 3 all-at-once
ones.

**What it shows.** [HW] Every register of r0 to r123 is storage of a firmware task started with 124
temporaries: it holds what the task wrote, for the range sizes run and all at once. [infer] The
registers hold their value across a `wdf` and a `stad` of the same job, as E485 showed for a fill.

**What it does not show.** That the 124 registers are 124 distinct storages: r0 was written only
alone, and no job wrote a register of regsB (r1 to r7, r9 to r11, r30) together with one of r12 to
r123, so distinctness is shown for r8 and r12 to r123 (the 112 of the all-at-once jobs, in which the
wrapper's r6 and r9 are live as bases, which excludes aliasing for those two) and among the 12
registers of regsB, and nothing shows that r0 is not another register's alias; registers as the
operands of the ALU or of `mov` (only `ldad` destinations and `stad` sources were used); r124 to
r127 (no operand names them, Q168); a TRC above 48 or the stock tick under a task that clobbers more
(nothing past the tail call was clobbered but the temporaries); whether the values survive from one
task to the next (Q158); what an unwritten register holds.
