+++
id = "E1057"
claim = "r15-dpm stage pr4 on module B60AB0B4 (Q036: r14-dpm's pr3 re-run with the sampling-period gate at 2000 ns; 0x0748 sampled alone at 0, 1, 4 and 7 partial renders, 10 jobs, all ran, rc 0): the period read 1655 to 1700 ns (gate passed), the two PR 0 controls read no bit 2 clear, and 17 clear events fell in the 8 jobs with a partial render (35 labelled partial renders, 0.49 each; frozen R-PULSE needed at least one per partial render at every row: 1 held, 7 FAILED; frozen R-RARE-TOTAL 1-8 FAILED at 17; ranking NO RANKING; log-loss R-PULSE 9.29, R-RARE 6.80, R-CONST 7.25); every clear is 3890 to 4090 ns wide with 0x0748 reading 0xb or 0x1b"
unit = "dpm"
method = "r15-dpm (render/closing-r15-dpm), stage pr4 of the question-closing pass (round 15, decision R15-3 (a): session r15-dpm of the round 15 plan, row pr4, safe class only, r14-dpm's pr3 rows and predictions with the period gate at 2000 ns), dataset render-closing-r15-dpm; attempt out/20261114-071243 (scores score-pr4.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, stock firmware; tool ~/sgxfive-test-t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06, under ~/regtimeline, sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, sampling the one register 0x0748; 10 rows of probe --tri pixel --width 3072 --height 2048 --vertices 1500 with p1139-green.bin at partial-render counts 0, 1, 4 and 7 by render_pb_pages 0x422, 0x2b6, 0xe2 and 0x82, run order 0, 1, 4, 7, 1, 0, 7, 4, 7, 4); freezes: FROZEN.sha256 d8485b61f3eaea357b1fb446aa3fae6b59f26e39c687d8a10bb177f68a964a76 (46 files), PREDICTIONS.sha256 e9da1ed889bef03fda2f16510dcaf8f6b44e0d6ba9706f64e9d009183b6c717a (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 158bdc54, resgx545:tools/closing/kit/lib_kit.sh at 158bdc54, resgx545:tools/closing/kit/run_stage.sh at 158bdc54, resgx545:tools/closing/kit/kitscore.py at 158bdc54, resgx545:tools/closing/kit/fake/sudo at 158bdc54, resgx545:tools/closing/kit/fake/timeout at 158bdc54, resgx545:tools/closing/kit/fake/df at 158bdc54, resgx545:tools/closing/kit/fake/modinfo at 158bdc54, resgx545:tools/closing/kit/fake/sha256sum at 158bdc54, resgx545:tools/closing/kit/fake/tool.sh at 158bdc54, resgx545:tools/closing/kit/fake/tool.py at 158bdc54, resgx545:tools/closing/kit/fake/ssh.py at 158bdc54, resgx545:tools/closing/scorekit.py at 158bdc54, resgx545:tools/closing/sessioncheck.py at 158bdc54, data:render/closing-r9-ldpm/bins/p1139-green.bin at cddc7b60, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-cal-c1208.txt.gz at cddc7b60, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0xc0.txt.gz at cddc7b60, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0x60.txt.gz at cddc7b60, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-c1208-0x294.txt.gz at cddc7b60, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-cal-c1208.txt.gz at cddc7b60, data:render/closing-r13-dpm/out/20261113-212348/pr2/pr2-c4-2.txt.gz at cddc7b60, data:render/closing-r13-dpm/out/20261113-212348/pr2/pr2-c0-1.txt.gz at cddc7b60, data:render/closing-r13-dpm/out/20261113-212348/pr2/pr2-c1-1.txt.gz at cddc7b60, data:render/closing-r8-ldpm/tables/f9.txt at cddc7b60, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 158bdc54, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; pinned commits named by the session: resgx545 main 158bdc5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-14"
data = ["render-closing-r15-dpm:out/20261114-071243/pr4/", "render-closing-r15-dpm:fold/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS"]
+++
**What ran.** Q036's pr4, the re-run of r14-dpm's pr3 (E1044) with the one change that the
period gate (`short`) is 2000 ns, not 1000: 0x0748 sampled alone under regtimeline at partial-render
counts 0, 1, 4 and 7 of one scene (3072 x 2048, 1500 vertices, p1139-green.bin), ten rows, run order
0, 1, 4, 7, 1, 0, 7, 4, 7, 4. All ten ran (rc 0, class ok; the knob proof is each job's rc). The PR
is the row's label (the knob), not a reading. The run log is `fold/run-r15d.log`.

**Frozen verdict (as printed).** `out/20261114-071243/score-pr4.txt`: "CONTROL pr4-c0-1: clr 0
pulses 0 period 1655 ns short 1 (frozen clr 0, short 1): PASS", "CONTROL pr4-c0-2: clr 0 pulses 0
period 1666 ns short 1 ...: PASS", "MODEL R-PULSE: 1 held, 7 FAILED, 0 cannot tell of 8", "MODEL
R-RARE-TOTAL: 0 held, 1 FAILED, 0 cannot tell of 1" (total pulses 17, frozen 1-8), "MODEL log-loss:
R-PULSE 9.29, R-RARE 6.80, R-CONST 7.25", "SUMMARY: pr4: DECISION: R-PULSE FAILS (a clear event per
partial render at the short period, 1 held, 7 FAILED, 0 cannot tell of 8); ranking: NO RANKING"
(R-RARE has the lowest log-loss but not by the frozen 1.0 nat over R-CONST). The frozen scorer
re-run on the kept files is byte-identical (`fold/reproduce.out`).

**Results [HW].** Periods 1655 to 1700 ns (end over samples), inside the 2000 ns gate; both PR 0
controls read no bit 2 clear (0 of 131 and 0 of 113 lines). Clear events (runs of lines with 0x0748
bit 2 clear) per job, by label: PR 1: 0, 1; PR 4: 3, 0, 2; PR 7: 5, 3, 3; total 17 over 35 labelled
partial renders, 0.49 a partial render (E1032 saw 0.07, E1019 fitted 0.17 [infer: the rate rose
because the period fell 4.5 times, so a clear E1032 missed is visible]). Every clear is one run
3890 to 4090 ns wide (mean 3970), 0x0748 reads 0xb or 0x1b in the run (0xf or 0x1f outside it: bit 2
alone), 215 to 424 ms after the command starts, a few tens of ms apart (post hoc,
`fold/readall.out`). Jobs with the same label differ (PR 4: 3, 0, 2; PR 7: 5, 3, 3), 6 of the 8 jobs
with a label above 0 have a clear, and none has as many as its label (at most 5 at PR 7).

**What it shows.** The period was the obstacle: at 1.7 us bit 2's clear is seen (17 events in 8
jobs with a label above 0) where a 7.5 us sampler saw one in 14 partial renders (E1032) [infer], and
none at PR 0 (2 of 2 jobs here, with E1032's 2 of 2). The clear is a fixed pulse about 4 us wide,
so a sampler needs a period under about 4 us. The strict per-partial-render form is refuted at this
period: fewer clears than the label in 7 of 8 jobs, the one that held (PR 1, one clear) being one
event. The clears grow with the label (mean 0.5 at PR 1, 1.7 at 4, 3.7 at 7: about half a partial
render [infer]); whether a clear marks about half the partial renders or a shorter pulse is still
missed is not decided.

**What it does not show.** Not what the bit marks (a partial render's start or store, a DPM
state change, a page boundary), and not that the label equals the partial-render count: the count
is not read back with one register (0x0658 is not sampled), so a label that missed its count would
look like a missing pulse. 17 pulses are an observation, not a rate fit: R-RARE's 0.109 per partial
render and its 1-8 total were frozen and fail, and no rival was ranked first. The other bits of
0x0748, the other registers, CR_DMS_CTRL and the builder-fault clause of Q036 are untouched. The
builder's reading of the pulse width (about 2.4 samples) is post hoc.
