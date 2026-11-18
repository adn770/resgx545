+++
id = "E1145"
claim = "r35-sa stage t (23 jobs, t30 probe fills with --pixels, module 7CE8E38E): every kit control passed, but the frozen reader form control (a fill that reads r20 without writing it, right after a fill that wrote a marker to r20, frozen to read the marker in 2048 of 2048 pixels after E484 and E593) failed on both rows, 2024 pixels at the marker and 24 at 0x0000200f, so every held-out reader is cannot tell and the frozen rule decided no group ('Q193 RULE: NARROW: clause (a) decided for no group of t1, t2, t3, t4'); not a decode error (each reader's pixels agree with its o0 line, the decode passed its controls in stage a): the frozen premise did not hold; post hoc [infer]: every reader read the last r20 writer's marker in 2023 to 2025 pixels, after a colour fill, the t10 triangle and a debugfs reset alike, and values 0x0000n00f or 0x0000n02f in 23 or 24 pixels at even coordinates in two 16 x 8 blocks, at positions that differ from row to row; after a --temps 8 writer of r0-r5, 1388 pixels read its r4 marker and 637 the r20 marker"
unit = "usse"
method = "r35-sa (render/closing-r35-sa), stage t of the question-closing pass (round 35: closing29/plan/rank-round35.md sections 1, 3.2 and 3.4, decisions R35-1a, R35-3a and R35-5a, safe class), dataset render-closing-r35-sa; attempt out/20261118-085610 (scores score-t.txt); on the laptop at home (192.168.12.234, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tools ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, built from resgx545 42c4de7) for every probe fill (`probe --temps 32 --pixels FILE`, 64 x 32, 2048 instances, our program as the pixel task, every pixel printed; c1 with `--coords`; stage t's T8 with `--temps 8`) and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the triangle rows and the kit's health pair, every job one process of the kit runner, a debugfs reset before each group's first row and the t3 readers, `noreset` elsewhere, 2026-11-18 08:59:11 to about 09:01; the rows are tables/t.txt, the frozen predictions predictions/t.tsv (gen/make.py), the rule score/score.py's q193 command (fold/q193-rule.out), the score reproduced byte for byte (fold/reproduce-t.out), the post hoc reading fold/posthoc.py (fold/posthoc.out)); freezes: FROZEN.sha256 067f55e6181ae21a79f1482a95e0d7884e1b654f761dda1f292b7f8d882764df (89 files), PREDICTIONS.sha256 a041ca6a036edb5f77bc2db3f8d3d675e9064c0a67d8b950f9b22566fd13d722 (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at eea6d2ab, resgx545:tools/closing/kit/lib_kit.sh at eea6d2ab, resgx545:tools/closing/kit/run_stage.sh at eea6d2ab, resgx545:tools/closing/kit/kitscore.py at eea6d2ab, resgx545:tools/closing/kit/fake/sudo at eea6d2ab, resgx545:tools/closing/kit/fake/timeout at eea6d2ab, resgx545:tools/closing/kit/fake/df at eea6d2ab, resgx545:tools/closing/kit/fake/modinfo at eea6d2ab, resgx545:tools/closing/kit/fake/sha256sum at eea6d2ab, resgx545:tools/closing/kit/fake/tool.sh at eea6d2ab, resgx545:tools/closing/kit/fake/tool.py at eea6d2ab, resgx545:tools/closing/kit/fake/ssh.py at eea6d2ab, resgx545:tools/closing/scorekit.py at eea6d2ab, resgx545:tools/closing/sessioncheck.py at eea6d2ab, data:render/closing-r34-q010/out/20261116-231015/c/begin.fill1.txt.gz at 1f5ebe6b, data:render/closing-r34-q010/out/20261116-231015/c/begin.health1.txt.gz at 1f5ebe6b, 42c4de7855d6f310321cc03fa0780b698a735e4d at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main eea6d2ab8f45; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-18"
data = ["render-closing-r35-sa:out/20261118-085610/t/", "render-closing-r35-sa:fold/"]
terms = []
+++
**What ran.** One stage t of 23 jobs, every probe a t30 fill printing every pixel. T writes a
marker 0x7e00RR14 of its own to r20 in every instance, dword 0 = r20, o0 = K1 0xc0de0a01. U runs
`mov r10, r20` without writing r20, dword 0 = o0 = r10. T8 (`--temps 8`) writes 0x7e08RR0k to r0
to r5 and outputs K1. Groups: c (T, U, the reader form control, twice); t1 (T, K, U), t2 (T, t10
tri, U), t3 (T, a debugfs reset, U), twice each; t4 (T, T8, U), once. The second replicate is in
reverse order.

**Frozen verdict (as printed).** fold/q193-rule.out: "Q193 RULE (a) t1: controls 4 of 4 passed, form
NOT passed; H-LASTWRITER 0 held, 0 FAILED, 2 cannot tell of 2; H-LASTJOB 0 held, 0 FAILED, 2 cannot
tell of 2; H-SPLIT 0 held, 0 FAILED, 2 cannot tell of 2: not decided"
"Q193 RULE (a) t2: controls 2 of 2 passed, form NOT passed; H-LASTWRITER 0 held, 0 FAILED, 2 cannot
tell of 2; H-LASTJOB 0 held, 0 FAILED, 2 cannot tell of 2; H-SPLIT 0 held, 0 FAILED, 2 cannot tell
of 2; H-TRI1536 0 held, 0 FAILED, 2 cannot tell of 2: not decided"
"Q193 RULE (a) t3: controls 2 of 2 passed, form NOT passed; H-LASTWRITER 0 held, 0 FAILED, 2 cannot
tell of 2; H-LASTJOB 0 held, 0 FAILED, 2 cannot tell of 2; H-SPLIT 0 held, 0 FAILED, 2 cannot tell
of 2; H-RESETCLR 0 held, 0 FAILED, 2 cannot tell of 2: not decided"
"Q193 RULE (a) t4: controls 2 of 2 passed, form NOT passed; H-LASTWRITER 0 held, 0 FAILED, 1 cannot
tell of 1; H-LASTJOB 0 held, 0 FAILED, 1 cannot tell of 1; H-SPLIT 0 held, 0 FAILED, 1 cannot tell
of 1: not decided"
"Q193 RULE (b): another context: decided by construction (every row is its own process with its own
VM and context, t30's side_init); a power cycle and a module reload: open (R35-5a)"
"Q193 RULE: NARROW: clause (a) decided for no group of t1, t2, t3, t4; the power cycle and module
reload clauses stay open".

**Results [HW].** Every T read its marker back in dword 0 and output K1 in 2048 pixels; K and
T8 read their own values. The two c readers read the marker in 2024 pixels and 0x0000200f in
24, so the form control failed and every held-out reader is cannot tell (score-t.txt: "FORM
ca-u ... FAILED", "FORM cb-u ... FAILED"). Each reader's dword 0 was one of its pixel values. The
other readers (post hoc, fold/posthoc.out): t1 the marker in 2024 or 2025 pixels and 0x0000300f
in 23 or 24; t2 the marker in 2024 and 0x0000302f in 24; t3 the marker in 2025 and 0x0000100f in
23; t4 0x7e080604 (T8's r4 marker) in 1388, the T marker in 637 and 0x0000300f in 23. The small
values sit at even x in 0-14 and 32-46 and even y in 0-6 and 16-22, at positions that change from
row to row. No job failed or hung, and no BIF fault line appeared.

**What it shows.** [HW] The stage decided nothing: its reader form did not read the marker in
every pixel, as its frozen control required. That premise came from E484's r40 and E593's
first order; with r20 here about 24 pixels read something else. The decode is not at fault (the
pixels agree with the o0 lines, and stage a's decode controls passed). Post hoc [infer]: an
unwritten r20 reads the last r20 write in about 2024 pixels across a colour fill, the t10
triangle and a debugfs reset, with no other job's marker; after a fill with 8 temporaries most
pixels read that fill's r4 (20 = 2 x 8 + 4), as if the register file is indexed modulo the
smaller allocation [infer]. None of this was frozen.

**What it does not show.** A decided answer to any group of Q193's clause (a); what the 23-24
small values are; a power cycle or a module reload (clause (b), R35-5a).
