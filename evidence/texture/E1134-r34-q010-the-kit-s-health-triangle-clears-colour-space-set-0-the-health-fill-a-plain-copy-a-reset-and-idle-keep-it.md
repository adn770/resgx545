+++
id = "E1134"
claim = "r34-q010 stage c (Q010, 32 jobs, safe): the kit's health triangle clears colour-space set 0 and the health fill does not: after a BT.601 load, a copy without the load read black 0xd3522437a14b6325 after a t10 `tri` (t2a-rd, t2b-rd) and after the fill-then-triangle pair (t6-rd), and E037's 0xb6067a95fa98de2d after a t10 `fill` (t1a-rd, t1b-rd), a plain copy (t3a-rd, t3b-rd), 60 s and 120 s idle (t4-rd, t5-rd) and a debugfs reset alone (t0a-rd, t0b-rd, controls); frozen 'H-TRI ... (9 of 9 rows decided)', H-FILL '5 held, 4 FAILED', H-BOTH '7 held, 2 FAILED', H-NONE '6 held, 3 FAILED', H-IDLE and H-COPYNL '0 held, 2 FAILED', every one of 15 controls passed, and the frozen Q010 rule printed 'one job hypothesis, H-TRI: RETIRE-CAPABLE'"
unit = "texture"
method = "r34-q010 (render/closing-r34-q010), stage c of the question-closing pass (round 34, R34-1 (a): closing29/plan/rank-round34.md section 3.1, safe class: no planned fault or hang, no kreg, no knob), dataset render-closing-r34-q010; attempt out/20261116-231015 (scores score-c.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tools ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, built from resgx545 42c4de7) for every copy and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the fill and triangle rows and the kit's health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 5745c8d), a debugfs reset before every row but t6-xt (noreset), the health fill and triangle only at the stage's begin and end; the rows are tables/c.txt, the frozen predictions predictions/c.tsv (gen/make.py), the rule score/score.py's q010 command (fold/q010-rule.out), the score reproduced byte for byte (fold/reproduce.out)); freezes: FROZEN.sha256 00c4f48aac64c67747fc80e6dd59661e569c3e9588911f450ac163c793ebfc1c (45 files), PREDICTIONS.sha256 66553c637f2febcb993cf0219e79b59a33067938ad14e756fc3d1f88b947452d (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 5745c8dc, resgx545:tools/closing/kit/lib_kit.sh at 5745c8dc, resgx545:tools/closing/kit/run_stage.sh at 5745c8dc, resgx545:tools/closing/kit/kitscore.py at 5745c8dc, resgx545:tools/closing/kit/fake/sudo at 5745c8dc, resgx545:tools/closing/kit/fake/timeout at 5745c8dc, resgx545:tools/closing/kit/fake/df at 5745c8dc, resgx545:tools/closing/kit/fake/modinfo at 5745c8dc, resgx545:tools/closing/kit/fake/sha256sum at 5745c8dc, resgx545:tools/closing/kit/fake/tool.sh at 5745c8dc, resgx545:tools/closing/kit/fake/tool.py at 5745c8dc, resgx545:tools/closing/kit/fake/ssh.py at 5745c8dc, resgx545:tools/closing/scorekit.py at 5745c8dc, resgx545:tools/closing/sessioncheck.py at 5745c8dc, data:render/closing-r29-flag2/out/20261116-073242/h1/q010-pre.txt.gz at 8e59b150, data:render/closing-r29-flag2/out/20261116-073242/h1/q010-af.txt.gz at 8e59b150, data:render/closing-r29-flag2/out/20261116-073242/h1/q010-ld2.txt.gz at 8e59b150, data:render/closing-r29-flag2/out/20261116-073242/h1/q010-p1.txt.gz at 8e59b150, data:render/closing-r29-flag2/out/20261116-073242/h1/begin.fill1.txt.gz at 8e59b150, data:render/closing-r29-flag2/out/20261116-073242/h1/begin.health1.txt.gz at 8e59b150, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 42c4de7855d6f310321cc03fa0780b698a735e4d at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 253fd15bcb6a0a6381d20aacbb635af1c99d764388f394f9a24dc61266b6418d 42c4de7855d6f310321cc03fa0780b698a735e4d:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; pinned commits named by the session: resgx545 main 5745c8d, resgx545 main 5745c8dc1a8d, resgx545-data main 8e59b150be5f; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-16"
data = ["render-closing-r34-q010:out/20261116-231015/c/", "render-closing-r34-q010:fold/"]
terms = ["transfer_cmd.load_yuv_csc"]
+++
**What ran.** One stage, every row in it, each row after the kit's debugfs reset. E037's UYVY
copy (`copy --every-value --pixels --poke tex:1=0x7d03f01f --poke tex:0^=0x90`) on t30; a load adds
`--poke xfer:17^=0x1` and set 0's five words in xfer:18 to 22. z0-ld (load zeros) and z0-rd (the
copy without the load): references of this session, both controls. Then triples L (load BT.601,
control), X (the job under test), R (the copy without the load, held out): T0 no X (R a control),
T1 t10 `fill`, T2 t10 `tri` (the health pair's own argv), T3 t30 `copy --every-value --pixels` (a
plain copy, no YUV, no load), T4 `idle:60` and T5 `idle:120` before R, T6 t10 `fill` then t10 `tri`
with `noreset` (the pair as the kit's health runs it). Order z0, t0a, t1a, t2a, t3a, t4, t5, t6,
then t3b, t2b, t1b, t0b (second replicates reversed). Frozen per R row: H-FILL, H-TRI, H-BOTH,
H-NONE (all nine held-out R rows), H-IDLE (t4-rd, t5-rd black) and H-COPYNL (t3a-rd, t3b-rd
black); KEPT and CLEARED are E1112's kept copies' hashes, re-read here by every L and by z0.

**Frozen verdict (as printed).** attempt 20261116-231015, stage c (score-c.txt): `SUMMARY: c:
H-TRI: the t10 triangle clears colour-space set 0 (T2, T6 CLEARED; T0, T1, T3-T5 KEPT) (9 of 9
rows decided)`; `SUMMARY: c: H-FILL: ... is not supported: 5 held, 4 FAILED, 0 cannot tell of 9`;
`SUMMARY: c: H-BOTH: ... is not supported: 7 held, 2 FAILED, 0 cannot tell of 9`; `SUMMARY: c:
H-NONE: ... is not supported: 6 held, 3 FAILED, 0 cannot tell of 9`; `SUMMARY: c: H-IDLE: ... is
not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; `SUMMARY: c: H-COPYNL: ... is not supported:
0 held, 2 FAILED, 0 cannot tell of 2`; the rule (fold/q010-rule.out): `Q010 RULE: controls 15 of 15
passed; held-out R rows decided 9 of 9; full patterns holding on every row: H-TRI; ...: one job
hypothesis, H-TRI: RETIRE-CAPABLE`.

**Results [HW].** z0-ld, z0-rd 0xd3522437a14b6325; every L (t0a-ld to t0b-ld, 13 rows)
0xb6067a95fa98de2d; t0a-rd, t0b-rd 0xb6067a95fa98de2d. Held out: t2a-rd, t2b-rd, t6-rd
0xd3522437a14b6325 (black); t1a-rd, t1b-rd, t3a-rd, t3b-rd, t4-rd, t5-rd 0xb6067a95fa98de2d.
Every X row ended rc 0 (`fill: ok`; the triangles `diff: 0 of 4096`; the plain copies `job: ok`).
No fault, hang or stop; 32 of 32 rows class ok.

**What it shows.** [HW] The 64 x 64 triangle job of the kit's health (t10 `tri`, a 3D render)
leaves colour-space set 0 at zeros: a later copy without the load reads black, both replicates and
in the pair. The health fill (a transfer fill without the load flag), a plain copy, a debugfs reset
and 60 s or 120 s of idle keep the loaded set, held out. So E1112's q010-af (black after the health
pair with no fault) is the triangle's doing, and Q010's question, which job clears the set between
jobs, is answered for the jobs the kit runs. [infer] Each recovery of E1112 ran the strict health
pair before its copy, and E271's first job followed hung jobs whose own jobs and recovery are not
known: both fit the triangle clearing the set; neither is re-run here (a hang is flagged class).

**What it does not show.** Whether the triangle clears the set or loads zeros (the same reading);
which part of a render does it (the TA, the 3D or the kernel's render submission) or whether any
3D render does; whether a recovery without a health job clears it; the power-on state; set 1 and
the luma-key words.
