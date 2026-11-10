+++
id = "E800"
claim = "R3-geo stage g-c6 (5 jobs, the tool's triangle with 1500 vertices at a 2048x2048 target in a render context made for up to 4096x4096, --max-width 4096 --max-height 4096): the calibration at P 0x422 (thr0 0x400) never overflowed (0 partial renders, peak 0x213, the page need of the plain 2048x2048 context in E785), the cell at g-c4's last raise (P 0x104, thr0 0xe2) raised the threshold (peaks 0xe2, 0x102, 0x9b), the cell at g-c4's first silent (P 0x105, thr0 0xe3) did not (0xe3 three times) and neither did thr0 0x100 (P 0x122; 0x100, 0x100, 0x4f), and the cell at thr0 0x120 was skipped by the runner (twice its thr0, 576, not below the page need 531); H-target (the flip of g-c4) HOLDS, 3 of 3 cells, and H-context (the 4096x4096 limit, a raise at every valid cell) is REFUTED"
unit = "dpm"
method = "R3-geo stage g-c6 of the question-closing pass, round 3 (session L1, decision R3-G6; seventh of nine stages, 5 jobs, the cells at g-c4's flip read by the runner from g-c4's kept observations), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:53:32 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width 2048 --height 2048 --max-width 4096 --max-height 4096 --vertices 1500 --dump-render with p1139-green, render_pb_pages written to P and read back, the regtimeline of g-c4, a debugfs reset before each job, 4 run of class ok (rc 3 for the 3 that overflowed, rc 0 for the calibration), 1 skipped; scored by the frozen score/score_r3.py g-c6 (out/score-g-c6.txt) with g-c4's controls (same session, tool and day)"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-c6/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** R2's 2048x2048 jobs (E785) and g-c4 (E799) ran in a render context made for
2048x2048, so the target and the context changed together against 4096x4096. G-c6 keeps the
2048x2048 target and makes the context for 4096x4096: H-target says the flip stays at g-c4's
(0xe2 raises, 0xe3 does not), H-context says the 4096x4096 limit applies (a raise at every valid
cell).

**Frozen verdict (as printed).** `controls pass (g-c4's); H-target HOLDS (3 of 3 cells as g-c4's
flip at 0xe2); H-context REFUTED; page need 0x213 at P 0x422 (0 partial renders)`.

**Results [HW].**

| job | P | thr0 | partial renders | peaks | raise |
|---|---|---|---|---|---|
| c6-cal | 0x422 | 0x400 | 0 | 0x213 | none (no overflow) |
| c6-L | 0x104 | 0xe2 | 2 | 0xe2, 0x102, 0x9b | raised |
| c6-F | 0x105 | 0xe3 | 2 | 0xe3, 0xe3, 0xe3 | none |
| c6-0x100 | 0x122 | 0x100 | 2 | 0x100, 0x100, 0x4f | none |
| c6-0x120 | 0x142 | - | - | - | skipped (twice thr0, 576, not below the need, 531) |

The three cells that ran gave the peaks of g-c4's cells at the same thr0 (c4-b5, c4-b6 and
c3-2048-0x122).

**What it shows and does not.** With the target held at 2048x2048, a context made for 4096x4096
changed neither the page need (0x213) nor the flip: the limit follows the render target (or the
scene drawn into it) and not the size the context was made for. One target and one scene; the
cell at 0x120 could not run with this scene's page need.
