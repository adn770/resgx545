+++
id = "E1112"
claim = "r29-flag2 stage h1 and h2's first row (Q010, 7 copies on t22 and E737's bit-24 hang twice on t10, 2 planned hangs, both recovered): a copy without the load read black 0xd3522437a14b6325 after each recovered hang (q010-p1, q010-p2), the reading of the rival H-RECOV-CLR, not of the frozen H-KEEP (E037's 0xb6067a95fa98de2d), and so did q010-af, the first copy after s0's BT.601 copies with no fault or hang between, only the kit's health fill and triangle and debugfs resets; q010-pre, after a load and a debugfs reset alone, read E037's hash as E1097 and E1103; frozen 'H-RECOV-CLR ... (1 of 2 rows decided)' (h1) and '(1 of 1 rows decided)' (h2), 'H-KEEP ... 0 held, 1 FAILED, 1 cannot tell of 2' and '0 held, 1 FAILED', R29-3 (a)'s rule 'not one hypothesis: narrow only' (q010-af cannot tell: no fault before it); the six copy controls passed"
unit = "texture"
method = "r29-flag2 (render/closing-r29-flag2), stages h1, h2 of the question-closing pass (round 29, the flagged session's hang stages run apart after r29-flag stopped in f2 (rc 5) before them: closing29/DECISIONS-R29.md (R29-1 to R29-6 (a), the user present: planned faults and recovered hangs only, the #limits capped at 14; no kernel change, no boot, no clock-gate write, no held reset), plan closing29/plan/rank-round29.md sections 1 and 3; r29-flag2's h1 and h2 are r29-flag's rows and predictions byte for byte), dataset render-closing-r29-flag2; attempt out/20261116-073242 (scores score-h1.txt, score-h2.txt); on the laptop over the travel cable (host cedar, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t22 (t22, sha256 9b62d31539564b0ca9e949aa1b44e325455b485a985fdfa65976684888d219ee, built from resgx545 3c68e8d) for the copies and ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the hangs, the stream rows and the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 c057181), a debugfs reset before every row but a noreset one, a reset and the strict health fill and triangle after every hang and at each stage's begin and end, every output and kernel slice kept gzipped; s0's four copy references passed (score-s0.txt); the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 edb5e2aba0492a14ddf7d38130e31ab6e4175ba9a1f7008dabf67a9d4973cf95 (59 files), PREDICTIONS.sha256 18b0d20746fdc8a4108af30e8878d0276f6781615a3f107c15f672b791cd8257 (3 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c0571816, resgx545:tools/closing/kit/lib_kit.sh at c0571816, resgx545:tools/closing/kit/run_stage.sh at c0571816, resgx545:tools/closing/kit/kitscore.py at c0571816, resgx545:tools/closing/kit/fake/sudo at c0571816, resgx545:tools/closing/kit/fake/timeout at c0571816, resgx545:tools/closing/kit/fake/df at c0571816, resgx545:tools/closing/kit/fake/modinfo at c0571816, resgx545:tools/closing/kit/fake/sha256sum at c0571816, resgx545:tools/closing/kit/fake/tool.sh at c0571816, resgx545:tools/closing/kit/fake/tool.py at c0571816, resgx545:tools/closing/kit/fake/ssh.py at c0571816, resgx545:tools/closing/scorekit.py at c0571816, resgx545:tools/closing/sessioncheck.py at c0571816, data:render/closing-r25-csc/out/20261115-213805/csc/y28-zc.txt.gz at 73e058d5, data:render/closing-r25-csc/out/20261115-213805/csc/y28-bc.txt.gz at 73e058d5, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-csc.txt.gz at 73e058d5, data:render/closing-r23-pk/out/20261115-202948/q181/c-copy-none.txt.gz at 73e058d5, data:render/closing-s1b/bins/p1139-green.bin at 73e058d5, data:render/closing-r13-flag/bins/p1131-green__0.bin at 73e058d5, data:render/closing-r13-flag/bins/p1131-blue__0.bin at 73e058d5, data:vdm/state-units/cases.tsv at 73e058d5, data:vdm/state-units/output.txt at 73e058d5, data:vdm/state-units/kernel.log at 73e058d5, data:vdm/verification-1141ta/out-hw/p1141ta-dumps/vdm-series-b-all/cases.tsv at 73e058d5, data:vdm/verification-1141ta/out-hw/p1141ta-dumps/vdm-series-b-all/kernel.log at 73e058d5, data:render/closing-r13-flag/tables/f3.txt at 73e058d5, data:render/closing-r13-flag/out/20261113-220930/f3/cases.tsv at 73e058d5, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 396252bdb513282a17ed9c17446754c6478984fc423fba55236b6865bfb023c0 3c68e8de6bdfeecd37b97e2d6095fef932e0e6d9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-16"
data = ["render-closing-r29-flag2:out/20261116-073242/s0/", "render-closing-r29-flag2:out/20261116-073242/h1/", "render-closing-r29-flag2:out/20261116-073242/h2/", "render-closing-r29-flag2:fold/"]
terms = ["transfer_cmd.load_yuv_csc"]
+++
**What ran.** E1103's copy forms on t22 (`copy --every-value --pixels --poke tex:1=0x7d03f01f
--poke tex:0^=0x90`, a load adding `--poke xfer:17^=0x1` and set 0's words in xfer:18 to 22, zeros
or BT.601). s0: c10-zc (load zeros), c10-zn (no load), c10-bc (load BT.601), c10-bn (no load),
controls. h1: `q010-af` (no load), `q010-ld2` (load BT.601, control), `q010-pre` (no load,
control), `q010-h1` (t10 `probe --tri pixel --vertices 15 --copy-depth --pixels --vdm
2^=0x01000000`, E737's bit-24 hang, `expectfault`), `q010-p1` (no load), `q010-h2` (the hang
again); h2's first row `q010-p2` (no load). Frozen: H-KEEP (a copy without the load after a
recovery reads 0xb6067a95fa98de2d) [infer: the fork's recovery runs the reset a debugfs reset runs]
against H-RECOV-CLR (0xd3522437a14b6325). A copy is scored only after its recovery (q010-af after
a fault in r29-flag's f1 or f2, which do not run here: cannot tell).

**Frozen verdict (as printed).** attempt 20261116-073242, stage h1 (run.log): `SUMMARY: h1:
H-RECOV-CLR: a recovered fault or hang clears colour-space set 0 to zeros (1 of 2 rows decided)`;
`SUMMARY: h1: H-KEEP: no recovered fault or hang clears colour-space set 0 (a copy without the load
reads the last set) is not supported: 0 held, 1 FAILED, 1 cannot tell of 2`; `SUMMARY: h1:
H-B24-HANG: VDM index list header bit 24 alone hangs E414's job (E737) (2 of 2 rows decided)`;
stage h2 (run.log): `SUMMARY: h2: H-RECOV-CLR: ... (1 of 1 rows decided)`, `SUMMARY: h2: H-KEEP:
... is not supported: 0 held, 1 FAILED, 0 cannot tell of 1`, `Q010 RULE: controls 6 of 6 passed;
copies q010-af none, q010-p1 H-RECOV-CLR, q010-p2 H-RECOV-CLR: not one hypothesis: narrow only`.

**Results [HW].** Hashes in run order: c10-zc, c10-zn 0xd3522437a14b6325; c10-bc, c10-bn
0xb6067a95fa98de2d; then s0's end health (t10 `fill`, `tri`), h1's begin health (the same) and a
debugfs reset; q010-af 0xd3522437a14b6325; q010-ld2, q010-pre 0xb6067a95fa98de2d; q010-h1 hung (`job
1654 hung,
recovering`), reset, health drew; q010-p1 0xd3522437a14b6325; q010-h2 hung, recovered; q010-p2
(next stage, after h1's end health and h2's begin health) 0xd3522437a14b6325. No `SGX recovery
failed` line. Scorers re-run byte for byte (fold/reproduce.out).

**What it shows.** [HW] After a recovered hang a copy without the load reads the zeros set, not
the last loaded one: the frozen H-KEEP fails 2 of 2 decided rows, H-RECOV-CLR holds. [HW] A debugfs
reset alone keeps the set (q010-pre, as E1097 and E1103). [post hoc] q010-af read the zeros set
with no fault or hang since c10-bn read BT.601: between them ran only the kit's health fill and
triangle (twice, at s0's end and h1's begin) and debugfs resets, and each recovery here also ran a
strict health pair before its copy. [infer] So the set is cleared by a job of the health pair (the
t10 `fill` or `tri`) or by the stage boundary, not by the reset, and the run does not part that
from a recovery clearing it; E1103's rows had no health job between them, and E271's zeros after
hung jobs fit either. The answer to Q010's clause is narrowed, not given.

**What it does not show.** Which of the health fill and the health triangle clears the set (or
loads zeros), whether a hang's recovery without a health job clears it, a power-on state, set 1
and the luma-key words.
