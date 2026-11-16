+++
id = "E1121"
claim = "r30-evst2 on module 7CE8E38E (Q111), stages e1 and e5 (CR_EVENT_STATUS alone at 539 to 548 ns a sample, every control passed, every row held out against E1115): CR_EVENT_STATUS reads 0x20000000 outside the job (13 of 13 rows) and 0x24000000 whenever bit 26 is set (9 rows); bit 26 is seen in 4 of 8 e1 jobs (H-PART held, H-EVERY refuted), its first episode 63.3 to 80.3 us in the three e1 rows with a render end and 4.2 us in one without (H-WIDE1 refuted once), rising 92.3 to 109.2 us before the render end where seen (H-BEFORE 3 of 3); bits 6, 9 and 20 never show in e1 (H-SUB 8 of 8); in -n 3 jobs four of five show bit 26 twice or more and one three times (H-ONCE and H-EACH both refuted), the first render's 53.5 to 76.5 us wide and the later ones 4.1 to 5.9 us"
unit = "platform"
method = "r30-evst2 (render/closing-r30-evst2), stages e1, e5 of the question-closing pass (round 30: the corrected rerun of r30-evst, whose e2-e4 controls had a wrong frozen CR_CACHE_CTRL value (E1116); the frozen files reserve E1117 and E1118, folded as E1120 and E1121 by the lead's record decision), dataset render-closing-r30-evst2; attempt out/20261116-132348 (scores score-e1.txt, score-e5.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline TOTAL LEAD REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64 [-n 3]` after a debugfs reset, no knob and no register write; the rows tables/STAGE.txt from gen/make.py, every non-control row held out, the frozen predictions predictions/STAGE.tsv from E1115's and E1116's kept rows); freezes: FROZEN.sha256 199da94a09bec800eaefcf4e49e5dbf59dcad301071609880b385444b5b97558 (62 files), PREDICTIONS.sha256 0168a6b58d1372f0feb1e0e8586dfeccbaa9a5ff1f49fcb73eb0a3e8a5742cd3 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 24e4a365, resgx545:tools/closing/kit/lib_kit.sh at 24e4a365, resgx545:tools/closing/kit/run_stage.sh at 24e4a365, resgx545:tools/closing/kit/kitscore.py at 24e4a365, resgx545:tools/closing/kit/fake/sudo at 24e4a365, resgx545:tools/closing/kit/fake/timeout at 24e4a365, resgx545:tools/closing/kit/fake/df at 24e4a365, resgx545:tools/closing/kit/fake/modinfo at 24e4a365, resgx545:tools/closing/kit/fake/sha256sum at 24e4a365, resgx545:tools/closing/kit/fake/tool.sh at 24e4a365, resgx545:tools/closing/kit/fake/tool.py at 24e4a365, resgx545:tools/closing/kit/fake/ssh.py at 24e4a365, resgx545:tools/closing/scorekit.py at 24e4a365, resgx545:tools/closing/sessioncheck.py at 24e4a365, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-1.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-2.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-3.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-4.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-5.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-1.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-2.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-3.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-4.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-5.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-idle-r2-1.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri256n3-r7-1.txt.gz at a1c3d8c3, data:platform/register-timelines/output.txt at a1c3d8c3, data:platform/event-bits/cases.tsv at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e1/e1-01.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e1/e1-12.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e5/e5-05.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-01.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-03.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-c1.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e3/e3-03.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e4/e4-01.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-c1.snap0.regs.gz at a1c3d8c3, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-evst2:out/20261116-132348/e1/", "render-closing-r30-evst2:out/20261116-132348/e5/", "render-closing-r30-evst2:fold/"]
terms = ["CR_EVENT_STATUS"]
+++
**What ran.** r30-evst2's stages e1 (10 jobs, `1.5 0.5 0x012c`, two controls and 8 held-out
rows) and e5 (7 jobs, the same with `-n 3`), every model frozen from E1115 (closing29/r30-evst2
README, pre-run): H-ALONE, H-WIDE1 (bit 26's first episode 40 to 140 us), H-BEFORE, H-SW, H-SUB,
H-IDLE, H-PART (seen in 0 to 7 of 8) against H-EVERY, and for e5, restated, H-ONCE (at most 2 of
5 rows with two or more episodes) against H-EACH (3 or more rows with three or more). Controls:
diff 0, idle 0x20000000, the sample interval within 300 to 2500 ns.

**Frozen verdict (as printed).** Controls PASS (ivl 539 to 547 ns). e1: `H-IDLE (8 of 8)`,
`H-ALONE (4 of 8 rows decided)`, `H-BEFORE (6 of 16 rows decided)` (two clauses a row), `H-SUB
(8 of 8)`, `H-SW (3 of 8)`, `H-PART (1 of 1)`, `H-EVERY ... not supported`, `H-WIDE1 ... not
supported: 3 held, 1 FAILED, 4 cannot tell of 8`. e5: `H-ALONE (5 of 5)`, `H-IDLE (5 of 5)`,
`H-SW (5 of 5)`, `H-ONCE ... not supported` (multi 4), `H-EACH ... not supported` (each 1).
fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** e1: bit 26 in e1-03 (4.2 us, no render end in the window), e1-05 (63.3 us),
e1-06 (80.3), e1-07 (76.7), first rise 92.3 to 109.2 us before the render end in the last three;
four rows without it. e5 (fold/posthoc.txt): e5-01 one episode (76.5 us), e5-02 two (5.9 us
before its second render's end, 4.2 us 18.9 ms after its third), e5-03 two (53.5, 5.9), e5-04
three (67.4, 4.1, 4.1: one a render, each 19.5 to 93.6 us before that render's end), e5-05 two
(54.8, 4.2); the later renders' episodes 19.5 to 107.7 us before their render's end. Every
sample with bit 26 read 0x24000000. Bits 6 and 9 once in e5-02. Every job drew exactly.

**What it shows.** E1115's idle word and its bit 26 word repeat on a held-out run and a second
module; bit 26 is again absent from about half the one-render jobs at 541 ns; a later render in
one context can show bit 26 too, short (4 to 6 us), so it is neither once a job nor reliably once
a render. The first episode's width is not a fixed 40 to 140 us (one of 4.2 us).

**What it does not show.** Whether an unseen bit 26 rose under a sample, which event sets it in
a later render, who clears it, and the other bits' events (Q111).
