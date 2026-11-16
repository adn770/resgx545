+++
id = "E1116"
claim = "r30-evst on module E0CC4027, stages e2, e3, e4 (CR_EVENT_STATUS with CR_EVENT_STATUS2, CR_CACHE_CTRL and CR_USE0_SERV_EVENT, and with 27 registers), readings only, no verdict: every frozen headline prints 'controls FAILED' because the controls' frozen CR_CACHE_CTRL value 0x1000ffff was the builder's error (taken from E258, read mid-session with no reset), while every control read 0x0000ffff after the runner's reset as the kit's own snapshots do; post hoc, CR_CACHE_CTRL reads 0x0000ffff after the reset, bit 28 sets 21 to 40 us before bit 26 rises in 7 of 10 rows where both show and stays to the end of the run (24 of 24); with these registers sampled bit 26 shows 4.9 to 12.6 us wide (10 episodes) against 55 to 93 us for most first episodes with CR_EVENT_STATUS alone (E1115); CR_USE0_SERV_EVENT counts 9 to 11 beyond the ticks over a plain triangle (24 of 24 rows), its tick rate 0.9975 to 1.0004 a ms, bit 16 clear in up to 6 samples of a job"
unit = "platform"
method = "r30-evst (render/closing-r30-evst), stages e2, e3, e4 of the question-closing pass (round 30: the fwsim run of resgx545 9cfced4 stopped on a CR_EVENT_STATUS read after a render kick's CR_CACHE_CTRL write; session built by the lead's request, safe class), dataset render-closing-r30-evst; attempt out/20261116-123552 (scores score-e2.txt, score-e3.txt, score-e4.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06) under ~/regtimeline (sha256 079f63590ce87ff2a1ac5499291e52340ff448d9c5e41942a9420264764de803, tools/sweep/regtimeline.c, read only through /dev/mem), every job `regtimeline TOTAL LEAD REGS -- ~/sgxfive-test-t10 tri --width 64 --height 64 [-n 3]` after a debugfs reset, no knob and no register write; the laptop's clock about 2 h 50 min behind (the kept times are regtimeline offsets); the rows tables/STAGE.txt from gen/make.py, the frozen predictions predictions/STAGE.tsv); freezes: FROZEN.sha256 e7800de13893174655530e02597ef34ebe23745aa43409c1035d982e35a7740c (53 files), PREDICTIONS.sha256 7dfc3ee0c5480b71c5261e7bddff13df89ccc02fddfe54bf8faaa5e459999406 (5 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 9cfced4d, resgx545:tools/closing/kit/lib_kit.sh at 9cfced4d, resgx545:tools/closing/kit/run_stage.sh at 9cfced4d, resgx545:tools/closing/kit/kitscore.py at 9cfced4d, resgx545:tools/closing/kit/fake/sudo at 9cfced4d, resgx545:tools/closing/kit/fake/timeout at 9cfced4d, resgx545:tools/closing/kit/fake/df at 9cfced4d, resgx545:tools/closing/kit/fake/modinfo at 9cfced4d, resgx545:tools/closing/kit/fake/sha256sum at 9cfced4d, resgx545:tools/closing/kit/fake/tool.sh at 9cfced4d, resgx545:tools/closing/kit/fake/tool.py at 9cfced4d, resgx545:tools/closing/kit/fake/ssh.py at 9cfced4d, resgx545:tools/closing/scorekit.py at 9cfced4d, resgx545:tools/closing/sessioncheck.py at 9cfced4d, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-1.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-2.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-3.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-4.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r2-5.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-1.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-2.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-3.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-4.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri64-r7-5.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-idle-r2-1.txt.gz at 2da50676, data:platform/event-bits/dumps/event-timelines/tl-tri256n3-r7-1.txt.gz at 2da50676, data:platform/register-timelines/output.txt at 2da50676, data:platform/event-bits/cases.tsv at 2da50676, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r30-evst:out/20261116-123552/e2/", "render-closing-r30-evst:out/20261116-123552/e3/", "render-closing-r30-evst:out/20261116-123552/e4/", "render-closing-r30-evst:fold/"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_CACHE_CTRL", "CR_USE0_SERV_EVENT"]
+++
**What ran.** The other three stages of r30-evst (E1115's What ran): e2 (12 jobs, `1.5 0.5
0x0118,0x012c,0x0804,0x0b14`), e3 (10 jobs, `0 0.3` with r23-dpm's timeline set, E547's 0x0218
and those four: 27 registers) and e4 (2 jobs, `6 5.5` with e2's four: 5.5 s of idle before one
triangle). Frozen besides E1115's models: H-ST2 (0x0118 0x400 throughout, E547), H-CC-FLAT
(0x0804 1000ffff throughout, E258) [infer], H-SE-EVENTS (0x0b14 counts 3 or more beyond the
ticks over the job) against H-SE-TICKS (within 1), H-DENSITY against H-INDEP (e1's seen fraction
against e3's), e4's tick rate 0.9 to 1.1 a ms. Controls (e2, e3 first and last, e4 first): diff
0, idle 0x20000000, idle2 0x400, cache 0x1000ffff, se16 1, the sample interval in its window.

**Frozen verdict (as printed).** Every headline of e2, e3 and e4: `controls FAILED: e2-c1:
FAILED; e2-c2: FAILED` (and e3-c1, e3-c2, e4-c1). Every one of those five controls read diff 0,
idle 0x20000000, idle2 0x400, se16 1 and an interval inside its window (1406 to 1542 ns with
four registers, 8989 to 9234 ns with 27); each failed on `cache`, read 0x0000ffff against the
frozen 0x1000ffff. The frozen value was the session builder's error, not a reading against a
right premise: it came from E258's register-timelines output, read after earlier jobs with no
reset between them, while the kit resets before every row, and the kit's own snapshots (every
`snap0.regs`, after the reset) read 0x0000ffff (fold/FOLD-NOTES.md). No hypothesis of these
stages is decided.

**Readings (post hoc, not frozen; fold/posthoc.txt).** [HW] CR_CACHE_CTRL reads 0x0000ffff after
the reset and 0x1000ffff from the job's first activity to the end of the run in 24 of 24 rows;
where bit 26 shows too, bit 28 came 21.3 to 40.0 us before it in 7 of 10 rows (114.7 us in
e3-01; in e2-01 and e2-02 bit 26 rose 21.1 and 16.7 ms after it). Bit 26, whenever set, read
0x24000000 (10 episodes in 10 rows), 4.9 to 7.6 us wide with four registers and 11.8 to 12.6 us
with 27; seen in 6 of 10 e2, 2 of 8 e3 and 1 of 1 e4 rows besides e3-c1. CR_EVENT_STATUS read
0x20000000
outside the job in 19 of 19 rows. CR_USE0_SERV_EVENT: 9 to 11 counts beyond the ticks over the
job in 24 of 24 rows (tick rate from the lead 0.9975 to 1.0004 a ms; e4's 5.5 s lead 0.9976),
bit 16 clear in 0 to 6 samples within a job. CR_EVENT_STATUS2 left 0x400 in 6 of 19 rows.

**What it shows.** Nothing by its frozen rules. Post hoc [infer]: the kick sets CR_CACHE_CTRL
bit 28 about 35 us before bit 26 shows, and a reset clears it; sampling these registers beside
CR_EVENT_STATUS goes with a much shorter bit 26 (5 to 13 us against E1115's 55 to 93 for most
first episodes), so the width depends on what else is read; CR_USE0_SERV_EVENT counts served
events beyond the ticks, about ten for a triangle.

**What it does not show.** Any frozen verdict; whether the CR_CACHE_CTRL bit is the firmware's
write or the hardware's; why the width changes; what each extra count of CR_USE0_SERV_EVENT is.
A rerun with the right frozen cache value (0x0000ffff) would decide H-CC-FLAT, H-SE-EVENTS and
the density models.
