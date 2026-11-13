+++
id = "E923"
claim = "Round 8 offline (Q284; no run): the (s, t) of TEXTYPE 2's cube faces under smp3d is the public cube-map table (+x s = -w, t = -v; -x s = +w, t = -v; +y s = +u, t = +w; -y s = +u, t = -w; +z s = +u, t = -v; -z s = -u, t = -v; each over |ma|, texel floor((q + 1) / 2 * 16), the face-local index the Morton interleave with t in bit 0): one rule a face up to the s/t-swap twin of the same index, fitted on E726's eight jobs (16376 of 16384 pixels), frozen by hash (q284_rule.json, 52162471...) and then held out offline on E844's two off-axis jobs, never used for a fit: 2046 and 2044 of 2048; all 14 misses of fit and held out are one texel low at an exact texel boundary with |ma| not a power of two, where 193 such pixels go up, and at the 3043 boundaries with |ma| a power of two the upper texel every time [HW]; the tie rule is not found (post hoc)"
unit = "texture"
method = "Offline, no run (round 8, decisions R8-1 a and R8-4 a; ranking closing8/rank/rank-round8.md finding 1). The ranking's closing8/rank/q284_st.py reads the kept dumps (0xD0000000 | the dword index read, per pixel) of E726's eight cube jobs (resgx545-data texture/p1141 tex-h-cube: cu-xp to cu-zn, cu-w02, cu-w11) and of E844's two off-axis jobs (render/closing-r4-render4x out/20261111-211315/c: c-cube-a, c-cube-b), with each pixel's coordinates as the probe programs compute them (an fmad of (1 + x / 64 or 1 + y / 32) by K plus C, or a constant, exact in f32; p1141-cube.toml and E844's method line). `fit` searched, per face, the 32 rules of which minor axis is s, the two signs, the Morton order (s or t in bit 0) and floor against ceil - 1 on E726's jobs only, kept the best (two rules a face reach it, the s/t-swap twins with the same index), and wrote q284_rule.json with its sha256 in q284_rule.sha256 (52162471d1c80fd1..., file time 2026-11-12 21:46:09); `score` checks the hash and scores fit and held-out jobs (q284_score.out, 21:46:24). Disclosed by the ranking: it had seen the first 19 values of c-cube-a's row 0 while checking the dump format before the freeze; E844's record had published only the faces. Post hoc, after the score: q284_ties.py (the direction at every exact boundary, by |ma| a power of two or not), q284_tievar.py and q284_rcp.py (reciprocal and product RZ or RN in f32). Standard library only; every script re-run in this fold from its published copy (cited/closing8/rank/) with the repository's .venv: the four outputs byte-identical, and `fit` rerun on a copy wrote q284_fit.out and q284_rule.json byte for byte. sgx-pipe's cube::point_index (this fold, the frozen rule with the ties refused) replays the same ten jobs and E844's cu-xn control in crates/sgx-pipe/tests/texture_cube.rs"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["texture-isp-msaa-verification-1141", "render-closing-r4-render4x:out/20261111-211315/c/", "cited-scratch:closing8/rank/"]
terms = ["TEXTYPE"]
+++
**What was done.** E726 found TEXTYPE 2 under smp3d to be six 16 x 16 faces of 256 dwords in the
order +x, -x, +y, -y, +z, -z, and E844 held out the face select (the coordinate of largest magnitude
and its sign); the index inside a face was not decoded. The ranking fitted the face-local (s, t) on
E726's eight jobs alone, froze the rule by hash and then scored E844's two off-axis jobs, whose
three coordinates all differ in magnitude and whose dominant axis changes inside each image. This
fold re-ran every script from its published copy (byte-identical) and wrote a sampler for sgx-pipe
from the frozen rule.

**Results [HW].** Fit (E726): one rule a face reaches the maximum, with its s/t-swap twin (32
candidates a face, exactly 2 at the best, the same index): 2048 of 2048 in each axis job and cu-w11,
2040 of 2048 in cu-w02 (8 misses on +z), 16376 of 16384. Read back, the rule is the public cube-map
table with our u, v, w as x, y, z [infer: the naming]: +x s = -w, t = -v; -x s = +w, t = -v; +y s =
+u, t = +w; -y s = +u, t = -w; +z s = +u, t = -v; -z s = -u, t = -v; each divided by |ma|, texel =
floor((q + 1) / 2 * 16), index = face * 256 + Morton(s, t) with t in bit 0 (E724's "y in the low
bit"). Held out, the frozen rule: c-cube-a 2046 of 2048 (faces -x, -y, +z, -z), c-cube-b 2044 of
2048 (+x, +y, -y, -z): 4090 of 4096. Every miss, 8 fit and 6 held out, is one texel low in s or t at
a pixel whose exact (q + 1) * 8 is an integer, with |ma| not a power of two.

**Read after the score [post hoc].** At every exact texel boundary with |ma| a power of two the
hardware takes the upper texel (3043 of 3043, fit and held out); with other |ma| 193 go up and 14
down (`q284_ties.out`). The 58 distinct (numerator, |ma|) pairs of those boundaries: the 14 down
pixels lie in 6 pairs, all with a positive signed numerator (6 of the 13 positive pairs, none of the
45 at zero or below), and the same |ma| goes both ways (0.625: +0.234375 down, -0.234375 up). A
reciprocal of |ma| rounded RZ or RN and a product rounded RZ or RN fit 51 or 52 of the 58 pairs,
none all (`q284_tievar.out`), and on whole jobs the exact quotient, RN and RZ score alike
(`q284_rcp.out`). sgx-pipe's `cube::point_index` gives the frozen rule and refuses an exact boundary
at a non-power-of-two |ma| (and a face tie, and a face size other than 16): it matches 16228 and
refuses 156 of E726's pixels, matches 4045 and refuses 51 of E844's held-out ones, and matches the
2048 of E844's cu-xn control, with no mismatch.

**What it shows.** [HW] A point sample of a 16 x 16 cube face reads the texel the public cube-map
table gives, with the faces' t in the low bit of the Morton index: frozen on E726 and held out on
4096 pixels of two jobs that took no part in the fit, off by one texel only at exact boundaries.
[infer] The sampler divides by |ma| in an arithmetic that is exact at a power of two and not
otherwise, so an exact boundary at other |ma| depends on a rounding the 58 pairs do not decide.

**What it does not show.** The tie rule (which rounding of 1 / |ma| or of the product, and why the
sign of the numerator matters post hoc), a face tie (|w| = |u|: no job ran one), bilinear filtering
across a face edge, and faces of other sizes (8 x 8, 32 x 32): Q284, narrowed to these, and R8-2's
rows of session r8-geo. The held-out score rests on the ranking's own file times (rule written 15 s
before the score) and its disclosure of the 19 glimpsed values, not on a commit; those 19 were
c-cube-a's row 0, one of 64 rows of one of the two jobs.
