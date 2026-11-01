+++
id = "E703"
claim = "With the output rows of VDM_TASK1 (bits 31:24) forced to a value other than the natural (4 + N + 3) / 4 by a xor on VDM word 7, the hardware accepts rows 4 to 7 (10 of 10 jobs completed, no hang or fault) and the render of every one of the 8 forced jobs differs from that of the natural jobs (the tool's o0 histogram: 418 to 1320 background pixels in 4 jobs and none among the listed values in 4, against 2288 and 2821 in the two natural jobs), at R*V of 30 and 32 as at 35, 36 and 40; the decoder reads 76 to 95 of the 126 vertices as lost in them (a reading under a layout assumption), none in the two natural jobs (R*V 32 and 33); no job with the forced field equal to the natural one exists (a xor cannot make it), so the forcing itself is not separated from wrong rows and the forced-rows route does not measure the capacity limit"
unit = "vdm"
method = "table capacity-rows (10 jobs, risky as declared, none hung: rows forced with --vdm 7^=, the field MAX_VERTICES set by --vdm 6^=, N = 8, 9, 11 and 2), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the tool's o0 mixed lines (the colour histogram of the render) were read after the run for the claims about images; the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE"]
+++
**What ran.** The tool sets the rows to (4 + N + 3) / 4 and caps N at 11 (the size field of OUTSEL
is 4 bits), so R*V of 34 and 35 are not reachable with a natural job; E546 had natural jobs at 32,
33 and 36 or more. Here the rows were forced by xor: N = 9 natural R = 4 V = 8 (32) and N = 8
natural R = 3 V = 11 (33), two plain natural jobs (their command lines carry the field MAX_VERTICES
xor and no xor on word 7); N = 8 R = 4 V = 8 (32); N = 11 R = 5 V = 6 (30), R = 6 V = 6 (36), R = 5
V = 7 (35), R = 5 V = 8 (40); N = 8 R = 5 V = 7 (35); N = 2 R = 7 V = 5 (35), twice. R is the value
the field holds after the xor, V the vertices of a task. A forced job with the field equal to the
natural value does not exist: xor 0 changes nothing, so no job here controls for the forcing.

**Results.** [HW] The observation is the render. The tool's `o0 mixed` line (the colour histogram of
the 64x64 render, not used by the first reading of this table) of the natural jobs reads
0xff203040 x2821 (N = 9, 32) and x2288 (N = 8, 33), other x1137 and x1670, as E702's intact jobs.
The 8 forced jobs read: N = 8 R = 4 (32) no background value in the list, other x4092; N = 11 R = 5
at 30 background x1320, other x2773; N = 11 R = 5 at 35 other x4084 (no background in the list);
N = 2 R = 7 at 35, twice, the same line both times, other x4090; N = 8 R = 5 at 35 background x418,
other x3672; N = 11 R = 6 at 36 background x1208, other x2885; N = 11 R = 5 at 40 background x933,
other x3160. All 10 jobs completed: no hang, no BIF fault, the health triangle never needed. The
decoder's reading (landed p1131 decoder, identities missing out of 126, under a layout assumption:
`per` from the first object, the vertex count from the primitive word) of the two natural jobs is
0 lost in regular objects (9 objects, 15 eight times and 6); of the forced jobs 95 (N = 8 R = 4),
76 (N = 11 R = 5 at 30), 87 and 84 (N = 2 R = 7 at 35, repeated), 95 (N = 11 R = 5 at 35), 84 (N = 8
R = 5 at 35), 95 (N = 11 R = 6 at 36) and 87 (N = 11 R = 5 at 40), in 10 to 14 objects of 3 to 16
vertices (sums 128 to 173) with 3 to 17 duplicated identities. The repeated N = 2 job shows how far
the decoder numbers can be trusted when the rows differ: the two jobs have the same o0 line but
different parameter-buffer dumps and the decoder reads 87 and 84 lost, in 10 and 13 objects. The
frozen models: C33 8 of 10 and C34 8 of 10 (both missed the jobs at 30 and 32, where they predicted
no loss), C35 4 of 10, Mnat (the allocation follows the natural rows, so no loss anywhere here) 2 of
10, all scored on the decoder's lost count.

**Page claim, post hoc.** Of the 12 objects with bit 21 in these 10 jobs, the page claim of Q164
identifies all vertices of 2 (the two natural jobs) and none of the 10 in the forced jobs (the
alternative page: 0 of 12); the forced jobs are broken, so they are not a test of the claim.

**What it shows.** [HW] The hardware takes rows 4 to 7 in the field, and a forced field changes the
render: with rows different from the natural value of the vertex's N (here +1 to +5) the images of
all 8 jobs differ from the natural ones at products as low as 30 and 32, which natural jobs keep
intact (E546, E702; the matched pair N = 9 natural R = 4 at 32, intact, against N = 8 forced R = 4
at 32, broken, has the same product). The 6 jobs at 35, 36 and 40 that every capacity model
predicted would lose vertices did differ, but products 30 and 32 show the break to be independent
of the product, so they are not evidence for a capacity of 34 or 35. [infer] The rows field is also
a layout field of the task's output (it must match N); that a forced larger value is read as 'more
rows a vertex, so fewer vertices fit' is not supported. No forced = natural control exists, so
'the forcing mechanism breaks a job' and 'wrong rows break a job' are not told apart.

**Not shown.** The limit between 33 and 35 (Q094): no natural job has R*V of 34 or 35, and a forced
one is confounded by this result; whether a field forced to the natural value leaves a job intact;
whether a real limit effect is hidden in the forced jobs at 35, 36 and 40 (they are broken anyway).
