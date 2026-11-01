+++
id = "E505"
claim = "At sizes whose macrotile rule has two macrotiles in a row (n = 2) the first and third boundary fields of the macrotile words are free: at 256 x 256, 28 of 28 poked words (B1 of each word 0 to 3 and 0 to 7, B3 5 to 8 and 9 to 12, four partitions of each word) draw exactly, and at the held-out 512 x 384, 8 of 8 (B1 zero and one less, B3 one and four more, on each word) draw exactly, 3 of 3 control runs a size exact"
unit = "ta"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/ta/mtile-fields.toml (script mtile-fields.sh, the safe half of Q100's batch): tri --tri-full with ta:143 or ta:144 poked (--kpoke-render 1:) to a word that differs from the rule's in one boundary field or in a coherent partition, the control (the rule's words) three times a size; every pixel counted green; one run each"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-mtile-fields"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE"]
+++

**Fields.** E247's widths: CR_TE_MTILE1 bit 31, 29:22 (B1), 19:12 (B2), 7:0 (B3); CR_TE_MTILE2
30:22, 20:12, 8:0. At 256 x 256 the rule's words are 0x01004004 and 0x02008008 (all fields (4, 4,
4) and (8, 8, 8)), the stride 0x20.

**256 x 256 (fit).** [HW] 28 cases: CR_TE_MTILE1 B1 0, 1, 2, 3 and B3 5, 6, 7, 8; CR_TE_MTILE2 B1 0
to 7 and B3 9 to 12; the partitions (0, 4, 8), (2, 4, 6), (2, 4, 8), (4, 4, 8) of word 1 and (0, 8,
8), (4, 8, 8), (4, 8, 12), (8, 8, 12) of word 2: all exact (65536 of 65536 pixels, 28 of 28). The
three control runs are exact.

**512 x 384 (held out).** [HW] The rule's words are 0x02008008, 0x0300c00c and a stride of 0x60 (n =
2). The 8 declared cases (B1 zero and one less, B3 one and four more, on each word) draw exactly in
8 of 8, the control 3 of 3.

**Against the declared predictions** (declared.tsv and predictions-declared.tsv of the dataset,
written before the first job). The declared PB and PC predicted exact for all 36 of these cases (B2,
bit 31 and the stride the rule's, B1 <= B2 <= B3 in every one) and are right 36 of 36; PA (exact
only if the words cut the tiles into the rule's runs) is right in 8 of 36 (6 of the 28 fit cases, 2
of the 8 held out) and is not supported at n = 2. The fit set contributes the E407 rows' conclusion
again: nothing at n = 2 tells PB from PC or from "B2 only" [infer]; the cases at n = 4 do (E506).

**What it does not show.** B2 itself, the stride, bit 31 and non-monotone sets are not in this
table (they are the risky script's cases, E509); the values of B1 and B3 beyond those tried.
