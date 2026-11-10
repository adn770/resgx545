+++
id = "E802"
claim = "R3-geo stage g-c7 (11 jobs, --tri-full --vertices 1500 at 2048x2048, a scene whose triangle covers the target, run last behind a calibration gate): the calibration at P 0x422 (thr0 0x400) made 3 partial renders (peaks 0x400 three times, the gate allowed at most 3) and the scorer read its page need as 0x400; the six cells at and around g-c4's flip all raised the threshold by 0x20, thr0 0xd2 (P 0xf4, 67 partial renders), 0xde (0x100, 63), 0xe2 (0x104, 13), 0xe3 (0x105, 13), 0xe7 (0x109, 13) and 0xf3 (0x115, 13), each second run peaking at thr0 + 0x20, so the four bisect cells were skipped (no silent cell above the last raise): no flip among the valid cells, the last raise above them (C at least 0x113 [arithmetic]), and g-c4's last raise 0xe2 outside that interval, the frozen verdict H-scene (the limit differs with the scene); every job ended in class ok with health ok after the stage"
unit = "dpm"
method = "R3-geo stage g-c7 of the question-closing pass, round 3 (session L1, decision R3-G7; the last of nine stages, 11 jobs: the calibration and gate, cells at g-c4's last raise L and first silent F read from g-c4's kept observations and L - 16, L - 4, F + 4, F + 16, then up to four bisect cells), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:58:18 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width 2048 --height 2048 --vertices 1500 --tri-full --dump-render with p1139-green, render_pb_pages written to P and read back, the regtimeline of g-c4, a debugfs reset before each job, 7 run of class ok (rc 3), 4 skipped by the runner; scored by the frozen score/score_r3.py g-c7 (out/score-g-c7.txt) with g-c4's controls and flip"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-c7/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** The 1350-vertex scene of E774 is a prefix of the 1500-vertex one, so E774's HP1 did
not separate the scene from the target, and every other limit (E785, E799, E800, E801) is of the
same triangle. G-c7 draws another scene, `--tri-full`, at 2048x2048, where g-c4 put the flip at
0xe2 / 0xe3: H-target says the same flip, H-scene another. The stage is of the class that ended in
the kernel's hang recovery before (E630, E706), so it ran last and behind a gate.

**Frozen verdict (as printed).** `controls pass (g-c4's); no flip among the valid cells (above):
last raise above the cells; H-scene (g-c4's 0xe2 is outside); calibration: page need 0x400 at P
0x422, 3 partial renders (gate: at most 3); skipped ['c7-b1', 'c7-b2', 'c7-b3', 'c7-b4']`.

**Results [HW].**

| job | P | thr0 | partial renders | peaks | raise |
|---|---|---|---|---|---|
| c7-cal | 0x422 | 0x400 | 3 | 0x400, 0x400, 0x400 | none |
| c7-L-16 | 0xf4 | 0xd2 | 67 | 0xd2, 0xf2, 0xf2 | raised |
| c7-L-4 | 0x100 | 0xde | 63 | 0xde, 0xfe, 0xfe | raised |
| c7-L | 0x104 | 0xe2 | 13 | 0xe2, 0x102, 0x102 | raised |
| c7-F | 0x105 | 0xe3 | 13 | 0xe3, 0x103, 0x103 | raised |
| c7-F+4 | 0x109 | 0xe7 | 13 | 0xe7, 0x107, 0x107 | raised |
| c7-F+16 | 0x115 | 0xf3 | 13 | 0xf3, 0x113, 0x113 | raised |
| c7-b1 to c7-b4 | - | - | - | - | skipped (no silent cell above the last raise) |

The jobs of 63 and 67 partial renders completed (class ok), the stage ran to its end without a
stop, and the health triangle after it was ok.

**What it shows and does not.** At the same target, size and context, with the same vertex count,
another scene raised the threshold at 0xe3, which g-c4's scene did not: the limit depends on the
scene, not on the target alone. C for this scene is at least 0x113; its value was not reached (no
silent cell, the bisect had nothing to bracket). Which property of the scene matters (its page
need, 0x400 or more here against 0x213, the triangles' coverage or their order) is not separated.
