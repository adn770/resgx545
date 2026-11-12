+++
id = "Q296"
question = "which mantissas of w whose exact 1/w lies half an ulp or more above RZ of 1/w store RZ + 1 as a kept vertex's 1/w word (106 of the 189 read do, 0 of 512703 declared table-plus-Newton and binary32 models fit, the offset e of floor(1/w + e) not constant over windows of 36 neighbouring mantissas, E872, E879), and is the word the same at the exponents of w not read"
unit = "ta"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E754", "E782", "E783", "E795", "E796", "E798", "E842", "E851", "E859", "E872", "E879"]
terms = ["PB_OBJ.RHW"]
+++

Split 2026-11-12 from Q230 (round 7 housekeeping, decision R7-1 a; ranking
`closing7/rank/rank-round7.md` section 5): the 1/w clause, numeric and offline-fittable, so it can
retire when a rule is found while Q230's geometry clauses stay open. Q230's line held it as "the
rule of the 1/w word of a vertex with w other than 1 (RZ of 1/w or one ulp above it in 514 of 514
words of kept vertices, w from 3e-5 to 8027; which of the two follows the mantissa of w alone, held
out 42 of 42 at other exponents, E859, and 72 of 72 at the exponents -12, -6, -3, 5, 8 and 12,
E879; a mantissa whose exact 1/w lies less than half an ulp above RZ stores RZ, 181 of 181, 117 of
117 held out, H-FRAC, E872, E879; which of the 189 mantissas read above half an ulp store RZ + 1,
106 of them, has no rule: 0 of 512703 declared table-plus-Newton and binary32 models fit, E872, and
the offset e of floor(1/w + e) is not constant over windows of 36 neighbouring mantissas at strides
1, 2^8 and 2^16, E879)". Q230's notes up to 2026-11-12 keep the history of the clause (E754 to
E879).

Known: the word of a kept vertex is RZ of 1/w or RZ + 1 (514 of 514); which one follows the
mantissa of w alone (H-MANT, 114 of 114 held out at other exponents); below half an ulp it is RZ
(H-FRAC, held out). [infer] The word is floor(1/w + e) with 0 <= e < 0.5 ulp and e not smooth in
the mantissa. The 1/w of a clip-made vertex and under a clamp stay with Q230.

To settle it: a family declared from the windows' reading before it is fitted on the dense table's
FIT half and scored on its HELD OUT half (still unused for fits), then words at the exponents
between and beyond those read. sgx-pipe gives RZ below half an ulp and the table of read mantissas
above it, at the exponents read, and refuses the rest (this question).
