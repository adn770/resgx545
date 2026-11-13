+++
id = "E1019"
claim = "Round 12 offline (Q036; no run): over every kept closing-pass job with a DPM register timeline (697 jobs, 285824 timeline lines of closing r1-pixgeo, r2-geo, r3-geo, r3-geo-c, r5, r6 and r7-dpm, r8 and r9-ldpm, r10-dpm, s1 and s1b) and every kept after-read of 0x071c (1594, r1 to r7 and s1, s1b), frozen by hash before any of them was scored, the high halves of the STATUS2 registers are 0 in every sample: 0x0710 bits 31:16 in 285824 of 285824 lines and 0x071c bits 31:16 in 1594 of 1594 after-reads, through jobs whose global page count (0x072c bits 31:16) reached 6 (104 jobs), 7 (79), 11 (3), 13 (5) and 18 (4), where every earlier record stopped at 5; the frozen rivals (a non-zero high half once the global list passes 5 pages, or anywhere) are refuted. 0x0748 bit 2 clears in 195 of 197136 held-out lines (one line in most jobs that clear it); by log-loss on the held-out jobs a rate per partial render beats a rate per line, the 0x100-page class and a constant at global counts up to 5 (199.5 against 224.9 for the constant) and above (67.5 against 114.1) [HW, held out offline; infer: bit 2 clears with partial renders, a ranking, not a rule]"
unit = "dpm"
method = "Offline, no run (round 12, decision R12-3 a of closing12/DECISIONS-R12.md and closing12/plan/rank-round12.md, finding 2). Data: every out/**/<case>.txt.gz of the published sessions render-closing-r1-pixgeo, -r2-geo, -r3-geo, -r3-geo-c, -r5-dpm, -r6-dpm, -r7-dpm, -r8-ldpm, -r9-ldpm, -r10-dpm, -s1 and -s1b with a 'timeline: regs' header holding 0x0710 and 0x0748, and every <case>.after.regs.txt.gz with a 0x071c line (those sessions and render-closing-r3-pixel, -r4-pixel, -r5-pixel and -r6-pixel; r8-ldpm, r9-ldpm and r10-dpm kept none). Check closing12/plan/c1-q036/: q036_rule.json (sha256 7be7002fb0e5045b48f06b59bb0e75af188fe31157c09d63568a02a323b38d02, FREEZE.log 2026-11-13T12:19:19Z: read before were the head of a0-cal-2048.txt.gz and of its after-read for the format, E873 and E1013 for the global count, dpm_raise.py's code) freezes H0 (both high halves 0 in every sample, whatever G), the rivals H-TAIL and H-ANY, G as the job's maximum of 0x072c bits 31:16 (38 jobs without 0x072c have no G), and for 0x0748 bit 2 four rates fitted on r1-pixgeo, r2-geo, r3-geo and r3-geo-c (139 jobs, 88688 lines, 96 clear lines) and scored by log-loss and Brier on the 558 jobs of the other eight sessions, split at G 5: R-LEN (a rate per line), R-PR (a rate per partial render, the stretches of 0x0658 bit 0), R-0x100 (the 0x100-page class by name) and R-CONST; scorer q036_score.py (q036_score.out), notes NOTE.md. This fold re-ran q036_score.py with python -I on resgx545-data ffd076572 and got a byte-identical output; sgx-pipe's `dpm::STATUS2_HIGH_HALF` holds the reading (status2_s_high_halves_are_zero_through_every_kept_timeline_e1019)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r1-pixgeo", "render-closing-r2-geo", "render-closing-r3-geo", "render-closing-r3-geo-c", "render-closing-r3-pixel", "render-closing-r4-pixel", "render-closing-r5-dpm", "render-closing-r5-pixel", "render-closing-r6-dpm", "render-closing-r6-pixel", "render-closing-r7-dpm", "render-closing-r8-ldpm", "render-closing-r9-ldpm", "render-closing-r10-dpm", "render-closing-s1", "render-closing-s1b", "cited-scratch:closing12/plan/c1-q036/", "cited-scratch:closing12/plan/rank-round12.md"]
terms = ["CR_DPM_3D_FREE_LIST_STATUS2", "CR_DPM_REG_0748", "Dynamic Parameter Management (DPM)"]
+++
**What was done.** E358, E443, E574 and E626 read STATUS2's high halves as 0 in every sample of
their timelines, all of jobs whose global list held at most five pages, and Q036 asked for a scene
past five. The closing pass has since kept register timelines of 0x0700 to 0x0750 in twelve
sessions, never read for these bits. The round 12 planner froze the reading by hash after seeing
only one file's head for the format, then scored every kept job; this fold re-ran the scorer byte
for byte.

**Results [HW, held out offline]** (q036_score.out):

- H0: 0x0710 bits 31:16 non-zero in 0 of 285824 timeline lines (697 jobs); 0x071c bits 31:16
  non-zero in 0 of 1594 after-reads. H-TAIL and H-ANY: no non-zero sample, refuted.
- G, the job's highest global page count: 0 (1 job), 1 (160), 2 (20), 3 (59), 4 (90), 5 (134), 6
  (104), 7 (79), 11 (3), 13 (5), 18 (4); 38 jobs without 0x072c in the header have none.
- 0x0748 bit 2, held out (558 jobs, 197136 lines): 195 clear lines in 169 jobs. Log-loss by split:

| split | jobs | R-PR | R-CONST | R-0x100 | R-LEN |
| --- | --- | --- | --- | --- | --- |
| G <= 5 | 334 | 199.5 | 224.9 | 226.0 | 276.6 |
| G >= 6 | 186 | 67.5 | 114.1 | 112.1 | 88.9 |

Fit: 0.171 clear lines per partial render (R-PR), 0.00108 per line (R-LEN). r10-dpm (17
jobs, one partial render) has no clear line; 38 held-out jobs without a G are in neither split.

**What it shows.** [HW, held out offline] The high halves of the STATUS2 registers hold nothing
through jobs whose global list reaches 18 pages: they are not a second page count or the list's
tail at any size the pass ran. E443's "0 in every sample" holds well past its five pages (an
appended note there). [infer] 0x0748 bit 2 clears with partial renders, not with the job's length
or the buffer's size: a ranking of four rates on held-out jobs, not a rule that predicts a line.

**What it does not show.** 0x071c during a job (it is only in after-reads) and after the jobs of
r8-ldpm, r9-ldpm and r10-dpm (none kept); what bit 2 marks, or a clear line predicted to the
sample (the sampling is about 8 us, a short pulse can be missed); the partial-render count's
confound with the session and the job type (none removed); the other bits of 0x0748,
`CR_DPM_3D_PAGE_COUNTS`' high half and the owner words (Q036). Refuted by: one non-zero high half
of 0x0710 or 0x071c in any job.
