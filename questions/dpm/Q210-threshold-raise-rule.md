+++
id = "Q210"
question = "what exception to the raise rule of E625 and R2 is wd-glist-1500 (no raise at dword 36 = 3, at every P tried from 0x422 to 0x500), and what makes the DPM raise the first abort's threshold by 0x20 otherwise"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E312", "E464", "E625", "E627", "E629", "E704"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_STATE_BASE0", "ta3d_ctl"]
+++

E625: of 70 overflowed jobs of the default triangle (the jobs `analysis/an_raise.py` selects:
1024x768 in 0x23 to 0x34 pages, 4096x4096 in 0x23 to 0x100, 5 pokes of the descriptor's threshold)
the dwords 37 and 38 read as a raise by 0x20 after the first abort in the 41 for which 2 * thr0 <
U + k (thr0 the first abort's status, U the whole-buffer need, 19 and 287 pages) and not in the
other 29; the boundary pairs are P = 0x2c and 0x2d at 1024x768 (k 2 or 3) and the thresholds 142
and 150 at 4096x4096 (k up to 13). The rule was read from those pairs after the follow-up ran: no
job is held out against it, and at 1024x768, where every count of partial renders is 1, the raise
is seen in the dwords and the second set of lists only, the physical raise being shown at
4096x4096 by the counts. E627: with the raise the state page holds the lists the TA built after
the last partial render, without it the abort's lists (sum thr0 - 1 in 28 of 28); E629: the sign
bit of the stored depth follows the raise in 44 of 44 jobs.

Open: what the DPM compares (pages still to come, a count of the TA's remaining work, a firmware
variable), why the raise is by 0x20, and the value of k, which the boundary pairs bound and do not
fix (the pages the count formula adds are Q211's). When the raised job's second set of lists is
stored is Q045's.

To settle it: a scene of a second shape (two triangles, a wider one) whose need U is known from
its whole-buffer page count, run over P across the predicted boundary, the cells declared before
the runs; a regtimeline of the state page's base and of 0x0658 through a raised job and an
unraised one, sampled while the TA runs.

Narrowed in 11.39 (E704). wd-glist-1500 (1500 vertices at 4096x4096, dword 36 = 3, no raise
although the rule R2 predicts one: the run after the first partial render reaches the status of
the first, R2 formed after reading tg-1024-n-0x28, so fitted, 109 of 110 timeline jobs of the
partial-model batch and 64 of 64 in E625's own scenes) repeated at P = 0x422, 0x424, 0x430,
0x440, 0x442, 0x460 and 0x500 and again at 0x422: the same timeline (status 0x400 at the first
partial render, peaks 0x400, 0x400, 0x11c) and the same control block words in 8 of 8 jobs, no
raise (dwords 37 and 38 zero). P above 0x422 changed nothing the TA does: its threshold register
read 0x400 at the first sample of every job and dword 35 was 0x3fe for every P from 0x422 to
0x500, the parameter-buffer dumps are byte-identical, so the 8 jobs are one condition and 7
repeats if the knob or the page buffer clamps P at 0x422. Two readings are open [infer]: a
ceiling of the threshold at status 0x400, or a P clamped at 0x422. The page-supply model (the
raise needs the pages) is untested above 0x422, not refuted: its 3 misses at P = 0x442 to 0x500
may not have had those pages. The threshold is held at 0x3fe only for P in 0x422 to 0x500; nothing
was run below. The controls below the step of dword 36 (1400 and 1300 vertices) did not run: the
tool refuses vertex counts that are not multiples of 3. Open: whether the knob takes effect, the
ceiling reading (P below 0x420, Q273), the part of dword 36, the exact step between 1350 and
1500.
