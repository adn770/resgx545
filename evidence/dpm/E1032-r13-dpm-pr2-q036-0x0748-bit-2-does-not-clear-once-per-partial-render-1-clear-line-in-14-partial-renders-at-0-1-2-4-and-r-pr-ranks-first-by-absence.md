+++
id = "E1032"
claim = "r13-dpm stage pr2 on module B60AB0B4 (Q036: does 0x0748 bit 2 clear with partial renders; one scene, 3072x2048 with 1500 vertices, at 0, 1, 2 and 4 partial renders, two replicates each, 8 jobs): both PR 0 controls passed (no partial render, no bit 2 clear line); every row read the frozen count (H-COUNT 8 of 8) and 0x0710's high half 0 (H0 8 of 8); the plan's strict form, a clear line at least once per partial render, failed at all 6 rows with a partial render (H-PR-STRICT 0 held, 6 FAILED), because 7 of the 8 jobs show no clear line at all and the eighth (PR 4, second replicate) one, 1 clear line in 14 partial renders ('DECISION: R-PR STRICT FAILS ... ranking: R-PR RANKED FIRST'); the frozen ranking puts R-PR first by log-loss (2.43 against R-LEN 4.06 and the constant 4.87), which was not the builder's expectation (no ranking) and rests on the absence of clears (R-PR gives the low probability 0.01 to 0.5, the rivals 0.35 to 0.44); bit 2 is therefore not cleared once per partial render and the 0x0748 clear is rare (0.07 lines per partial render here, E1019's fit 0.17); 0x0710 peaked at P - 1 (0x421, 0x2b5, 0x1c1, 0xe1)"
unit = "dpm"
method = "r13-dpm (render/closing-r13-dpm), round 13's session r13-dpm (decision R13-1 (a): safe class only, no held reset, no planned fault; the round 13 ranking plan, sections 2 and 3, row pr2), built on the session kit (resgx545 main 05b7039, data 75d01ee20) and frozen before the run, dataset render-closing-r13-dpm; attempt out/20261113-212348 (scores score-pr2.txt); run by the lead with the kit's driver (log fold/run-r13d.log), 2026-11-13, on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, loaded = installed, the kit's preflight, stock firmware), tool ~/sgxfive-test-t10 (sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06, every row replayed on the library mock built from it before the freeze) run under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row (P = thr0 + 0x22: 0x422, 0x2b6, 0x1c2, 0xe2), read back and restored to 0x422, a debugfs reset and the kit's health check around each job; no stop, fault, hang or lead decision. The frozen scorer re-run on the kept files gave output byte-identical to the kept score file (fold/reproduce.out); no post-run fix. Post hoc (after the score was read): fold/readall.py and its output, and the builder had read r8-ldpm's kept 3072x2048 clear lines before freezing. Stage pr2 (8 jobs): probe --tri pixel --width 3072 --height 2048 --vertices 1500 with p1139-green.bin at thr0 0x400 (0 partial renders, the two controls), 0x294 (1), 0x1a0 (2) and 0xc0 (4), two rows each, in the order 0, 1, 2, 4, 1, 0, 4, 2; the counts are r8-ldpm's kept readings of the scene; frozen rivals: H-PR-STRICT (the plan's R-PR, E1019: CLR >= PR at every row with a partial render, none at 0), E1019's per-job forms H-R-PR (1 - exp(-0.1708 PR)), H-R-LEN (1 - (1 - 0.00108)^N) and H-CONST (0.439) ranked by log-loss with a margin of 1.0 nat; freezes: FROZEN.sha256 f600f77c10009719aa6c7e645c23a3b10fe9af238efa0eedda83b767732d7f68 (49 files), PREDICTIONS.sha256 44dac96b9d3b2e404fec1a64caed56c462c46104f596caec98d7b48454889955 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 05b7039e, resgx545:tools/closing/kit/lib_kit.sh at 05b7039e, resgx545:tools/closing/kit/run_stage.sh at 05b7039e, resgx545:tools/closing/kit/kitscore.py at 05b7039e, resgx545:tools/closing/kit/fake/sudo at 05b7039e, resgx545:tools/closing/kit/fake/timeout at 05b7039e, resgx545:tools/closing/kit/fake/df at 05b7039e, resgx545:tools/closing/kit/fake/modinfo at 05b7039e, resgx545:tools/closing/kit/fake/sha256sum at 05b7039e, resgx545:tools/closing/kit/fake/tool.sh at 05b7039e, resgx545:tools/closing/kit/fake/tool.py at 05b7039e, resgx545:tools/closing/kit/fake/ssh.py at 05b7039e, resgx545:tools/closing/scorekit.py at 05b7039e, resgx545:tools/closing/sessioncheck.py at 05b7039e, data:render/closing-r9-ldpm/bins/p1139-green.bin at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-cal-c1208.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0xc0.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0x120.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0x1a0.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/f9/f9-c1208-0x60.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-c1208-0x292.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-c1208-0x293.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-c1208-0x294.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-c1208-0x296.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/out/20261113-021431/m6/m6-cal-c1208.txt.gz at 75d01ee2, data:render/closing-r8-ldpm/tables/m6.txt at 75d01ee2, data:render/closing-r8-ldpm/tables/f9.txt at 75d01ee2, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 05b7039e, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; pinned commits named by the session: resgx545 main 05b7039; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r13-dpm:out/20261113-212348/pr2/", "render-closing-r13-dpm:fold/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E1019 ranked, on 558 held-out jobs of earlier sessions, R-PR (0x0748 bit 2 clears in
proportion to the partial renders of a job) above R-LEN, R-0x100 and a constant, a ranking and no
pass rule; the plan's frozen form of R-PR was stronger: at least one clear line per partial render
and none at 0. Stage pr2 ran one scene (3072x2048, 1500 vertices) at 0, 1, 2 and 4 partial renders,
set by `render_pb_pages`, two replicates each, and sampled 0x0700, 0x070c, 0x0710, 0x0720 to 0x0728,
0x0748 and the rest of R5-dpm's 16 registers through the job.

**Frozen verdict (as printed).** `out/20261113-212348/score-pr2.txt`: "CONTROL pr2-c0-1: nparts 0
clr 0 pulses 0 (frozen 0, 0): PASS", the same for pr2-c0-2; "MODEL H-COUNT: 8 held, 0 FAILED, 0
cannot tell of 8"; "MODEL H0: 8 held, 0 FAILED, 0 cannot tell of 8"; "MODEL H-PR-STRICT: 0 held, 6
FAILED, 0 cannot tell of 6"; "MODEL log-loss: H-R-PR 2.43, H-R-LEN 4.06, H-CONST 4.87"; "SUMMARY:
pr2: DECISION: R-PR STRICT FAILS (the plan's clear per partial render, 0 held, 6 FAILED, 0 cannot
tell of 6); ranking: R-PR RANKED FIRST". The H-PR-STRICT SUMMARY line reads "H-PR-STRICT holds is
not supported: 0 held, 6 FAILED, 0 cannot tell of 6" (the scorer's phrasing).

**Results [HW].** Per row (partial renders, timeline lines, bit 2 clear lines, global pages
reached): c0 0, 360 and 358, 0, 7; c1 1, 410 and 416, 0, 6; c2 2, 464 and 467, 0, 5; c4 4, 494 and
515, 0 and 1, 3 (`fold/readall.out`). One clear line in 8 jobs and 14 partial renders: 0.07 per
partial render, E1019's fit 0.17. Readings, no frozen value: 0x0710's high half 0 at every line of
every job (H0 held, 8 of 8, G 3 to 7); 0x0710's highest value is P - 1 (0x421, 0x2b5, 0x1c1, 0xe1);
0x0728's highest is 0x305 at 0 partial renders, then 0x294, 0x1a0 and 0xe0; 0x0720 reads only 0 at 0
partial renders and 0, 0x5, 0x10 at 1 and 2 (0x6 also at 4); the global page count the jobs reach
falls with the count (7, 6, 5, 3) because thr0 is lower. The builder expected NO RANKING from a
total of two to four clear lines and the strict form to fail; the strict form failed as expected,
the ranking did not go as expected: R-PR came first.

**What it shows.** The plan's strict form of R-PR is refuted on this scene: a partial render does
not clear 0x0748 bit 2 at every sample-visible occurrence (6 of 6 rows). The frozen ranking
favours R-PR over R-LEN and the constant by 1.6 and 2.4 nats, but that is by absence of clears:
R-PR's low probability at 0 to 2 partial renders fits seven jobs without a clear, while R-LEN
and the constant spend 0.4 to 0.6 nats on each of them [infer]. The clear is rare and a short pulse
at about 8 us sampling can be missed [infer]. Both PR 0 controls read no clear line, so a clear
does not appear without a partial render (2 of 2, E1019's "none at 0" kept at this scene).

**What it does not show.** One clear line is one sample: the ranking margin rests on it and on the
seven jobs without one, and 8 jobs part the rivals weakly (the builder's power estimate). It does
not say what bit 2 marks, only that it is not a per-partial-render pulse the sampler sees. One
scene, one resolution; the 0x071c half of STATUS2 is not in the register set (E1019's caveat); the
owner words 0x0700 to 0x0728 are listed, not interpreted; CR_DMS_CTRL, the signature registers and
the page-table builder fault stay open. The builder read r8-ldpm's kept clear lines of this scene
before freezing, so the rows are new runs but not blind to those counts.
