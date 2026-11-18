+++
id = "E1144"
claim = "r35-sa stage a (40 jobs, t30 probe fills with --pixels, module 7CE8E38E): every control passed, the position decode on K3 and on --coords' (y << 16) | x and the sa5 reader form included; a fill whose pixel task writes sa_n (n = 0 to 15) with iaddu32 outputs the written value at exactly 4 pixels and K1 at the other 2044 (H-FOUR 21 of 21 held-out rows), the same 4 pixels in both replicates (H-VAR 0 of 6), and a writer of sa1, sa5 and sa7 shows the union of the three single writers' 12 pixels (H-UNION 2 of 2); the frozen position rules failed (H-FIXED4 and H-SHIFT, S0 + n d with S0 [0, 16, 512, 528] and d 1 fitted on sa1, 0 of 19); an sa5 written by one job and read after a job that wrote sa1 reads that job's output (H-ONEJOB 2 of 2, H-UNTILWRITE 0 of 2; E484's form reproduced), so an sa lasts one job also across a job that writes another sa; the frozen rule printed 'Q129 RULE: NARROW: clause (b) decided, clause (a) open'; post hoc [infer]: sa_n's 4 pixels are (x, y) = ((n & 1) + 2 (n >> 2) + {0, 16}, ((n >> 1) & 1) + {0, 8}), 29 of 29 position sets"
unit = "usse"
method = "r35-sa (render/closing-r35-sa), stage a of the question-closing pass (round 35: closing29/plan/rank-round35.md sections 1, 3.2 and 3.4, decisions R35-1a, R35-3a and R35-5a, safe class), dataset render-closing-r35-sa; attempt out/20261118-085610 (scores score-a.txt); on the laptop at home (192.168.12.234, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tools ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, built from resgx545 42c4de7) for every probe fill (`probe --temps 32 --pixels FILE`, 64 x 32, 2048 instances, our program as the pixel task, every pixel printed; c1 with `--coords`; stage t's T8 with `--temps 8`) and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the triangle rows and the kit's health pair, every job one process of the kit runner, a debugfs reset before each group's first row, `noreset` elsewhere, 2026-11-18 08:56:11 to 08:59:11; the rows are tables/a.txt, the frozen predictions predictions/a.tsv (gen/make.py), the rule score/score.py's q129 command (fold/q129-rule.out), the score reproduced byte for byte (fold/reproduce-a.out), the post hoc reading fold/posthoc.py (fold/posthoc.out)); freezes: FROZEN.sha256 067f55e6181ae21a79f1482a95e0d7884e1b654f761dda1f292b7f8d882764df (89 files), PREDICTIONS.sha256 a041ca6a036edb5f77bc2db3f8d3d675e9064c0a67d8b950f9b22566fd13d722 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at eea6d2ab, resgx545:tools/closing/kit/lib_kit.sh at eea6d2ab, resgx545:tools/closing/kit/run_stage.sh at eea6d2ab, resgx545:tools/closing/kit/kitscore.py at eea6d2ab, resgx545:tools/closing/kit/fake/sudo at eea6d2ab, resgx545:tools/closing/kit/fake/timeout at eea6d2ab, resgx545:tools/closing/kit/fake/df at eea6d2ab, resgx545:tools/closing/kit/fake/modinfo at eea6d2ab, resgx545:tools/closing/kit/fake/sha256sum at eea6d2ab, resgx545:tools/closing/kit/fake/tool.sh at eea6d2ab, resgx545:tools/closing/kit/fake/tool.py at eea6d2ab, resgx545:tools/closing/kit/fake/ssh.py at eea6d2ab, resgx545:tools/closing/scorekit.py at eea6d2ab, resgx545:tools/closing/sessioncheck.py at eea6d2ab, data:render/closing-r34-q010/out/20261116-231015/c/begin.fill1.txt.gz at 1f5ebe6b, data:render/closing-r34-q010/out/20261116-231015/c/begin.health1.txt.gz at 1f5ebe6b, 42c4de7855d6f310321cc03fa0780b698a735e4d at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main eea6d2ab8f45; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-18"
data = ["render-closing-r35-sa:out/20261118-085610/a/", "render-closing-r35-sa:fold/"]
terms = []
+++
**What ran.** One stage a of 40 jobs, every probe a t30 fill printing every pixel. A writer W_n
runs `iaddu32.testtaz.chan0 sa_n, p0, r1, r2` (r1 = 1, r2 = M - 1, so M), `mov r3, sa_n`, dword 0
= r3, o0 = K1 0xc0de0a01, with a marker M = 0x5a35RRNN of its own per row (RR the row, NN the sa);
W_157 does it for sa1, sa5 and sa7 (dwords 0-2). X_1 is a W_1 with o0 = K2 0xc0de0a02. R_5 runs
`mov r10, sa5`, dword 0 = o0 = r10 (E1140's form). K writes no sa: o0 = dword 0 = K3 0xc0de0a03.
C outputs pa0 under `--coords`. Groups:

- c0 (K) and c1 (C): the position decode on known pixels; c2 (W_5, R_5): the reader form on sa5;
- f (fit: W_0, W_1, twice each) and h (held out: W_2 to W_15, twice for 2, 3, 5, 7, 15, once for
  the others, and W_157 twice);
- p (W_5, X_1, R_5, twice) and q (W_5, K, R_5, once: E484's form).

The second replicate runs the two-replicate groups in reverse order. Pixel index i = y * 64 + x;
a writer's odd pixels are those that are not K1.

**Frozen verdict (as printed).** fold/q129-rule.out: "Q129 RULE (a): form controls c0, c1 passed; W
rows read 25 of 25; S0 [0, 16, 512, 528], d 1; H-FOUR 25 held, 0 FAILED, 0 cannot tell of 25;
H-OTHERN 0 held, 25 FAILED, 0 cannot tell of 25; H-FIXED4 0 held, 19 FAILED, 0 cannot tell of 19;
H-SHIFT 0 held, 19 FAILED, 0 cannot tell of 19; H-UNION 2 held, 0 FAILED, 0 cannot tell of 2; H-VAR
0 held, 8 FAILED, 0 cannot tell of 8: not decided (neither H-FIXED4 nor H-SHIFT holds on every
held-out sa)"
"Q129 RULE (b): controls 10 of 10 passed; reader form (c2) passed; q (E484's form) reads PREV: yes;
H-ONEJOB 2 held, 0 FAILED, 0 cannot tell of 2; H-UNTILWRITE 0 held, 2 FAILED, 0 cannot tell of 2 on
p: DECIDED, H-ONEJOB"
"Q129 RULE: NARROW: clause (b) decided, clause (a) open".

**Results [HW].** c0 read K3 in 2048 pixels, c1 read (y << 16) | x in 2048 of 2048, c2's readers
read their writer's marker in 2048 of 2048; every kit control passed. Every writer read its
markers back in its dwords and output K1 in 2044 pixels and its marker in 4 (W_157: 2036 and 4
of each of its three markers). The positions, the same in both replicates of every n run twice:

| n | pixels (x, y) |
|---|---|
| 0, 1 | (0, 0), (16, 0), (0, 8), (16, 8); (1, 0), (17, 0), (1, 8), (17, 8) |
| 2, 3 | (0, 1), (16, 1), (0, 9), (16, 9); (1, 1), (17, 1), (1, 9), (17, 9) |
| 4 to 7 | as 0 to 3 with x + 2 |
| 8 to 11 | as 0 to 3 with x + 4 |
| 12 to 15 | as 0 to 3 with x + 6 |

W_157 showed sa1's, sa5's and sa7's single-writer pixels. The p readers read X_1's colour K2 in
2048 pixels (X_1 output K2 in 2044 and its sa1 marker in 4); the q reader read K3 in 2048. No job
failed or hung, and no BIF fault line appeared.

**What it shows.** [HW] A 64 x 32 fill whose pixel task writes sa_n with iaddu32 shows the value
at exactly 4 pixels, the same 4 every run, one per 16 x 8 block of the top-left 32 x 16 pixels,
and writing three sa shows the union. H-SHIFT, a constant step in pixel index, does not hold.
[HW] An sa5 write is replaced by the next job's output even when that job writes another sa
(sa1): an sa lasts one job, E1140's rule for sa0 on sa5. Post hoc [infer] (fold/posthoc.out): n
maps to a pixel of a 2 x 2 quad and a quad in a row of four, x = (n & 1) + 2 (n >> 2), y = (n >> 1)
& 1, repeated at x + 16 and y + 8; it fits 29 of 29 position sets but was formed after the run.

**What it does not show.** Why those pixels show the write (the [infer] of the plan: the sa write
and o0 of those instances name one storage; Q098); whether the post hoc layout holds for sa16
and up or for other sizes; sa written by fewer instances; E484's mov form alone.
