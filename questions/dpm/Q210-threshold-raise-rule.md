+++
id = "Q210"
question = "what makes the DPM raise the first abort's threshold by 0x20 (TA3DCtl dwords 37 = 1 << 16 | P - 0x22 and 38 = 0x20) when twice the abort's status is below the scene's page need plus a constant k (2 or 3 at 1024x768, 2 to 13 at 4096x4096)?"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E312", "E464", "E625", "E627", "E629"]
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
