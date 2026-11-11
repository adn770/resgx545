+++
id = "E833"
claim = "Converted from the published closing-pass sessions (R3-pixel, R3-geo, R3-geo-c, R3k-pixel) as vectors, sgx-sim replays all 204 pixel-loop proofs of R3-pixel (q-f0 10, q-f1a 54, q-f1b 54, q-t 86) and its 8 direct-read jobs (48038 pixels, 0 mismatches); it refuses R3-pixel's 73 vertex loops (a `phas` wait on vcull, E121) and the 14 tables of depth words (57 jobs, E795-E798), dword 36 (60 jobs, E803), DPM counts (R3-geo, R3-geo-c), ZLS extents (15 jobs, E831) and parameter-buffer pages (10 dumps, E824), each with its reason; R3-pixel's 285 timing rows are data, not a prediction"
unit = "usse"
method = "offline, round 4 of the question-closing pass (decision R4-4 a, sim item 4): tools/usse-asm/closing_vectors.py and closing_tables.py convert each kept job of the published sessions (one attempt each, as scored) into vector files under the data repository's vectors/closing/; crates/sgx-sim/tests/closing_vectors.rs replays the loop proofs and direct reads and counts the refusals, closing_tables.rs requires every table to state its refusal; run with RESGX545_REQUIRE_DATA=1 on 2026-11-11"
tiers = ["HW"]
date = "2026-11-11"
data = [
    "vectors-closing-r3-pixel-loops", "vectors-closing-r3-pixel-direct-reads",
    "vectors-closing-r3-pixel-timings", "vectors-closing-r3-geo-depth",
    "vectors-closing-r3-geo-dword36", "vectors-closing-r3-geo-counts",
    "vectors-closing-r3-geo-c-counts", "vectors-closing-r3-geo-c-zls",
    "vectors-closing-r3k-pixel-pb-pages",
]
terms = []
+++
**What runs.** The closing pass's sessions kept every job's raw output beside its frozen scorer.
Each kept job becomes a vector: a pixel loop's program, its initial state and the image it
printed (`loops`); a direct read's image and the pixels its premise control left undecoded
(`direct-reads`); a table row per job for what the simulator does not model, with the raw file's
sha256 (`depth`, `dword36`, `counts`, `zls`, `pb-pages`); the burst, TA run and status bits per
job (`timings`). The control jobs a session scored only as gates are listed as skipped, not
converted (7 green controls of q-t, `v-ctl0`, the faulted k-f4 control, g-qh's 6 void cells).

**Results [HW].** On the merged round 4 tree:

| set | jobs | replay |
|---|---|---|
| R3-pixel loop proofs (q-f0, q-f1a, q-f1b, q-t) | 204 | 204 pass, 0 fail |
| R3-pixel direct reads (p-c3 and the rd rows) | 8 | 48038 pixels, 0 mismatches |
| R3-pixel vertex loops (q-v) | 73 | refused: `phas` wait vcull in a pixel task (E121) |
| R3-geo depth words (g-da to g-dd) | 57 | refused: no frozen formula held (E795, E796) |
| R3-geo dword 36 (g-d36 and g-c4 to g-c7) | 60 | refused; the table agrees with E803 in 60 of 60 |
| R3-geo and R3-geo-c DPM counts | 90 | refused: the abort sequence is not modelled |
| R3-geo-c ZLS extents (g-z) | 15 | refused: Q287 open at odd sizes (E831) |
| R3k-pixel parameter-buffer pages (k-f4) | 10 | refused: page writes not modelled |
| R3-pixel timings | 285 rows | data only |

The direct reads' premise fractions are 1.000, 0.995 and 0.996, as E808 printed them.

**What it shows.** [HW] The simulator's pixel-loop and direct-read paths agree with every kept
closing-pass job they claim, and every closing-pass result they do not model is held as data
with the reason it is refused, so a later model is checked against the same jobs.

**What it does not show.** A refused table is not a check of anything. The parameter-buffer page
model `ceil(tiles / 8) + 4` that the k-f4 table agrees with in 8 of 8 dumps was fitted to those
dumps (round 4 planning) and is not held out; the timing rows' bit 6 and bit 7 placements are
post hoc readings (E806, E807 corrections of 2026-11-11), not predictions.
