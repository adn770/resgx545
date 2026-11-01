+++
id = "E625"
claim = "A one-triangle scene overflows the parameter buffer exactly when the first abort's page status P - 0x22 is below the scene's whole-buffer page need, measured at the boundary as 19 pages at 1024x768 and 287 at 4096x4096 (E310's 0x13 and 0x11f): 1024x768 overflows at 0x33 and 0x34 pages and completes at 0x35 to 0x38, 4096x4096 overflows at 0x13e to 0x140 and completes at 0x141 to 0x144 (13 of 13 boundary jobs, one run each; the declared need of 21 and 289, an assumption 2 pages above the measure, missed 5 of the 13, those at 0x35, 0x36 twice, 0x141 and 0x142); the partial renders counted by the 0x0658 stretches are 1 at 1024x768 for every overflowing P from 0x23 to 0x34 (29 jobs of the default triangle, with and without a depth buffer) and at 4096x4096 10, 5, 3, 2, 2, 2, 1, 1, 1, 1 at 0x23, 0x40, 0x60, 0x80, 0x90, 0xa0, 0xb0, 0xb8, 0xc0 and 0x100, which fit 1 + floor((287 + k - thr0) / (thr0 + 0x1f)), thr0 = P - 0x22, for every k from 2 to 13 (the thr0 = 1 cell, 10 partial renders, sets k >= 2 and the 1024x768 0x23 cell, count 1, sets k <= 13; the spacing is not pinned either, 0x1e fits the 4096x4096 counts as well) and in 4 more cells of a poked descriptor; TA3DCtl dword 35 is the last abort's status less 2 (thr0 - 2 for one partial render, thr0 + 0x1e for more, 0 for a completing job) in all 59 jobs of the scene; dwords 37 and 38 read (1 << 16 | P - 0x22) and 0x20, read as the threshold's raise by 0x20 (HW for the dwords, infer for the raise at 1024x768, where every count is 1 and the dwords are the only sign), in the 41 overflowed jobs for which 2 * thr0 < U + k and 0 and 0 in the other 29 (70 of 70 jobs of the selection below, with k = 2 or 3 at 1024x768 and 2 to 13 at 4096x4096; a rule read after the runs, no job held out); a kernel poke of the descriptor's dword 11 (the ZLS threshold) in a 0x422-page buffer makes the 4096x4096 scene overflow with 5, 3, 2 and 1 partial renders for 0x20, 0x40, 0x80 and 0x100 and not at the default 0x400 (5 of 5)"
unit = "dpm"
method = "tri -n 1 --keep-overflow --dump-each --words --regs 0x0700-0x074c with render_pb_pages set before each job, on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...), regtimeline over 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x0724 and 0x0748 (read-only); the jobs of tables trig, free, state and depth and of follow-up a, a reset before each job except the declared noreset ones; the counts, the dwords and the raise rule are decoded by the dataset's analysis scripts"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_TA_ALLOC_FREE_LIST_STATUS1", "ta3d_ctl", "hw_pb_desc.page_table_base"]
+++

**What ran.** Tables `trig` (29 jobs), `free` (26), `state` and `depth` (jobs of the same scene),
and follow-up a (10 jobs: P = 0x2d to 0x2f at 1024x768, 0x90 to 0xb8 at 4096x4096), on the laptop
(direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and
loaded, never reloaded), stock firmware (own_arm off), tool `sgxfive-test-1135` (sha256
7732b945...; source f5cdccb1...), `tri -n 1 --keep-overflow --dump-each --words --regs
0x0700-0x074c` with `render_pb_pages` set before the job, regtimeline over 0x0654-0x0660,
0x0700-0x0710, 0x0720-0x0724 and 0x0748 (read-only; 0x0658 = 1 stretches count the partial
renders), no register write, a reset before every job except the declared `noreset` ones. The 4
pokes below the default ran in the risky script, the control at 0x400 in the safe one
(`--kpoke-render 1:pb:11=V`). Declared before the runs (`analysis/hashes.txt` in the dataset):
H-trig (overflow iff P - 0x22 < U), the counts R1 (threshold raised once by 0x20) against R3
(never raised), U = 289 at 4096x4096 and 21 at 1024x768 (assumed).

The populations. The 59 jobs of the single-triangle scene are those the tables name `tg-*`,
`fr-1024-*`, `fr-4096-*`, `st-*` jobs of the default triangle and follow-up a. The 70 overflowed
jobs of the raise rule are the ones `analysis/an_raise.py` selects by name (`tg-`, `fr-`,
`st-mv0_0`, `st-sweep`, `st-repeat`, `st-4096`, `dp-z05-g1` and `fa-` jobs): the 1024x768 jobs of
the `dp-z05-g33` and `dl-*` names (a deeper pitch, a load buffer) are not scored there.

**Results [HW].** Boundary: the 1024x768 jobs P = 0x33 to 0x38 and the 4096x4096 jobs 0x13e to
0x144, one run each: overflow below, completion above, the dword 35 of every overflowing one thr0
- 2 (0xf, 0x10 at 1024x768; 0x11a, 0x11b, 0x11c at 4096x4096). The scene's need at the boundary is
  19 and 287 pages, the same numbers E310 gave as the whole-buffer jobs' pages (0x13, 0x11f): a
  measure, so the relation "overflow iff thr0 < the pages a completing job takes" is 13 of 13 at
  the boundary and 5 of 5 with the pokes. The declared 21 and 289 were an assumption: H-trig
  fit 13 of 13, control 14 of 14, held out 36 of 47, and the 11 misses are the 5 boundary jobs at
  0x35, 0x36 (two), 0x141 and 0x142 (they assumed U = 21 and 289) and 6 two-triangle jobs of table
  `state` (0x3c, 0x40, 0x48) that fit in the buffer (a second triangle's need is not the one
  triangle's). R1 (partial renders 1 + floor((289 - thr0) / (thr0 + 0x1f)), dword 35 thr0 - 2 or
  thr0 + 0x1e) held out: 32 of 40 (the same 8 boundary scores), fit 8 of 8, 4 of 4 with the poked
  threshold; R3 (never raised): fit 8 of 8 and held out 23 of 40 (it predicts 20, 4, 2 partial
  renders at 0x24, 0x28, 0x2c at 1024x768 where 1 was seen, and 9, 4, 3 at 4096x4096 0x40, 0x60,
  0x80 where 5, 3, 2 were), so the threshold is raised and then stays: the aborts after the first
  come at the status thr0 + 0x20 (dword 35 0x3c at 0x40 = 0x3e - 2, 0x5c, 0x7c). The count
  formula: with the measured need 287 the counts fit for every k from 2 to 13 in the term U + k (k
  = 2 is the lone lower bound, the thr0 = 1 cell with 10 partial renders, which E204, E312 and the
  two jobs here share; 13 is the 1024x768 0x23 cell, where k = 14 gives 2), and with `thr0 + 0x1e`
  for `thr0 + 0x1f` every 4096x4096 count of the default triangle still fits, so neither the 2 nor
  the spacing is pinned (`analysis/an_trigger.py` for the 59 jobs with k = 2).

The raise: TA3DCtl dwords 37 and 38 are (1 << 16 | P - 0x22) and 0x20 in the jobs whose first
abort is followed by more geometry at the raised threshold and 0 and 0 otherwise. Across the 70
overflowed jobs, 2 * thr0 < U + k predicts which (`analysis/an_raise.py`, k = 2): raised at
1024x768 for P = 0x23 to 0x2c, not for 0x2d to 0x34 (P = 0x2d, 0x2e, 0x2f twice each), and at
4096x4096 raised for 0x23 to 0x80 and 0x90, 0xa0, 0xb0, not for 0xb8, 0xc0, 0x100. The boundary
pairs set the constant: at 1024x768 raised at 0x2c and not at 0x2d gives k in {2, 3}, at 4096x4096
raised at 0xb0 (thr0 142) and not at 0xb8 (150) gives k up to 13. The rule is wholly in sample:
follow-up a was declared and hashed before it ran (first case marker 11:51:13 in the kernel
journal; the hash file's own time is the author's word, the dataset's method says so) and
predicted status, count and dword 35 only (6 of 6 and 4 of 4 jobs hit), not the raise; the rule
was read afterwards, and its 70 are jobs, not cells (about a dozen distinct cells at each size).
At 1024x768 every count is 1, so there "raised" is the dwords 37 and 38 only; the physical raise
(the aborts after the first at thr0 + 0x20) is shown at 4096x4096 by the counts. The poke: the
descriptor's dword 11 sets the first abort's status (V = 0x20, 0x40, 0x80: raised, dword 35 0x3e,
0x5e, 0x9e; V = 0x100: not raised, dword 35 0xfe) while dword 37's low half stays 0x400 = P - 0x22
(so it is computed from P, not read from the descriptor); the default V = 0x400 completes, as the
buffer needs only 287 pages. Journal: no fault, no hang in the 59 jobs.

**Reading [infer].** The 2 more pages in the count (k = 2 where the boundary says 287) fit the
counts and are not shown by a job: they may be pages the final lists or the global list take in
the partial-render path, or any k to 13. The raise rule (the pages still to come after the first
abort exceed the abort's own status) was read from the 1024x768 and 4096x4096 boundary pairs after
the follow-up ran; no job is held out against it, and at 1024x768 the raise itself is read from
the dwords and the second set of lists in the state page (E627) alone. U = 19 and 287 are for the
default triangle only; the scenes of 300 to 900 vertices (E630) refuse the model (the two ranges
of the 300-vertex scene do not meet).

**Not shown.** The count at other scenes' needs (a second triangle's need lies between 23 and 26
pages at 1024x768: overflow at 0x38, completion at 0x3c); what the 2 more pages are; why the raise
follows this rule; the threshold after more than one raise (never seen).
