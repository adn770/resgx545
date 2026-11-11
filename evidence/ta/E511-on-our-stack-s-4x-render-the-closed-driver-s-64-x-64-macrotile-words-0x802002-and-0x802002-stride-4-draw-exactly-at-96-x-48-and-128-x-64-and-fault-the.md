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

**Correction, 2026-11-09 (11.35).** The measurements above are unchanged. The sentence that 47
pixels of the last printed row are missing from the rows is wrong. The tool message is inserted at
the last 4096-byte boundary of the dump's stream (row 126, 127 and 94 in the three dumps), and the
row is whole once the message line is deleted and the split token rejoined: 16384, 32768 and 18432
pixel tokens in the three dumps, 7680 of them green and 512 background (the first tile, 32 x 16) in
each. The first reading of the rows (the script that skips a token it cannot parse and takes a row
from its own line) dropped 5, 134 and 101 pixels of that row, none of them green. The 47 that the
tool counts as equal beyond the 7680 green pixels (7727, from its diff lines) are [infer] the tool's
tolerance at the triangle's edges: it accepts the background colour where the reference says "edge",
and in the 512 background pixels of the first tile the x = 0 column and the y = 0 row are 16 + 32 -
1 = 47 pixels. So the dump's rows give 7680 green; the tool's count of 7727 equal is not a count of
green. The first tile's 512 background pixels are the dump's.

**Correction 2026-11-11:** The 20 cases at 320 x 160 and larger were skipped because 4x faulted
with the rule's own words (E507, Q140); that fault was our kernel's one-array layout (E788; E824:
with four arrays the kernel's own layout completes every held-out size to 1024 x 768), so the
skipped cases can now run. The three faults of the HS family at 128 x 128 to 256 x 128 are at
0x10000012 to 0x10000016, not at the layout's pages 0x20006 to 0x2000a, and the unpoked render
completed at those sizes (E507), so the measurements above stand [infer: E824 ran no poked words].
"Cannot be fitted from our stack alone" is withdrawn as far as it rested on the faults at 320 x
160 and above; the closed driver's rule still needs the capture batch (Q086).
