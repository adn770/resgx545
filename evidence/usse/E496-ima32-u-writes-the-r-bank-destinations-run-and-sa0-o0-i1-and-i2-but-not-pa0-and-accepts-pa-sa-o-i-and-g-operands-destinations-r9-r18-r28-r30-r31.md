+++
id = "E496"
claim = "ima32.u writes the six r-bank destinations run, r9, r18, r28, r30, r31 and r0 (the other dumped registers untouched: 18 of 18 cases) and sa0, o0, i1 and i2 (read back in the same job: 12 of 12), but not pa0: in the jobs of pa-dest, `ima32.u pa0, ...` twice and `mov pa0, r1` once (3 of 3 jobs) left pa0 at the value it read before (0xff00ff00 in 1536 pixels and 0xff203040 in 512), the pa0 destination jobs of the dest probe read 0x02dadf6f in all three (two of the three jobs separate it from the result, 0x79 and 0 expected), and the persistence of an sa0 written by ima32.u from one job to the next is not separated from the colour rule of E484 (job 8 reads 0x79 in sa0, 2048 of 2048 pixels, which is also the colour that job 7, the writer, output; job 9 reads 0x79 in pa0, also the colour job 8 output); ima32.u accepts the operands pa0, pa1, pa4, sa0, sa1, sa4, o0, o1, o3, i0, i1 and i2 in source 1 and pa0, pa1, pa4, sa0, sa1, sa4, o0, o1, g0, g1, g7, i0, i1 and i2 in sources 2 and 3 and reads 0 where mov reads 0 and the preset in i0 to i2 (40 of 40 cases: 31 of them read 0 by both routes, so a bank field that the instruction ignored would pass there, and only the 9 cases of i0 to i2 show a nonzero value)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/ima32-forms.toml probes banks (40 cases) and dest (33) (dump.s) and probes/usse/pa-dest.toml (10 jobs, in the order below); the campaign runner once for each table, no probe.py first run; the dest probe read NONE in the runner's verdict (the table's model: every destination takes the result; 31 of 33 fit; the two misfits are the first two pa0 jobs, whose readback 0x02dadf6f equals the result of the third pa0 job, which therefore fits), kept in the dataset as ran"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-ima32-forms", "usse-pa-dest"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL", "REGTYPE.FPCONSTANT"]
+++

**What runs.** banks: each case does `mov r11, X`, then `ima32.u r10, X, #5, #3` (X in source 1),
`ima32.u r10, r1, X, #3` or `ima32.u r10, r1, #5, X` (r1 = 0x01010101), the same with r11 in place
of X into r12, and `xor r13, r10, r12`; r13 is 0 when the bank is read as `mov` reads it. i0 to i2
are preset to 0x01234567 + n. dest: `ima32.u D, r1, r2, r3; mov r10, D` for D in r9, r18, r28, r30,
r31, r0, pa0, sa0, o0, i1 and i2 over (a, b, c) = (3, 7, 100), (0xffffffff, 0xffffffff, 0xffffffff)
and (0x12345678, 0x9abcdef0, 0xdeadbeef), results 0x79, 0 and 0x02dadf6f. pa-dest, in order: job 0 a
pa0 reader; job 1 `ima32.u pa0, ...; mov r10, pa0` (0x79); job 2 a reader; job 3 `ima32.u pa0` (5 *
5 + 5 = 30); job 4 a reader; job 5 `mov pa0, r1; mov r10, pa0` (0xabcd); job 6 a reader; job 7
`ima32.u sa0, ...; mov r10, sa0` (0x79); job 8 an sa0 reader; job 9 a pa0 reader. The dest table ran
each destination once per triple, in the order listed, r0 before pa0 before sa0.

**Results.** banks: r13 = 0 in 40 of 40; r11 = 0 in the 31 cases of pa, sa, o and g and 0x01234567
to 0x01234569 in the 9 cases of i (the cases of i0 to i2 in sources 1, 2 and 3). dest: r10 = the
result and the other dumped registers as preset in the 18 r-bank cases (r9, r18, r28, r30, r31, r0:
three triples each); sa0, o0, i1 and i2 read back the result (12 cases); the pa0 jobs read
0x02dadf6f three times, the result of the third triple, which is also what the r0 job before them
wrote and read. pa-dest: jobs 0 to 6 read pa0 as 0xff00ff00 in 1536 pixels and 0xff203040 in 512 (a
per-pixel left-over), unchanged by the writes of jobs 1, 3 and 5 (the readback in the same job
included); job 7 reads sa0 = 0x79 back in the job that wrote it, job 8 reads sa0 = 0x79 and job 9
pa0 = 0x79 in 2048 of 2048 pixels each. Every job outputs the value it read as its pixel colour (o0
= r10): job 8's colour is 0x79, and job 9 read what the job before it output; jobs 1 to 6 likewise
output the mixture they read.

**What it shows.** [HW] The destination field of ima32 reaches the r bank (r0, r9, r18, r28, r30 and
r31 of the 32 a fill has), sa0, o0, i1 and i2, and ima32's source banks are accepted and read 0
where `mov` reads 0 (31 of 40 cases) and the presets of i0 to i2 (9 of 40). [HW] A pa0 destination
is not written (jobs 1 and 3, `ima32.u`) and neither is it by `mov pa0` (job 5), as Q098 had for
`mov`; the model of the probe tables, that every destination takes the result, fails for pa0. Job 8
read the sa0 value 0x79, which is also the colour job 7 output, so whether an sa0 written by `ima32`
persists to the next job is not separated from the colour rule that E484 and Q098 give (E484 found a
persistence for `sa1`, `sa5` and `sa7`, which does not settle this one). [infer] E484 and Q098 have
an unwritten pa or sa read the colour the job before output: that reading explains the rest of the
table, since each job outputs what it read: the pa0 jobs of the dest probe read 0x02dadf6f, the r10
(pixel colour) of the r0 job before them, which two of the three jobs distinguish from the result
written; jobs 1 to 6 of pa-dest read the mixture that each job before output; job 9 read the 0x79
that job 8 output. The mixture's first value, in job 0, came from the job before the table (the
runner's baseline job), whose colours were not checked for 0xff00ff00 and 0xff203040. The same
reading says that the 0 read by every pa, sa and o operand of the banks probe is the colour the job
before it output (r13 = 0), not a value the registers hold.

**What it does not show.** Operand values other than 0 from pa, sa, o and g (the 31 cases read 0
both ways, so 'reads the integer it holds' is shown for i0 to i2 only), a pa destination other than
pa0 and an o or g destination other than o0, `ima32.s` destinations, the persistence of an sa0 write
over one job or two (jobs 8 and 9 each read the colour the job before output), whether the colour
rule or a held value gives the zeros of the banks probe, and what sets the 0xff00ff00 and 0xff203040
mixture. Narrows Q127 (the operand banks and the destinations other than r10) and Q098 (the pa0
destination is lost as `mov`'s is; the sa0 persistence is not separated from the colour rule); Q136
asks what is left.
