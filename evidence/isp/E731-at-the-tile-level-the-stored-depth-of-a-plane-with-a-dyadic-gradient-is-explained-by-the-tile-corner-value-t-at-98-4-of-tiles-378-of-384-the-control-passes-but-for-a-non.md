+++
id = "E731"
claim = "Under the premise that the stored word is trunc(T + A (x + 0.5) + B (y + 0.5)) with a tile-corner value T, the three frozen candidates for T (RN of the plane at the corner, its truncation, a walk fl(T(i) + RN(32 A))) fit, by direction and binade: for a dyadic gradient all three fit 378 of 384 tiles (a control that does not discriminate, and fails in binade 2: 3 tiles each in dp-ax-b2 and dp-ay-b2); for a non-dyadic gradient in y, truncation and the walk fit 63 of 63 consistent tiles in b0 and 64 of 64 in b1 (RN 63 and 56); in x, 0 of 58 consistent tiles in b0 and 34, 40, 38 of 43 in b1; in b2 no tile admits a single T, so the premise fails there; class c 232, 200 and 64 of 384 in total; Q200 is not settled"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** isp-b-depth: 21 jobs, rc 0 (each with 5 kernel pokes in the log), a 256 x 128 target
(64 tiles of 32 x 16 in a 8 x 8 grid), `tri --tri-v --tri-z --depth --depth-dump` with a vertex
triple of whole pixels and z on a dyadic lattice. Class a (6 jobs: the control, A and B chosen so
that 32 A is exact in float32), class b (6 jobs + 3 vertex permutations of dp-bx-b0: non-dyadic
gradient, in x or in y), class c (6 jobs: non-dyadic with z so that the exact T at every odd tile
sits on a float32 tie), z0 in three binades (b0, b1, b2) for a, b and c. All held out except the
control class.

**Hypotheses (frozen).** T(i) in each tile and the stored words w(x, y) = trunc to float32 of T +
A (x + 0.5) + B (y + 0.5); three candidates for T per tile: RN of the exact plane at the tile's
corner, the truncation of it, a walk adding RN(32 A) per tile. Criterion: class a must have every
candidate inside the interval the words allow in at least 95% of tiles or the tile structure is
rejected.

**Results.** [HW] (recompute section F; a tile counts when at least 60 pixels are covered, all of
them here.) Class a: all three candidates inside the interval in 378 of 384 tiles (98.4%; the 6
missing are 3 tiles in each of dp-ax-b2 and dp-ay-b2): control passed. Class b: RN 153, trunc 167,
walk 165 of 576 tiles. Class c: RN 232 (60%), trunc 200 (52%), walk 64 (17%) of 384. No candidate
reaches the 95% of the control on class b or c. Per job (tiles of 64 with any consistent T, then
the candidates RN, trunc, walk): dp-bx-b0 58 with 0, 0, 0 (so are dp-bx-b0-p1, -p2, -r: the vertex
order changes nothing); dp-by-b0 63, 63, 63, 63; dp-bx-b1 43, 34, 40, 38; dp-by-b1 64, 56, 64, 64;
dp-bx-b2 0 and dp-by-b2 0 (no consistent single T in any tile); dp-cx/cy-b0 62: 58, 50, 16; dp-
cx/cy-b1 62: 58, 50, 16; dp-cx/cy-b2 43: 0, 0, 0.

**Reading by direction and binade.** The totals (class b 153 to 167 of 576) average a positive
result away: in y (dp-by) truncation and the walk explain every consistent tile in b0 and b1. The
failing part is x (dp-bx-b0: 58 consistent tiles, 0 fit) and b2. In b2 the dyadic control already
fails (3 of 64 tiles in each of dp-ax-b2 and dp-ay-b2, the 98.4%) and the non-dyadic b2 jobs have 0
consistent tiles, so the shared premise is broken there and no candidate for T can be refuted in
b2. The control cannot validate the tile structure at all: for dyadic gradients every candidate
passes.

**Population.** The tile-corner statistic of the earlier analysis (60% of tiles main, 75% fine2)
is a minority effect of unknown cause (plan.md section 1.6); this is the clean-slate test it
called for, and it does not confirm the three candidates in x. The control passing at 98.4% shows
the interval method works where the arithmetic is exact in b0 and b1; it does not discriminate
between the candidates.

**What it shows.** [HW] The words stored for a plane of non-dyadic gradient in x are not explained
by RN, truncation or the walk of the tile corner in b0 (0 of 58): Q200's arithmetic is not found;
in y truncation and the walk fit in b0 and b1. The three candidates split on class
c (232, 200, 64 of 384), so the class does discriminate, and the walk is the worst. In the y
direction (dp-by) truncation and the walk fit 63 and 64 of the consistent tiles in b0 and b1; in x
with a non-dyadic A (dp-bx-b0) no candidate fits a single tile. [infer] The x step between tiles
in b0 is not fl(T + RN(32 A)).

**What it does not show.** The rule that does explain the words (Q288); why 64 of 64 tiles of dp-
bx-b2 and dp-by-b2 admit no single T under truncation of the stored word (the words may not be a
truncation of T plus the gradient term at all in that binade).
