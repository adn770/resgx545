+++
id = "E730"
claim = "Re-scored post hoc, not a held-out confirmation (the frozen recompute scored 0 of 12 and favoured the alternative \"whole tile area stored\", 12 of 12, because its observable counted every dword not 0xdeadbeef): with E465's observable the set of stored non-background dwords of the ZLS store is the set x < 1.25 W and y < 1.25 H on 12 of 12 jobs (6 sizes, ramp in x and in y; the centre rule x + 0.5 < 1.25 W is inference, as the sets are the same for the edge forms), 924 on the 34 x 18 control as in E465, 484 at 18 x 18, 1984 at 50 x 26, 3444 at 66 x 34, 7564 at 98 x 50 and 2604 at 34 x 50, with 0 mismatching pixels"
unit = "zls"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** isp-a-guard: 12 jobs, rc 0 and "diff: 0 of N pixels" (the target's own pixels), a
`--tri-full` triangle (0,0), (3W,0), (0,3H) with a depth ramp (x or y), `--depth-dump`, the depth
buffer pre-filled with 0xdeadbeef: 34 x 18 (control, E465), 18 x 18, 50 x 26, 66 x 34, 98 x 50 and
34 x 50, each with the x ramp and the y ramp. The 10 non-control jobs were held out; the rule was
fitted on the 34 x 18 dump of E465 (one size).

**Hypotheses (frozen).** The stored set is {x + 0.5 < 1.25 W and y + 0.5 < 1.25 H} over the tile
area; the alternatives, the target clip and the whole tile area. They differ in 100s to 1000s of
pixels at the sizes chosen so that 1.25 W falls inside the last tile.

**Results as scored by the frozen recompute: 0 of 12 (a scorer defect).** recompute_p1141tex.py
counts a dword as stored when it is not 0xdeadbeef. The store writes the whole tile (2048 dwords
on the control), the pixels outside the band holding the background depth 1.0 (E465: 1124 on the
34 x 18 job), so every dword of the tile area was "stored" and the whole-tile alternative matched
on 12 of 12 and the frozen set on 0. The plan's own control (924 stored on 34 x 18) shows that the
observable meant is "not the background depth", E465's, so the recompute did not reproduce its
control.

**Results with E465's observable (post hoc, post/post_1141tex.py section guard).** [HW] A dword is
stored if it is not 0x3f800000 (1.0f): the set equals the frozen set on 12 of 12 jobs, the counts
above, extent x < 42, 22, 62, 82, 122, 42 and y < 22, 22, 32, 42, 62, 62; 0 dwords 0xdeadbeef
inside any tile area. The control reproduces 924 (612 target + 312 outside).

**Population.** Fitted on one size (E465's 34 x 18, both ramps); the 10 other jobs were not used
to fit it, but the score reported is post hoc: the observable was chosen after the data were read.
The frozen recompute scored the hypothesis 0 of 12 and the declared alternative "whole tile area
stored" 12 of 12 (recompute-report.txt), so under the frozen observable the declared alternative
won. The plan's wording mixed two observables ("control, E: 924 stored", while E465 uses "stored"
for the 2048 dwords that left the fill and "hold the ramp" for the 924), and the frozen script took
the other one. plan.md is not in manifest-1141tex.sha256 and was edited at 14:20:09, after the
manifest (14:18:15), so the intended observable is not hash-frozen. The sha256 of the predicted
set (clip at 1.25 W, 1.25 H) equals the observed set on all 12 jobs (reviewer's own decoder:
every non-1.0, non-deadbeef dword equals the ramp value of its own pixel), so the hypothesis
predicted the right sets; but this is a re-score, not a confirmation.

**What it shows.** [HW] On the sizes run the ZLS store's triangle depth stops at 1.25 times the
target's width and height from the origin; beyond it the dwords hold the background depth. [infer]
The centre test (x + 0.5 < 1.25 W) is not determined: every width is 2 mod 4 and height 2 mod 8, so
x + 0.5 < 1.25 W, x < floor(1.25 W) and x + 1 <= 1.25 W give identical sets on all 12. Q122's rule
(which outside pixels hold the ramp) is this band at these alignments. [infer] a guard band of a
clip at 1.25 of the target, as the earlier report guessed; no clip result was measured.

**What it does not show.** Every width tested is 2 mod 4 and every height 2 mod 8 (1.25 W is x.5
on all of them), so the rounding at 1.25 W with a fraction .25 or .75 (the band's edge at a pixel
centre or a quarter-pixel) is not tested; triangles that do not cover the band; targets that end
on a tile boundary (the band is then outside the tile area); colour output; whether the same band
applies to a triangle's iterated attributes.
