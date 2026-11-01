+++
id = "E509"
claim = "At 256 x 256 (two macrotile columns) the second boundary B2 alone decides: of 56 poked words that change only B1 or B3 over 0 to 12, 16 and 20 (below and above B2, so also non-monotone) all 56 draw exactly, and of 28 that change only B2 none does (16 fault, 12 wrong); the stride is not the rule's in 12 of 12 (256 x 256: 0 to 31 draw wrong, 33 to 128 fault), bit 31 set faults, and at the held-out sizes B2 one and four more is not exact in 12 of 12 (512 x 384: 4 wrong; 768 x 640 and 1280 x 720: 8 faults); with four macrotile columns (640 x 480) B1, B3 and B2 are all read and a B2 at or past B3 (24 and above) of CR_TE_MTILE2 draws exactly"
unit = "ta"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/ta/mtile-fields-risky.toml (script mtile-fields-risky.sh, run in the resume, after the recovery path was changed: the change is in the script's header and in phases.toml): tri --tri-full with ta:143 or ta:144 poked to words that change B1 and B3 over 0 to 40, B2, the stride, bit 31, partitions, 223 jobs, one run each; the safe half is E505, E506"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-mtile-fields-risky", "ta-mtile-fields"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++

**What ran.** All 223 jobs of the risky script: 211 fit (256 x 256: 95, 640 x 480: 116) and 12 held
out (B2 one and four more, on each word, at 512 x 384, 768 x 640, 1280 x 720). Outcome: 45 exact,
59 wrong images, 119 faulted jobs (111 fit, 8 held out); no job hung the GPU for good. Three
recoveries needed the retry added to the script's health check (a second reset and a wait, in the
script's header); none of the 223 failed a recovery. The declared fit sizes are 256 x 256 and 640 x
480, the declared held-out sizes 512 x 384, 768 x 640 and 1280 x 720.

**256 x 256 (rule 0x01004004, 0x02008008, stride 0x20).** B1 and B3 of each word over 0 to 12, 16
and 20, which puts B1 above B2 and B3 below B2: with the safe script's 20 such cases (E505), 56
poked words, 56 exact. B2 of each word over 0 to 12, 16, 20 (rule 4 and 8, not repeated):
CR_TE_MTILE1 14 cases, 6 faults and 8 wrong; CR_TE_MTILE2 14, 10 faults and 4 wrong; none exact.
Stride 0, 1, 2, 4, 8, 16, 24, 31 draw wrong (8 of 8) and 33, 40, 64, 128 fault (4 of 4): the stride
must be the rule's, not a count at least that large (22 of 22 not exact with the 640 x 480 values
below: 12 wrong images and 10 faults). Bit 31 set in CR_TE_MTILE1 faults. The 18 other partitions:
13 faults, 5 wrong.

**640 x 480 (rule bit 31 with (8, 16, 24) and (8, 16, 24), stride 0x40).** B1 at values outside the
safe sweep (9 values each word): 8 wrong and 1 fault in each word; B3 (14 each): CR_TE_MTILE1 3
exact (32, 36, 40) and 11 faults; CR_TE_MTILE2 14 faults; B2 (20 each): CR_TE_MTILE1 12 faults and
8 wrong; CR_TE_MTILE2 14 faults and 6 exact (B2 = 24, 25, 28, 32, 36, 40, that is at or past B3);
the stride 0 and 1 fault, 4 to 63 draw wrong (4 of 4), 65 to 256 fault (4 of 4), so below the
rule's value an image is wrong except that 0 and 1 fault; bit 31 cleared in CR_TE_MTILE1 draws
wrong; 19 partitions, 18 faults and 1 wrong.

**Held out.** B2 one and four more: 512 x 384 wrong in 4 of 4, 768 x 640 and 1280 x 720 fault in 8
of 8: 12 of 12 not exact, as every declared hypothesis predicted.

**Hypotheses.** Risky fit set (211 cases): PA right 150, PB 174, PC 162. Held-out (12): all three 12
of 12. Over the whole of Q100 (safe and risky, controls excluded): fit 278 cases: PA 190, PB 204, PC
192; held-out 36 cases: PA 30, PB 22, PC 22. By the number of macrotile columns (n = 2: 256 x 256
and 512 x 384; n = 4: the other sizes): fit n = 2, 123 cases: PA 59, PB 95, PC 123; fit n = 4, 155
cases: PA 131, PB 109, PC 69; held-out n = 2, 12 cases: PA 6, PB 12, PC 12; held-out n = 4, 24
cases: PA 24, PB 10, PC 10. So none of the three fits both kinds of size: the coded PC holds at n =
2 and PA at n = 4, where PC is right in 69 of 155 fit cases (58 under "B2 only"). PB and PC differ
on 68 cases of the fit set (words whose boundaries are not in order or whose B2 is the rule's): PB
is right in 40 and PC in 28; at 256 x 256, where B1 and B3 are free over their whole range, PC holds
and PB's order does not.

PC as coded. The numbers above are those of the code of the recompute script
(recompute_p1126b.py, `predicates`: PC is exact iff B2 of both words, bit 31 and the stride are the
rule's, B1 and B3 free), which the declared tsv follows: it has PC false for the 24 cases that
change the stride or bit 31 (and PA true there). The declared prose (plan.md section 2, "PC exact
iff B2 is the rule's", and the script's docstring) glosses PC as B2 only, which differs from the
code, and plan.md, declared.tsv and predictions-declared.tsv were not altered. As a recount under
that gloss ("B2 only", labelled so and not the declared PC) PC is right on 110 of the 123 fit cases
at n = 2 and on 58 of 155 at n = 4, and unchanged on the held out cases (12 of 12 and 10 of 24).
None of the three fits both kinds of size under either definition.

**What it shows.** [HW] With two macrotile columns the second boundary is the one the TA reads and
the first and third are not (56 of 56 over 0 to 20, either side of B2); only the rule's stride
draws exactly (22 of 22 others do not); the first and third boundary matter at four columns (E506),
and at 640 x 480 a second boundary at or past the third draws exactly in CR_TE_MTILE2. [infer] The
fields are boundaries between macrotile columns (rows) in tiles, compared in order of use: B2
splits n = 2, and n = 4 needs B1, B2, B3. The stride is the macrotile pitch in region headers,
which must match the RT data's layout, so a wrong stride draws a shifted image or faults.

**What it does not show.** Bit 31's role beyond one toggle at each size; tile maps of the wrong
images (the digit maps are in the output, not read); the rows of CR_TE_MTILE2's B2 at other sizes.
