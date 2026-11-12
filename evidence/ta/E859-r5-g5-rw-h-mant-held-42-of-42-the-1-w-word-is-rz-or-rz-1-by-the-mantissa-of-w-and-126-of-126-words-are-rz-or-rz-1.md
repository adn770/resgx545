+++
id = "E859"
claim = "R5-pixel stages g5-rwa and g5-rw (Q230, 12 and 36 jobs in E842's shape with every vertex inside the viewport; frozen verdicts 'part a: PASS' and 'H-MANT held: 42 of 42 m words equal R4's delta at another exponent; every word is RZ or RZ+1 of 1/w (126 of 126 rows decided)'): whether the stored 1/w of a kept vertex is RZ of 1/w or one ulp above follows the mantissa of w: E842's 14 triangles rerun with every w halved (7 jobs) or multiplied by four (7 jobs) stored R4's delta at all 42 vertices (11 RZ + 1), held out, and the replicates of two of them the same six words; the six quarter-scaled triangles E842 lost at the guard band, now scaled to stay inside the viewport, wrote 3-vertex objects whose 18 words (w 0.254 to 0.443) are RZ or RZ + 1 (3 RZ + 1), the 4 of them at a mantissa read before equal to it; a dense table of 60 new mantissas (w 0.254 to 7.54, 20 jobs) is RZ or RZ + 1 at all 60 (8 RZ + 1), split FIT / HELD OUT by a frozen hash for a later fit; the six controls exact; read post hoc over all 196 words now known, none of the 47 mantissas read at two or more exponents shows both RZ and RZ + 1, and which mantissas store RZ + 1 has no rule"
unit = "ta"
method = "R5-pixel stages g5-rwa and g5-rw of the question-closing pass, round 5 (decisions R5-3 a, pixel 4 a and 5 a, plan closing5/pixel/exp-pixel-r5.md section 4, PREFLIGHT.md 3 and 7.1), dataset render-closing-r5-pixel, on the laptop (host cedar, direct cable), 2026-11-12, attempt out/20261112-091752 (g5-rwa started 09:22:58 and g5-rw 09:24:16 Mac time, after p5-o4; run-r5p.log), the boot, module, firmware, tool and freeze of E858 (FROZEN.sha256 b4ea4eca..., FROZEN.commits at f0d5b39); knob `stophang s2` on every job (STATUS2 0x400 at every read), a reset before each job, no fault, every job class ok, health ok after each stage, both gates PASS (g5-rwa's: every control word exact and fewer than three q jobs FAILED shape, run before g5-rw's 36 jobs); no stop and no lead decision during the run; the /tmp condition and the check of the kept files as E858. Each job `probe --temps 8 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render DIR --slot pixel=pix_green.bin PROGRAM`, R4's g4-rw command byte for byte; programs from bins/ (gen/r5_rw.py, score/rwdesign5.py): rw-k0 to rw-k3, rw-07 and rw-10 R4's own programs (vtx_zw.s), the rest from the new template vtx_zws.s (o0 = S x, o1 = S y, w = C x + D), every vertex inside the viewport asserted by the generator; predictions frozen in predictions/g5-rwa.tsv and g5-rw.tsv; scored by the frozen score/score_r5.py (score/score_rw5.py; R4's rwdesign.py and score_rw.py decode, pinned; scorekit copied from resgx545); the kept score and gate files of both stages and the verdict lines were reproduced byte for byte at the fold (2026-11-12) by the frozen scorer on the kept files; fold/posthoc_r5.py section C (output fold/posthoc_r5.txt) groups every word known by the mantissa of w, a post hoc reading at the fold; no fit family was declared at the fold, so the dense table's FIT and HELD OUT halves are both unused"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-pixel:out/20261112-091752/g5-rwa/", "render-closing-r5-pixel:out/20261112-091752/g5-rw/", "render-closing-r5-pixel:fold/"]
terms = ["PB_OBJ.RHW"]
+++
**What ran.** E851 read H-MANT post hoc from E842's words: whether the stored 1/w is RZ of 1/w or
one ulp above (RZ + 1) is a function of the 23-bit mantissa of w alone. g5-rw tests it held out
and reads the 18 words E842 lost. The vertex program scales x and y by S (o0 = S x, o1 = S y), so
every vertex of every job stays inside the viewport at any w (the generator asserts it; the same
check flags exactly E842's six lost jobs). The rows, as two job tables so that the controls gate
the rest: g5-rwa, six controls (R4's rw-k0 to rw-k3 and two new ones at w 0.3 and 0.7 with known
words) and q-15 to q-20 (E842's quarter-scaled jobs at S 1/4); g5-rw, m-01 to m-07 (E842's
rw-01 to rw-07 with every w halved) and m-08 to m-14 (rw-08 to rw-14 with every w times four),
the replicates rw-07 and rw-10, and d-01 to d-20, 60 new mantissas at scales 1/4 to 4 with a FIT /
HELD OUT split fixed by a frozen hash. Frozen per job: an object of 3 vertices at the window 32 +
32 S x / w, depth 0x3f000000, every word RZ or RZ + 1; H-MANT held iff the controls pass and all
42 m words equal R4's delta at the same mantissa.

**Results [HW].** Frozen verdicts, printed: g5-rwa "part a: PASS", g5-rw "H-MANT held: 42 of 42 m
words equal R4's delta at another exponent; every word is RZ or RZ+1 of 1/w (126 of 126 rows
decided)"; both gates PASS. From `out/20261112-091752/score-g5-rw.txt`:

| rows | jobs | words | RZ + 1 | w | result |
|---|---|---|---|---|---|
| controls rw-k0 to rw-k5 | 6 | | | | exact, PASS |
| q-15 to q-20 | 6 | 18 | 3 | 0.254 to 0.443 | shape 6 of 6, RZ or RZ + 1 18 of 18, H-MANT 4 of 4 |
| m-01 to m-14 | 14 | 42 | 11 | 0.516 to 31.4 | shape 14 of 14, H-MANT 42 of 42 |
| replicates rw-07, rw-10 | 2 | 6 | 3 | 1.41 to 6.75 | R4's six words, 6 of 6 |
| d-01 to d-20 | 20 | 60 | 8 | 0.254 to 7.54 | shape 20 of 20, RZ or RZ + 1 60 of 60 |

Eleven of the 42 m words are RZ + 1, so a chance pass of H-MANT was out of reach (the plan's
reason for the row). With E842's 42, the earlier 23 and the five RZ w that sgx-pipe listed from
E782, E783, E795 and E796, 196 words of kept vertices are known: 155 RZ, 41 RZ + 1, none other.

**Read after the run, post hoc (`fold/posthoc_r5.txt` section C) [infer].** The 196 words fall on
130 mantissas; 47 were read at two or more exponents and none of them shows both RZ and RZ + 1. The
exponents of w read are -16 and -9 (E754's 3e-5 and 0.003) and -2 to 4; this run's words are at
-2, -1, 0, 1, 2 and 4. 23 of the 130 mantissas store RZ + 1; nothing here says which.

**What it shows.** The delta between the stored 1/w and RZ of 1/w is set by the mantissa of w:
42 of 42 held-out words at another exponent repeat it, and the replicates repeat E842's words. The
1/w word is RZ or RZ + 1 at w below 1 too (63 of the 126 words, w from 0.254). So a
simulator can give the word for a w whose mantissa was read, at the exponents run [infer beyond the
pairs read]; sgx-pipe takes the 130 mantissas as a table and refuses the rest. Refuted by: a word
of a read mantissa at another exponent with the other delta (none of 42 held out, none of 47 post
hoc).

**What it does not show.** Which mantissas store RZ + 1, by what algorithm (no family was declared
at this fold: E851's 225 frozen models and 32000 explored ones fit none of the earlier words; the
dense table's halves wait for a declared family); the word at exponents outside -2 to 4 other than
the two read; the 1/w and depth of a clip-made vertex and the depth formula at w other than 1
(Q230).
