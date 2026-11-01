+++
id = "E595"
claim = "In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, the two-instruction 64-bit compares `ima32.u t, i0, b, c56, a` then `xor.testtanz.chan0 !c0, p0, b, i0` and `ima32.s t, i0, b, c56, a` then `xor.testtanz.chan0 !c0, p0, i0, #0` gave a < b (unsigned and signed) in 256 of 256 jobs: 192 of 192 on the registers r5/r6/r7, r26/r27/r28, r31/r30/r25, r64/r65/r66 (started with 80 temporaries), r123/r122/r121 (124 temporaries) and with the result register equal to a source (r1/r2/r1), 16 pairs each, p0 set to the opposite first, and 64 of 64 right after another compare that left i0 holding its own high word, so the test read the fresh high word and never the one before (32 of 32 unsigned, 32 of 32 signed, 49 of the 64 cases would read the opposite from a stale i0); no job failed [HW]; the measurement is a client pixel task: whether a firmware (EDM) task does the same is not measured, the firmware-task verifier refuses `ima32` with the extra operand i0"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, printed by the campaign runner and recorded in env.toml), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, built on the laptop from tools/sgxfive-test.c of the 11.35 tree, sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b) with the 11.35 probe.py and the 11.35 campaign runner; table probes/usse/fw37-compare.toml (frozen sha256 listed in probes/p1136/manifest-1137.sha256; run with each probe name prefixed usse-fw37-compare- as the runner requires, sha256 c22003b55ff0fbb406420066d3ef215854111aa01526894a4e4eaf4f7c71850f), made by probes/p1136/gen_client.py, 14 probes, 256 jobs, one process per job, SGX_PROBE_BETWEEN a debugfs reset and 3 s before every job; the baseline triangle drew 0 of 4096 pixels wrong before and after each of the 14 probes; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, rows P37_C7 and P37_C7prev) were written and hashed before the first run. Run usse-fw37-compare (one run). Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-fw37-compare", "vectors-usse-fw37"]
terms = []
+++
**What ran.** E501, E527 and E528 ran the compare on r1, r2 and r11 only, with i0 preset to 0x55 or
untouched. This run repeats the two sequences on five more register triples (a, b, t) and on the
result register equal to a source, with 16 pairs each (the corner pairs of E527 and two random ones;
`a < b` for the unsigned one, `sext(a) < sext(b)` for the signed one), `p0` first set to the
opposite of the expected answer by an `and.testtanz` so that a compare that does not write `p0`
shows, then `r10 = 0; p0 mov r10, #1`. Two more probes (32 cases each, 16 pairs, an adversarial and
a random previous pair) run a first compare that leaves i0 holding its own high word and then the
tested one: a test that read the previous high word would read the opposite in 25 of the 32 unsigned
and 24 of the 32 signed cases (the frozen prediction text says 28 of 32; counting the hypotheses
gives 25 and 24).

**Results.** [HW] 256 of 256 jobs read r10 = a < b: 192 of 192 on the six register layouts, in both
signs (12 probes, 16 jobs each, every one SETTLED on the model); 64 of 64 in the two
previous-high-word probes (32 of 32 unsigned, 32 of 32 signed), 49 of them cases a stale i0 would
have given wrong. Job times, single samples, 874 to 1615 microseconds. No job failed or hung; the
kernel log of the run (8964 lines) shows the 256 debugfs resets with BIF_FAULT 0x0 and no job fault;
the baseline drew exactly before and after each of the 14 probes. The registers include r123, r122,
r121 under 124 temporaries and r64 to r66 under 80.

**Against the predictions.** P37_C7 192 of 192 held; P37_C7prev 64 of 64 held (the stated "28 of 32"
cases that tell was a miscount, 25 and 24 tell).

**What it shows.** [HW] The unsigned and the signed 64-bit compare of the backend's code, as a
client pixel task, gives the right answer on the registers tried, whatever the result register (also
equal to a source), and reads the high word its own `ima32` wrote, not one from an earlier compare.
[infer] The registers between those tried behave alike.

**What it does not show.** A firmware (EDM) task: the verifier refuses `ima32.u t, i0, b, c56, a`
(unknown form), so the compare as the backend emits it cannot run in one until the loader accepts
the form; the `.s` test of i0 against #0 and the `xor.testtanz` of i0 against a register are
accepted by it, but the `ima32` that writes i0 is not. Registers r124 to r127. Q196 asks for the
firmware-task repeat.
