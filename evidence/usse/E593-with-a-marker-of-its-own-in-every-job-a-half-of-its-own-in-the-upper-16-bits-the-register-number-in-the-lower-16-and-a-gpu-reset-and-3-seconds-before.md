+++
id = "E593"
claim = "With a marker of its own in every job (a half of its own in the upper 16 bits, the register number in the lower 16) and a GPU reset and 3 seconds before each job, the 25 jobs of E485's two tables (temps-max 15, temps-sparse 10), run in the table's order and in the reverse order, read back in every register read (the pixel, which is the top register r123, and the first 32 dwords the tool shows) the job's own marker: 742 of 742 values of each run in the 25 jobs of each order, with no failed job, no marker of another job and no wrapped register number among them; for the 10 jobs of temps-max with T >= 80 (T = 80, 96, 112, 124 and 128, both sweeps) the registers past the 32 shown (8, 16, 24, 30 and 30 more) were counted as changed, as predicted, and not read; so E485's finding stands without its fixed marker, for the registers read: a register a job wrote reads back what that job wrote, up to r123, and the i0-i3 job still reads i3 as i0; in the one job of each order that reads r123 without writing it (the i0-i3 job) the pixel holds markers of earlier jobs of the run, one job's marker in 2048 pixels in one order and those of two earlier jobs in 1536 and 512 pixels in the other, after a reset in front of the job [HW]; the temporaries are not cleared between jobs by the debugfs reset [infer]"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip 1dd291a61499, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, printed by the campaign runner and recorded in env.toml), stock firmware, tool sgxfive-test-1135 (sha256 7732b94538cd221f25be85f307d93168413ef57cfae81065a268a73f08902687, built on the laptop from tools/sgxfive-test.c of this tree, sha256 f5cdccb15a73de6584e33e43c5a2eb1ba5e37de7e43a07c39cb9a8d386c6e74b); tables probes/usse/temps-fresh-a.toml (sha256 8d3b5eb846d2dc2fdeb795667fccc563f2a2f8e4f0183a7b6c9d77903763846d, 12 probes, 25 jobs: temps-max t052 to t128 then temps-sparse t080 to t128, as E485's) and temps-fresh-b.toml (sha256 9eb7eb2ef0056e2c149cad1636dc82b8557a3ce67a7d2f5e7ebe2f8f312670e8, the same jobs in the reverse order), made by probes/p1135/gen_temps.py from probes/usse/temps-max.toml and temps-sparse.toml with 25 distinct halves from seed 1135 and 1136 (a half is never 0x7e57 or 0x1e57, the halves E485's jobs all shared), run by the campaign runner with SGX_PROBE_BETWEEN set to a debugfs reset and a 3 second wait before every job, one process per job; the baseline triangle drew 0 of 4096 pixels wrong before and after each probe of both runs; the predictions (predictions-1135.toml, sha256 d60b94cf9cce7e5370b434d8d3af8823ebb9a68680de77839fa20f37911fd603) were written and hashed before the first run. Runs usse-temps-fresh-a and usse-temps-fresh-b (one each); recompute probes/p1135/recompute_temps.py. Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-temps-fresh-a", "usse-temps-fresh-b", "vectors-usse-temps-fresh"]
terms = []
+++

**What ran.** E485's jobs, with the fixed marker 0x7E570000 | n replaced by (h << 16) | n, h a half
of the job's own (25 distinct halves a run, none shared between the two runs), n the register number
so that a read of another register's value (a wrap) shows as a different n. The GPU was reset by
debugfs, and 3 seconds waited, before every job, so that a job starts on a reset GPU; the jobs are
E485's 25 (temps-max T = 52, 64, 80, 96, 112, 124 and 128 with the sweeps ascending and descending,
T = 128 also the i0-i3 job, 15 jobs; temps-sparse T = 80 to 128, 10 jobs) in the table's order (run
a) and in the reverse order (run b). The tool shows at most 32 changed scratch dwords and counts the
rest; the tables now state that count (`scratch_more`), and in temps-max the writes past 32 dwords
are counted, not read.

**Results.** [HW] No job failed or hung (50 of 50), the kernel logs of both runs show no job fault
or hang (the 50 debugfs resets print BIF_FAULT 0x0) and the baseline drew exactly before and after
each of the 24 probes. In run a the 25 jobs read 743 values (the pixel and the shown dwords) and 742
are the job's own marker, run b 744 and 742; none has another job's half in a register read that the
job wrote, none a wrapped register number (every dword's lower half is the register stored: 0 of 742
wrong in each run). The counted dwords past the 32 shown in the sweeps of temps-max are 0 for T = 52
and 64, 8 for T = 80, 16 for 96, 24 for 112 and 30 for 124 and 128 (40, 48, 56 and 62 registers
written), in both orders, as predicted; these 8 to 30 registers of each of the 10 jobs with T >= 80
are counted, not read, so a changed count cannot tell an own marker from a leftover there. The i0-i3
job (T = 128): i0, i1 and i2 read their markers and i3 reads i0's marker (0x...0000, i.e. the half
and 0), in both runs, as E485 had it with the fixed marker. The verdict of every probe but the two T
= 128 probes of temps-max is the documented model's (SETTLED); the T = 128 probes read NONE because
the table's hypothesis for the i0-i3 job expects four separate registers, the same table error E485
reported. Job times, single samples, 794 to 2885 microseconds (the i0-i3 job 794 to 824: it stores 4
dwords, the sweeps 1083 to 2885).

The one pixel that is not the job's own: the i0-i3 job reads r123 as its pixel (OUT) and never
writes it. In run a the pixel is 0x3e87007b, the marker of the job just before (temps-max T = 128
descending, half 0x3e87), in 2048 of 2048 pixels; in run b it is mixed, 0x1b94007b in 1536 and
0x6860007b in 512 pixels: the markers of the second and the fourth job of the run (temps-sparse T =
128 and T = 124, both ascending sweeps: r2 written first, r123 last), nine and seven jobs before,
each with a GPU reset in front of every job in between. In run a the job whose marker is read is the
descending temps-max T = 128 job just before (r123 written first). No last-writer or ordering rule
is visible: in run b the last job before that wrote r123 supplies 512 pixels, the one before it
none, and a job two earlier 1536.

**Against the predictions.** Declared before the runs: 50 of 50 jobs complete, the dwords shown and
counted as above, i0 to i2 their own and i3 = i0 (all held); the stale-read prediction ("occur in 0
of 50 jobs") was wrong as written: 2 of the 50 jobs (the i0-i3 job of each order) read a value of an
earlier job, in the register they did not write; in a register a job wrote the stale reads are 0 of
1484 values read in the two runs. The declared falsification criterion of that prediction ("any job
returns a value whose half is another job's") fired as worded, in 2 of the 50 jobs (the i0-i3 job of
each order); "stands" above reads E485's claim as about the registers a job wrote, which the
criterion did not say.

**What it shows.** [HW] E485's finding stands, read as about written registers, with a marker of its
own in every job: a register a job wrote and that was read reads back the job's own value, so a
stale read of an earlier job's register (E484) is not what the read-back of r2 to r123 under
`--temps` 52 to 128 was, and the file does not wrap at 32, 48 or 64 at the registers sampled. [HW]
In the two i0-i3 jobs (one register, r123, read through the pixel only, no coordinates) a temporary
the job does not write read back a value an earlier job wrote, with a debugfs reset in front of the
job (25 resets a run in the kernel log). [infer] The temporaries are not cleared by the reset the
debugfs file runs; what that reset does to the register banks is not known (the log shows the EDM
restart only), and the cause of E484's persistence, which had no reset, is not shown. Which earlier
job (the last one in one order, an older one in the other) is not a rule shown; nor is a slot per
instance (1536 and 512 are pixel counts).

**What it does not show.** The registers between the sampled ones (r3, r5 ... and, in temps-sparse,
three of every four); r124 to r127 as storage; that a power cycle or a module reload clears them;
whether a firmware task's temporaries behave alike; the jobs with E487's requests above 124 (E594);
the 8 to 30 counted dwords of each of the 10 temps-max jobs with T >= 80 past the 32 shown (their
values were not read; temps-sparse, every fourth register, shows all of its sampled ones). All of
this was measured in client pixel tasks (fills), not in firmware tasks.
