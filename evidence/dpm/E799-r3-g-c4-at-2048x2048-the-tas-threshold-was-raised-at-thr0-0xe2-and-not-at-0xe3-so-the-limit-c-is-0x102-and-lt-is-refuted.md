+++
id = "E799"
claim = "R3-geo stage g-c4 (10 jobs, the tool's triangle with 1500 vertices, p1139-green, the first threshold thr0 = P - 0x22 set by render_pb_pages and read from the job's own 0x0624): the four controls passed (4096x4096: P 0x372 raised, 0x374 not; 2048x2048: P 0xe2 raised, 0x122 not; E785's cells repeated), and at 2048x2048 the six bisect cells the runner picked from the kept observations (P 0x102, 0x112, 0x10a, 0x106, 0x104 and 0x105, thr0 0xe0, 0xf0, 0xe8, 0xe4, 0xe2 and 0xe3) raised the threshold by 0x20 at thr0 0xe0 and 0xe2 and not at 0xe3, 0xe4, 0xe8 and 0xf0, every cell's second run reaching thr0: one exact flip, last raise at thr0 0xe2 (C = 0x102), first silent 0xe3; LT, frozen before the run (last raise at thr0 floor(0x351 R / 32768) = 0xd4 at this target), REFUTED"
unit = "dpm"
method = "R3-geo stage g-c4 of the question-closing pass, round 3 (session L1, decision R3-G4; fifth of nine stages, 10 jobs: 4 controls and 6 bisect cells whose P the runner computed on the laptop from the observations kept so far, the midpoint of the bracket between the highest raise and the lowest silent cell), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:51:17 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width W --height H --vertices 1500 --dump-render with p1139-green, the knob render_pb_pages written to P and read back, regtimeline 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x072c and 0x0748, a debugfs reset before each job, all 10 of class ok (rc 3 'scene overflowed'); the raise read from the control block after the job (dword 38 = 0x20), the knob proof from each job's own 0x0624, the run peaks of 0x0724 and the partial renders (stretches of 0x0658) by the frozen score/score_r3.py g-c4 (out/score-g-c4.txt), which re-derives every runner pick and flags a pick off the rule (none flagged); C = the last raised thr0 + 0x20 is the scorer's arithmetic (E774's definition)"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-c4/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** E785 bracketed the raise limit at 2048x2048 with 1500 vertices: the threshold was
raised at thr0 0x80 and 0xc0 and not at 0x100, so C (the highest raised threshold the TA accepts,
raise iff thr0 + 0x20 <= C, E774) was in [0xe0, 0x120). G-c4 closes the bracket by bisection, the
runner picking each cell from the observations already kept, after the 4096x4096 and 2048x2048
controls of R2. LT was frozen as the one-parameter prediction from 4096x4096 alone: the last
raise at thr0 floor(0x351 R / 32768), R the region count, 0xd4 at 2048x2048.

**Frozen verdict (as printed).** `controls pass (4 of 4); LT REFUTED: exact flip, last raise thr0
0xe2 (C = 0x102), first silent 0xe3; LT said 0xd4; the measured C replaces it`, with the
observations `0xc0:R 0xe0:R 0xe2:R 0xe3:N 0xe4:N 0xe8:N 0xf0:N 0x100:N`.

**Results [HW].**

| job | set | P | thr0 (0x0624) | partial renders | peaks | raise |
|---|---|---|---|---|---|---|
| c3-4096-0x372 | control | 0x372 | 0x350 | 2 | 0x350, 0x370, 0x23d | raised |
| c3-4096-0x374 | control | 0x374 | 0x352 | 2 | 0x352, 0x352, 0x352 | none |
| c3-2048-0xe2 | control | 0xe2 | 0xc0 | 3 | 0xc0, 0xe0, 0xe0 | raised |
| c3-2048-0x122 | control | 0x122 | 0x100 | 2 | 0x100, 0x100, 0x4f | none |
| c4-b1 | held out | 0x102 | 0xe0 | 2 | 0xe0, 0x100, 0x9b | raised |
| c4-b2 | held out | 0x112 | 0xf0 | 2 | 0xf0, 0xf0, 0x51 | none |
| c4-b3 | held out | 0x10a | 0xe8 | 2 | 0xe8, 0xe8, 0x52 | none |
| c4-b4 | held out | 0x106 | 0xe4 | 2 | 0xe4, 0xe4, 0x9c | none |
| c4-b5 | held out | 0x104 | 0xe2 | 2 | 0xe2, 0x102, 0x9b | raised |
| c4-b6 | held out | 0x105 | 0xe3 | 2 | 0xe3, 0xe3, 0xe3 | none |

In the raised cells the second run peaked at thr0 + 0x20 (0x100 and 0x102); in the silent ones at
thr0. The controls repeated R2's readings (E785 at both targets).

**What it shows and does not.** At 2048x2048, 1500 vertices of the tool's triangle, the raise
happens iff the first threshold is at most 0xe2: the highest raised threshold accepted is 0x102 and
0x103 is refused, inside E785's bracket. LT (C proportional to the region count from 4096x4096's
0x351) put the flip at 0xd4 and is refuted. One scene and one target; what C depends on is E800,
E801 and E802's.

**Correction 2026-11-11:** This adds a reading of the flip's timelines and of one miss, made offline
in round 4 with the guard of the firmware's out-of-memory routine read from the instructions
(reading R-5, `closing4/p7/reading-r5.md`, with `flips.py`, `flips.out`, `guard.py` and
`sweep_last.out` beside it), and leaves the claim as is. [data, SEMI] The cells c4-b5 (last raise,
0xe2) and c4-b6 (first silent, 0xe3) have 3 global pages at the abort, 2 and 1 at the resume, 4 and
3 at the next entry: raise and no raise, 2 of 2 as the guard predicts. One cell is not predicted:
c4-b3 (thr0 0xe8, silent) has the inputs of c4-b5 and no raise. It is the only one of 101 jobs whose
timeline shows the global list grown before the first abort (0x0628 reads 0x10003, then 0x100e8
again), so either the guard misses a condition the grow leaves behind or a gate before 0xbbf took
the second entry out [open]; the sampled registers cannot say which. On the rule "refuted by one
flip on the wrong side" this cell is on the wrong side of the ladder, so the guard is a reading that
fits the flips and 288 of 289 decisions, not a law, until c4-b3 is repeated with `0x0734` and sa8
observed.
