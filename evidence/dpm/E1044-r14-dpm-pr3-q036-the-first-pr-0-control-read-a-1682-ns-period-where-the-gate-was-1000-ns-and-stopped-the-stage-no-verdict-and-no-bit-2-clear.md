+++
id = "E1044"
claim = "r14-dpm stage pr3 on module B60AB0B4 (Q036: 0x0748 sampled alone at 0, 1, 4 and 7 partial renders, 10 planned jobs): ONE job ran, the PR 0 control pr3-c0-1, and the stage stopped by its own rule (rc 24) because its sampling period read 1682 ns where the frozen premise was at most 1000 ns (extrapolated at 0.46 us a register; the period has a floor near 1.3 us plus 0.4 us a register); the control read no bit 2 clear (0 of 118 lines); no verdict ('cannot tell' for every model, the other nine jobs never ran)"
unit = "dpm"
method = "r14-dpm (render/closing-r14-dpm), stage pr3 of the question-closing pass (round 14, decision R14-1 (a): session r14-dpm of the round 14 plan, row pr3, safe class only), built on the session kit (resgx545 main dddadbd, data 3309b5fd9) and frozen before the run, dataset render-closing-r14-dpm; attempt out/20261114-052638 (scores score-pr3.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, stock firmware; tool ~/sgxfive-test-t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06, under ~/regtimeline, sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, sampling the one register 0x0748; planned 10 rows of probe --tri pixel --width 3072 --height 2048 --vertices 1500 with p1139-green.bin at partial-render counts 0, 1, 4 and 7 by render_pb_pages; ONE job ran, pr3-c0-1, then the stage stopped by its own rule); freezes: FROZEN.sha256 67d692c0c9fcfc48a0a1b718ba30a33333a3fd4bc825593797bce03cce9701b5 (46 files), PREDICTIONS.sha256 79e8ea19c646669de512e3ac172c0d4d0ae0db8c6b221c5a980b5188521b2a98 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at dddadbdd, resgx545:tools/closing/kit/lib_kit.sh at dddadbdd, resgx545:tools/closing/kit/run_stage.sh at dddadbdd, resgx545:tools/closing/kit/kitscore.py at dddadbdd, resgx545:tools/closing/kit/fake/sudo at dddadbdd, resgx545:tools/closing/kit/fake/timeout at dddadbdd, resgx545:tools/closing/kit/fake/df at dddadbdd, resgx545:tools/closing/kit/fake/modinfo at dddadbdd, resgx545:tools/closing/kit/fake/sha256sum at dddadbdd, resgx545:tools/closing/kit/fake/tool.sh at dddadbdd, resgx545:tools/closing/kit/fake/tool.py at dddadbdd, resgx545:tools/closing/kit/fake/ssh.py at dddadbdd, resgx545:tools/closing/scorekit.py at dddadbdd, resgx545:tools/closing/sessioncheck.py at dddadbdd, data:render/closing-r9-ldpm/bins/p1139-green.bin at 3309b5fd, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-cal-c1208.txt.gz at 3309b5fd, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0xc0.txt.gz at 3309b5fd, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0x60.txt.gz at 3309b5fd, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-c1208-0x294.txt.gz at 3309b5fd, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-cal-c1208.txt.gz at 3309b5fd, data:render/closing-r13-dpm/out/20261113-212348/pr2/pr2-c4-2.txt.gz at 3309b5fd, data:render/closing-r13-dpm/out/20261113-212348/pr2/pr2-c0-1.txt.gz at 3309b5fd, data:render/closing-r13-dpm/out/20261113-212348/pr2/pr2-c1-1.txt.gz at 3309b5fd, data:render/closing-r8-ldpm/tables/f9.txt at 3309b5fd, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at dddadbdd, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; pinned commits named by the session: resgx545 main dddadbd; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r14-dpm:out/20261114-052638/pr3/", "render-closing-r14-dpm:fold/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS"]
+++
**What ran.** Q036's pr3: 0x0748 sampled alone, to shorten the sampling period against r13-dpm's
16 registers (7.5 us), at partial-render counts 0, 1, 4 and 7 of one scene, ten rows. The first row
is a PR 0 control. It ran (rc 0, class ok), its reading was taken, and the stage stopped by its own
rule (rc 24) before the second row: `control pr3-c0-1 reads short=0 where the frozen value is 1`.
One job of ten ran. The run log is `fold/run-r14d.log`.

**Frozen verdict (as printed).** `out/20261114-052638/score-pr3.txt`: "CONTROL pr3-c0-1: clr 0
pulses 0 period 1682 ns short 0 (frozen clr 0, short 1): FAILED", "CONTROL pr3-c0-2: cannot tell",
"MODEL R-PULSE: 0 held, 0 FAILED, 8 cannot tell of 8", "SUMMARY: pr3: DECISION: cannot tell (a clear
event per partial render at the short period, 0 held, 0 FAILED, 8 cannot tell of 8); ranking:
cannot tell (a control did not pass)". The frozen scorer re-run on the kept files is byte-identical
(`fold/reproduce.out`). No verdict on R-PULSE, R-RARE or R-CONST.

**Results [HW].** One timeline over 0x0748 alone read fine: 118 lines, 894110 samples over 1.5045
s, a period of 1682 ns (end over samples). The frozen premise was a period of at most 1000 ns,
extrapolated from the kept timelines at 0.46 us a register; the period has a floor, about 1.3 us
plus 0.4 us a register (16 registers 7.5 us), so one register is 4.5 times faster than 16, not 16
times (`fold/readall.out`, post hoc). The PR 0 control read no bit 2 clear: 0x0748 bit 2 was set in
all 118 lines (values 0x6, 0x7, 0xe, 0xf, 0x1d, 0x1f), which would have passed the control's
`clr 0` clause. No job with a partial render ran.

**What it shows.** The control failed on the builder's wrong period premise, not on the hardware:
single-register regtimeline works on module B60AB0B4 and samples every 1.7 us. A stage stop
for a period over 1000 ns was a gate set too tight [infer]; the plan's question (is a clear
event visible at a shorter period) is unanswered, and the next run's gain is 4.5 times, not 16.

**What it does not show.** Nothing about what 0x0748 bit 2 marks, nothing at a partial render,
and no verdict on the three models. One PR 0 job without a clear is one more such job (E1032 had
two). The 1000 ns gate and the 0.46 us figure were the builder's; a re-run needs a new session
(a freeze is never rewritten) whose period gate is about 2000 ns or only reported.
