+++
id = "E785"
claim = "R2-geo stage g-c3 (11 jobs, the tool's triangle with 1500 vertices, p1139-green, the first threshold thr0 = P - 0x22 set by render_pb_pages and read from the job's own 0x0624 in 11 of 11): the controls at 4096x4096 passed (c3-4096-0x372 raised, thr0 0x350, run peaks 0x350, 0x370, 0x23d, dword 38 = 0x20; c3-4096-0x374 did not, thr0 0x352, peaks 0x352 three times: E774's flip reproduced), and at 2048x2048 the scene's page need was 0x213 (531 pages, the calibration c3-2048-cal at P = 0x422 overflowed no threshold, peak status 0x213, held-out 'no overflow'), so the five cells with thr0 from 0x332 to 0x400 (P = 0x354, 0x372, 0x374 and 0x394, and the calibration) never reached a first abort (0 partial renders: void), the cell P = 0x162 (thr0 0x140) overflowed but its second run peaked at 0xe6 below thr0 (void), and the three cells that read: P = 0xa2 (thr0 0x80, peaks 0x80, 0xa0, 0xa0) and P = 0xe2 (thr0 0xc0, peaks 0xc0, 0xe0, 0xe0) raised the threshold by 0x20 (dword 38 = 0x20), P = 0x122 (thr0 0x100, peaks 0x100, 0x100, 0x4f) did not; the frozen verdict was a flip at 2048x2048 with C in [0xe0, 0x120) and H-same (the limit of 4096x4096, 0x371, at this target) REFUTED, 2 of 3 cells as 0x371 predicts (the cell 0x122 predicted a raise)"
unit = "dpm"
method = "R2-geo stage g-c3 of the question-closing pass, round 2 (fourth of five stages, 11 jobs: 2 controls at 4096x4096, the calibration and 8 cells at 2048x2048 of which the proposal's four (P = 0x354, 0x372, 0x374 and 0x394) and four low ones added in preparation because the tool's vertex cap of 1500 left a quarter of the area's page need below thr0 at those P; the fallback g-c3f was not needed and not run), dataset render-closing-r2-geo, on the laptop (host cedar), 2026-11-10 at 10:51:00 laptop time (09:51 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width W --height H --vertices 1500 --dump-render with p1139-green (the 4096x4096 jobs keep a 4.6 MB PB dump), the knob render_pb_pages written to P and read back, regtimeline 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x072c and 0x0748, a debugfs reset before each job, all 11 of class ok (rc 3 'scene overflowed' for the 6 that overflowed, rc 0 for the 5 that did not); the knob proof per job its own 0x0624 rows, the raise read from the control block (dword 38 = 0x20, dword 37) and the run peaks of 0x0724; scored by the frozen score/score_r2.py g-c3 (out/score-g-c3.txt) with the frozen readers of R1; the combined reading with E774 and E786 is the lead's and is in Q210, not here"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-geo:out/g-c3/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** E774 gave the raise limit at 4096x4096: the TA's threshold is raised by 0x20 iff
thr0 + 0x20 <= C = 0x371, with P and the threshold moving together. Whether C belongs to the
core, follows P or follows the target was open. C3 repeats the question at 2048x2048, with the 4096
controls first. The tool cannot make a larger scene than 1500 vertices, and the page need of this
scene scales with the target's area (about 1300 pages at 4096x4096, from E704's first abort at
0x400 and the pages after it), so at 2048x2048 the high cells were expected not to overflow, and
four low cells and a calibration job were added to the table.

**Frozen verdict.** `controls pass; 2048x2048: 0xa2:R 0xe2:R 0x122:- 0x162:void 0x354:void
0x372:void 0x374:void 0x394:void -> flip: last raise 0xe2, first silent 0x122: C in [0xe0, 0x120);
H-same REFUTED (2 of 3 cells as 0x371 predicts); D36 unraised 2/3, raised 1/3`. The scorer's
interval is in P - 2 and means the raised threshold thr0 + 0x20 (0xe0 accepted, 0x120 refused).

**Results [HW].**

| job | thr0 (0x0624) | peaks | partial renders | dword 36, 37, 38 | raise |
|---|---|---|---|---|---|
| c3-4096-0x372 (control) | 0x350 | 0x350, 0x370, 0x23d | 2 | 3, 0x10350, 0x20 | raised |
| c3-4096-0x374 (control) | 0x352 | 0x352 x 3 | 2 | 1, 0, 0 | none |
| c3-2048-cal (P 0x422) | 0x400 | 0x213 | 0 | 0, 0, 0 | no overflow |
| c3-2048-0x354 | 0x332 | 0x213 | 0 | 0, 0, 0 | no overflow (void) |
| c3-2048-0x372 | 0x350 | 0x213 | 0 | 0, 0, 0 | no overflow (void) |
| c3-2048-0x374 | 0x352 | 0x213 | 0 | 0, 0, 0 | no overflow (void) |
| c3-2048-0x394 | 0x372 | 0x213 | 0 | 0, 0, 0 | no overflow (void) |
| c3-2048-0x162 | 0x140 | 0x140, 0xe6 | 1 | 3, 0, 0 | none, second run below thr0 (void) |
| c3-2048-0x122 | 0x100 | 0x100, 0x100, 0x4f | 2 | 3, 0, 0 | none |
| c3-2048-0xe2 | 0xc0 | 0xc0, 0xe0, 0xe0 | 3 | 1, 0x100c0, 0x20 | raised |
| c3-2048-0xa2 | 0x80 | 0x80, 0xa0, 0xa0 | 3 | 2, 0x10080, 0x20 | raised |

The "partial renders" column is the scorer's count of 0x0658 stretches. A cell is a reading only
when its second run reaches thr0 (E625): the five no-overflow cells and 0x162 are void. In the two
raised cells the second run reached thr0 + 0x20 (0xe0 and 0xa0).

**What it shows and does not.** At 2048x2048 with 1500 vertices the raise happens at a first
threshold of 0x80 and 0xc0 and not at 0x100: the limit on thr0 + 0x20 is in [0xe0, 0x120). That is
not 0x371, so the limit is not one constant across the two targets (H-same refuted, one flip). It
is bracketed, not exact: the cells between (thr0 0xc1 to 0xff) did not run, and 0x162, which would
have been the next cell above, was void. The scene's page need at 2048x2048 is 0x213 pages; at 4096
it is larger. A quarter of 0x371 is 0xdc, just below the bracket's lower end, so proportionality to
the area is not what the bracket shows, with C exact at one target only [infer, arithmetic on two
brackets]. What C depends on, the target, the page need or the scene, is not separated: both
changed together (a quarter of the area, a lower page need, the same vertex count). The cells above
thr0 0x140 could not be run with a scene this size. The dword 36 column is E790's.
