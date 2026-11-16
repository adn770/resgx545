+++
id = "E1123"
claim = "r31-cc on module 7CE8E38E (Q111, the fwsim read of CR_CACHE_CTRL after a kick), stages c4 (CR_EVENT_STATUS, CR_CACHE_CTRL, CR_DMS_CTRL, CR_USE0_SERV_EVENT and CR_BIF_CTRL at 1766 to 1789 ns a sample, plain triangles) and c5 (the same without CR_DMS_CTRL, the default fill), every control passed, every row held out: CR_BIF_CTRL reads 0x00000008 from 5.7 and 6.8 us before CR_CACHE_CTRL's change to its sample in the 2 rows that order them (c4-04, c5-01; H-BIF-FIRST held, H-BIF-LATER refuted there; 12 rows cannot tell), which the fold reads as the firmware's BIF write of the kick pass [infer], so the hardware does not set bit 28 at the kick; the change comes before every CR_EVENT_STATUS event (H-CCFIRST 14 of 14), once from 0x0000ffff to 0x1000ffff (H-CC-ONE 14 of 14), with no served count in the 30 us before it (H-CNT-LAG 14 of 14, H-CNT-LEAD refuted); CR_DMS_CTRL is written 31.0 to 43.6 us after it (H-DMS 8 of 8); a fill's kick changes it as a triangle's does (H-CC-XFER 6 of 6, H-CC-TA refuted)"
unit = "platform"
method = "r31-cc (render/closing-r31-cc), stages c4, c5 of the question-closing pass (round 31: the fwsim run of resgx545 2ffa9a9 stopped on the microkernel's CR_CACHE_CTRL read after a TA kick, before its own write, and this session times the change against the kick; session built by the lead's request, safe class; the frozen README reserves E1122, folded as E1122 and E1123 by the lead's record decision), dataset render-closing-r31-cc; attempt out/20261116-144402 (scores score-c4.txt, score-c5.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline 1.5 0.5 REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64` (c5: `fill`, 64 x 32) after a debugfs reset, no knob and no register write; the rows tables/STAGE.txt from gen/make.py, every non-control row held out, the frozen predictions predictions/STAGE.tsv from E1120's kept rows (post hoc there), the kit's snapshots and E013); freezes: FROZEN.sha256 19ad7fb59f0babb9f49394bc3d7fd1f3a721746edc54634f4dcd46b40283fd76 (54 files), PREDICTIONS.sha256 b9924da15695f86418e16ff63fca276b791cb2110b01aaf469a9abc48587955b (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 2ffa9a93, resgx545:tools/closing/kit/lib_kit.sh at 2ffa9a93, resgx545:tools/closing/kit/run_stage.sh at 2ffa9a93, resgx545:tools/closing/kit/kitscore.py at 2ffa9a93, resgx545:tools/closing/kit/fake/sudo at 2ffa9a93, resgx545:tools/closing/kit/fake/timeout at 2ffa9a93, resgx545:tools/closing/kit/fake/df at 2ffa9a93, resgx545:tools/closing/kit/fake/modinfo at 2ffa9a93, resgx545:tools/closing/kit/fake/sha256sum at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.sh at 2ffa9a93, resgx545:tools/closing/kit/fake/tool.py at 2ffa9a93, resgx545:tools/closing/kit/fake/ssh.py at 2ffa9a93, resgx545:tools/closing/scorekit.py at 2ffa9a93, resgx545:tools/closing/sessioncheck.py at 2ffa9a93, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-01.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-03.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-04.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-05.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e3/e3-05.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e3/e3-07.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e4/e4-01.txt.gz at dc838e60, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-c1.snap0.regs.gz at dc838e60, data:render/closing-r8-k2/out/20261113-032428/xf/xf-c-fill.snap0.regs.gz at dc838e60, data:render/closing-r8-k2/out/20261113-032428/xf/xf-c-fill.snap9.regs.gz at dc838e60, data:render/closing-r8-k2/out/20261113-032428/xf/xf-c-fill.txt.gz at dc838e60, data:render/closing-r9-faults/out/20261113-084720/xf2/xf-c-fill.snap0.regs.gz at dc838e60, data:render/closing-r9-faults/out/20261113-084720/xf2/xf-c-fill.snap9.regs.gz at dc838e60, data:platform/register-timelines/output.txt at dc838e60, data:platform/event-bits/cases.tsv at dc838e60, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r31-cc:out/20261116-144402/c4/", "render-closing-r31-cc:out/20261116-144402/c5/", "render-closing-r31-cc:fold/"]
terms = ["CR_CACHE_CTRL", "CR_USE0_SERV_EVENT", "CR_BIF_CTRL", "CR_EVENT_STATUS", "CR_DMS_CTRL"]
+++
**What ran.** r31-cc's last two stages (closing29/r31-cc README, pre-run): c4 (10 jobs,
`0x012c,0x0804,0x0a74,0x0b14,0x0c00`, plain 64x64 triangles) and c5 (8, `0x012c,0x0804,0x0b14,
0x0c00`, the default fill, whose kick our kernel sends with INVAL_DATA and no TA). Frozen: E1122's
H-CC-ONE, H-CC-LAT (c4), H-CNT-LAG against H-CNT-LEAD and H-BIF-FIRST against H-BIF-LATER (with
H-BIF-VISIBLE against H-BIF-HIDDEN a stage); H-CCFIRST (the change before every CR_EVENT_STATUS
event, E1120); H-IDLE; c4: H-CC-26 (bit 26 15 to 120 us after the change where it precedes the
render end), H-DMS (CR_DMS_CTRL written 20 to 70 us after it, E1120 e3), H-WAIT (after bit 26's
first rise) against H-NOWAIT; c5: H-CC-XFER (one change, as a triangle's; post hoc from the
kit's snapshots of plain fills) against H-CC-TA (no change). Controls as E1122's with
CR_EVENT_STATUS 0x20000000 and CR_DMS_CTRL 0x00208200.

**Frozen verdict (as printed).** Every control PASS (c4-c1, c4-c2, c5-c1, c5-c2: diff 0,
ivl 1770, 1772, 1457, 1447 ns, cache 0x0000ffff, idle 0x20000000, se16 1, bif0 0, dms0
0x00208200). c4: `H-CC-ONE (24 of 24)`, `H-CC-LAT (8 of 8)`, `H-CCFIRST (8 of 8)`, `H-CNT-LAG (16
of 16)`, `H-CNT-LEAD ... not supported: 0 held, 8 FAILED`, `H-DMS (8 of 8)`, `H-IDLE (8 of 8)`,
`H-BIF-FIRST ... (1 of 8 rows decided)`, `H-BIF-LATER ... not supported: 0 held, 1 FAILED, 7
cannot tell of 8`, `H-BIF-VISIBLE (1 of 1)`, `H-BIF-HIDDEN ... 1 FAILED`, `H-CC-26 [held]: cannot
tell: no row decided`, `H-NOWAIT ... (1 of 8 rows decided)`, `H-WAIT ... not supported: 0 held, 1
FAILED, 7 cannot tell of 8`. c5: `H-CC-XFER (18 of 18)`, `H-CC-TA ... not supported: 0 held, 6
FAILED`, `H-CCFIRST (6 of 6)`, `H-CNT-LAG (12 of 12)`, `H-CNT-LEAD ... 6 FAILED`, `H-IDLE (6 of
6)`, `H-BIF-FIRST ... (1 of 6 rows decided)`, `H-BIF-LATER ... 1 FAILED, 5 cannot tell of 6`,
`H-BIF-VISIBLE (1 of 1)`. fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** CR_BIF_CTRL (fold/posthoc.txt): 0x00000008 in c4-04 from 5.7 us before the
change to its sample (set 3.9 to 7.4 us), in c5-01 from 6.8 us before it (5.3 to 8.2 us), the
change's sample reading 0 again in both; inside the job, with no CR_CACHE_CTRL change, in c4-05
5.07 ms after it (3.5 to 7.1 us, a served count 5.5 us after it clears); no other word, no other
row. The c4-05 and c3-01 (E1122) words show the same bit with no change. CR_CACHE_CTRL: one
change in all 18 rows, before every CR_EVENT_STATUS event, 19.0 to 25.1 ms (c4) and 5.6 to 6.8
ms (c5) after the tool starts. Next served count 5.4 to 7.5 us after the change (c4, 7 rows), 5.0
to 7.4 (c5, 4 rows), in its sample in three rows; none in the 30 us before it. CR_DMS_CTRL
0x00208200 to 0x50208200 31.0 to 43.6 us after the change (8 of 8). Bit 26 showed in c4-05 only,
5.09 ms after the change and after its render end, so H-NOWAIT's one decided row compares the
TA path's write with a late bit 26 (its clause did not require bit 26 before the render end). A
fill adds 2 to 4 served counts beyond the ticks, a triangle 9 to 11. Every job drew exactly.

**What it shows.** Whose the 0x8 is [infer]: bit 3 (INVALDC) is written by the host too (fork
8bc0877e8603: gma500's mmu.c flushes for its own GEM objects, sgx_seq.c at the boot's reset and
for debugfs bif_flush), but each host write is set and cleared by two back-to-back MMIO writes,
no sgxfive job path calls them, and these words last 4 to 8 us and clear in the very sample of
CR_CACHE_CTRL's change, in 2 of 2; the firmware's kick pass writes CR_BIF_CTRL `| 0x8` in the
routine it calls for cache-control bits 0 and 1 before its CR_CACHE_CTRL write (E013). So in the
two ordered rows a firmware response to the kick precedes the change: the hardware does not set
bit 28 at the kick (H-CC-HW refuted where decided), and the change is the firmware's own `|
0x10000000` [infer]. A transfer kick sets it too, so it is the command's cache control and not
the TA. For the fwsim read rule: the firmware's read after the kick saw 0x0000ffff up to its BIF
write and its write leaves 0x1000ffff, the word read until the reset; sgx-sim answers the read
with the reset word and the write after it (crates/sgx-sim/src/hw.rs).

**What it does not show.** The value of the read itself (it lies inside the sample in which
the change shows; E013 gives it no test, so either value writes 0x1000ffff); a served kick
without INVAL_DATA (the design closing29/r31-cc/fold/next-miscinfo.md); when CR_USE0_SERV_EVENT
counts within a pass; bit 26's lead (no c4 row showed it before a render end); whether the
firmware waits for bit 26 before the TA path.
