+++
id = "E594"
claim = "With a marker of its own in each job, E487's jobs T = 132 to 192 read their marker back: T = 132, 136, 144 and 160 started with 8 temporaries and T = 192 started with 8, 32, 64 and 128 (8 of 8 jobs, the same pixel in 2048 of 2048 pixels, the same value in the one scratch dword), each with a marker no other job writes (0x7nnnnnnn from seed 1137), so in these 8 jobs a write of the job's own marker lands and is read back (a clean rerun cannot show what E487's read-back was; that it was a write and not a leftover is [infer]); none hung, as E519's rule predicts (T mod 256 is 4 to 192)"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, both recorded), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, source sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b), template probes/usse/templates/temps_phas.s (E519's and E535's, unchanged), table probes/usse/temps-fresh-c.toml (sha256 22e191f506535e619118008ee3acab12856300e20de86df20ad240bf067987dc; 4 probes, 8 jobs: T = 132, 136, 144, 160 and 192 with --temps 8, then T = 192 with --temps 32, 64 and 128; r123 written; markers from seed 1137 by probes/p1135/gen_temps.py), run by the campaign runner, one process per job, no reset between the jobs (as E535's runs); the baseline triangle 0 of 4096 wrong before and after each probe; predictions (predictions-1135.toml, sha256 d60b94cf9cce7e5370b434d8d3af8823ebb9a68680de77839fa20f37911fd603) declared before the run. Run usse-temps-fresh-c (one run); recompute probes/p1135/recompute_temps.py. Client pixel job, not a firmware task"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-temps-fresh-c", "vectors-usse-temps-fresh"]
terms = []
+++

**What ran.** E535's template (`temps_phas.s`: `phas #2, #T, pixel, none, parallel`, phase 1 writes
the job's marker to r123, reads it back, stores it and returns it as the pixel) for the 8 jobs the
audit of the capture path listed: the requests T = 132, 136, 144 and 160 started with 8 temporaries,
and T = 192 started with 8, 32, 64 and 128 (E535 had T = 192 started with 8 as a control; it is
repeated here with the others). Each job has a distinct marker (0x76628a32, 0x793836e6, 0x735b3e79,
0x74074160, 0x7af00d44, 0x777b18a4, 0x73235707, 0x7b5584f3). The jobs ran in this order, the 5
started with 8 first, without a reset between them.

**Results.** [HW] 8 of 8 jobs completed; the pixel was the job's own marker in 2048 of 2048 pixels
and the scratch dword the same value, in each. The jobs took 463 to 938 microseconds (463 to 777 for
the five started with 8; 701, 712 and 938 for the starts 32, 64 and 128), single samples. No job
hung and the kernel log of the run shows no fault. Declared before the run: the 8 jobs read their
own marker (held), none hangs (held), the job time 420 to 600 microseconds: wrong for five of the 8
(633, 777, 701, 712 and 938).

**What it shows.** [HW] In the 8 jobs the requests 132, 136, 144, 160 and 192 each run and write
r123: the marker read back is the job's own, which a stale read of the marker of an earlier job
(E484) cannot be. [infer] E487's read-back at these requests was then a write that landed and not a
leftover of the job before; the rerun cannot show what the old run read. With E535 (T = 124, 128,
192 and 260 and up), every request of E487 from 124 up has been read back with a marker of its own;
the jobs T = 8, 16, 32, 64 and 96 wrote their registers (r7 to r95) for the first time in the
table's order and were not repeated. The times are the request's cost in single samples and show no
trend (463 to 938 microseconds, the largest for the largest allocation at start).

**What it does not show.** That a request allocates the registers it asks for: only r123 was written
(usse-asm cannot name more); the requests between and above those run; E487's hang range (not run
here); a firmware task (E540); Q133.
