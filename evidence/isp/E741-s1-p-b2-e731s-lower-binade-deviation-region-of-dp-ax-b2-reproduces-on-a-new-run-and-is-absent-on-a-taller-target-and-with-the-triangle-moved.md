+++
id = "E741"
claim = "E731's deviation of the stored depth below trunc32 of the exact plane in dp-ax-b2 reproduced on a new run as the frozen control, pixel for pixel (7680 pixels at -1 ulp and 1536 at -2, exactly those with x + 2y >= 319 on the 256 x 128 target); the frozen verdict on the held-out jobs is cannot tell (d-shift matches neither the target-tied nor the triangle-tied set), because the frozen deviation reader counted the cleared depth 1.0 as covered; read after the run with the clear excluded, the triangle moved by (64, 32), the same triangle on a 256 x 512 target (also in the 128 rows it shares with the control) and a y gradient on 256 x 512 deviate at no pixel, and z0 = 0.0625 deviates at the same 9216 pixels by -1 to -3 ulps"
unit = "isp"
method = "S1 stage p-b2 (5 jobs; paths relative to render/closing-s1/ of the dataset: tri with --tri-v and --tri-z, --depth with a 256-wide depth buffer, --depth-dump; d-ctl first), a debugfs reset before each, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage with the two region sets (predictions/p-b2-set-*.bits); scored by the frozen score/score_s1.py p-b2 (out/score-p-b2.txt, gen/b2model.py); the corrected reading by analysis/scripts/pixel_b2_posthoc.py, written after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/p-b2/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** Q200 asks for the arithmetic that stores a plane's depth below the exact value. E731
found the deviation of dp-ax-b2 confined to x + 2y >= 319 although the plane has no y term. Frozen:
HT (the region is tied to target coordinates) and HV (tied to the triangle), sets per job; the
control d-ctl must reproduce 7680 at -1 and 1536 at -2.

**Frozen verdict.** control reproduces dp-ax-b2; cannot tell: d-shift matches neither set (Jaccard
0.000 against both) (out/score-p-b2.txt).

**Results [HW].** d-ctl: 7680 pixels at -1 ulp, 1536 at -2, per tile row 0, 0, 256, 768, 1280,
1792, 2304, 2816, the line x + 2y >= 319: E731's set exactly. d-shift leaves 14336 pixels at the
clear value 1.0, d-tall and d-ygrad 32896.

**Why the held-out verdict is empty: the scorer [infer from the frozen code].** The reader takes
every dword other than the background and 0 as covered, so the cleared 1.0 pixels enter with
"deviations" of 57 to 118 million ulps and fill the observed set.

**Post hoc [infer].** With 1.0 excluded: d-shift (18432 covered pixels), d-tall and d-ygrad have no
deviating pixel; d-tall has none in rows 0 to 127 either, where it repeats d-ctl's geometry. d-b3
deviates at d-ctl's 9216 pixels, 4608 at -1, 3072 at -2, 1536 at -3. So the region follows neither
target coordinates nor the triangle alone; it appears with this triangle on this target. One
untested candidate: the plane is set up from the clipped polygon, whose vertices change with the
target and the move. A frozen run with those hypotheses and the parameter-buffer dump confirms.

**Not shown.** The arithmetic; why x + 2y; the region on other targets.

**Correction 2026-11-10:** S1b's p-b2 (E758) tests the candidate left untested above and extends the
target dependence. The plane set up from the clipped polygon (HCLIP) is refuted: in the frozen
held-out rows 1 of 4, in the repeat rows 2 of 3, target-tied (HT) 4 of 4 and triangle-tied (HV) 2 of
2. The control reproduced 7680 pixels at -1 ulp and 1536 at -2 on 256 x 128 (2 of 2); the dyadic
plane deviates on 256 x 256 (18528 of 65536 pixels) and not on 256 x 192, not on 256 x 512 and not
with the triangle moved by (64, 32) (0 deviating pixels each), and two smaller triangles of the same
plane deviated at all 32768 covered pixels of 256 x 128 (-5 to -1 ulps). 'It appears with this
triangle on this target' is therefore refined: it is present on the 128 and 256 row targets and
absent on 192 and 512, with no one of the three readings fitting.
