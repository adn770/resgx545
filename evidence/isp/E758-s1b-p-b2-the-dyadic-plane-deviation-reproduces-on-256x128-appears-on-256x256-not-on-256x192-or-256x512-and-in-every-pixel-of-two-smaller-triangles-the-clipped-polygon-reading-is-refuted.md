+++
id = "E758"
claim = "The lower-binade deviation of the dyadic depth plane of E731 (A = 1/8192, B = 0, depth 0.125 at two vertices and 0.1875 at the third, stored minus truncated exact plane, the cleared 1.0 excluded) reproduced exactly on 256 x 128 (the control, 2 of 2 runs: 7680 pixels at -1 ulp and 1536 at -2, the set of dp-ax-b2) and was absent on the target 256 x 192 (0 of 49152 covered pixels), present on 256 x 256 (18528 of 65536: 13920 at -1 and 4608 at -2) and absent again on 256 x 512 and with the triangle moved by (64, 32) (the two repeats, 0 deviating pixels), and a smaller triangle of the same plane (vertices at 448 and at 384 pixels) deviated at every one of the 32768 covered pixels of 256 x 128 (-5 to -1 ulps); the frozen verdict: held out: no hypothesis consistent, HT (the region is tied to target coordinates) refuted in 4 of 4, HV (tied to the triangle) in 2 of 2 and HCLIP (the plane is set up from the clipped polygon in the parameter buffer: a job deviates iff its stored polygon is not the original triangle) in 1 of 4; as repeats HT and HV 2 of 2 and HCLIP 2 of 3"
unit = "isp"
method = "S1b stage p-b2 of the question-closing pass (8 jobs: tri --keep-overflow --wait-ms 20000 --tri-v and --tri-z with vertices in 1/256 pixel, --depth --depth-ctl 0x17103c --depth-fill 0xdeadbeef --depth-dump --depth-pages N --poke blk:1=0x00400200 and --dump-render so that the parameter buffer and the TA data of each job are kept; paths relative to render/closing-s1b/ of the dataset: d-ctl and d-ctl-r2 256 x 128 with the triangle (0,0), (131072,0), (0,131072), d-shift the same moved by (64, 32), d-t192 256 x 192, d-t256 256 x 256, d-tall 256 x 512, d-L448 and d-L384 256 x 128 with the legs 114688 and 98304 and the depth 0.1796875 and 0.171875 at the far vertices, which keeps A = 1/8192), a debugfs reset before each job, run 1794266037-20117 on 2026-11-10 00:14 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); tables, predictions (the bit sets p-b2-set-ctl, -ht_shift and -hv_shift among them), scorer, generator and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256; verified before the stage and before scoring); the deviation is stored minus the float32 truncation of the exact plane (gen/b2model.py, with the fix that the clear 1.0 is not covered), the stored polygon is decoded from each job's own parameter buffer dump; verdict by the frozen score/score_s1.py p-b2 (out/score-p-b2.txt, reproduced on the kept files)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/p-b2/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E741 (S1) found E731's region on the 256 x 128 target and no deviation with the
triangle moved or on a taller target, once the scorer's count of the clear value was fixed by
hand, and left one untested candidate, a plane set up from the clipped polygon. S1b froze three
hypotheses and ran new targets and triangles: HT (the region is fixed in target coordinates), HV
(it moves with the triangle), HCLIP (a job deviates iff the polygon the TA stored is a clipped one,
and two jobs with the same stored polygon deviate alike). The scorer's coverage no longer counts the
clear 1.0 (the S1 defect behind E740 and E741's empty verdict). d-ctl must reproduce dp-ax-b2;
d-shift and d-tall are repeats of S1 jobs (S1 post hoc: no deviating pixel) and are scored as
repeats, never held out; d-t192, d-t256, d-L448 and d-L384 are new.

**Frozen verdict.** control reproduces dp-ax-b2; held out: consistent none, refuted ['HT
(target-tied) (4 of 4)', 'HV (vertex-tied) (2 of 2)', 'HCLIP (S1 post hoc: plane from the clipped
polygon) (1 of 4)']; repeat only: consistent ['S1 post hoc (no deviating pixel) (2)'], refuted ['HT
(target-tied) (2 of 2)', 'HV (vertex-tied) (2 of 2)', 'HCLIP (S1 post hoc: plane from the clipped
polygon) (2 of 3)'] (out/score-p-b2.txt). The line "same stored polygon: d-ctl and d-ctl-r2: maps
equal in the 256 x 128 window" is the control pair and counts as a repeat entry of HCLIP.

**Results [HW].** All eight jobs rc 0, `tri: 1 renders ok`, `diff: 0` (the colour image exact).
Deviations by job (ulps: pixels), the stored object from the parameter buffer:

| job | target | deviating | histogram | stored object (pixels) |
|---|---|---|---|---|
| d-ctl, d-ctl-r2 | 256 x 128 | 9216 | -2: 1536, -1: 7680 | 4 vertices, (0,0) (0,160) (320,0) (320,160) |
| d-shift | 256 x 128 | 0 | none | 4 vertices, (64,32) (64,160) (320,32) (320,160) |
| d-t192 | 256 x 192 | 0 | none | 5 vertices (clipped), ends (320,192) |
| d-t256 | 256 x 256 | 18528 | -2: 4608, -1: 13920 | 5 vertices (clipped), (0,320) (192,320) |
| d-tall | 256 x 512 | 0 | none | 4 vertices, (0,512) (320,192) |
| d-L448 | 256 x 128 | 32768 | -5: 1024, -4: 7680, -3: 16685, -2: 5376, -1: 2003 | 5 vertices |
| d-L384 | 256 x 128 | 32768 | -5: 1024, -4: 6116, -3: 17000, -2: 6570, -1: 2058 | 5 vertices |

In d-ctl the per-tile-row counts (16 rows) are 0, 0, 256, 768, 1280, 1792, 2304, 2816, as E731 and
E741. In every job the stored polygon is a clipped one (never the original three vertices), so
HCLIP's "deviates iff clipped" predicted a deviation in all eight and failed on d-shift, d-tall
and d-t192; its second clause (equal stored polygons, equal maps) held for the control pair only.
HT, which predicted d-ctl's set inside the 256 x 128 window for every target, failed on the four
new jobs (none for d-t192, a different set for d-t256, every pixel for d-L448 and d-L384). HV
predicted d-ctl's set for d-t192 and d-t256 as well (the triangle is not moved there) and failed on
both. d-shift and d-tall reproduced S1's "no deviating pixel" (the repeat support the
scorer prints).

**Post hoc (read after the run, [infer], not held out).** On 256 x 256 the deviating set is
exactly the covered pixels with x + y >= 319 (0 of 65536 pixels differ), and on 256 x 128 exactly
those with x + 2y >= 319 (E731, E741); the per-tile-row counts of d-t256 are 0, 0, 0, 0, 136, 392,
648, 904, ... in steps of 256, those of d-ctl in steps of 512. In d-L448 and d-L384 every covered
pixel deviates and by up to five ulps, against two for the larger triangle. By target height (128:
region; 192: none; 256: region; 512: none) the presence is not monotone in the target's size, and
the same dyadic plane deviates by up to five ulps when the triangle is smaller. A rule in the plane
set-up from the vertices of the stored polygon is not excluded by these jobs, only the one frozen
as HCLIP (the criterion "clipped or not"): the stored polygon of d-t192 and of d-t256 both have
five vertices.

**Caveats.** The scorer reads a deviation against the float32 truncation of the exact plane in
the 256 x 128 window for HT and HV, so a deviation outside that window (d-t256's rows 128 to 255)
is not in the frozen test of those two. HV and HT make the same prediction (d-ctl's set) for every
job that is not moved, so the two held-out HV entries add nothing to HT's. d-L448 and
d-L384 change the vertices, the legs and the depth gradient's offset together with the polygon, so
what in them carries the extra ulps is not separated.

**Not shown.** The arithmetic of the plane; why x + 2y at 128 rows and x + y at 256; what decides
the presence at 192 and 512 rows; the region on other binades.
