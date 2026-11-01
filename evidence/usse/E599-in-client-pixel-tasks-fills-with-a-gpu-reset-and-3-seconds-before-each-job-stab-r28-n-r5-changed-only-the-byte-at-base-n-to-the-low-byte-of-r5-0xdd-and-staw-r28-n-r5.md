+++
id = "E599"
claim = "In client pixel tasks (fills), with a GPU reset and 3 seconds before each job, `stab [r28,+#n], r5` changed only the byte at base + n to the low byte of r5 (0xdd) and `staw [r28,+#n], r5` only the two bytes at base + 2n to its low halfword (0xccdd), nothing else changed, in 23 of 23 jobs (`stab` 16: bases at +0, +1, +2 and +3 bytes and n = 0 to 3, so also at odd addresses; `staw` 7: bases at +0 and +2 and n up to 3, aligned), and a plain `stad` control landed at an aligned address and nowhere at an unaligned one in 3 of 3 jobs (as usse_isa 7.10 has it): 26 of 26 jobs; no job faulted or hung [HW]; client pixel jobs: a narrow store was not run in a firmware task (the verifier refuses `stab` and `staw`), and a `staw` at an odd address and a narrow store with a register offset, a negative offset or an increment form were not run"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, recorded in env.toml), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, built on the laptop from tools/sgxfive-test.c of the 11.35 tree, sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b) with the 11.35 probe.py and campaign runner; table probes/usse/fw37-narrow.toml (frozen file in probes/p1136/manifest-1137.sha256; run with each probe name prefixed usse-fw37-narrow-, sha256 d7d480e06d9acda1bedf1d15c49d7dfa47ec875f666f6bdb2dcd8efa8726543f), made by probes/p1136/gen_client.py, 6 probes, 48 jobs, template narrow.s (scratch dwords 16 and 17 preset to 0x9c8db6a7 and 0x7e6d5c4b, bytes a7 b6 8d 9c 4b 5c 6d 7e; r28 the base, r5 = 0xaabbccdd the store source), SGX_PROBE_BETWEEN a debugfs reset and 3 s before every job; the baseline triangle drew 0 of 4096 pixels wrong before and after each of the 6 probes; the predictions (probes/p1136/predictions-1137.toml, sha256 17f6cc521ce8e58c3a995aa395641a5cba09d6627ef7578705400a7fc2af45b2, rows P37_C13c) were written and hashed before the first run. Run usse-fw37-narrow (one run, shared with E598 and E599). Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-fw37-narrow", "vectors-usse-fw37"]
terms = []
+++
**What ran.** Three probes of the same table: `stab [r28,+#n], r5` (16 jobs: the base at +0, +1, +2
and +3 bytes past the aligned one, n = 0 to 3), `staw [r28,+#n], r5` (7 jobs: bases +0 and +2, n = 0
to 3 where the halfword stays inside the two preset dwords) and `stad [r28,+#0], r5` as the control
(3 jobs: bases +0, +1 and +2). Scratch dwords 16 and 17 hold 0x9c8db6a7 and 0x7e6d5c4b before the
store; the host reads them after the job, so a store shows exactly the bytes it changed.

**Results.** [HW] 26 of 26 jobs read the model. `stab`: the byte at base + n holds 0xdd and the
other seven bytes keep theirs, in 16 of 16 jobs, with the base on an odd address as well (addresses
0 to 6 of the pair; byte 7 was never stored). `staw`: the halfword at base + 2n holds 0xccdd and the
other six bytes keep theirs in 7 of 7 jobs (aligned). `stad`: the dword lands at the aligned base
and nowhere at base + 1 and base + 2 (no change, no fault), 3 of 3. The source is r5 = 0xaabbccdd,
so the upper bytes of the source are not stored, and the "lands nowhere" rival, which differs from
the model in all 16 `stab` and all 7 `staw` jobs, read as the hardware in none. No job failed or
hung; the 48 jobs of the table took 778 to 1705 microseconds, the kernel log (1682 lines) shows no
fault.

**Against the predictions.** P37_C13c 26 of 26 held.

**What it shows.** [HW] A narrow store changes only its own bytes and puts the low bytes of its
source there, `stab` at the addresses 0 to 6 of the two dwords (bases +0 to +3 with n = 0 to 3) and
`staw` at the even ones that ran. An odd-address `staw` was not run: nothing is shown about it.

**What it does not show.** A firmware (EDM) task (the verifier refuses `stab` and `staw`); a `staw`
at an odd address; a store with a register offset, a negative offset or an increment form; a narrow
store racing a client job or another store to the same dword; whether the store needs an `idf` or a
`wdf` before the host sees it (these probes had both before the readback); Q195 lists the rest.
