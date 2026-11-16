+++
id = "E1131"
claim = "r33-tim on module 7CE8E38E (fwsim's tim, E1130), stages t1 (CR_EVENT_STATUS, CR_CACHE_CTRL and CR_EVENT_TIMER) and t1d (CR_EVENT_TIMER alone), regtimeline over plain 64x64 triangles: every control FAILED on its sample interval (t1 4850 to 4901 ns against the frozen 700 to 2000, t1d 3696 against 400 to 1200; the frozen premise took the idle loop's spacing of E1115, E1120 and E1122 for the job's, a builder's error), so no frozen verdict stands; readings post hoc, no verdict: the sampler is spaced 1213 ns (three registers) and 622 ns (one) before t10 starts and 4.6 to 6.2 us (median) while it runs; CR_EVENT_TIMER keeps bit 24 in every sample of 15 rows, counts down 398.96 to 399.01 a us with a period of 1002.497 to 1002.535 us, and once reads exactly 400000; CR_CACHE_CTRL changes 22.93 to 24.10 ms after the tool starts (11 of 11), where the count sits anywhere in the period (7389 to 384863 on its line); over the 120 us after the change the samples stay within 255 counts of the line fitted before it in 3 rows and step to +568 to +633 counts for about 100 us in 5 [infer: the host's read timing]"
unit = "platform"
method = "r33-tim (render/closing-r33-tim), stages t1, t1d of the question-closing pass (round 33: the lead's request after fwsim's M2 kick stopped on PDS #14's tim, E1130; safe class; record E1131 reserved by the frozen README), dataset render-closing-r33-tim; attempt out/20261116-211055 (scores score-t1.txt, score-t1d.txt); on the laptop host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike, fork 8bc0877e8603), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline TOTAL 0.005 REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64` after a debugfs reset (t1: 0.06 and 0x012c,0x0804,0x0acc, 11 rows with controls t1-c1, t1-c2, t1-c3; t1d: 0.04 and 0x0acc, 4 rows with control t1d-c1), no knob and no register write; the rows tables/STAGE.txt from gen/make.py, every row held out, the frozen predictions predictions/STAGE.tsv; the post-hoc readings fold/posthoc.py and posthoc.txt, not frozen; freezes: FROZEN.sha256 db2e208ecd1ea5260aac52b9a6b678b67dc8f6df065d1945656271332ec8436a (37 files), PREDICTIONS.sha256 a8b63be8d8198a75b6dde063fe1655cfcc44d7f3c04ffc63eb13865f9564bbb8 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at f888bb76, resgx545:tools/closing/kit/lib_kit.sh at f888bb76, resgx545:tools/closing/kit/run_stage.sh at f888bb76, resgx545:tools/closing/kit/kitscore.py at f888bb76, resgx545:tools/closing/kit/fake/sudo at f888bb76, resgx545:tools/closing/kit/fake/timeout at f888bb76, resgx545:tools/closing/kit/fake/df at f888bb76, resgx545:tools/closing/kit/fake/modinfo at f888bb76, resgx545:tools/closing/kit/fake/sha256sum at f888bb76, resgx545:tools/closing/kit/fake/tool.sh at f888bb76, resgx545:tools/closing/kit/fake/tool.py at f888bb76, resgx545:tools/closing/kit/fake/ssh.py at f888bb76, resgx545:tools/closing/scorekit.py at f888bb76, resgx545:tools/closing/sessioncheck.py at f888bb76, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-01.txt.gz at 052c0a8b, data:render/closing-r30-evst2/out/20261116-132348/e2/e2-02.txt.gz at 052c0a8b, data:render/closing-r32-misc/out/20261116-185655/m2/m2-01.snap0.regs.gz at 052c0a8b, data:render/closing-r32-misc/out/20261116-185655/m2/m2-01.snap9.regs.gz at 052c0a8b, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main f888bb7, resgx545 main f888bb7694a6; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r33-tim:out/20261116-211055/t1/", "render-closing-r33-tim:out/20261116-211055/t1d/", "render-closing-r33-tim:fold/"]
terms = ["CR_EVENT_TIMER", "CR_CACHE_CTRL", "CR_EVENT_STATUS", "CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE"]
+++
**What ran.** r33-tim (closing29/r33-tim README, pre-run): 15 plain 64x64 triangles of t10 under
regtimeline, sampling from 5 ms before t10 starts for 60 ms (t1: CR_EVENT_STATUS 0x012c,
CR_CACHE_CTRL 0x0804, CR_EVENT_TIMER 0x0acc) or 40 ms (t1d: 0x0acc alone). The frozen hypotheses
were the timer's run bit and range, its reload, its rate (H-TIM-399 against H-TIM-400), the count
across the window from CR_CACHE_CTRL's change to bit 26's fall (H-TIM-FREE against H-TIM-WRITE)
and its phase at the change across rows (H-TIM-ASYNC against H-TIM-SYNC); controls diff 0, ivl
(700 to 2000 ns in t1, 400 to 1200 in t1d), every 0x0acc sample a running count, snap0 and snap9
the same.

**Frozen verdict (as printed).** `CONTROL t1-c1: diff=0 ivl=4897 ten=1 ten0=1 ten9=1: FAILED`,
t1-c2 ivl 4850 and ten 0 FAILED, t1-c3 ivl 4901 FAILED, `CONTROL t1d-c1: diff=0 ivl=3696 ten=1
ten0=1 ten9=1: FAILED`; every SUMMARY line of both stages reads `controls FAILED`.
fold/reproduce.out reproduces both scores byte for byte. No hypothesis is decided.

**Why the controls failed.** The frozen intervals were the TOTAL/samples averages of E1115, E1120
and E1122, whose 1.5 s windows are mostly the idle loop around a 0.11 s job. Here the windows are
almost all job time: before t10 starts the sampler is spaced 1213 to 1283 ns (median, three
registers) and 622 to 782 ns (one), as those averages say, and while it runs 4.6 to 5.7 us (t1)
and 5.2 to 6.2 us (t1d), with one gap of 0.68 to 2.31 ms in every row (fold/posthoc.txt `lead`,
`job`, `gmax`) [infer: the sampler shares the CPU with t10 and the kernel]. Storing every sample
(0x0acc changes each time) is not the cause: the lead stores every sample too. The premise was
the builder's error; the run and the tool behaved.

**Results [HW], post hoc (not frozen).** CR_EVENT_TIMER: bit 24 set and bits 31:25 clear in every
sample of 15 of 15 rows and in every snap0 and snap9; the piecewise fit gives 398.96 to 399.01
counts a us and a period of 1002.497 to 1002.535 us in 15 of 15 rows; the largest count is 399960
to 399998, and t1-c2 has one sample of exactly 400000 (0x01061a80). CR_CACHE_CTRL changes once, to
0x1000ffff, 22.93 to 24.10 ms after the tool starts (11 of 11), between samples 4.8 to 7.1 us
apart. Bit 26 shows within 200 us of the change in 4 of 11 rows (19.9, 18.8, 0.0 and 107.7 us
after it, 6.5, 4.7, 5.9 and 4.7 us wide). Against a line fitted on the 1 ms before the change
(dropping samples more than 1000 counts off a first fit): the change sample within -103 to +137
counts in 10 of 11 rows (t1-08 -29478, a read about 74 us late); the window's samples within 255
counts in t1-02, t1-04 and t1-07, a step to +568 to +633 counts from 18 to 40 us after the change
that is gone 120 to 300 us after it in t1-01, t1-03, t1-05, t1-06 and t1-c3, within 101 but one
sample 1603 off in t1-c1, and -298 to -347 in t1-c2. The line's count at the change is 7389 to
384863 over the 11 rows; at bit 26's rise 399432, 185802, 326108 and 341895.

**What it shows.** Nothing frozen. The readings agree with the timer model of hw_spec 12.2
(E746, E751): a running down-counter of 399 counts a us with a 1002.5 us period, which a kick's
window does not visibly stop or reload over 120 us, at a phase that differs from row to row
(E746, E747). A sample of exactly 400000 says the reload word itself is read [HW, once]. The
transient +600 count step returns to the line, which a stopped or rewritten counter would not
[infer]; the two rows without it are those with the shortest job spacing (4.6 us), so it reads as
the host's read timing [infer]. These readings become held-out hypotheses of the rerun r33-tim2,
whose interval premise comes from this run.

**What it does not show.** Any verdict (every control failed); the count PDS #14 reads inside the
kick pass (between samples 4.8 to 7.1 us apart: 1900 to 2800 counts); bit 26's episodes that fall
between samples; where PDS #14's douta lands (not built: README "t2").
