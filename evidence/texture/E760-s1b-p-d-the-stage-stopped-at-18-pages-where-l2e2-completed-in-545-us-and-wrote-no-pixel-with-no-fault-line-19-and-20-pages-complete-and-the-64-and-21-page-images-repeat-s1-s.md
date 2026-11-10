+++
id = "E760"
claim = "With the probe's scratch at 20 and 19 pages (80 and 76 KiB) the L2e2 job (E722's extent 86016 bytes) completed with rc 0 and no fault line, each image of 2048 pixels with 128 distinct words none of them tagged 0xD, the two images different (every pixel past the scratch in the model), and with 18 pages (72 KiB) the job completed in 545 us, wrote no pixel (the tool: `failed: no pixel written`, rc 3) and left no fault line and no BIF fault (bif_faults 0), an outcome neither HM (completes) nor HB-end (faults) predicted, which stopped the runner at the stage's eighth job: the 17-page job and the control d-L2e2-16 did not run, so the frozen verdict is cannot tell (the control void); the 64-page control d-ok-64 was A4 exact, and the repeats of S1's post-hoc fits gave the images S1 recorded byte for byte, the three jobs that faulted at 16 pages (L2e2, L3e3, st-L3e2) at 64 pages and L2e2 at 21 pages, each A4 exact at its own page count (4 of 4)"
unit = "texture"
method = "S1b stage p-d of the question-closing pass (10 jobs table, 8 run; paths relative to render/closing-s1b/ of the dataset: probe --temps 32 --coords --pixels --scratch-pages N on the T3 address programs s1d-tw64x64-l2e2, -l3e3, s1d-st128x32-l3e2 and s1d-tw128x32-l0e2 of bins/, N = 64 for the control d-ok-64 and for the three repeats, 21 for a fourth repeat, then 20, 19 and 18 for the held-out rows, a debugfs reset before each job), run 1794266508-28894 on 2026-11-10 00:21 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); tables, predictions (predictions/p-d-A4.tsv: A4 of E722's model rendered at each job's own page count, every pixel), scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256; verified before the stage and before scoring); the probe's own `scratch at ... (N KiB)` line is the knob proof of each job; the stage ran its jobs in the order of its table (controls first, hypothesis rows last, the control d-L2e2-16 last) and the runner stopped at the first unexplained failure (d-L2e2-18: class fail, rc 3, which is neither a hang nor a fault, so the row's hypothesis allowance did not cover it; STOP, exit 4); the next stages p-f and g-e4w ran in a resumed attempt (out-s1b-2.log); verdict by the frozen score/score_s1.py p-d (out/score-p-d.txt, reproduced on the kept files); the stopped run is the only run (out/p-d/)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/p-d/"]
terms = ["T3.BIT10", "T3.BITS19_18", "T3.BITS28_27", "CR_BIF_FAULT"]
+++
**What ran.** E743 (S1) found that E722's three faulting T3 jobs complete with the scratch at 64
pages and that L2e2 completes at 21 and 20 pages and faults at 16, and read it post hoc as "the
fault follows the mapping": the hardware read past the scratch at 20 pages without a fault. S1b
froze A4 (E722's address model) at each job's own page count, S1's four completing images as repeats
(HB-A4: complete and A4 exact; HX: a 64 KiB buffer, so a fault) and, for 20 to 17 pages, HM
(complete; the model has no in-scratch pixel to test at these sizes, so only the outcome counts)
against HB-end (a fault when the scratch ends). The control d-L2e2-16 (E722's job unchanged, `BIF
fault 0x90002`) ran last by design.

**Frozen verdict.** cannot tell: controls failed or void ['d-L2e2-16']: {'d-L2e2-16': None}
(out/score-p-d.txt): the control did not run. The runner's exit was 4 at d-L2e2-18; 17 pages and
the control are in cases.tsv's table but not in its rows. No hypothesis was scored.

**Results [HW].** Jobs run, with the probe's scratch line and job time: d-ok-64 (256 KiB, 488 us),
d-L2e2-64, d-L3e3-64, d-st-L3e2-64 (256 KiB), d-L2e2-21 (84 KiB, 490 us), d-L2e2-20 (80 KiB, 480
us), d-L2e2-19 (76 KiB, 548 us), d-L2e2-18 (72 KiB, 545 us). All rc 0, class ok and no fault line in
the kernel log but d-L2e2-18: rc 3, class fail, 167 bytes of output (`programs asm`, the scratch
line, `job time: 545 us`, `failed: no pixel written`), the dmesg slice empty, `bif_faults 0` in the
kernel log lines around it. Images (2048 pixels): d-ok-64 A4 exact; d-L2e2-64 and d-L2e2-21
identical to each other (128 distinct words), A4 exact at their own pages, and with d-L3e3-64 and
d-st-L3e2-64 (32 distinct words each) A4 exact (the scorer's `A4 exact`); all six images are
byte for byte the rows S1 kept for the same names (out/p-d of render-closing-s1). d-L2e2-20 and
-19: every pixel is past the scratch in the model (A4's 2048 of 2048 out of range), none of the
words carries the 0xD tag (0 of 2048), each image has 128 distinct words, row 0 starts 0x00000000,
0x00000008, 0x00000020, 0x00000028, 0x00020000 at 20 pages and 0x00100000, 0x00100008, 0x00100020,
0x00100028, 0x00120000 at 19, and the two images differ; the 20-page image equals S1's.

**Read after the run [infer, not held out].** The 18-page job is a third outcome: the job ran for
the time of its neighbours (545 against 548 us at 19 pages), the kernel logged no fault and no
error, and the tool found no pixel written. Between 19 and 18 pages the probe's output changes from
128 words read past the scratch to none written, with no fault word. It is not shown whether the
job's pixel task stored nothing, stored outside the buffer it dumps, or was not run; no register of
the failed job was read other than the stage's own regs dump (kept as after.regs). The S1 post-hoc
reading ("the fault follows the mapping") predicted completion for 17 to 20 pages and is not
supported at 18; HB-end (a fault at the scratch's end) is not supported at 19 or 20. The repeats
agree with S1's frozen-after-the-fact fits (4 of 4), which makes them a reproduction, not a test.

**Caveats.** The verdict is "cannot tell" by the frozen rule because the last row, the control,
did not run; no hypothesis of the stage was scored, and the held-out rows 20 and 19 completed
while their model (A4) is vacuous there (no in-scratch pixel), so only their outcome speaks. The
stopped run kept rc 3 as class `fail`, which the table treated as unexplained; the 17-page job and
the control never ran in this session.

**Not shown.** What the 18-page failure is (nothing written, no fault); the first page count below
19 at which it appears and whether 17 behaves as 18; whether the fault of 16 pages (E722, E743)
and the empty write of 18 are one effect with the mapping behind the scratch; how large a buffer the
sampler may read.
