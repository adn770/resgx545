+++
id = "E743"
claim = "With the probe's scratch at 64 pages the three T3 address jobs that faulted with 16 pages in E722 (L2e2 and L3e3 at 64x64, st-L3e2 at 128x32) completed (rc 0, no fault line), as did L2e2 at 21 and at 20 pages, while 16 pages reproduced the fault (BIF fault 0x90002 at 0x3e017001, the scratch base plus 80 KiB) and the 64-page control reproduced E722's A4 image; the frozen verdict is cannot tell (mixed: the completing jobs differ from the frozen A4 images), because the frozen A4 hashes were taken from E722's 16-page predictions, which for these three cases are the image of the model's out-of-buffer sentinel; read after the run, E722's model rendered with each job's own page count equals all four completing images (2048 of 2048 pixels each), and at 20 pages the hardware read words past the scratch without a fault"
unit = "texture"
method = "S1 stage p-d (7 jobs; paths relative to render/closing-s1/ of the dataset: E722's probe commands with the scratch size set by --scratch, the probe's own `scratch at ... (N KiB)` line as the knob proof; d-ok-64 the control first, d-L2e2-16 the expected-fault control last), a debugfs reset before each job and a recovery after the fault, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage; scored by the frozen score/score_s1.py p-d (out/score-p-d.txt); the A4 images re-rendered after the run with E722's recompute/tex2.py at the jobs' page counts (analysis/scripts/pixel_d_*.py)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/p-d/"]
terms = ["T3.BIT10", "T3.BITS19_18", "T3.BITS28_27", "CR_BIF_FAULT"]
+++
**What ran.** Q281 asks whether E722's three faulting T3 jobs complete and fit the address model
(A4) when the scratch is larger than 64 KiB. Jobs: the 64-page control (an A4-exact case), the three
at 64 pages, L2e2 at 21 and 20 pages (the extent boundary), and L2e2 at 16 pages (E722's fault).

**Frozen verdict.** cannot tell: mixed outcomes (the three 64-page jobs ok but not equal to the
frozen A4 image) (out/score-p-d.txt).

**Results [HW].** Scratch lines 256, 256, 256, 256, 84, 80 and 64 KiB as set. d-ok-64: A4 exact. The
three 64-page jobs and the 21- and 20-page jobs: rc 0, no fault line; L2e2 at 64 and at 21 pages
give identical images. 16 pages: `BIF fault 0x90002 at 0x3e017001`, recovered.

**Why the image test is void: the generator [infer from the frozen files].** The frozen A4 hash of
the three cases was copied from E722's case file, rendered for 16 pages; there the model reads
outside the buffer for every pixel and returns its sentinel 0xDEADBEEF, so the frozen "A4" is an
all-sentinel image (one hash for all three, as the preflight noticed).

**Post hoc [infer].** E722's own model rendered with 64, 21 and 20 pages equals the four completing
images (L2e2, L3e3, st-L3e2 at 64 and L2e2 at 21) on 2048 of 2048 pixels each; of E722's two
alternative models, "shift idx only" misses all four and "stride chain" equals A4 on three of them
and misses st-L3e2. At 20 pages the model reads past the scratch everywhere; the hardware completed
and returned 128 distinct words without the fill's 0xD tag: memory mapped after the scratch, not a
fault. The 16-page fault address, 0x3e017001, is 80 KiB above the scratch base, 16 KiB past a
16-page scratch; the same offsets read at 20 pages did not fault. So what lies past the scratch
differs between the two jobs; the cause is not shown. A frozen rerun with predictions at the jobs'
own pages confirms.

**Not shown.** The first page count that faults between 16 and 20, and what memory lies after the
scratch.
