+++
id = "E787"
claim = "R2-pixel stages r2-d-safe and r2-d-fault (7 jobs, the T3 address program s1d-tw64x64-l2e2 whose A4 reads land 80 to 83 KiB above the probe's scratch base, with the scratch at N pages and the probe's 3-page coords surface after it): the controls passed (d-ok-64: A4 exact; d-L2e2-19: the image byte-identical to S1b's; d-L2e2-19x, the variant program that stores r10 xor 1 in o0: S1b's image xor 1; d-L2e2-16: fault 0x90002 at 0x3e017001 as E722) and both held-out rows agreed with HL, the reading that the 18-page outcome and the fault are the probe's own layout (the sampler reads what lies past the scratch: the coords surface's words, then its sentinel page, then an unmapped page): d-L2e2-18x (18 pages, the variant) completed with rc 0 and read 0xdeadbeee on 2048 of 2048 pixels, the probe's sentinel 0xdeadbeef with the variant's xor, and d-L2e2-17 (17 pages) faulted with BIF_INT_STAT 0x90002 at 0x3e017001, the address of the 16-page fault; the repeat d-L2e2-18 (the unmodified program, 18 pages, S1b's rc 3 'no pixel written' and no fault) was reproduced; the 18-page 'no pixel written' of E760 is therefore a sentinel image: the probe tests the target against 0xdeadbeef and the job wrote it"
unit = "texture"
method = "R2-pixel stages r2-d-safe (5 jobs: d-ok-64, d-L2e2-19, d-L2e2-19x, d-L2e2-18x, d-L2e2-18) and r2-d-fault (2 jobs: d-L2e2-17, then the control d-L2e2-16 last) of the question-closing pass, round 2 (decisions R2-7 to R2-9 and R2-17; faults last, the two fault jobs at class risky), dataset render-closing-r2-pixel (attempt 20261110-105258), on the laptop (host cedar), 2026-11-10 from 10:52:58 laptop time (09:52 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, not rebuilt); each job probe --temps 32 --coords --pixels --scratch-pages N on the program from the frozen bins (s1d-tw64x64-l2e2 for the L2e2 rows, s1d-tw128x32-l0e2 for d-ok-64; the variant s1d-tw64x64-l2e2-x1 differs from S1b's program in its last instruction, `xor.skipinv.end o0, r10, #1`, a one-line change checked offline), the probe's echo `scratch at 0x3e003000 (N KiB)` the knob proof of each row (another base would void it), a debugfs reset before each job, the rows with expectnopix recording an rc 3 'no pixel written' as a result and not a stop, the d17 and d16 rows hypo-labelled; the 18-page 'no pixel written' rows class ok (rc 3 allowed for d-L2e2-18 only by the frozen scorer); scored by the frozen score/score_r2.py (out/20261110-105258/score-r2-d-safe.txt, score-r2-d-fault.txt and verdict.txt); the layout reading (the probe's allocation order, the sentinel fill, the coords words in the first two pages) is from the source of sgxfive-test.c (probe_one, surface, coord_texel, pixels_all) and from the S1b dumps, read offline before the run and frozen in the table, so the rows for 21, 20 and 19 pages are a fit and 18x and 17 are held out"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-pixel:out/20261110-105258/r2-d-safe/", "render-closing-r2-pixel:out/20261110-105258/r2-d-fault/"]
terms = ["T3.BITS19_18", "T3.BITS28_27", "CR_BIF_FAULT"]
+++
**What ran.** E743 and E760 left the three T3 address jobs that faulted at 16 pages (E722)
completing with the scratch at 64, 21, 20 and 19 pages, and L2e2 at 18 pages finishing in 545 us
with no pixel written and no fault. HL, read from the probe's source before the run, says the
probe allocates in one heap the 64x32 target (2 pages), the scratch (N pages) and a read-only
3-page coords surface after it, fills every page with the sentinel 0xdeadbeef and overwrites only
the first 2048 dwords of the coords surface (pages 0 and 1) with texel coordinates (y << 16 | x);
L2e2's A4 reads land at 80 to 83 KiB above the scratch base whatever N is. So the reads fall in
the scratch (N = 21), in coords page 0 (20), in coords page 1 (19), in the sentinel page 2 (18) and
past the surface in an unmapped page (17 and 16). The test for page 2 is a variant program that
stores the sampled word xor 1: if the pixels are written with the sentinel the image reads
0xdeadbeee, if nothing is written the probe's own "no pixel written" test cannot tell.

**Frozen verdict.** `Q281: HL: all 2 held-out rows agree (d-L2e2-18x, d-L2e2-17); repeat
d-L2e2-18 {'d-L2e2-18': 'PASS'}; controls {'d-ok-64': 'PASS', 'd-L2e2-19': 'PASS', 'd-L2e2-19x':
'PASS', 'd-L2e2-16': 'PASS'}`.

**Results [HW].** r2-d-safe: d-ok-64 complete, A4 exact; d-L2e2-19 complete, byte-identical to
S1b's image; d-L2e2-19x complete, S1b's image xor 1; d-L2e2-18x complete, 0xdeadbeee 2048 of 2048
(HL); d-L2e2-18 rc 3 'no pixel written', as S1b measured. r2-d-fault: d-L2e2-17 fault 0x90002 at
0x3e017001 (HL), d-L2e2-16 fault 0x90002 at 0x3e017001. No job hung and each health triangle
afterwards passed.

**What it shows and does not.** The sampler of L2e2 at 18 pages reads the sentinel page of the
probe's own surfaces, completes, and writes the sentinel: the image is not absent, it is
0xdeadbeef (0xdeadbeee for the variant), and "no pixel written" is the probe's name for that.
There is no hardware effect between 16 and 19 pages that the layout does not explain: the three
rows at 19, 18 and 17 pages and the control at 16 all fall on the layout's prediction, two of them
held out and frozen as such. The 16- and 17-page faults are at one page, 0x3e017001, and a read
past the last mapped page of the probe's surfaces faults (E722, E765). What is
not shown: the largest extent the sampler reads exactly is L3e3's 170 KiB at 64 pages (the probe
cannot build a larger scratch), so no limit is measured below that and none above it.
