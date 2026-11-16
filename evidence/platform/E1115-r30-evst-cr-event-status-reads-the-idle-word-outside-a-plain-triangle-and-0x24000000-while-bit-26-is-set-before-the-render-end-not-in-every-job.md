+++
id = "E1115"
claim = "r30-evst on module E0CC4027 (Q111), stages e1 and e5 (CR_EVENT_STATUS alone at 541 ns a sample, every control passed): in plain 64x64 triangles CR_EVENT_STATUS reads 0x20000000 in every sample outside the job (14 of 14 e1 rows, 5 of 5 e5 rows) and, whenever bit 26 (MADD_CACHE_INVALCOMPLETE) is set, exactly 0x24000000 (19 episodes in 13 rows); in a one-render job its first rise comes 87.7 to 118.7 us before the first rise of bit 18 or 0 and it falls before that (8 of 8); it is seen in 8 of 14 e1 jobs (H-EVERY refuted, H-PART held), its first episode 55 to 93 us wide in 7 of 8 but some episodes 4.2 to 21.1 us (H-WIDE refuted on the held-out rows); bits 6, 9 and 20 never show at 541 ns in e1 (14 of 14); with -n 3 bit 26 shows once in 4 of 5 jobs and twice in one (H-ONCE and H-EACH both refuted as frozen), in two jobs after an earlier render's end"
unit = "platform"
method = "r30-evst (render/closing-r30-evst), stages e1, e5 of the question-closing pass (round 30: the fwsim run of resgx545 9cfced4 stopped on a CR_EVENT_STATUS read after a render kick's CR_CACHE_CTRL write; session built by the lead's request, safe class), dataset render-closing-r30-evst; attempt out/20261116-123552 (scores score-e1.txt, score-e5.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline TOTAL LEAD REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64 [-n 3]` after a debugfs reset, no knob and no register write; the laptop's clock about 2 h 50 min behind (the kept times are regtimeline offsets); the rows tables/STAGE.txt from gen/make.py, the frozen predictions predictions/STAGE.tsv); freezes: FROZEN.sha256 e7800de13893174655530e02597ef34ebe23745aa43409c1035d982e35a7740c (53 files), PREDICTIONS.sha256 7dfc3ee0c5480b71c5261e7bddff13df89ccc02fddfe54bf8faaa5e459999406 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 9cfced4d, resgx545:tools/closing/kit/lib_kit.sh at 9cfced4d, resgx545:tools/closing/kit/run_stage.sh at 9cfced4d, resgx545:tools/closing/kit/kitscore.py at 9cfced4d, resgx545:tools/closing/kit/fake/sudo at 9cfced4d, resgx545:tools/closing/kit/fake/timeout at 9cfced4d, resgx545:tools/closing/kit/fake/df at 9cfced4d, resgx545:tools/closing/kit/fake/modinfo at 9cfced4d, resgx545:tools/closing/kit/fake/sha256sum at 9cfced4d, resgx545:tools/closing/kit/fake/tool.sh at 9cfced4d, resgx545:tools/closing/kit/fake/tool.py at 9cfced4d, resgx545:tools/closing/kit/fake/ssh.py at 9cfced4d, resgx545:tools/closing/scorekit.py at 9cfced4d, resgx545:tools/closing/sessioncheck.py at 9cfced4d, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-1.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-2.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-3.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-4.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-5.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-1.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-2.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-3.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-4.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-5.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-idle-r2-1.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri256n3-r7-1.txt.gz at 2da50676, data:platform/register-timelines/output.txt at 2da50676, data:platform/event-bits/cases.tsv at 2da50676, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-evst:out/20261116-123552/e1/", "render-closing-r30-evst:out/20261116-123552/e5/", "render-closing-r30-evst:fold/"]
terms = ["CR_EVENT_STATUS"]
+++
**What ran.** 47 jobs in five stages, each a plain 64x64 triangle of t10 under regtimeline,
which samples registers read-only from LEAD seconds before the job and keeps every change
(closing29/r30-evst README, pre-run). This record holds e1 (16 jobs: `1.5 0.5 0x012c`, two
controls, 6 fit and 8 held-out rows) and e5 (7 jobs: the same with `-n 3`, two renders after the
first in one context). Frozen from E547's kept tri64 rows (predictions/e1.tsv, e5.tsv): H-ALONE
(bit 26 as 0x24000000 only), H-WIDE (40 to 140 us), H-BEFORE (first rise 60 to 200 us before
the first rise of bit 18 or 0, fallen before it), H-SW, H-SUB (bits 6, 9, 20 never seen), H-IDLE
(0x20000000 outside the job: before the start and after the end plus 5 ms), H-EVERY (seen in 13
or 14 of 14) against H-PART, and for e5 H-ONCE (no row with two episodes) against H-EACH (two
or more such rows). Controls (first and last row): diff 0, idle 0x20000000, the mean sample
interval within 300 to 2500 ns.

**Frozen verdict (as printed).** e1 controls PASS (ivl 539 to 542 ns); `H-IDLE [held]: ... (8 of
8 rows decided)` and fit 6 of 6; `H-ALONE [held]: ... (5 of 8 rows decided)`; `H-BEFORE [held]:
... (10 of 16 rows decided)` (two quantities a row); `H-SUB [held]: (8 of 8)`; `H-SW [held]: (7
of 8)`; `H-PART [held]: bit 26 is missed in some plain triangles at the densest sampling`;
`H-EVERY ... is not supported: 0 held, 1 FAILED`; `H-WIDE [fit]: (3 of 6 rows decided)` and
`H-WIDE [held] ... is not supported: 2 held, 3 FAILED, 3 cannot tell of 8`. e5 controls PASS;
H-ALONE 5 of 5, H-IDLE 5 of 5, H-SW 5 of 5 held; `H-ONCE ... not supported` and `H-EACH ... not
supported` (multi 1); H-BEFORE 2 FAILED of 6 in each set; H-WIDE not supported; H-SUB FAILED on
e5-02 (fit). fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** e1: bit 26 seen in e1-01, 05, 06, 07, 10, 11, 12, 14 (8 of 14), 13 episodes,
widths 55.1, 92.8, 81.2, (55.8, 4.2, 76.1), 60.4, (57.7, 4.4), 21.1, 63.8 us, first rise 87.7 to
118.7 us before the render end; every sample with bit 26 reads 0x24000000. The six rows without
it show the render end (bits 18 or 0, 13) and SW_EVENT with MASTER_INTERRUPT. e5: one episode in
e5-01 to 04 (53.6, 8.3, 4.0, 52.3 us), two in e5-05 (56.5, 4.2); in e5-02 and e5-03 the episode
comes 10.0 and 5.3 ms after an earlier render's end. Bit 20 once in e5-02. Every job drew
exactly.

**What it shows.** For the fwsim read rule: outside a job the hardware reads 0x20000000 through
the ticks; the only word with bit 26 a plain triangle shows is 0x24000000, and in a one-render
job it comes before the render end. Bit 26 is not visible in every job at 541 ns: in 6 of 14 it
is absent or shorter than a sample [infer]. Its width is not one value (4 to 93 us). For Q111:
bit 26 precedes bits 18 and 0 in a one-render job (order); bits 6, 9 and 20 stay under 541 ns in
e1.

**What it does not show.** When bit 26 rises after the firmware's CR_CACHE_CTRL write, how many
reads the firmware's loop makes, whether an unseen bit 26 rose under a sample (regtimeline does
not report its longest gap), who clears it, and the other bits' events. E1116 holds the
register-set stages, whose frozen controls failed.
