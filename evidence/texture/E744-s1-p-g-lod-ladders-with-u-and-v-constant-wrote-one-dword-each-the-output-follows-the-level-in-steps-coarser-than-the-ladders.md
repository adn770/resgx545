+++
id = "E744"
claim = "Eight ladders of the LOD fraction over 64 columns, with the sampling coordinates u and v held constant and each ladder spanning 0.031 of a 1/64 level step around n/64 for n = 2, 13, 22 and 56 (two runs each), wrote one constant dword over all 2048 pixels of each job (0xd00001aa, 0xd00004aa, 0xd00006aa, 0xd0000eaa; the repeats equal), so no transition was measured and the frozen verdict is cannot tell, while the control reproduced E721's lf-r8 image hash; read after the run, the constant's bits 8 to 11 (1, 4, 6, 14) follow n coarsely, near n / 4"
unit = "texture"
method = "S1 stage p-g (9 jobs, 5 conditions; paths relative to render/closing-s1/ of the dataset: E721's gradient-sampling program with u and v as constants and the LOD laddered across the columns at a pitch of 1/2048 step, g-ctl-lf-r8 first), a debugfs reset before each, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage; scored by the frozen score/score_s1.py p-g (out/score-p-g.txt); the dwords read after the run (analysis/pixel.md)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/p-g/"]
terms = ["T0.MIPFILTER"]
+++
**What ran.** Q280 asks what makes up to 56 of 2048 pixels of E721's gradient jobs differ from the
Euclidean footprint with a LOD fraction truncated to 1/64. G laddered the fraction around four
boundaries to find the first column that changes against the exact crossing.

**Frozen verdict.** cannot tell: ladders void or without a transition (measured nothing): all
eight; the control's image hash matched E721's (out/score-p-g.txt).

**Results [HW].** One dword per job over every pixel: n = 2 0xd00001aa, 13 0xd00004aa, 22
0xd00006aa, 56 0xd0000eaa, each repeat equal.

**Why: the design [infer].** E721's ladders moved u with the column; here only the fraction moved,
by 0.03 of a 1/64 step in total. No record had shown that a point-sampled raw output changes with
the fraction alone (the preflight flagged it). Post hoc, the output does follow the level, but its
bits 8 to 11 go 1, 4, 6, 14 for n = 2, 13, 22, 56, about n / 4: a resolution nearer 1/16 than 1/64
of a level, which a ladder this narrow cannot cross except by chance.

**Not shown.** The precision of the LOD fraction in the footprint; where the output's steps lie.
