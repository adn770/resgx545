+++
id = "E1120"
claim = "r30-evst2 on module 7CE8E38E (Q111, the fwsim read rules), stages e2, e3, e4 (CR_EVENT_STATUS with CR_EVENT_STATUS2, CR_CACHE_CTRL and CR_USE0_SERV_EVENT, and with 27 registers), every control passed, every row held out: CR_CACHE_CTRL reads 0x0000ffff after the reset (24 of 24 first samples) and 0x1000ffff from one change to the end of the run (19 of 19 rows; H-CC-FLAT refuted), the change coming before every event bit of the job and 19.6 to 48.3 us before bit 26 in 5 of 6 read leads but 106.6 us in one (H-CC-KICK's timing clause refuted as frozen); CR_USE0_SERV_EVENT counts 9 to 11 beyond the ticks over a plain triangle (H-SE-EVENTS 19 of 19, H-SE-TICKS refuted); bit 26's first episode is 5.0 to 7.2 us with four registers sampled (H-NARROW4 7 of 7) and 11.9 and 15.7 us with 27 (H-NARROW27 2 of 2); bit 26 is seen in 2 of 8 rows with 27 registers against 4 of 8 with CR_EVENT_STATUS alone (H-DENSITY held at 0.25, on its 0.2 bound); once bit 26 shows together with SW_EVENT and MASTER_INTERRUPT (0xa4004000; H-ALONE refuted once); CR_EVENT_STATUS reads 0x20000000 outside the job (19 of 19)"
unit = "platform"
method = "r30-evst2 (render/closing-r30-evst2), stages e2, e3, e4 of the question-closing pass (round 30: the corrected rerun of r30-evst, whose e2-e4 controls had a wrong frozen CR_CACHE_CTRL value (E1116); the frozen files reserve E1117 and E1118, folded as E1120 and E1121 by the lead's record decision), dataset render-closing-r30-evst2; attempt out/20261116-132348 (scores score-e2.txt, score-e3.txt, score-e4.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (N1; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline TOTAL LEAD REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64 [-n 3]` after a debugfs reset, no knob and no register write; the rows tables/STAGE.txt from gen/make.py, every non-control row held out, the frozen predictions predictions/STAGE.tsv from E1115's and E1116's kept rows); freezes: FROZEN.sha256 199da94a09bec800eaefcf4e49e5dbf59dcad301071609880b385444b5b97558 (62 files), PREDICTIONS.sha256 0168a6b58d1372f0feb1e0e8586dfeccbaa9a5ff1f49fcb73eb0a3e8a5742cd3 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 24e4a365, resgx545:tools/closing/kit/lib_kit.sh at 24e4a365, resgx545:tools/closing/kit/run_stage.sh at 24e4a365, resgx545:tools/closing/kit/kitscore.py at 24e4a365, resgx545:tools/closing/kit/fake/sudo at 24e4a365, resgx545:tools/closing/kit/fake/timeout at 24e4a365, resgx545:tools/closing/kit/fake/df at 24e4a365, resgx545:tools/closing/kit/fake/modinfo at 24e4a365, resgx545:tools/closing/kit/fake/sha256sum at 24e4a365, resgx545:tools/closing/kit/fake/tool.sh at 24e4a365, resgx545:tools/closing/kit/fake/tool.py at 24e4a365, resgx545:tools/closing/kit/fake/ssh.py at 24e4a365, resgx545:tools/closing/scorekit.py at 24e4a365, resgx545:tools/closing/sessioncheck.py at 24e4a365, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-1.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-2.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-3.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-4.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-5.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-1.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-2.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-3.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-4.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-5.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-idle-r2-1.txt.gz at a1c3d8c3, data:platform/event-bits/dumps/event-timelines/tl-tri256n3-r7-1.txt.gz at a1c3d8c3, data:platform/register-timelines/output.txt at a1c3d8c3, data:platform/event-bits/cases.tsv at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e1/e1-01.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e1/e1-12.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e5/e5-05.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-01.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-03.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-c1.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e3/e3-03.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e4/e4-01.txt.gz at a1c3d8c3, data:render/closing-r30-evst/out/20261116-123552/e2/e2-c1.snap0.regs.gz at a1c3d8c3, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-evst2:out/20261116-132348/e2/", "render-closing-r30-evst2:out/20261116-132348/e3/", "render-closing-r30-evst2:out/20261116-132348/e4/", "render-closing-r30-evst2:fold/"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_CACHE_CTRL", "CR_USE0_SERV_EVENT"]
+++
**What ran.** The corrected rerun of r30-evst's stages e2-e4 (E1116), with the control premises
the kit's post-reset values (CR_CACHE_CTRL 0x0000ffff, read in every kit `snap0.regs`) and
E1116's post-hoc readings frozen as held-out hypotheses (closing29/r30-evst2 README, pre-run):
e2 (12 jobs, `1.5 0.5 0x0118,0x012c,0x0804,0x0b14`), e3 (10 jobs, `0 0.3` with r23-dpm's set,
0x0218 and those four: 27 registers), e4 (2 jobs, `6 5.5` with e2's four). Frozen: H-ALONE,
H-SW, H-IDLE; H-NARROW4 (bit 26's first episode 3 to 12 us, e2 and e4) and H-NARROW27 (8 to 20
us, e3); H-CC-KICK (CR_CACHE_CTRL 0x1000ffff after its change, held to the end of the run, the
change 15 to 60 us before bit 26's first rise, that lead read only where bit 26 precedes a
render end the row saw) against H-CC-FLAT; H-SE-EVENTS (7 to 13 counts beyond the ticks)
against H-SE-TICKS (within 1); H-DENSITY (E1121's e1 seen fraction at least 0.2 above e3's)
against H-INDEP; e4's tick rate 0.9 to 1.1 a ms.

**Frozen verdict (as printed).** Every control PASS (e2-c1, e2-c2, e3-c1, e3-c2, e4-c1: diff 0,
idle 0x20000000, idle2 0x400, cache 0x0000ffff, se16 1, ivl 1406 to 1465 and 9045 to 9063 ns).
e2: `H-CC-KICK ... is not supported: 24 held, 1 FAILED, 5 cannot tell of 30` (three clauses a
row: the word after the change 10 of 10, held to the end 10 of 10, the lead 4 held, 1 FAILED,
5 cannot tell), `H-CC-FLAT ... not supported: 0 held, 10 FAILED`, `H-SE-EVENTS (10 of 10 rows
decided)`, `H-SE-TICKS ... 10 FAILED`, `H-NARROW4 (6 of 10 rows decided)`, `H-IDLE (10 of 10)`,
`H-SW (8 of 10)`, `H-ALONE ... not supported: 5 held, 1 FAILED, 4 cannot tell of 10`. e3:
`H-CC-KICK ... (17 of 24 rows decided)`, H-CC-FLAT 8 FAILED, `H-SE-EVENTS (8 of 8)`,
H-SE-TICKS 8 FAILED, `H-NARROW27 (2 of 8 rows decided)`, `H-DENSITY (1 of 1)` with density 0.25
(printed 0.2), `H-INDEP ... 1 FAILED`, H-IDLE 8 of 8, H-ALONE 2 of 8, H-SW 6 of 8. e4:
`H-CC-KICK (3 of 3)`, H-SE-EVENTS 1 of 1, H-NARROW4 1 of 1, H-IDLE 2 of 2 and tick rate 0.998
held. fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** CR_CACHE_CTRL: 0x0000ffff in the first sample of all 24 rows (controls too), one
change to 0x1000ffff and no return in all 24. The change precedes every CR_EVENT_STATUS event of
the job; bit 26 follows it by 19.5 to 48.3 us in 9 of the 12 rows where it shows
(controls included), by 106.6 us in e2-04 (after bit 13 at 62.4 us, 19.5 us before the render
end), and in two rows only 5.3 and 17.7 ms later. The FAILED lead clause is e2-04's.
CR_USE0_SERV_EVENT: 9 to 11 counts beyond the ticks over each triangle (24 of 24 rows with the
controls), the tick rate 0.9975 to 1.0004 a ms before the job, bit 16 clear in 0 to 8 samples of
a job. Bit 26: first episodes 5.0 to 7.2 us (e2, e4) and 11.9, 15.7 us (e3), whenever set
0x24000000 except one sample of e2-03's second episode, 0xa4004000 with SW_EVENT and
MASTER_INTERRUPT. CR_EVENT_STATUS2 left 0x400 in 4 of 10 e2 rows. Every job drew exactly.

**What it shows.** For the fwsim read rules: CR_CACHE_CTRL reads 0x0000ffff after a reset and
0x1000ffff from a change ahead of every event of a kicked job until a reset; the change does not
come a fixed time before bit 26 [infer: it marks the firmware's write or the kick]. A plain
triangle adds 9 to 11 to CR_USE0_SERV_EVENT's count beyond the ticks. The word while bit 26 is
set is the idle word with bit 26 and any other pending event bit, not always 0x24000000. Bit
26's visible width depends on what else regtimeline reads (about 6 us with four registers,
12 to 16 with 27, against 55 to 93 for most first episodes alone, E1121) [infer].

**What it does not show.** Whether the CR_CACHE_CTRL change is the firmware's write or the
hardware's answer to the kick, when it comes after the kick, what a read between the kick and
the firmware's write returns, which served events count in CR_USE0_SERV_EVENT, and how many
reads the firmware's poll makes.
