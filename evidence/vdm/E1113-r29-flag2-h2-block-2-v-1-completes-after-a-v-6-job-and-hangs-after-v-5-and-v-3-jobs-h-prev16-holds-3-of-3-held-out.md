+++
id = "E1113"
claim = "r29-flag2 stage h2 (Q163, 9 rows of E700's two-block stream on t10 in three triples from a reset, the kit's noreset, 2 planned hangs): a block-2 v = 1 job completed at c = 8 after (6,2) (h2-a3) and hung at c = 3 after (5,2) (h2-b3) and at c = 1 after (3,2) (h2-c3), as O29-2's H-PREV16 (it completes iff the job right before it, no reset between, completed with a block at v 1 or 6) predicted, held out 3 of 3 with the control h2-c-b (the second (6,2), c = 8 under M1) completing; frozen 'H-PREV16 ... (3 of 3 rows decided)', D-PREVADD and D-C '1 held, 2 FAILED', H-ALWAYS '2 held, 1 FAILED'; H-PREV16 was formed after E1035 was read (post hoc on 18 kept jobs), so these rows are its only held-out test"
unit = "vdm"
method = "r29-flag2 (render/closing-r29-flag2), stage h2 of the question-closing pass (round 29, the flagged session's hang stages run apart after r29-flag stopped in f2 (rc 5) before them: closing29/DECISIONS-R29.md (R29-1 to R29-6 (a), the user present: planned faults and recovered hangs only, the #limits capped at 14; no kernel change, no boot, no clock-gate write, no held reset), plan closing29/plan/rank-round29.md sections 1 and 3; r29-flag2's h1 and h2 are r29-flag's rows and predictions byte for byte), dataset render-closing-r29-flag2; attempt out/20261116-073242 (scores score-h2.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t22 (t22, sha256 9b62d31539564b0ca9e949aa1b44e325455b485a985fdfa65976684888d219ee, built from resgx545 3c68e8d) for the copies and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the hangs, the stream rows and the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 c057181), a debugfs reset before every row but a noreset one, a reset and the strict health fill and triangle after every hang and at each stage's begin and end, every output and kernel slice kept gzipped; s0's four copy references passed (score-s0.txt); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 edb5e2aba0492a14ddf7d38130e31ab6e4175ba9a1f7008dabf67a9d4973cf95 (59 files), PREDICTIONS.sha256 18b0d20746fdc8a4108af30e8878d0276f6781615a3f107c15f672b791cd8257 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c0571816, resgx545:tools/closing/kit/lib_kit.sh at c0571816, resgx545:tools/closing/kit/run_stage.sh at c0571816, resgx545:tools/closing/kit/kitscore.py at c0571816, resgx545:tools/closing/kit/fake/sudo at c0571816, resgx545:tools/closing/kit/fake/timeout at c0571816, resgx545:tools/closing/kit/fake/df at c0571816, resgx545:tools/closing/kit/fake/modinfo at c0571816, resgx545:tools/closing/kit/fake/sha256sum at c0571816, resgx545:tools/closing/kit/fake/tool.sh at c0571816, resgx545:tools/closing/kit/fake/tool.py at c0571816, resgx545:tools/closing/kit/fake/ssh.py at c0571816, resgx545:tools/closing/scorekit.py at c0571816, resgx545:tools/closing/sessioncheck.py at c0571816, data:render/closing-r25-csc/out/20261115-213805/csc/y28-zc.txt.gz at 73e058d5, data:render/closing-r25-csc/out/20261115-213805/csc/y28-bc.txt.gz at 73e058d5, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-csc.txt.gz at 73e058d5, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-none.txt.gz at 73e058d5, data:render/closing-s1b/bins/p1139-green.bin at 73e058d5, data:render/closing-r13-flag/bins/p1131-green__0.bin at 73e058d5, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 73e058d5, data:vdm/state-units/cases.tsv at 73e058d5, data:vdm/state-units/output.txt at 73e058d5, data:vdm/state-units/kernel.log at 73e058d5, data:vdm/verification-1141ta/out-hw/p1141ta-dumps/vdm-series-b-all/cases.tsv at 73e058d5, data:vdm/verification-1141ta/out-hw/p1141ta-dumps/vdm-series-b-all/kernel.log at 73e058d5, data:render/closing-r13-flag/tables/f3.txt at 73e058d5, data:render/closing-r13-flag/out/20261113-220930/f3/cases.tsv at 73e058d5, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 396252bdb513282a17ed9c17446754c6478984fc423fba55236b6865bfb023c0 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none; O29-2 is fit/o29_2.py and fit/o29_2.out (r29-flag's, carried byte for byte: the deciders fitted on E545's and E701's 15 block-2 v = 1 jobs, E1035's three read before H-PREV16 was formed)"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r29-flag2:out/20261116-073242/h2/", "render-closing-r29-flag2:fold/", "render-closing-r29-flag2:fit/"]
terms = ["VDM_STATE1.BITS11_9"]
+++
**What ran.** E700's stream (`probe --tri pixel --temps 32 --pixels --width 64 --height 64
--vertices 12 --obj2 6 ...`, p1131-blue and p1131-green), block 1's bits 11:9 by `--vdm 1^=`,
block 2's by `--vdm 9^=0x00000600` (v = 1), block 2's bits 7:0 at 5. Triples from a reset, the
second and third rows `noreset`: (6,2) (6,2) (2,1) (`h2-c-a`, `h2-c-b` the control, `h2-a3`),
(2,2) (5,2) (2,1) (`h2-b1`, `h2-b2`, `h2-b3`), (2,2) (3,2) (2,1) (`h2-c1`, `h2-c2`, `h2-c3`); the
(2,1) rows `expectfault`, `#limit 3`. Frozen (fit/o29_2.out): H-PREV16 (ok, hang, hang) against
D-PREVADD (a non-zero add before: ok x 3, the fit set's own form, E1035 1 of 3), D-C (c alone: ok x
3) and H-ALWAYS (hang x 3, E1035 3 of 3 on module B60AB0B4).

**Frozen verdict (as printed).** attempt 20261116-073242, stage h2 (run.log): `SUMMARY: h2:
H-PREV16: a block-2 v = 1 job completes iff the job before it completed with a block at v 1 or 6 (3
of 3 rows decided)`; `SUMMARY: h2: D-PREVADD: ... is not supported: 1 held, 2 FAILED, 0 cannot tell
of 3`; `SUMMARY: h2: D-C: ... is not supported: 1 held, 2 FAILED, 0 cannot tell of 3`; `SUMMARY: h2:
H-ALWAYS: ... is not supported: 2 held, 1 FAILED, 0 cannot tell of 3`.

**Results [HW].** h2-c-a, h2-c-b, h2-a3 completed (o0 read); h2-b1, h2-b2 completed, h2-b3 hung
(`job 1671 hung, recovering`); h2-c1, h2-c2 completed, h2-c3 hung; each hang reset clean, its
strict health drawing at the first try, no `SGX recovery failed` line. Scorer re-run byte for byte
(fold/reproduce.out).

**What it shows.** [HW, held out] A block-2 v = 1 job completes after (6,2) at c = 8 (E701's lone
completion, replicated on module E0CC4027) and hangs after a (5,2) or a (3,2) job that completed,
at c = 3 and 1, where neither c nor the previous job's add decides it: H-PREV16 holds 3 of 3 and
fits all 21 kept block-2 v = 1 jobs (E545, E701, E1035, these). [infer] What decides it is the job
right before, a block at v 1 or 6 (E545's own reading "v 1 or 6", moved one job back); why those
two values is not shown.

**What it does not show.** What the counter or the previous-job state is (the VDM, the TA or a USE
partition), v = 0 in block 1 below c = 4, a previous job at v 0 in block 1 or v 3 to 7 in block 2,
and other stream shapes for this clause.
