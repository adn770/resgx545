+++
id = "E596"
claim = "In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, the predicated register moves `p0 mov r, r` and `!p0 mov r, r` and the predicated limm moves `p0 mov r, #n` and `!p0 mov r, #n` followed p0 in 64 of 64 jobs (8 gaps between the test that sets p0 and the move: none, 1, 4, 16 and 64 `mov` limm, and 1, 4 and 16 `ldad` with one `wdf`; p0 set to 0 and to 1 for each, a marker of its own per job), and a predicated `ba` whose predicate is false (`p0 ba` with p0 = 0, `!p0 ba` with p0 = 1, five gaps each) fell through to the next instruction in 10 of 10 jobs, so p0 survived every gap and no form ignored it [HW]; a client pixel task: the verifier of the firmware tasks refuses `p0 mov r, r`, `!p0 mov r, r` and every predicated `ba`, so these forms were not run in a firmware task, and the taken `ba` was not run"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, built on the laptop from tools/sgxfive-test.c of the 11.35 tree, sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b) with the 11.35 probe.py and campaign runner; table probes/usse/fw37-pred.toml (frozen file in probes/p1136/manifest-1137.sha256; run with each probe name prefixed usse-fw37-pred-, sha256 78124fa99ea9421e27acc22f942750a921bb390d8aa1f946c061eb497be3a0ce), made by probes/p1136/gen_client.py, 6 probes, 74 jobs, template pred37.s, SGX_PROBE_BETWEEN a debugfs reset and 3 s before every job; the baseline triangle drew 0 of 4096 pixels wrong before and after each of the 6 probes; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, row P37_C8) were written and hashed before the first run. Run usse-fw37-pred (one run). Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-fw37-pred", "vectors-usse-fw37"]
terms = []
+++
**What ran.** Four probes of 16 jobs, one per form (`p0 mov r10, r11`, `!p0 mov r10, r11`, `p0 mov
r10, #imm`, `!p0 mov r10, #imm`): for each of eight gaps and p0 = 0 and 1, `and.testtanz.chan0 !c0,
p0, r1, r1` sets p0 from the job's P, the gap runs (no instruction; 1, 4, 16 or 64 `mov rK, #limm`;
1, 4 or 16 `ldad r, [r29,+#k], drc0` then `wdf drc0`), then the form, and the tool reads r10, which
holds the job's own marker (r11) or the preset 0xA0A1A2A3. Two probes of 5 jobs each run `p0 ba
#8198` with p0 = 0 and `!p0 ba #8198` with p0 = 1 over the first five gaps: not taken, so the next
`mov r10, r11` must run (the taken `ba` was not run: it needs a placed program, as the place-ctl2
table of E476 did).

**Results.** [HW] 74 of 74 jobs read the model: 64 of 64 for the four mov forms (16 of 16 each: the
form wrote iff its predicate was true, over every gap, the register move and the limm move alike)
and 10 of 10 for the two not-taken `ba` probes (the marker of the next `mov`, never the preset). Job
times, single samples, 424 to 1334 microseconds. No job failed or hung; the kernel log (2592 lines)
shows 74 debugfs resets with BIF_FAULT 0x0 and no fault; the baseline drew exactly before and after
each of the 6 probes.

**Against the predictions.** P37_C8: 74 of 74 held.

**What it shows.** [HW] In a fill p0 is kept across up to 64 `mov` limm and across 16 `ldad` with a
`wdf` before a predicated `mov` register or limm form, and a false predicated `ba` does not jump.
[infer] The same holds for the gaps in between, and for the backend's compares and conditional moves
of the same shape.

**What it does not show.** A firmware (EDM) task (the verifier refuses the register-move forms and
`ba`; the firmware tasks `p1137_pred` of the same phase measured the `p0 mov r, #n` and `p0 br`
forms that the verifier accepts); a taken `!p0 ba`; p0 across a call, a `savelink` or an event (Q196
asks for the firmware-task repeat).
