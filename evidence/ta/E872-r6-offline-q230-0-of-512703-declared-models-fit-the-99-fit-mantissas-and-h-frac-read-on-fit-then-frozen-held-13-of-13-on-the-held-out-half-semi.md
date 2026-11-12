+++
id = "E872"
claim = "Offline fit and test on E859's kept 1/w words (Q230; no new job): the fit E859 left undone was run on the FIT mantissas only (every mantissa read except the 30 of the dense table E859's frozen hash marked HELD OUT; 99 with w = 1 left out, 15 RZ + 1): 0 of 512703 models declared before the run fit all 99 (family A, fixed-point table plus one or two Newton steps with truncated products, 511056; B, binary32 compositions, 1539; C, RZ of 1/w with w cut to 12 to 23 bits, 108; best of B and C 89 of 99, 'always RZ' 84); then H-FRAC, read on FIT ('a mantissa M whose exact 1/w lies less than half an ulp above RZ, the fraction of 2^47 / M below 0.5, never stores RZ + 1': 0 of 51 FIT mantissas below 0.5 do, the 15 RZ + 1 at 0.583 to 0.995), was frozen with a hash before its script ran and held on the HELD OUT half: 13 mantissas below 0.5, 8 RZ + 1, none of them below 0.5 (chance 0.0042 if the delta were independent of the fraction); SEMI, not held out: the planner had read the 130 deltas unlabelled in E859's fold output before the freeze; read as the stored word being floor(1/w + e) with 0 <= e < 0.5 ulp and e not smooth in the mantissa [infer]"
unit = "ta"
method = "Offline, 2026-11-12, round 6 planning and fold of the closing pass (plan closing6/pixel/exp-pixel-r6.md section 3, user decision R6-1 a: land the offline results before any freeze), no laptop, no job; standard-library scripts in closing6/pixel: rw6_data.py loads the 1/w words of kept vertices from E842's out/20261111-210423/score-g4-rw.txt (render-closing-r4-pixel), E859's out/20261112-091752/score-g5-rwa.txt and score-g5-rw.txt (render-closing-r5-pixel) and the earlier w transcribed from E859's fold/posthoc_r5.py section C (E754, E782, E783, E795, E796, E798), and never parses the word of a row of score-g5-rw.txt that E859's frozen split (score/rwdesign5.py split(), column half) marked HELD OUT; rw6_fit.py (output rw6_fit.out) declares its families in its docstring and code, hashed with rw6_data.py in rw6_fit.sha256 (2026-11-12T11:22:30Z, the planner's own record of the time; a shift bug was fixed before any score was printed, the hash is of the fixed script), and scores them on FIT; its step 2 (HELD OUT) runs only if a model fits all of FIT and did not run; rw6_look.py (rw6_look.out) lists the FIT mantissas by the fraction of 2^47 / M, a reading after the data; the prediction for H-FRAC, with its cannot-tell rule (at least 3 RZ + 1 and at least 8 mantissas below 0.5), was written to rw6_hfrac.predictions.txt and hashed with rw6_hfrac.py, rw6_data.py and rw6_look.out in rw6_hfrac.sha256 (2026-11-12T11:23:33Z) before rw6_hfrac.py ran once on HELD OUT, printing counts only; disclosure (plan section 3): before the freeze the planner had read E859's fold/posthoc_r5.txt, which prints all 130 mantissas with their deltas without the FIT / HELD OUT label, and computed nothing on a HELD OUT mantissa, so the H-FRAC test is SEMI, not held out; rw6_sepchance.py (rw6_sepchance.out) sizes the next run's windows and is not a result; every script re-run at the fold from its published copy (cited/closing6/pixel in resgx545-data) with output byte-identical to the kept .out files, and the hashes of the published rw6_fit.py, rw6_data.py, rw6_hfrac.py, rw6_hfrac.predictions.txt and rw6_look.out equal the frozen ones"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r4-pixel:out/20261111-210423/", "render-closing-r5-pixel:out/20261112-091752/", "render-closing-r5-pixel:fold/", "cited-scratch:closing6/pixel/"]
terms = ["PB_OBJ.RHW"]
+++
**What was read.** E859 held H-MANT out (whether the stored 1/w of a kept vertex is RZ of 1/w or
one ulp above, RZ + 1, follows the mantissa of w) and left a dense table of 60 new mantissas split
FIT / HELD OUT by a frozen hash for a fit declared later; no family was declared at its fold. Here
the FIT set is every mantissa read except the 30 HELD OUT ones of that table: 100 mantissas, all
explored before (E851, E859's section C), 99 with w = 1 left out, 15 of them RZ + 1. The loader
does not parse a HELD OUT word, so the fit cannot see those deltas.

**Results [HW], the fit (`closing6/pixel/rw6_fit.out`).** Target per mantissa M (w = M / 2^23):
floor(2^47 / M) + delta, the stored mantissa. Families declared before the run:

| family | what | models | fit 99 of 99 |
|---|---|---|---|
| A | table plus 1 or 2 Newton steps, truncated products | 511056 | 0 |
| B | binary32 compositions, every rounding | 1539 | 0 |
| C | RZ of 1/w' with w cut to 12 to 23 bits | 108 | 0 |

A: table indexed by 4 to 10 bits, three table points, three entry roundings, products
truncated to 24 to 36 bits, exact or one's-complement 2 - v, two final cuts. B: reciprocal of
reciprocal, one Newton step from a p-bit quotient in three forms. None of 512703 fits; the best
of B and C match 89 of 99 against 84 for "always RZ". Step 2 had no model to score and did not
run, so the HELD OUT half was not used by the fit. A blind search has now failed three times
(E851's 225 frozen and 32000 explored models, and these).

**Results [HW], H-FRAC (`rw6_look.out`, `rw6_hfrac.out`).** With frac(M) the fractional part of
2^47 / M (how far the exact 1/w lies above RZ, in ulp of the stored word), on FIT: 0 of 51
mantissas with frac below 0.5 store RZ + 1; the 15 RZ + 1 have frac 0.583 to 0.995, by decile
from 0.5: 1 of 13, 2 of 11, 2 of 8, 3 of 9, 7 of 8. Frozen (`rw6_hfrac.predictions.txt`, sha256
a1424db9...): "no HELD OUT mantissa with frac < 0.5 stores RZ + 1", held iff the count is 0 with at
least 3 RZ + 1 and at least 8 mantissas below 0.5. Printed once on HELD OUT: 30 mantissas, 13
below 0.5, 8 RZ + 1, 0 of them below 0.5, chance 0.0042 if the delta were independent of frac,
"H-FRAC: HELD". Reported, not scored: RZ + 1 at 2 of 7 in [0.5, 0.75) and 6 of 10 in [0.75, 1).

**Label.** SEMI. The prediction was read on FIT and frozen, with its script, before the one count
on HELD OUT, and nothing was computed on a HELD OUT mantissa before; but the planner had read E859's
`fold/posthoc_r5.txt`, which prints all 130 deltas without the half they belong to, before the
freeze. With the 64 mantissas below 0.5 of both halves, all RZ, the rule is well supported; it is
not a clean held-out result.

**What it shows.** No table-plus-Newton or binary32 model of the declared families gives the
words. Every mantissa read whose exact 1/w lies less than half an ulp above RZ stores RZ (64 of
64). Read [infer]: the stored word is floor(1/w + e) with 0 <= e < 0.5 ulp, or a round to nearest
of an under-estimate; the bound 0.5 is the FIT set's own cut, the smallest frac read with RZ + 1
being 0.583. e is not smooth across the table (on FIT, e < 0.06 at 1.0625, e >= 0.42 at 1.0696, e
>= 0.09 at 1.09375). Refuted by: one RZ + 1 word at a mantissa with frac below 0.5 (none of 64).

**What it does not show.** Which mantissas with frac of 0.5 or more store RZ + 1 (e(M) >= 1 -
frac(M)): no rule. How e varies between neighbouring mantissas, and on what scale (the plan's
windows of stage g6-rw). Exponents outside -2 to 4, the made vertex's 1/w and the depth formula
(Q230). The HELD OUT half has now been used once, for counts: a second use for a variant of H-FRAC
would not be held out; it stays unread for a declared model fit. sgx-pipe does not take H-FRAC as
a rule for unread mantissas (decision 6 of the plan: after g6-rw).

**Correction 2026-11-12:** (adds a reading; the claim stands.) "What it does not show" says
sgx-pipe does not take H-FRAC until g6-rw has run. g6-rw ran (E879): of 240 mantissas never read
before, the 117 whose exact 1/w lies less than half an ulp above RZ all stored RZ, held out, and
83 of the 123 above it RZ + 1. With that, sgx-pipe gives RZ for an unread mantissa below half an
ulp (decision R6-7 a); the windows of neighbouring mantissas did not decide how e varies.
