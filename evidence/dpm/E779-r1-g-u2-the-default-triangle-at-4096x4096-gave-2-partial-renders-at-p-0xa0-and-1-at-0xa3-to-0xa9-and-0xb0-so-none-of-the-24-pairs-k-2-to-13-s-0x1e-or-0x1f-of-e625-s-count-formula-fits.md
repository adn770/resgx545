+++
id = "E779"
claim = "R1-pixgeo stage g-u2 (9 jobs: the tool's triangle at 4096x4096, one render, render_pb_pages P = 0xa0 to 0xb0, U = 287 by E625 and HU1): the number of partial renders (0x0658 bit 0 stretches) was 2 at P = 0xa0 and 1 at P = 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9 and 0xb0 (the controls 2 and 1 as E625 measured passed; every job's 0x0624 read P - 0x22), while the count formula of E625, partial renders = 1 + floor((U + k - thr0) / (thr0 + s)) with the first threshold thr0 = P - 0x22 and every k from 2 to 13 and s = 0x1e or 0x1f (24 frozen pairs), predicts 2 at P = 0xa3 for every pair and 1 only from P = 0xa4 to 0xa9 according to k: the frozen verdict is that E625's count formula is REFUTED at U = 287, none of the 24 (k, s) pairs fitting the 7 held-out cells' counts; the thresholds were raised by 0x20 in all 9 jobs, as the rule of E774 says"
unit = "dpm"
method = "R1-pixgeo stage g-u2 of the question-closing pass, round 2 (decision R2-16; 9 jobs: the controls k-0xa0 and k-0xb0 and the cells k-0xa3 to k-0xa9, the three spacing cells of the proposal not run) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:49 laptop time (08:49 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job tri --width 4096 --height 4096 -n 1 --keep-overflow --wait-ms 20000 --words --regs 0x0700-0x074c with the knob render_pb_pages written to P and the regtimeline 0x0624-0x0628, 0x0654-0x0660 and 0x0720-0x072c (the gate had passed), a debugfs reset before each job, all 9 of class ok (rc 0); the knob proof the job's own 0x0624 rows (P - 0x22: 0x7e at P = 0xa0 up to 0x8e at 0xb0), the count read from the rising edges of 0x0658 bit 0 in the timeline; frozen predictions for each of the 24 pairs from E625's formula (count 2 iff 2 thr0 <= 256 + k for s = 0x1f, 257 + k for s = 0x1e); scored by the frozen score/score_r1.py g-u2 (out/score-g-u2.txt), re-run on the kept files with the same SUMMARY; the form of the post hoc reading at the end was computed by hand from the formula"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-u2/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)"]
+++
**What ran.** E625 fitted the count of partial renders of the one-triangle scene at 4096x4096 with
1 + floor((U + k - thr0) / (thr0 + s)), U = 287, for every k from 2 to 13 and s = 0x1f (0x1e fits
the counts too). The frozen ladder of this stage took the first cells where the pairs split: thr0
129 to 135 (P = 0xa3 to 0xa9), where the formula changes from 2 to 1 at a thr0 that depends on k,
with E625's own jobs at P = 0xa0 (2) and 0xb0 (1) as controls.

**Frozen verdict.** `E625's count formula REFUTED at U = 287: none of 24 (k, s) pairs fits the 7
cells' counts; void []`.

**Results [HW].** Partial renders: P = 0xa0: 2 (control); 0xa3, 0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9:
1 each; 0xb0: 1 (control). With s = 0x1f the formula gives 2 at thr0 129 for every k from 2 up
(2 thr0 <= 256 + k), and for s = 0x1e from k = 1 up, so every pair predicted 2 at P = 0xa3 and the
cell read 1; the other six cells only add that the count stays 1. In all 9 jobs dwords 37 and 38
read a raise (dword 38 = 0x20, dword 37 = 0x10000 | thr0), as E774's limit gives for thr0 at most
0x351.

**Read after the run [infer; not held out].** The step from 2 to 1 lies between thr0 = 126 (P =
0xa0, E625's count 2) and 129 (P = 0xa3); P = 0xa1 and 0xa2 did not run. The formula's form (count
2 iff 2 thr0 <= 256 + k for s = 0x1f, 257 + k for s = 0x1e) agrees with those two cells for k at
most 1 (s = 0x1f) or 0 (s = 0x1e), not for E625's 2 to 13; whether E625's other count cells and
boundary pairs then fit was not recomputed here. So what is refuted is the 24 pairs (k from 2 to
13), not the formula's form.

**What it shows.** At 4096x4096 the default triangle's second partial render is absent from a
first threshold of 129 pages up (0xa3), earlier than E625's pairs put it; k and s are not fixed
(Q211).

**Not shown.** U = 287 was not measured again (the jobs are partial renders at a small P, where the
need is not read); the spacing cells at count 3 did not run; the cells P = 0xa1 and 0xa2; other
scenes.
