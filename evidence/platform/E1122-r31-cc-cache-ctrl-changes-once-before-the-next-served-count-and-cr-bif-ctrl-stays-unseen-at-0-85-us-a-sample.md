+++
id = "E1122"
claim = "r31-cc on module 7CE8E38E (Q111, the fwsim read of CR_CACHE_CTRL after a kick), stages c1, c2, c3 (CR_CACHE_CTRL alone at 540 to 542 ns a sample, with CR_USE0_SERV_EVENT, with CR_BIF_CTRL, both at 849 to 864 ns), every control passed, every row held out: CR_CACHE_CTRL changes once from 0x0000ffff to 0x1000ffff and stays (H-CC-ONE 28 of 28 rows), 18.3 to 25.2 ms after the tool starts (H-CC-LAT 28 of 28); no CR_USE0_SERV_EVENT count comes in the 30 us before the change and the next comes 4.4 to 8.8 us after it in 8 rows and in its sample in 1 (H-CNT-LAG 9 of 9 decided, H-CNT-LEAD refuted); CR_BIF_CTRL shows no word near the change in 10 of 10 rows (H-BIF-HIDDEN held, H-BIF-FIRST and H-BIF-LATER cannot tell)"
unit = "platform"
method = "r31-cc (render/closing-r31-cc), stages c1, c2, c3 of the question-closing pass (round 31: the fwsim run of resgx545 2ffa9a9 stopped on the microkernel's CR_CACHE_CTRL read after a TA kick, before its own write, and this session times the change against the kick; session built by the lead's request, safe class; the frozen README reserves E1122, folded as E1122 and E1123 by the lead's record decision), dataset render-closing-r31-cc; attempt out/20261116-144402 (scores score-c1.txt, score-c2.txt, score-c3.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline 1.5 0.5 REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64` (c5: `fill`, 64 x 32) after a debugfs reset, no knob and no register write; the rows tables/STAGE.txt from gen/make.py, every non-control row held out, the frozen predictions predictions/STAGE.tsv from E1120's kept rows (post hoc there), the kit's snapshots and E013); freezes: FROZEN.sha256 19ad7fb59f0babb9f49394bc3d7fd1f3a721746edc54634f4dcd46b40283fd76 (54 files), PREDICTIONS.sha256 b9924da15695f86418e16ff63fca276b791cb2110b01aaf469a9abc48587955b (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2ffa9a93, resgx545:tools/closing/kit/lib_kit.sh at 2ffa9a93, resgx545:tools/closing/kit/run_stage.sh at 2ffa9a93, resgx545:tools/closing/kit/kitscore.py at 2ffa9a93, resgx545:tools/closing/kit/fake/sudo at 2ffa9a93, resgx545:tools/closing/kit/fake/timeout at 2ffa9a93, resgx545:tools/closing/kit/fake/df at 2ffa9a93, resgx545:tools/closing/kit/fake/modinfo at 2ffa9a93, resgx545:tools/closing/kit/fake/sha256sum at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.sh at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.py at 2ffa9a93, resgx545:tools/closing/kit/fake/ssh.py at 2ffa9a93, resgx545:tools/closing/scorekit.py at 2ffa9a93, resgx545:tools/closing/sessioncheck.py at 2ffa9a93, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-01.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-03.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-04.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-05.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e3/e3-05.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e3/e3-07.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e4/e4-01.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-c1.snap0.regs.gz at dc838e60, data:render/closing-r8-k2/out/20261113-032428/xf/xf-c-fill.snap0.regs.gz at dc838e60, data:render/closing-r8-k2/out/20261113-032428/xf/xf-c-fill.snap9.regs.gz at dc838e60, data:render/closing-r8-k2/out/20261113-032428/xf/xf-c-fill.txt.gz at dc838e60, data:render/closing-r9-faults/out/20261113-084720/xf2/xf-c-fill.snap0.regs.gz at dc838e60, data:render/closing-r9-faults/out/20261113-084720/xf2/xf-c-fill.snap9.regs.gz at dc838e60, data:platform/register-timelines/output.txt at dc838e60, data:platform/event-bits/cases.tsv at dc838e60, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r31-cc:out/20261116-144402/c1/", "render-closing-r31-cc:out/20261116-144402/c2/", "render-closing-r31-cc:out/20261116-144402/c3/", "render-closing-r31-cc:fold/"]
terms = ["CR_CACHE_CTRL", "CR_USE0_SERV_EVENT", "CR_BIF_CTRL"]
+++
**What ran.** r31-cc's first three stages (closing29/r31-cc README, pre-run): c1 (10 jobs,
`0x0804` alone), c2 (12, `0x0804,0x0b14`) and c3 (12, `0x0804,0x0c00`), each a plain 64x64
triangle after the kit's reset, two controls and the rest held out. Frozen from E1120's kept rows
(post hoc there) and E013: H-CC-ONE (one change, 0x0000ffff to 0x1000ffff, held to the end),
H-CC-LAT (10 to 40 ms after the tool starts), H-CNT-LAG (no served count in the 30 us before the
change, the next 0 to 12 us after it) against H-CNT-LEAD (a count in the 30 us before it), and
H-BIF-FIRST (a CR_BIF_CTRL word other than its first in the 30 us before the change: the
firmware's BIF calls for cache-control bits 0 and 1 precede its write at bit 3, E013) against
H-BIF-LATER (only in the 15 us after it), with H-BIF-HIDDEN (no row decides, E258) against
H-BIF-VISIBLE. Controls: diff 0, the sample interval in the stage's window, the first sample's
CR_CACHE_CTRL 0x0000ffff, CR_USE0_SERV_EVENT bit 16 and CR_BIF_CTRL 0 as the kit's snapshot after
the reset reads them.

**Frozen verdict (as printed).** Every control PASS (c1-c1, c1-c2, c2-c1, c2-c2, c3-c1,
c3-c2: diff 0, ivl 540 to 542, 854 to 860 and 850 to 855 ns, cache 0x0000ffff, se16 1, bif0 0).
`c1 H-CC-ONE ... (24 of 24 rows decided)` (three clauses a row), `c1 H-CC-LAT (8 of 8)`; `c2
H-CC-ONE (30 of 30)`, `c2 H-CC-LAT (10 of 10)`, `c2 H-CNT-LAG ... (18 of 20 rows decided)` (two
clauses a row; c2-08 cannot tell, a tick near the change), `c2 H-CNT-LEAD ... is not supported: 0
held, 9 FAILED, 1 cannot tell of 10`; `c3 H-CC-ONE (30 of 30)`, `c3 H-CC-LAT (10 of 10)`, `c3
H-BIF-HIDDEN ... (1 of 1 rows decided)`, `c3 H-BIF-VISIBLE ... is not supported: 0 held, 1
FAILED`, `c3 H-BIF-FIRST [held]: cannot tell: no row decided` and the same for H-BIF-LATER.
fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** CR_CACHE_CTRL: 0x0000ffff in the first sample of all 34 rows, one change to
0x1000ffff and no return in all 34, 18.3 to 23.0 ms (c1), 18.7 to 23.5 (c2) and 20.4 to 25.2 (c3)
after the tool starts. CR_USE0_SERV_EVENT: no count in the 30 us before the change where a tick
cannot fall there (9 of 9), the next count 4.4 to 8.8 us after it (8 rows) or in its sample
(c2-09), 10 to 11 counts beyond the ticks over each triangle, bit 16 never seen clear in the 30 us
before the change. CR_BIF_CTRL: 0 near the change in all 12 c3 rows; once 0x00000008 for 4.0 to
5.7 us, 44.6 ms after the change inside c3-01's job (fold/posthoc.txt). Every job drew exactly.

**What it shows.** At about 0.85 us a sample the change still comes before the kick's next
served count, never after a count in the 30 us before it, so the count does not mark a
firmware pass that ends before the change. CR_BIF_CTRL's word near the change is shorter than
about 0.85 us or absent in every c3 row; E1123's five-register rows saw it twice [infer: the
firmware's BIF write lasts a few us only sometimes, or its sample lands by chance].

**What it does not show.** When CR_USE0_SERV_EVENT counts within a pass (at the task's start
or end), so H-CNT-LAG alone does not order the change against the firmware; whether the
hardware or the firmware sets bit 28 (E1123 orders two rows).
