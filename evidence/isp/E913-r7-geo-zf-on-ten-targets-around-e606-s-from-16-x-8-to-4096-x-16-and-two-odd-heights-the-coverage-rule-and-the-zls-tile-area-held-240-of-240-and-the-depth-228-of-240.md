+++
id = "E913"
claim = "R7-geo stage zf (Q240; 242 depth jobs, no fault): on ten targets E606 did not run, 64 x 128, 128 x 64, 256 x 64, 128 x 96, 128 x 144, 32 x 16 and 16 x 8 (below one tile), 4096 x 16, and the odd heights 64 x 33 and 96 x 47 (round 6's t6 tool), 12 small and 12 medium random triangles each with vertices inside the target on the 1/256 grid, E606's coverage rule drew every image and triangle count (H-E606, 240 of 240) and the depth store wrote the whole tile area and nothing outside it (H-ZLS, 240 of 240), held out; the depth stayed within E606's 3 units of 2^-23 in 228 of 240 jobs (H-DEPTH; misses at every size but 128 x 64, 256 x 64 and 128 x 96, 15.90 units at most), every miss a triangle covering 1 or 2 pixels (post hoc); controls pass (E606's cases 262 at 64 x 64 and 926 at 128 x 128: hash, triangle count and dump sha256); frozen verdicts 'Q240 family H-E606 held on every size (240 of 240 rows decided)', the same for H-ZLS, and 'Q240 family H-DEPTH held on every size is not supported: 228 held, 12 FAILED, 0 cannot tell of 240'"
unit = "isp"
method = "R7-geo stage zf of the question-closing pass, round 7 (decisions R7-2 a, R7-7 a, decision 3 a of closing7/rank/rank-round7.md; plan R7-2 b), dataset render-closing-r7-geo, on the laptop (host cedar), 2026-11-12, attempt out/20261112-211113 (stage started 21:30:20 Mac time, run-r7g-2.log), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at the stage start and end), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558...) for 194 jobs and, for the 48 jobs at 64 x 33 and 96 x 47, which t4 refuses, round 6's t6 (built by the lead on the build host from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c, TOOL6.sha256; staged by run/stage_g.sh from the session's bin/t6/, checked on the laptop before the stage; the binary is not published: the session's FROZEN.commits binds it to its source, sgxfive-test.c at d9b2969 built by render/closing-r6-misc/lead/build_tool6.sh); jobs of E606's D form as E912's (`--pixels` at every size), the first row of 32 x 16, 16 x 8, 64 x 33 and 96 x 47 a gate (a refusal would have skipped its size: none was refused), every job class ok, health ok after the stage. Frozen before the first job (FROZEN.sha256 84ba6d23..., PREDICTIONS.sha256 a52a549b...) as E912's. Scored by the frozen score/score_g.py zf (score-zf.txt); at the fold the same scorer re-ran byte-identical on the kept files, and the 1456 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh). Post hoc at the fold, not frozen: fold/depth_read.py"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-geo:out/20261112-211113/zf/", "render-closing-r7-geo:fold/"]
terms = []
+++
**What ran.** The simulator admits E606's coverage and depth on its three targets only, and the
coverage alone on E680's ten (Q240). Stage zf ran E606's depth jobs on ten more: the power-of-two
family around E606's sizes (64 x 128, 128 x 64, 256 x 64), the half-sizes that are not powers of two
of the first-triangle fixtures (128 x 96, 128 x 144), two targets below one tile (32 x 16, 16 x 8),
a wide strip (4096 x 16) and two odd heights (64 x 33, 96 x 47; the userspace tool refuses odd
widths), 24 triangles each, frozen as E912's: coverage (H-E606), the store (H-ZLS) and the 3-unit
depth tolerance (H-DEPTH).

**Frozen verdict (as printed).** `Q240 family H-E606 held on every size (240 of 240 rows decided)`,
`Q240 family H-ZLS held on every size (240 of 240 rows decided)`, `Q240 family H-DEPTH held on
every size is not supported: 228 held, 12 FAILED, 0 cannot tell of 240`. Both controls passed.

**Results [HW].** Per size (`score-zf.txt`; depth error in units of 2^-23, largest of the size):

| target | coverage, store | depth within 3 U | largest |
|---|---|---|---|
| 64 x 128 | 24 / 24, 24 / 24 | 23 of 24 | 5.21 |
| 128 x 64 | 24 / 24, 24 / 24 | 24 of 24 | 2.01 |
| 256 x 64 | 24 / 24, 24 / 24 | 24 of 24 | 2.58 |
| 128 x 96 | 24 / 24, 24 / 24 | 24 of 24 | 2.15 |
| 128 x 144 | 24 / 24, 24 / 24 | 23 of 24 | 3.23 |
| 32 x 16 | 24 / 24, 24 / 24 | 22 of 24 | 5.08 |
| 16 x 8 | 24 / 24, 24 / 24 | 23 of 24 | 6.65 |
| 4096 x 16 | 24 / 24, 24 / 24 | 20 of 24 | 9.88 |
| 64 x 33 (t6) | 24 / 24, 24 / 24 | 23 of 24 | 12.16 |
| 96 x 47 (t6) | 24 / 24, 24 / 24 | 22 of 24 | 15.90 |

Every gate row ran; no size was skipped.

**Read after the run (post hoc, not frozen; `fold/depth_read.py`).** Each of the 12 misses is a
triangle covering 1 or 2 pixels (8 of the small class, 4 of the medium class whose triangle came
out as thin as that; areas 0.03 to 2.2 pixels), one or two pixels above 3 units each. With E912's
zd rows, every job covering 5 pixels or more is within 2.64 units (138 of 138).

**What it shows.** [HW] E606's coverage rule holds, held out, on targets around E606's three, below
one tile, 4096 pixels wide and 16 high, and at odd heights, and the depth store writes the whole
tile area of each and nothing past it. The 3-unit depth tolerance fails on 1- and 2-pixel triangles
at seven of the ten sizes, as on E912's larger targets. [infer] The coverage rule is independent of
the target among the sizes run; the depth misses follow the triangle's size, not the target's.

**What it does not show.** Odd widths (the tool refuses them; E903 ran them with a tool that takes
them), sizes past 4096, the sizes between those run, vertices outside the target, a bound on the
depth error of tiny triangles (Q200), and the iterated attributes on these targets.
