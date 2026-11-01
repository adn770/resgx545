+++
id = "E506"
claim = "At sizes with four macrotiles in a row (n = 4: 640 x 480, 768 x 640, 1280 x 720) the first and third boundary fields are not free and the declared PB and PC fail: of the 39 fit cases at 640 x 480 only 2 draw exactly (CR_TE_MTILE1 B3 25 and 28, both beyond the 20 tile columns) with 34 faults and 3 wrong images, and of the 16 held-out cases at 768 x 640 and 1280 x 720 2 draw exactly (768 x 640, CR_TE_MTILE1 B3 one and four more) while PB and PC predicted all 16; B1 zero or one less faults the job in 8 of 8 of them; PA, expected to fail, is right in 16 of 16 of them and in 34 of 39 at 640 x 480; the controls draw exactly 3 of 3 a size"
unit = "ta"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/ta/mtile-fields.toml (script mtile-fields.sh): as E505 at 640 x 480 (fit), 768 x 640 and 1280 x 720 (held out); the recompute script's predicates PA, PB, PC built from the words and compared with the observed result (exact, wrong, fault) by set"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-mtile-fields"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++

**640 x 480 (fit; rule 0x82010018, 0x02010018, stride 0x40: bit 31 with (8, 16, 24) and (8, 16,
24)).** 39 cases: CR_TE_MTILE1 B1 0, 1, 2, 4, 5, 6, 7, 9, 12, 15, 16 (11), B3 16, 17, 20, 23, 25, 28
(6) and CR_TE_MTILE2 the same 17, and five partitions. Observed [HW]: 2 exact (CR_TE_MTILE1 B3 25
and 28), 3 wrong (CR_TE_MTILE2 B1 16: 258048 of 307200 pixels green; B3 25: 296960; B3 28: 266240),
34 faults (a faulting job leaves between 0 and 253248 pixels green; every CR_TE_MTILE1 B1 and every
B3 below 24 faults, and so does each partition). The three controls draw exactly.

**Held out.** 768 x 640 (rule 0x82010018, 0x03018024, stride 0x60) and 1280 x 720 (0x83018024,
0x03018024, 0x90): 8 cases each, B1 zero and one less and B3 one and four more on each word. 512 x
384 is in E505. At 768 x 640: CR_TE_MTILE1 B1 zero and one less fault, B3 +1 and +4 draw exactly;
CR_TE_MTILE2 B1 zero and one less fault, B3 +1 is wrong (479232 of 491520), B3 +4 faults. At 1280 x
720: all 8 are wrong or fault (CR_TE_MTILE1: B1 zero and one less fault, B3 +1 and +4 wrong; the
same for CR_TE_MTILE2). So 2 of 16 draw exactly.

**Hypotheses against the data.** Fit set (67 cases: 28 at 256 x 256, 39 at 640 x 480): PA right 40
of 67 (6 and 34), PB and PC 30 of 67 (28 and 2). Held-out set (24 cases: 8 at each of 512 x 384,
768 x 640, 1280 x 720): PA right 18 of 24 (2, 8, 8), PB and PC 10 of 24 (8, 2, 0). Controls: all
three 15 of 15. PB and PC predict "exact" for every case run here and are right at n = 2 and wrong
at n = 4; PA predicts "not exact" for most cases and is right at n = 4 (50 of 55, 16 of 16 on the
held-out sizes, whose predictions were written before the run) and wrong at n = 2 (8 of 36). None
of PA, PB and PC fits both kinds of size (safe script: PA 8 of 36 cases at n = 2 and 50 of 55 at n
= 4, PB and PC 36 of 36 at n = 2 and 4 of 55 at n = 4), and the one expected to fail (PA, E407: 4
of 10) holds at n = 4 on the sizes it was not fitted on. Its 5 misses at 640 x 480 are words that
cut the tiles as the rule does (CR_TE_MTILE1 B3 16, 20, 23 and two partitions) and still fault. The
declared outcome "B1 zero or one less, B3 one or four more exact" fails at n = 4 for B1 (8 of 8
fault) and for B3 (6 of 8 not exact).

**Reading [infer].** With two macrotile columns B1 and B3 are not read (E505); with four, the B1
values 0 to 16 of the safe script fault CR_TE_MTILE1 (11 of 11 at 640 x 480, and zero and one less
at the held-out sizes) and fault or draw wrong in CR_TE_MTILE2 (10 and 1 of 11; the values 17 to 40
of the risky script draw wrong or fault, E509), and a B3 below the rule's faults at 640 x 480. A B3
beyond the screen's 20 tile columns (25, 28) draws exactly in CR_TE_MTILE1 and wrong in
CR_TE_MTILE2. So the fields are tile boundaries read one by one when there are four macrotiles; bit
31, B2, the stride and the non-monotone sets belong to the risky script (E509).

**What it does not show.** B2's role, the stride, bit 31 and B1 above B2 (none changes in this
table; the risky script's cases are in E509), wrong-image tile maps (the digit maps are in the dumps
but were not read).
