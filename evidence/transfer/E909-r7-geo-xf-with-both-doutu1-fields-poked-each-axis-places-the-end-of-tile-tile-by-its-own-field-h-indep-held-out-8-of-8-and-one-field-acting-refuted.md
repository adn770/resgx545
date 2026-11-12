+++
id = "E909"
claim = "R7-geo stage xf (Q206's both-fields clause, 10 fills at 128 x 64, no fault): with the fill's end-of-tile DOUTU1 x field (bits 11:3) and y field (bits 21:12) XORed in one poke, H-INDEP (each 32 x 16 tile t stored at (2t | f) >> 1 on each axis by that axis's own field, E884's rule applied to both at once, nothing stored past the target) gave the tool's image hash in 8 of 8 held-out rows (x field 2 to 7 with y field 2 to 6), H-XFIRST (only the x field acts when both move) and H-YFIRST (only the y field) 0 of 8 each; controls pass (E884's 128 x 64 x ^ 0x10 hash 0xa817f56116104325 and the baseline 0xf7befd67a3c8e325); frozen verdict 'Q206 both fields: H-INDEP held (8 of 8 rows decided)'"
unit = "transfer"
method = "R7-geo stage xf of the question-closing pass, round 7 (decisions R7-2 a, R7-7 a; plan closing7/rank/rank-round7.md R7-5), dataset render-closing-r7-geo, on the laptop (host cedar, direct cable), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start and end, checked read-only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, TOOL.sha256); laptop files under ~/scratch/r7g/ and one mktemp work directory under ~/scratch/tmp; 10 jobs `fill --width 128 --height 64 --stride 512` with `--poke pds:pixev:12^=V` (V = 0x2010, 0x3018, 0x4010, 0x2020, 0x6028, 0x4030, 0x2038, 0x6020; the control 0x10) or none (the baseline), every job class ok, health ok after the stage; tables and predictions (the three images hashed with libsgxfive's FNV-1a by gen/models.py) frozen before the first job (FROZEN.sha256 84ba6d23..., PREDICTIONS.sha256 a52a549b...; FROZEN.commits pins the resgx545 files at 1c64f3a, f911618 and 382b736). The lead's first attempt (out/20261112-211042) ran nothing: run/stage_g.sh had mode 644 and was staged with bash, and the driver stopped at xf with exit 127 before any job ('run/run/run_stage.sh: No such file or directory', run-r7g.log); the lead staged again and the second attempt (out/20261112-211113, stage started 21:11:13 Mac time, run-r7g-2.log) ran all six stages, no stop, no other lead decision. Scored by the frozen score/score_g.py xf in the run (score-xf.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one (in the scratch session with the freeze verifying, and in the published copy by fold/reproduce.sh, whose output is fold/reproduce.out), and the 54 kept files of the stage decompress to the raw sha256 the laptop logged"
tiers = ["HW"]
date = "2026-11-12"
data = ["render-closing-r7-geo:out/20261112-211113/xf/", "render-closing-r7-geo:fold/"]
terms = ["PIXEL_EVENT.END_OF_TILE", "DOUTU1.BITS11_3", "DOUTU1.BITS21_12"]
+++
**What ran.** E884 held out where the fill's end-of-tile task stores a tile when one DOUTU1 tile
field is poked: each 32 x 16 tile t of that axis at (2t | f) >> 1, the field f in half-tile units,
nothing past the target. Every run so far moved one field alone, so Q206 kept the case of both
fields moved at once. Stage xf poked both fields of the pixel-event program's U1 word (dword 12)
in one XOR on a 128 x 64 fill (four tiles each way) and froze three readings, every pair of which
predicts a different image hash for every row: H-INDEP (each axis placed by its own field, E884's
rule on both), H-XFIRST (only the x field acts when both move) and H-YFIRST (only the y field). The
controls were E884's 128 x 64 x ^ 0x10 case and the unpoked baseline, both with kept hashes.

**Frozen verdict (as printed).** `SUMMARY: Q206 both fields: H-INDEP held (8 of 8 rows decided)`;
H-XFIRST and H-YFIRST `held is not supported: 0 held, 8 FAILED, 0 cannot tell of 8`.

**Results [HW].** From `out/20261112-211113/score-xf.txt` and the runner's log (diff: pixels unlike
the fill colour, of 8192; the places are H-INDEP's tiles (x, y) of the 4 x 4):

| poke V | fields x, y | hash | diff | tiles stored |
|---|---|---|---|---|
| control 0x10 | 2, 0 | `0xa817f56116104325` (E884's) | 4096 | columns 1 and 3 |
| none (baseline) | 0, 0 | `0xf7befd67a3c8e325` | 0 | all 16 |
| 0x2010, 0x3018 | 2, 2 and 3, 3 | `0x93da8f7201d3f325` | 6144 | (1 or 3, 1 or 3) |
| 0x4010 | 2, 4 | `0x66c7472dedd3f325` | 6144 | (1 or 3, 2 or 3) |
| 0x2020 | 4, 2 | `0x4922c1e46003f325` | 6144 | (2 or 3, 1 or 3) |
| 0x6028, 0x6020 | 5, 6 and 4, 6 | `0x5544b027a6cdcb25` | 7168 | (2, 3), (3, 3) |
| 0x4030 | 6, 4 | `0xdb6ffcfa5fe5cb25` | 7168 | (3, 2), (3, 3) |
| 0x2038 | 7, 2 | `0x873c0ba869e5cb25` | 7168 | (3, 1), (3, 3) |

All ten jobs completed with no fault; the two controls matched their kept hashes. The rows whose
fields differ only in bit 0 (0x2010 and 0x3018, 0x6028 and 0x6020) gave the same image, as the
half-tile reading says.

**What it shows.** With both tile fields of the end-of-tile task's U1 moved at once, each axis is
placed by its own field exactly as when it moves alone: the tile t is stored at ((2t | fx) >> 1,
(2t | fy) >> 1), and a place past the target stores nothing. Neither field overrides the other.
The pipeline simulator's transfer model now places such a tile instead of refusing it.

**What it does not show.** Fields poked by other operations than the program's OR (E126's XOR
flips on a render moved one field at a time), other targets than 128 x 64, a copy rather than a
fill, and the other words and bits Q206 still covers.
