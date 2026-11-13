+++
id = "E968"
claim = "Round 9 offline (Q078; no run): with T3 bit 14 set, smp on a strided texture reads dword i + K + M c, i the dword the same job reads without the bit and c its column, read on E566's fit job s64x32-t3b14 (W = S = 64: K = 32, M = 64, 2048 of 2048); six rivals for K (W / 2, S / 2, 32) and M (S, W), equal on the fit job, were frozen by hash (q078_b14_rule.json, fbd25356...) before E566's two other bit 14 jobs were read: s64x16-t3b14 (W = S = 64) 2048 of 2048 for all six, and s32x32-t3b14 (W = 32, S = 64) 0 of 2048 for all six, which refutes every one of them where the width is not the stride [HW, held out offline]; post hoc, dword i + floor(S * S * u) with u the sample's coordinate clamped to [0, 1] (R-U01) is exact on all three jobs (2048 of 2048 each), where the ranking's R-U, S * S * (c + 1/2) / W, misses s32x32's 1024 pixels whose u lies past the texture (they read u = 1, not the clamped column's centre) and the unclamped u misses the same 1024 [fitted]; the twiddled job tw32-t3b14 faulted in E566 and kept no image"
unit = "texture"
method = "Offline, no run (round 9, decisions X-1 a (O9-1) and X-6 a; ranking closing9/rank/rank-round9.md finding 1). Data: E566's kept dumps (resgx545-data texture/p1132/tx-t3, the probe's named memory: dword i reads 0xD0000000 | i). The ranking's scripts (closing9/rank/q078_b14_look.py: the per-pixel (column, row) moves on the fit job; q078_b14.py freeze: the six rivals scored on the fit job and written with their sha256, q078_b14_rule.json and .sha256; q078_b14.py score: the held-out jobs, after the hash check) imported the sampler model through resgx545-data texture/p1141/recompute/lib.py, which loads texmodel.py and specs.json from the retired kit path; this fold copied them to closing9/offline/q078/ with the import pointed at the published copies (q078_lib.py: texture/p1141/support/texmodel.py ffa41eb9... and specs.json 2b891d92..., the same bytes as the kit's), re-ran them with the repository's .venv and got q078_b14_fit.out, q078_b14_rule.json, q078_b14_rule.sha256 and q078_b14_score.out byte-identical to the ranking's (the score stops with a TypeError at tw32-t3b14, which kept no image, after the two held-out jobs' lines, as the ranking's did). The ranking's rule, fit and score files carry the same file time (07:13:35): the order freeze then score rests on the script (score checks the hash) and the ranking's account. Post hoc, after the score: closing9/offline/q078/q078_ru.py (standard library) re-derives the ranking's R-U (its q078_b14_post.out kept no script) and adds the raw and the [0, 1]-clamped u (texmodel.ev of the pixel), output q078_ru.out"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["texture-p1132-tx-t3", "cited-scratch:closing9/rank/", "cited-scratch:closing9/offline/q078/"]
terms = ["T3.BIT14"]
+++
**What was done.** E566 set T3 bit 14 on strided textures of 64 x 32, 64 x 16 and 32 x 32 (stride
64 each) and on a twiddled 32 x 32, and saw offsets that change with the pixel (+32 and -32 over
1024 pixels each at 64 x 32) without a rule; the twiddled job faulted. The round 9 ranking read the
fit job s64x32-t3b14 pixel by pixel, declared six rivals for the constant and the column multiplier
that all fit it, froze them by hash and only then scored the two other strided jobs. This fold
re-ran the ranking's scripts from copies whose import points at the published model (byte-identical
outputs) and read the off pixels after the score.

**Results [HW].** Fit (s64x32-t3b14, W = S = 64): every pixel reads its control dword plus 32 plus
64 times its column, 2048 of 2048, so each of the six rivals K in {W / 2, S / 2, 32}, M in {S, W}
fits. Held out (frozen fbd25356...): s64x16-t3b14 (W = S = 64) 2048 of 2048 for all six, which
cannot separate them; s32x32-t3b14 (W = 32, S = 64) 0 of 2048 for all six, all refuted.

**Read after the score [fitted].** On s32x32 the pixels of columns 0 to 31 read i + 128 c + 64 =
i + S * S * (c + 1/2) / W, which is i + S * S * u for the pixel's u (the texel centres here); the
pixels of columns 32 to 63, whose u runs from 1.016 to 1.984 past the texture (the control reads
the clamped column 31 there), all read i + 4096 = i + S * S * 1: the shear takes u clamped to [0,
1], not the clamped column's centre (R-U, the ranking's reading, 1024 of 2048) nor the raw u (1024
of 2048). R-U01, i + floor(S * S * min(max(u, 0), 1)), gives 2048 of 2048 on all three jobs
(`q078_ru.out`); at W = S it is the frozen rule. Read as rows of the stride: the row moves by S u
rows [infer: a shear by the normalised u].

**What it shows.** [HW] Bit 14's read on a strided texture whose width is the stride (64) is the
dword plus 32 plus 64 per column, held out offline on one job; at W = 32, S = 64 none of the six
frozen forms holds. [fitted] R-U01 fits every pixel of the three jobs.

**What it does not show.** R-U01 held out (it was formed on s32x32's pixels): other W != S, a width
that is no power of two, u below 0, and the twiddled texture (E566's job faulted); bits 11 and 12
(Q078; the round 9 session r9-x's stage t3 runs both). The T0 bit 27 clause of Q078 is E723's (a
point sample decodes sRGB to half; the bilinear part is Q282). sgx-sim keeps refusing T3 bit 14.
