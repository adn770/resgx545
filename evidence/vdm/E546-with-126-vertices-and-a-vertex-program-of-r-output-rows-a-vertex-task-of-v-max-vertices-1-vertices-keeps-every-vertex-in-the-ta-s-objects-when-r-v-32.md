+++
id = "E546"
claim = "With 126 vertices and a vertex program of R output rows, a vertex task of V = MAX_VERTICES + 1 vertices keeps every vertex in the TA's objects when R * V <= 32 (31 of 31 jobs, regular objects of 15 vertices) and breaks the regular objects when R * V >= 36 (21 of 21 jobs, no fault, no hang; vertices lost or repeated [infer]), at 33 depending on the program (5 regular, 4 irregular; at the same R = 3 and V = 11, N = 6 splits and N = 5 and 8 do not, so R * V is not a sufficient statistic); the splitting is the same on every repeat (13 of 13) and the task's attribute rows (VDM_TASK1 bits 14:7) enter it: at R * V = 33 rows 8 splits objects that rows 2 and 4 keep regular (4 of 12 jobs differ from the default rows); the top nibble of the index list's first trailing word changes no object in 9 of 9 jobs"
unit = "vdm"
method = "script tables vdm-vtask (28 jobs), vdm-vtask2 (12), vdm-vtask3 (8), vdm-vtask4 (13), vdm-vtask5 (12) and vdm-vtask-risky (9), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: `probe --tri pixpds:12 --vertices 126 --vtx-coords N` with the pixel program of E437 and the vertex program of N coordinate outputs (N = 2 to 11, R = ceil((4 + N) / 4) rows), the vertex task word `--vdm 6^=` setting VDM_TASK0.MAX_VERTICES to 15, 13, 9, 7, 2, 3, 1 and others; the object vertex counts from every region's stream; H94-none, H94-MD, H94-MR, H94-MR2, H94-DET, H94-ATTR and H92-none declared before the runs (plan.md sections 1, 6, 7, 10, 15); the declared and predictions files of vdm-vtask5 (declared-followup10.tsv and predictions-followup10.tsv, hashes in plan.md section 15) were written at 00:09:47 and vdm-vtask5 started at 00:09:48, one second later and by the same step, so their file times show the order by that second only; output.txt prints rc 0 for every job, also for a job that hung or faulted (the tool returns 0 on a failed job), so the failures are read from the failed line of each kept txt"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["vdm-vtask-capacity"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE", "VDM_INDEX2.WORD", "CSTREAM.PRIM_VERTICES"]
+++

**What is measured.** [HW] The TA writes 126 vertices as nine objects when the task keeps them:
eight of 15 vertices (five triangles) and a last of 6 (the table analysis/vtask-table.txt of the
dataset, `regular`). The measure is the list of vertex counts of the distinct objects of the control
streams and its sum.

**Capacity.** [HW] The first run (vdm-vtask, 28 jobs: N = 2, 4, 8, 11, fields 15, 13, 9, 7, 2, 3, 1)
kept all 126 vertices in 23 and not in 5 (N = 8 at fields 15 and 13: 104 and 113 vertices in
objects; N = 11 at 15, 13, 9: 93, 106, 121), so H94-none ("every vertex is found at every field")
was right in 21 of 24 held-out and 2 of 4 fit jobs. A dword budget (H94-MD: (4 + N) * V safe to 128
and lost from 150) was wrong in 3 of 7 decisive jobs (N = 5 at field 13, 126 dwords, N = 9 at field
8, 117, and N = 6 at field 11, 120, all declared kept); a row budget (H94-MR: R * V safe to 32, lost
from 40) was right in 6 of 6; H94-MR2 (safe to 33, lost from 36), declared after that, in 8 of 8. In
all 61 jobs: R * V up to 32: all objects regular (31 of 31); 36 and above: irregular, the objects
holding 3, 6, 9, 10, 12 or 16 vertices and the sum 93 to 130 (21 of 21; [infer] sums over 126 mean
vertices counted twice, the identity of the vertices not being read); 33: regular at N = 5 and N = 8
and irregular at N = 6 (the sum is 126 in all). A task that overruns does not fault or hang [HW];
[infer] the vertices are dropped or repeated in objects of other sizes. The same job repeated gives
the same list (H94-DET 13 of 13: six cases at N = 6 (field 10 and 9), 8, 5, 9 and 11). R = 2 (N = 2,
4) never overran at any field up to 15 (V = 16, R * V = 32). [infer] The limit is on the outputs a
vertex task holds: R * V in 32 to 35 rows; the attribute rows (VDM_TASK1 bits 14:7) were not varied
in an overrunning job, so the capacity as a function of them is open (Q094).

**Attribute rows.** [HW] vdm-vtask5 (12 jobs, declared after vdm-vtask4, plan.md section 15;
H94-ATTR: the attribute rows change nothing) set VDM_TASK1 bits 14:7 (word 7 of the stream, default
1) to 2, 4, 8 and 16: right in 8 of 12, wrong in 4. N = 8 at field 11 (R * V = 36, irregular at the
default rows) gave the default's objects at rows 2 and a different split at rows 4, 8 and 16; N = 8
at field 10 (R * V = 33, regular at the default and at rows 2 and 4) split at rows 8 into [15, 15,
15, 15, 9, 15, 9, 15, 15, 3] (the sum 126); N = 11 at field 7 and N = 2 at field 15 (R * V = 32)
stayed regular at rows up to 8 (5 of 5). So the attribute rows add to what a task holds [infer: the
limit counts the attribute rows with the output rows; these jobs do not give the weight]: Q094.

**The index list's first trailing word.** [HW] With five copies, the top nibble of the word at 0xf,
0xd and 0x7 and the attribute rows (VDM_TASK1 bits 14:7) at 1, 2 and 4: the object's PDS words,
first vertex, format word and primitive list equal the control's in 9 of 9 jobs. So bits 31:28 are
neither the task's maximum nor the attribute count in anything our jobs show (as E414); what they
count is still open (Q092).

**What it does not show.** The vertices' fate in an overrun by identity (which are dropped); whether
the pixels follow (the jobs ran without the pixel readback); the closed driver's choices of 15, 13,
9, 7 and 2.

**Correction 2026-11-10:** E702's a = 8 words at R * V = 33 lost a vertex again on later runs:
vertex 70 in 2 of 3 runs of S1 (E738) and 5 of 6 of S1b (E755), three different outcomes over the
six (x2156 with a split of 9, 9 and 3, x2260 with the regular split, x2288 with none). So the lost
vertex at 33 with 8 rows is a recurring event of that job and not a one-off, intermittent under a
reset before every job. That the vertex lost here is vertex 70 is not shown (this record does not
give its id).
