+++
id = "E597"
claim = "In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, `ima32.u d, i0, a, b, c` and `ima32.s d, i0, a, b, c` with the four operands in every one of the 15 partitions into registers (d, a, b and c each its own register, any two or three alike, all four the same one; `mov d, #0; ima32 d, i0, a, b, d; mov d, i0` of the request is the partition with c in d's group) read their sources before the write: r10 held the low word and i0 the high word of the 64-bit a*b+c (c sign-extended for .s) in 300 of 300 jobs (30 probes of 10, i0 preset to a marker of its own each so that an unwritten i0 shows), with the markers never read back from i0 [HW]; a client pixel task: the firmware-task verifier refuses `ima32` with the extra operand i0, so the form was not run in a firmware task"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, built on the laptop from tools/sgxfive-test.c of the 11.35 tree, sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b) with the 11.35 probe.py and campaign runner; table probes/usse/fw37-ima32hi-repeat.toml (frozen file in probes/p1136/manifest-1137.sha256; run with each probe name prefixed usse-fw37-ima32hi-repeat-, sha256 8633f1b592d9b4b269ae57eba7dde21067c5b7275bc7dfcd44a2ff443ca5b3e7), made by probes/p1136/gen_client.py, 30 probes, 300 jobs, template dump.s, SGX_PROBE_BETWEEN a debugfs reset and 3 s before every job; the baseline triangle drew 0 of 4096 pixels wrong before and after each probe; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, row P37_C9) were written and hashed before the first run. Run usse-fw37-ima32hi-repeat (one run). Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-fw37-ima32hi-repeat", "vectors-usse-fw37"]
terms = []
+++
**What ran.** E525 and E526 ran `ima32` with the extra operand, d distinct from a, b and c. Here the
registers are the representatives r10 (d), r1 (a), r2 (b) and r3 (c); a partition names which of the
four operands share a register (for example `abca`: d and c in one register, a and b distinct;
`aaaa`: all four r10). Ten jobs per probe: the four corner triples (all ones, 0xffffffff with
0x80000000 and 0, 0x80000000 twice and 0xffffffff, 0x10001 with 0xffffffff and 1) and six random
ones, each register of a group holding the value of its group (d's group holds a random value with
its top bit set, which the operands read before the write). Each job presets i0 with a marker of its
own (0x0A5A5A00 + 17 k) by `mov i0, r8`, runs the `ima32`, and stores r10 and `mov r11, i0`; the
unwritten-i0 rival reads the marker back.

**Results.** [HW] 300 of 300 jobs read the model: r10 = the low word and r11 = the high word of the
64-bit product plus addend (unsigned for `.u`, signed with c sign-extended for `.s`), computed from
the registers' values before the write; 0 jobs read an unwritten i0 (the marker), 0 failed (job
times 928 to 9712 microseconds; the kernel log of 10505 lines shows the 300 debugfs resets at
BIF_FAULT 0x0 and no job fault; the baseline drew exactly before and after each of the 30 probes).
30 of 30 probes SETTLED on the model.

**Against the predictions.** P37_C9: 300 of 300 held.

**What it shows.** [HW] A source shared with the destination, in any of the 15 partitions, is read
before the destination is written, for both signs, and the high word reaches i0 whatever the
sharing. [infer] The backend's form `mov d, #0; ima32 d, i0, a, b, d; mov d, i0` is exact; the value
it uses, d's group holding 0, was not run (d's group held a random value with the top bit set, never
d = c = 0).

**What it does not show.** A firmware (EDM) task (verifier: unknown form for `ima32.u r10, i0, r10,
r10, r10`); i0 with `.neg`, `cie` or a source constant (Q135); Q196 asks for the firmware-task
repeat.
