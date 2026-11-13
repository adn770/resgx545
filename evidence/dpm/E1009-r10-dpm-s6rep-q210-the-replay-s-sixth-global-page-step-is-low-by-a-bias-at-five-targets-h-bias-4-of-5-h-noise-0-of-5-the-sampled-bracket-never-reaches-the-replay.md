+++
id = "E1009"
claim = "r10-dpm stage s6rep on module B60AB0B4 (Q210: is E874's step replay low at S6 by noise or by bias; 3 calibration replicates at each of five targets, 17 jobs): the a0 premise pair passed ('s6rep: the premise held'); the replay's S6 lay inside no target's replicate range (H-NOISE 0 of 5) and every replicate but one read R + 1 or R + 2 (H-BIAS 4 of 5 targets, 14 of 15 replicates; 'DECISION: BIAS decided; classes 4096x1024 BIAS, 4096x1536 NEITHER, 3584x1024 BIAS, 2048x512 BIAS, 2048x2304 BIAS'); the fifth read 0x245 (R + 28) in one replicate of 4096x1536, a sampling gap; post hoc, the sampled bracket of S6 has its lower end at R + 1 in 15 of 15 replicates (and in E962's four and E961's seven reads at 2048x2304), so the replay is below the bracket at all five targets and the spread above is the sampler's: a bias, not noise; the needs were the replay's (30 of 30) and the replay's S6 was exact at the 2048x2048 control (0x181)"
unit = "dpm"
method = "r10-dpm (render/closing-r10-dpm), round 10's session S10-dpm (decision R10-5 (a): safe class only, no held reset, no planned fault; round 10 seed plan, section 10), built on the session kit (resgx545 main 9849dab, data 1324301b) and frozen before the run, dataset render-closing-r10-dpm; attempt out/20261113-102513 (scores score-s6rep.txt); run by the lead with the kit's driver (log fold/run-r10d.log), 2026-11-13, on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, loaded = installed, the kit's preflight, stock firmware), tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, source resgx545 4623753, every row replayed on the library mock built from it before the freeze) run under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row (0x162 for a0-cal-2048, else 0x422), read back and restored to 0x422, a debugfs reset and the kit's health check around each job; no stop, fault, hang or lead decision. The frozen scorer re-run on the kept files gave output byte-identical to the kept score file (fold/reproduce.out); no post-run fix. Post hoc (after the score was read): fold/readall.py and fold/brackets.py and their outputs. The predictions came from gen/r9_tables.json (the byte copy of r9-ldpm's, E874's replay) and E962's and E961's kept S6. Stage s6rep (17 jobs): r9-ldpm's two a0 premise controls (a0-cal-2048 at P 0x162 and a0-cal-2048f at P 0x422, token for token) and, round-robin, three calibration replicates (probe --tri pixel --vertices 1500, p1139-green.bin, P 0x422 = thr0 0x400 above every need) at 4096x1024, 4096x1536, 3584x1024, 2048x512 and 2048x2304; the rivals frozen per target with the replay's S6 R: H-NOISE (R in the replicates' range, the range at most 2 pages) against H-BIAS (every replicate at R + 1 or R + 2), the decision 4 of 5 targets; freezes: FROZEN.sha256 dbc711ede59127d7599ac623b0d914ce3b0005addece0ef7cacef3d9510c028d (43 files), PREDICTIONS.sha256 3ea047daa824ab634f8f00a4cfe2f4fc80c1cc57deb6a50f23fd413b6f307641 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 9849dab7, resgx545:tools/closing/kit/lib_kit.sh at 9849dab7, resgx545:tools/closing/kit/run_stage.sh at 9849dab7, resgx545:tools/closing/kit/kitscore.py at 9849dab7, resgx545:tools/closing/kit/fake/sudo at 9849dab7, resgx545:tools/closing/kit/fake/timeout at 9849dab7, resgx545:tools/closing/kit/fake/df at 9849dab7, resgx545:tools/closing/kit/fake/modinfo at 9849dab7, resgx545:tools/closing/kit/fake/sha256sum at 9849dab7, resgx545:tools/closing/kit/fake/tool.sh at 9849dab7, resgx545:tools/closing/kit/fake/tool.py at 9849dab7, resgx545:tools/closing/kit/fake/ssh.py at 9849dab7, resgx545:tools/closing/scorekit.py at 9849dab7, resgx545:tools/closing/sessioncheck.py at 9849dab7, data:render/closing-r9-ldpm/gen/r9_tables.json at 1324301b, data:render/closing-r9-ldpm/score/read.py at 1324301b, data:render/closing-r9-ldpm/bins/p1139-green.bin at 1324301b, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; pinned commits named by the session: resgx545 main 9849dab; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-dpm:out/20261113-102513/s6rep/", "render-closing-r10-dpm:fold/", "vectors-closing-r10-dpm-dpm"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E962 read the replay's S6 one or two pages low at four wide targets, one calibration
each, and E961 at 2048x2304; the spread of S6 between runs of one target (1 to 4 pages at 1536x1536,
1792x1792, 2304x1792, 2304x2304 and 4096x2048) left noise or bias open. Stage s6rep ran three
calibration replicates at each of the five targets, in rounds (replicate 1 of the five, then 2,
then 3), and the a0 pair first. S_6 is the reader's value (the upper end of the bracket the two
samples around the global page step give).

**Frozen verdict (as printed).** `out/20261113-102513/score-s6rep.txt`: "CONTROL a0-cal-2048:
PASS", "CONTROL a0-cal-2048f: PASS"; "TARGET 4096x1024 (replay S_6 0x17c, kept 0x17e): replicates
0x17d,0x17e,0x17e: BIAS"; "TARGET 4096x1536 (replay S_6 0x229, kept 0x22b): replicates
0x22a,0x245,0x22b: NEITHER"; "TARGET 3584x1024 (replay S_6 0x14d, kept 0x14f): replicates
0x14e,0x14f,0x14e: BIAS"; "TARGET 2048x512 (replay S_6 0x6e, kept 0x6f): replicates
0x6f,0x6f,0x6f: BIAS"; "TARGET 2048x2304 (replay S_6 0x1ac, kept 0x1ad): replicates
0x1ad,0x1ad,0x1ad: BIAS"; "MODEL H-BIAS: 4 held, 1 FAILED, 0 cannot tell of 5"; "MODEL H-NOISE: 0
held, 5 FAILED"; "MODEL H-REPLAY: 30 held, 0 FAILED" (the need and no partial render);
"MODEL H-REPLAY6: 0 held, 15 FAILED of 15"; "MODEL H-BIAS-SAME: 10 held, 5 FAILED of 15";
"SUMMARY: s6rep: the premise held (the a0 pair repeats E935 on B60AB0B4) (1 of 1 rows decided)";
"SUMMARY: s6rep: DECISION: BIAS decided; classes 4096x1024 BIAS, 4096x1536 NEITHER, 3584x1024 BIAS,
2048x512 BIAS, 2048x2304 BIAS" (the rule frozen in README.md and score.py: at least 4 of 5
targets BIAS and at most 1 NOISE). The two SUMMARY lines "H-NOISE holds at the target is not
supported" and "H-BIAS holds at the target is not supported: 4 held, 1 FAILED" are the headline
text of the per-target tallies, not the decision.

**Results [HW].** S_6 of the replicates (replay R): 4096x1024 0x17d, 0x17e, 0x17e (0x17c);
4096x1536 0x22a, 0x245, 0x22b (0x229); 3584x1024 0x14e, 0x14f, 0x14e (0x14d); 2048x512 0x6f three
times (0x6e); 2048x2304 0x1ad three times (0x1ac). The 2048x2048 control read 0x181 (R), its steps
S2 to S7 and the need 0x213 the replay's. Needs all the replay's (0x20f, 0x302, 0x1d0, 0x9a, 0x24f),
no partial render, S2 to S7 monotone. Other steps: S3 of 4096x1536 0xe1 (R + 1) and of 2048x2304
0xae (R + 1) in all three replicates; S2 of 2048x512 0x1a, 0x1b, 0x1b and of 4096x1536 0x74,
0x73, 0x74 (a page of run to run spread).

**Read after the run (post hoc).** `fold/brackets.out`: the bracket of S_6 is (a, max(a, b - 1)) for
the 0x0724 high halves a and b of the samples around the step; its lower end a is R + 1 in 15 of
15 replicates, its width 1 page in 10, 2 in 4 and 28 in the 0x245 one (one sample interval holding
28 pages). The same lower end R + 1 holds for E962's four calibrations (0x6f, 0x14e, 0x17d, 0x22a)
and E961's seven reads at 2048x2304 (0x1ad). The upper end moved by one page between runs of one
target at 4096x1024 and 3584x1024 (and S2 at two), the replay's R never.

**What it shows.** E874's replay is low at S6 by a bias of at least one page at these five targets:
no replicate's bracket reaches R, 15 of 15, so run to run noise does not explain E962's misses
(H-NOISE 0 of 5). The offset is not the same everywhere: the reader's S_6 equalled the replay in at least one run
at 1280x1280, 1536x1536, 1792x1792, 2048x2048, 2304x1792, 2304x2304, 2560x2048 and 4096x2048 (E936,
E961, E963 and this session's control), where the replay is held. No rule for where the bias comes
in was fitted here [infer: five biased targets and no held-out one]. What the sampler adds is a
spread of one page above the lower end (and one stalled interval), which H-BIAS's "R + 1 or R + 2"
covers.

**What it does not show.** Which targets carry the bias or why (the five are the four targets wider than 2:1 and
2048x2304; the eight without it are square, 2:1 or near square); whether the bias is in the
replay's lag (3 objects) or in the block and region counts; a calibration against a
partial-render cell (2304x2304 read 0x1e1 in its calibration and 0x1dd in its cells, E961); S3
or S2 as steps of their own (S3 was one above at two targets).
