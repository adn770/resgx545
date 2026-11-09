+++
id = "E740"
claim = "Eleven depth ramps on a 1024 x 32 target (a control, a dyadic control and nine ramp jobs, eight non-dyadic gradients with one of them twice) were frozen to give, per job, the joint range of gradients that fits every row with one line; the frozen reader returned no row for any job (EMPTY at row 0), because it counted the cleared depth 1.0 (20496 of 32768 pixels in the control) as covered, so the frozen verdict is cannot tell; read after the run with the clear excluded, the dyadic control fits all 32 rows (16 ulps wide, which the frozen width rule would still call wide), and for the control and every ramp one line fits only over the first 32 to 96 pixels of a row (the control up to 160 and 288 pixels in rows 16 and 31); the same plane stored on this target differs from E731's 256 x 128 dump by one ulp at 167 of 8192 shared pixels"
unit = "isp"
method = "S1 stage p-b1 (paths relative to render/closing-s1/ of the dataset; 11 jobs, 10 conditions: tri with --tri-v and --tri-z on a 1024 x 32 target, a 1024-wide depth buffer of 48 pages, --depth-dump; g-ctl and g-dyadic first), a debugfs reset before each, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage; scored by the frozen score/score_s1.py p-b1 (out/score-p-b1.txt); the corrected reading and the comparison with E731 by analysis/scripts/pixel_b1_*.py, written after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/p-b1/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** Q288 asks which rule gives the stored depth of a plane with a non-dyadic gradient in
x. B1 fitted, per row, the range of gradients g with stored = f(z0 + g x), sixteen candidate rules
placed against the joint range; controls g-ctl (E731's dp-bx-b0 plane) and g-dyadic (every rule
equal to f32 of the gradient).

**Frozen verdict.** cannot tell: controls failed or unusable (g-ctl EMPTY, g-dyadic EMPTY)
(out/score-p-b1.txt).

**Results [HW].** 11 jobs rc 0, a 49152-dword depth dump each; in g-ctl the store wrote 1.0 at 20496
pixels the triangle does not cover. g-r2 and its repeat are byte-identical.

**Why: the scorer, then the design [infer].** The row reader treats every dword other than the
background and 0 as covered, so every row mixes the plane with 1.0 and no line fits: all 11 jobs
empty at row 0. With 1.0 excluded (post hoc): g-dyadic fits all 32 rows with a 16-ulp range, every
rule inside, still "wide" by the frozen 4-ulp rule; g-ctl and all nine ramp jobs still empty by the
row fit (a tile-segment fit of 32 pixels, joint over rows, is empty for all of them but g-r7, whose
joint range is 963 ulps wide: uninformative). One line holds only over the first 32 to 96 pixels of
a row (one to three tiles; the control 160 and 288 in rows 16 and 31); tile starts drift about -0.08
ulp a tile against the exact plane. The control's premise came from E731's 256 x 128 target, and the
same plane here differs from that dump by +-1 ulp at 167 of 8192 shared pixels: the stored depth of
one plane depends on the target, so a row-wide fit does not carry between targets.

**Not shown.** The rule Q288 asks for.
