+++
id = "E522"
claim = "The simulator of 11.28 matches 5406 of the 5750 USSE vectors of the usse runs of 11.23 to 11.27, stops on 135, skips 9, leaves 156 out of the replay and differs on none (the model of 11.27 matched 3148, differed on 218 and stopped on 2100), and over all 34510 USSE vectors 30260 match, 1112 are fitted, 908 stop and none differs"
unit = "usse"
method = "offline: tools/usse-asm/convert_extra.py on the raw readbacks and saved programs of 74 usse tables of 11.23, 11.24, 11.25 and 11.27 into vectors/nokernel/usse/ (338 files, 5815 vectors, 5750 USSE and 65 PDS), then cargo run --release -p sgx-sim --example replay and cargo test --release -p sgx-sim over the whole data repository (RESGX545_DATA); one run each, no run on the hardware"
tiers = ["HW"]
date = "2026-11-08"
data = ["vectors-usse-nokernel"]
terms = []
+++

**Results.** The replay lists one line per USSE vector. Over the 5750 new vectors: 5406 match, 135
stop (30 on a register past the task's allocation, Q147; 26 on a read before its load lands, `wdf`;
the others on a read of an unwritten register, a repeat flag or an operand the records did not run),
9 are skipped (another instance's unfenced store, E514, Q143), 156 are left out (124 with mixed
pixels and no single `o0`, 32 whose job faulted) and 44 jobs that hung are not replayed, 42 of them
with the `phas` request that hangs (E519) predicted by the simulator. The model of 11.27, run on the
same files, matched 3148, differed on 218, stopped on 2100 and skipped 84. Over all 34510 USSE
vectors, the 28760 of the data repository included: 30260 match (30067 scalar and 193 pixel
vectors), 1112 are fitted, 908 stop, 175 are skipped, 1925 are left out, 130 jobs that hung (48
predicted) and none differs; the data repository's own vectors change only by six predicted hangs.
One vector went from a match to a stop on purpose, `usse-ima32-forms-dest__20`: its program writes
`pa0` and reads it back, and a write to a `pa` is lost in a fill (E496). The 65 PDS vectors of the
`emit-addend` and `emitpds` runs are skipped (the job faulted or hung in the task an `emitpds`
started, E488, E520); the other PDS vectors match as before (1305, 98 stop, none differ).

**What it shows.** [HW] The USSE model that the records of 11.15 to 11.27 describe reproduces the
hardware's readback on 5406 of the cases those records rest on, and stops, rather than guess, on
the 135 it has no rule for.

**What it does not show.** That the model is right where no case was run: several of its rules were
fitted to these same readbacks (E515, E516 and the `o` join of E529, read from its first 90), so a
match on them checks the fit and does not predict; the modulo-256 rule of E519 and the `o` join on
three fresh tables (E529) were predicted before the run, and their records say so. The ZLS and the
multisampling are not in the model, and no pipeline is.
