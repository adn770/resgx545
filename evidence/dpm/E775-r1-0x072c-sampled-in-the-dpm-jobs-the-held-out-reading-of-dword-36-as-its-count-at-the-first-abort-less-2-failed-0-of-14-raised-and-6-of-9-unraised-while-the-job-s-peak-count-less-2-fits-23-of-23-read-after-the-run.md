+++
id = "E775"
claim = "CR_DPM_GLOBAL_PAGE_STATUS (0x072c) was sampled in the register timelines of the DPM jobs of R1-pixgeo (the gate of two trial jobs, u-ctl-1 and u-ctl-2a, ran clean: normal class, no log line but ours, 0x0724 peaks 19 and 29 as the controls, a plain triangle exact after each; every later DPM job sampled it), its low and high halves equal at 0x10001 to 0x50005 in the 4096x4096 jobs, and the frozen side-table reading 'dword 36 of the control block = max(the 0x072c count in the sample before the first abort - 2, 0)' failed its held-out part: raised jobs 0 of 14 (g-c1 0 of 13, g-c1f 0 of 1; every one read dword 36 = 3 against a predicted 1) and unraised jobs 6 of 9 in g-c1 and 2 of 2 in g-u1 (the three misses read 3 where the TA data's global list holds 4 pages and dword 36 = 2), while the 9 raised jobs of g-u2 (count 1, floor 0) fit trivially; read after the run and not held out [infer over data]: the page count of the global list in the TA data at the state page (E753's correction of 2026-11-10) equals dword 36 + 2 in the 9 unraised jobs of g-c1 (9 of 9, a reading made before the run and tested on new jobs) and in none of the 14 raised ones (0 of 14, as E627 says: after a raise the page holds the lists of the later runs), and the maximum of the 0x072c count over the whole job less 2 (floor 0) equals dword 36 in all 23 jobs of g-c1 and g-c1f (14 raised, 9 unraised; 3 in every raised job where the count reaches 5, 1 or 2 in the unraised where it reaches 3 or 4)"
unit = "dpm"
method = "R1-pixgeo of the question-closing pass, round 2 (decisions R2-13 and R2-14), the gate of g-u1's first two jobs and the D36 side table of g-u1, g-c1, g-c1f and g-u2 of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:40 laptop time (08:40 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053), the register timeline widened to 0x0720-0x072c (it reads 0x0728 too), read-only; the gate (PREFLIGHT.md section 2, runner and score/gate072c.py): clean = G1 normal class, G2 kernel-log slice with no line but our markers, G3 the header lists 0x072c and 0x0724 and at least 10 rows, G4 every 0x072c sample plausible (not 0xffffffff or 0xdeadbeef, halves at most 0x40, a low half non-zero once), G5 the 0x0724 low-half peak equals the control's frozen U (19, then 29), G6 a plain 64x64 triangle exact right after the job without a reset; two clean jobs in a row gave state pass (gate072c.txt of out/g-u1: u-ctl-1 CLEAN -> pass1, u-ctl-2a CLEAN -> pass), and every later DPM job (b-* of g-u1, g-c1, g-c1f, g-u2) carried the note 072c=sampled; the D36 side table (never gating) as scored by the frozen score/score_r1.py (the count is the low half of 0x072c in the sample before the first rising edge of 0x0658 bit 0, predicted dword 36 = max(count - 2, 0), dword 36 from the buf09 control block after the job); the dump-based and peak-based readings were computed after the run by scratch scripts that import the frozen scorer's reader (score_geo2 reg_series, r1lib Kept and timeline) and the data scripts of closing2/geometry (dw36_glist), not in the repository"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-u1/", "render-closing-r1-pixgeo:out/g-c1/", "render-closing-r1-pixgeo:out/g-c1f/", "render-closing-r1-pixgeo:out/g-u2/"]
terms = ["CR_DPM_GLOBAL_PAGE_STATUS", "ta3d_ctl", "Dynamic Parameter Management (DPM)"]
+++
**What ran.** f0f8720's correction of E753 read dword 36 of the control block post hoc as the page
count of the global list at the first abort, less 2 and not below 0 (99 of 99 jobs that were not
raised, a fit), and named the raised jobs as the held-out part, to be scored by sampling 0x072c
(glossary G0828), which no earlier timeline of these jobs held. The frozen tables of R1-pixgeo
carried that as a side table in every DPM job, never gating, and ran 0x072c first on two trial
jobs.

**The gate [HW].** u-ctl-1 and u-ctl-2a (1024x768, U = 19 and 29) were clean on all six checks, so
the register was sampled in the later DPM jobs; nothing in the kernel logs of the stages differed
from the earlier sessions (BIF_FAULT 0x0 at every reset). In the 4096x4096 jobs of g-c1 the
register rose by one page at a time, 0x10001, 0x20002, 0x30003, fell to 0x20002 or 0x10001 at the
first partial render, rose again and returned to 0 at the end (c-1500-0x360: 1, 2, 3, then 2, 3,
4, 5, then 2, 3, 0); the two halves were equal in every sample read.

**Frozen verdict (side table, as the scorers printed).** g-c1: `D36: unraised jobs 6 of 9; raised
jobs (held out) 0 of 13`; g-c1f: `unraised jobs 0 of 0; raised jobs (held out) 0 of 1`; g-u1:
`unraised jobs 2 of 2; raised jobs (held out) 0 of 0` (the b-lo jobs; the other 19 never started a
partial render); g-u2: `unraised jobs 0 of 0; raised jobs (held out) 9 of 9`. The held-out part of
the reading failed where it could fail: in all 14 raised 4096x4096 jobs the count at the first abort
was 3 (predicted dword 36 = 1) and dword 36 read 3. The g-u2 hits are the floor: the count was 1 and
dword 36 was 0 in all nine, which any reading that predicts 0 for them shares. Of the nine
unraised g-c1 jobs the three misses (P = 0x37a and 0x37c at 1500 vertices and 0x37a at 1350) read
count 3 and dword 36 = 2.

**Read after the run [infer over data; not held out, not frozen].**
- The dump. The global list in the TA data at the state page (offset 0x42000 at 4096x4096; list 16
  of the state page's 17 lists, its count) holds g = 4 pages in five unraised jobs (the three
  misses among them) and 3 in the other four, and dword 36 = max(g - 2, 0) in 9 of 9 unraised
  jobs; in the 14 raised jobs
  g is 3 (11 jobs of 1500 vertices) or 2 (the 3 of 1350) against dword 36 = 3, 0 of 14. This is the
  dump-based reading of E753's correction, on jobs not in its 150: it holds on the unraised ones and
  fails on the raised ones exactly as E627 says (the state page of a raised job holds the lists the
  TA built after the last partial render). The register's count at the first abort was one below the
  dump's in the three jobs where g = 4 and it read 3 (in f-1500-0x37a it read 3 for some 120
  samples before the first partial render and its next change came after it, so the difference is
  not a sampling gap there) [infer: whether the register counts the fourth page only after the
  abort was not read].
- The peak. The maximum over the job of the low half of 0x072c, less 2, not below 0, equals dword
  36 in all 23 jobs of g-c1 and g-c1f: 14 raised (peak 5, dword 36 = 3) and 9 unraised (peak 3
  gives 1 in 4 jobs, peak 4 gives 2 in 5). It also fits the 30 jobs of g-u1 and g-u2 that never
  exceed a count of 2 (dword 36 = 0), where it cannot fail. It was read after the data and has no
  held-out job; it is the one reading of dword 36 that fits the raised jobs.

**Not shown.** Which of the two quantities the firmware reads (the global list's page count at the
first abort or the highest the count reached), since in the unraised jobs they are the same and in
the raised jobs only the second fits; why the peak is reached after a raise (the second run's lists,
as E627); whether dword 36 behaves so at other targets and vertex counts. The peak reading wants a
frozen test on scenes where the peak and the first-abort count differ (raised jobs at another
vertex count or target).
