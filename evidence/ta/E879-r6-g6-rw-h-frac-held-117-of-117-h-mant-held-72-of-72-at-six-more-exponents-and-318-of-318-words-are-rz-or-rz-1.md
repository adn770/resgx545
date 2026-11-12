+++
id = "E879"
claim = "R6-pixel stages g6-rwa and g6-rw (Q230, 8 and 106 jobs in E859's shape with every vertex inside the viewport; frozen verdicts 'part a: PASS' and 'H-FRAC PASS (0 RZ + 1 of 117 below 0.5); H-SMOOTH 2^1 mixed, 2^8 cannot tell, 2^16 cannot tell; H-MANT -12: held 12 of 12, -6: held 12 of 12, -3: held 12 of 12, 5: held 12 of 12, 8: held 12 of 12, 12: held 12 of 12; every word is RZ or RZ+1 of 1/w (318 of 318 rows decided)'): H-FRAC held out: of 240 new mantissas (six windows of 36 neighbours at strides 1, 2^8 and 2^16, and 24 near the half ulp), the 117 whose exact 1/w lies less than half an ulp above RZ all stored RZ, and 83 of the 123 above it RZ + 1, the smallest at frac 0.5294; H-MANT held at 72 of 72 words of R4's rw-01, rw-02, rw-10 and rw-12 rerun at the exponents -12, -6, -3, 5, 8 and 12 of w (w from 2.5e-4 to 8027); every one of the 318 words is RZ or RZ + 1 and every job wrote its 3-vertex object; the eight controls exact and the two replicates repeated their six words; how e varies between neighbours is not decided: at stride 1 one window was separable by frac (e in [0.2809, 0.3220)) and the other had 3 inversions, at 2^8 and 2^16 one window each had too few RZ words above 0.5 and the other inversions (the printed '2^1' is the stride-1 pair, a label slip of the frozen scorer)"
unit = "ta"
method = "R6-pixel stages g6-rwa and g6-rw of the question-closing pass, round 6 (decisions R6-2 a and pixel 7 a, plan closing6/pixel/exp-pixel-r6.md section 4, PREFLIGHT.md 3), dataset render-closing-r6-pixel, on the laptop (host cedar, direct cable), 2026-11-12, attempt out/20261112-142113 (g6-rwa started 14:27:21 and g6-rw 14:28:19 Mac time, after p6-rd and p6-l3; run-r6p.log), the boot, module, firmware, tool, freeze and pins of E878 (FROZEN.sha256 e6371195..., FROZEN.commits at d9b2969); knob `stophang s2` on every job (STATUS2 0x400 at every read), a reset before each job, no fault, every job class ok, health ok after each stage, both gates PASS (g6-rwa's: every control word exact, run before g6-rw); no stop, no refreeze and no lead decision during the run. Each job `probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render DIR --slot pixel=pix_green.bin PROGRAM`, R5's g5-rw command byte for byte; programs from bins/ (gen/r6_rw.py, score/rwdesign6.py; R5's template vtx_zws.s, o0 = S x, o1 = S y, w = C x + D, every vertex inside the viewport asserted by the generator): g6-rwa R5's rw-k0 to rw-k5, d-01 and d-02 byte for byte (four of d-01's and d-02's six words are words of E859's dense HELD OUT half, used here as replicate controls, not for a fit); g6-rw L, six windows of 12 jobs (36 mantissas Bw + o s, o in 0 to 41, strides 1, 2^8, 2^16, bases from sha256 of `r6-rw-win-<n>`, disjoint from every mantissa read before), B, 8 jobs whose 24 mantissas have frac in [0.42, 0.62), two replicates of L jobs, and E, R4's four rows with the most RZ + 1 words at S = 2^-12, 2^-6, 2^-3, 2^5, 2^8 and 2^12; predictions frozen in predictions/g6-rwa.tsv and g6-rw.tsv (H-FRAC as E872 froze it, H-SMOOTH per stride with none predicted to hold, H-MANT with R4's deltas); scored by the frozen score/score_r6.py (score/score_rw6.py; R5's and R4's readers pinned; scorekit copied from resgx545); the kept score and gate files of both stages and the verdict lines were reproduced byte for byte at the fold (2026-11-12) by the frozen scorer on the kept files; fold/posthoc_r6.py section C (output fold/posthoc_r6.txt) counts the words by set and lists the new mantissas by frac, a reading at the fold; no model family was declared or fitted at this fold, so E859's dense HELD OUT half stays unread for fits"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-pixel:out/20261112-142113/g6-rwa/", "render-closing-r6-pixel:out/20261112-142113/g6-rw/", "render-closing-r6-pixel:fold/"]
terms = ["PB_OBJ.RHW"]
+++
**What ran.** E872 read H-FRAC on FIT and held it, SEMI, on E859's dense HELD OUT half: a mantissa
M of w whose exact 1/w lies less than half an ulp above RZ (frac(M), the fraction of 2^47 / M,
below 0.5) never stores RZ + 1, the word reading as floor(1/w + e) with 0 <= e < 0.5 ulp
[infer]. g6-rw asks two things held out: does H-FRAC hold on mantissas never read, and how does e
vary between neighbouring mantissas (a window of 36 is "separable" when every RZ + 1 word has a
larger frac than every RZ word, which is what an e constant over the window gives); and, apart, does
H-MANT (the delta follows the mantissa alone, E859) hold at exponents far from -2 to 4. g6-rwa ran
the eight controls first, as a table of its own, so that a failed control stops the session before
g6-rw.

**Results [HW].** Frozen verdicts, printed: g6-rwa "part a: PASS"; g6-rw "H-FRAC PASS (0 RZ + 1 of
117 below 0.5); H-SMOOTH 2^1 mixed, 2^8 cannot tell, 2^16 cannot tell; H-MANT -12: held 12 of 12,
-6: held 12 of 12, -3: held 12 of 12, 5: held 12 of 12, 8: held 12 of 12, 12: held 12 of 12; every
word is RZ or RZ+1 of 1/w (318 of 318 rows decided)"; both gates PASS. From
`out/20261112-142113/score-g6-rw.txt` and `fold/posthoc_r6.txt` section C:

| rows | jobs | words | RZ + 1 | result |
|---|---|---|---|---|
| controls rw-k0 to rw-k5, d-01, d-02 | 8 | | | exact, PASS |
| L, six windows | 72 | 216 | 81 | shape 72 of 72 |
| B, frac 0.42 to 0.62 | 8 | 24 | 2 | shape 8 of 8, smallest RZ + 1 frac 0.5747 |
| replicates of L jobs | 2 | 6 | 3 | their L job's words, 6 of 6 |
| E, 4 rows x 6 exponents | 24 | 72 | 36 | H-MANT 12 of 12 at each exponent |

- H-FRAC on L and B (240 new mantissas): 117 with frac below 0.5, none RZ + 1; 123 above, 83 RZ + 1;
  the smallest frac storing RZ + 1 is 0.5294 (0.583 on E872's FIT set).
- Windows: 1a separable, RZ + 1 from frac 0.7191 and RZ up to 0.6780, so e in [0.2809, 0.3220);
  1b 3 pairs out of order (RZ + 1 from 0.6305, RZ up to 0.6835); 8a 2 pairs out of order; 8b cannot
  tell (18 RZ + 1, 2 RZ above 0.5, the frozen minimum is 4); 16a cannot tell (13 RZ + 1, 2 RZ above
  0.5); 16b 10 pairs out of order. So H-SMOOTH is mixed at stride 1 and cannot tell at 2^8 and
  2^16. The frozen scorer prints the stride-1 entry as "2^1": it names the stride pairs "1", "8",
  "16" and prints "2^" before each name, so "2^1" is stride 1 (2^0); the rows and the verdict are
  those of stride 1, only the label is wrong.
- E: R4's rw-01, rw-02, rw-10 and rw-12 at S = 2^-12 to 2^12 (w from 2.5e-4 to 8027) stored R4's
  delta at 72 of 72 vertices, 36 of them RZ + 1.

With the 196 words known before (E859), 514 words of kept vertices are now known, on 370 mantissas,
every one RZ or RZ + 1; 181 mantissas lie below half an ulp and all store RZ (64 read before H-FRAC
was frozen, 117 held out here).

**What it shows.** H-FRAC holds held out: no mantissa whose exact 1/w lies less than half an ulp
above RZ stores RZ + 1 (117 of 117 new ones, where about 79 would if the delta did not depend on
frac and came at the rate read above 0.5, 83 of 123), so the stored word is RZ below half an ulp at
every mantissa [infer beyond those read], and a simulator can give it there. H-MANT holds at six
more exponents, from 2^-12 to 2^12: the delta is a property of the mantissa. Refuted by: an RZ + 1
word at frac below 0.5, or a read mantissa with the other delta at another exponent (none).

**What it does not show.** Which mantissas above half an ulp store RZ + 1: e is not constant over
the windows that could be scored at strides 1 and 2^8 and 2^16 (inversions in 3 of the 4 windows
scored), and two windows were not scored; a model family for e was not declared at this
fold, and none was fitted, so E859's dense HELD OUT half stays unused for fits. Exponents between
those read other than 3 (-11 to -7, -5, -4, 6, 7, 9 to 11) and beyond them; the 1/w of a clip-made
vertex, the depth formula at w other than 1 and the rest of Q230.
