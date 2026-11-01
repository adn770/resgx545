+++
id = "E511"
claim = "On our stack's 4x render the closed driver's 64 x 64 macrotile words (0x802002 and 0x802002, stride 4) draw exactly at 96 x 48 and 128 x 64 and fault the job (BIF fault at 0x10000012 to 0x10000016) at 128 x 128, 192 x 96 and 256 x 128; a macrotile of two tiles with only CR_TE_MTILE1 poked draws exactly at 128 x 128; the tile signature of every job that completes equals the unpoked rule's (3 of 3 U2 jobs here, 4 of 4 with E507's U2 job at 64 x 64; the 6 R jobs of E507 are the rule itself), and the 20 held-out and larger cases of the 26 declared were not run"
unit = "ta"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/ta/mtile-msaa-risky.toml (script mtile-msaa-risky.sh with SKIP_AREA=51200: only sizes below 320 x 160; run in the resume after the recovery path was changed, see the script's header and phases.toml): tri --tri-full, mode 2, 0xe0000000, ta:143, ta:144, ta:146 poked (--kpoke-render 1:) to the closed words or U2's at six fit sizes, 6 jobs, one run each"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-mtile-msaa-risky"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_TE_AA"]
+++

**What ran.** 6 of the 26 declared jobs: q086-128x64-U2 (0x802002, 0x802002, stride 4: the closed
words, since U2 and the closed words coincide at 128 x 64 and 96 x 48), 128x128-U2 (CR_TE_MTILE1
0x802002 with the unpoked CR_TE_MTILE2 and stride 8), 96x48-U2, and the HS family at 128 x 128, 256
x 128 and 192 x 96, which the script lists with the closed words (0x802002 twice, stride 4). 20
cases at 320 x 160 and larger were **not run** by decision: 4x at those sizes faults with the
rule's own words (E507, Q140), so a poked family would test nothing; they are listed in skipped.tsv
of the dataset (and the 1024 x 768 R of the safe script, likewise). declared.tsv is unchanged:
those cases are not run against it.

**Results.** 128 x 64, 128 x 128 (U2) and 96 x 48 draw exactly (8192, 16384 and 4608 pixels green);
the HS jobs at 128 x 128, 256 x 128 and 192 x 96 fault, with 7727 pixels equal to green by the
tool's diff lines (8657 of 16384, 25041 of 32768 and 10705 of 18432 differ) and 7680 in the printed
rows of each dump: the last printed row of each dump has a tool message inserted into it (131, 130
and 99 tokens instead of 128, 256 and 192), so 47 pixels of that row are missing from the rows, and
the tool's count is the whole buffer (the script's summary of the 128 x 128 job crashed on that
message and printed none), `BIF_FAULT` 0x90100 at 0x10000016, 0x10000012 and 0x10000013, so words
that are right at 64 x 64 are not right once the target has more tiles than the words' macrotile
covers: the words and the RT data disagree and the job faults [infer], as the plan said it might.
H86i: the 3 jobs that complete give the same tile signature as R at their size (3 of 3 U2 jobs),
which cannot fail in this form, since every job that completes is all green; with E507's U2 job at
64 x 64, 4 of 4 (the 6 R jobs of E507 and its 64 x 64 U2 job are not counted twice); the held-out
test did not run.

**What it shows.** [HW] The closed driver's words are accepted only where the target is small
enough (they complete at 96 x 48 and 128 x 64 and fault at 128 x 128 and larger of the sizes run,
and 128 x 128 with a macrotile of two in CR_TE_MTILE1 only is exact); so the rule over sizes (Q086)
cannot be fitted from our stack alone and needs the capture batch.

**What it does not show.** Any 4x case at 320 x 160 and above; U2Q, HS and FX there; the closed
driver's own words past 64 x 64.
