+++
id = "E1048"
claim = "r14-flag stage f2 (6 TA-dump jobs, t10: the unpoked 256 x 256 and 768 x 640 baselines and four CR_TE_MTILE1 words never run, the first macrotile 14 and 15 tiles wide at 256 x 256 and 26 and 27 at 768 x 640, fx 2 or 3 mod 4 and covering the target; 4 planned faults, none happened): every row drew, and E950's H-EVEN (a block row of the first macrotile takes 8 floor(fx / 2) slots) gave every header slot of all four, held out; frozen 'H-COVER (4 of 4 rows decided)', 'H-FAULT23' '0 held, 4 FAILED'; with the dumps (score.py dumps f2, fold/score-f2-dumps.txt) 'H-EVEN (4 of 4 rows decided)', R7-BLK 'blkrow' '0 held, 4 FAILED', 'H-LASTBLOCK (4 of 4 rows decided)', 'H-HIGHSLOT' '2 held, 2 FAILED' (it fails on the two 768 x 640 rows, the only ones that part the two); both baselines passed"
unit = "ta"
method = "r14-flag (render/closing-r14-flag), stage f2 of the question-closing pass round 14, the flagged session: decision R14-5 (a) of closing14/DECISIONS-R14.md with the user's OK for these planned faults only, R14-4 (a) for t14, plan closing14/plan/rank-round14.md sections 2 and 3; folded with the lead's confirmation, the user's standing instruction to proceed at the recommendations, dataset render-closing-r14-flag; attempt out/20261114-060824 (f2 06:09:08 Mac time; driver log run.log; its freeze FROZEN.sha256 1d702048e64b9cc43bc424c558f2ab799b00c2b50d2d715ec541c672bc90dcd8; scores score-f2.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06) for the rows and the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 c58f9f9), a debugfs reset before every row, a reset and the strict health fill and triangle after any fault (none happened), no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 1d702048e64b9cc43bc424c558f2ab799b00c2b50d2d715ec541c672bc90dcd8 (111 files), PREDICTIONS.sha256 f74107b52cdf9eff8e47688c6b05c0238f98bdb7f8c658e36a0545c03e821044 (26 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c58f9f9c, resgx545:tools/closing/kit/lib_kit.sh at c58f9f9c, resgx545:tools/closing/kit/run_stage.sh at c58f9f9c, resgx545:tools/closing/kit/kitscore.py at c58f9f9c, resgx545:tools/closing/kit/fake/sudo at c58f9f9c, resgx545:tools/closing/kit/fake/timeout at c58f9f9c, resgx545:tools/closing/kit/fake/df at c58f9f9c, resgx545:tools/closing/kit/fake/modinfo at c58f9f9c, resgx545:tools/closing/kit/fake/sha256sum at c58f9f9c, resgx545:tools/closing/kit/fake/tool.sh at c58f9f9c, resgx545:tools/closing/kit/fake/tool.py at c58f9f9c, resgx545:tools/closing/kit/fake/ssh.py at c58f9f9c, resgx545:tools/closing/scorekit.py at c58f9f9c, resgx545:tools/closing/sessioncheck.py at c58f9f9c, data:texture/p1141/templates/tx_map.s at 3309b5fd, data:texture/p1141/support/build.py at 3309b5fd, data:texture/p1141/support/texmodel.py at 3309b5fd, data:texture/p1141/support/specs.json at 3309b5fd, data:texture/p1132/tx-t3/tw32-ctl.txt.gz at 3309b5fd, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__33.bin at 3309b5fd, data:render/closing-r10-tex/gen/pins.py at 3309b5fd, data:render/closing-r10-tex/gen/tex.py at 3309b5fd, data:render/closing-r10-tex/gen/addr.py at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/cases.tsv at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-ref-a.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-ref-b.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-tw32.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-tw32.dmesg.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-small.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-small.dmesg.gz at 3309b5fd, data:render/closing-r10-geo/gen/q139_fit.py at 3309b5fd, data:render/closing-r10-geo/gen/q139model.py at 3309b5fd, data:render/closing-r10-geo/gen/q139even.py at 3309b5fd, data:render/closing-r10-geo/score/lib_dump.py at 3309b5fd, data:render/closing-r10-geo/score/pbdump_dump.py at 3309b5fd, data:render/closing-r10-geo/score/region_tiles_dump.py at 3309b5fd, data:render/closing-r10-geo/out/20261113-103256/q139c/q139c-ctl-256x256.txt.gz at 3309b5fd, data:render/closing-r10-geo/out/20261113-103256/q139c/q139c-ctl-256x256.tri.param.bin.gz at 3309b5fd, data:render/closing-r10-geo/out/20261113-103256/q139c/q139c-ctl-256x256.tri.tadata.bin.gz at 3309b5fd, data:render/closing-r9-lgeo/out/20261113-080029/q139b/q139b-ctl-768x640.txt.gz at 3309b5fd, data:render/closing-r9-lgeo/out/20261113-080029/q139b/q139b-ctl-768x640.tri.param.bin.gz at 3309b5fd, data:render/closing-r9-lgeo/out/20261113-080029/q139b/q139b-ctl-768x640.tri.tadata.bin.gz at 3309b5fd, data:ta/mtile-fields/output.txt at 3309b5fd, data:ta/mtile-fields-risky/output.txt at 3309b5fd, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r14-flag:out/20261114-060824/f2/", "render-closing-r14-flag:fold/"]
terms = ["CR_TE_MTILE1", "CR_TE_MACROTILE_STRIDE"]
+++
**What ran.** r10-geo q139c's form (E1007) on t10: `tri --tri-full --pixels --width W --height H
--max-width W --max-height H [--kpoke-render 1:ta:143=V] --wait-ms 20000 --keep-going
--dump-render "$W"`. Rows in run order: f2-ctl-256 (control, the unpoked 256 x 256 baseline),
f2-h-256-fx14 (0x0100e004), f2-h-256-fx15 (0x0100f004), f2-ctl-768 (control, the unpoked 768 x
640 baseline), f2-h-768-fx26 (0x86810018), f2-h-768-fx27 (0x86c10018); the four poked rows were
the stage's planned rows (`expectfault expectdiff`, `#limit 4`). The header base of each size is
its baseline's (lib_dump.baseline_layout: 0x4000 and 0x7000). The kit's scorer reads the ends and
the controls' images; the slot and flag verdicts read the dumps (`score.py dumps f2`, frozen with
the session: the kit checks REQUIRED files on every row and a faulted row would have had no dump).



**Frozen verdict (as printed).** attempt 20261114-060824, stage f2 (run.log): `SUMMARY: f2: H-COVER:
a job at fx 2 or 3 mod 4 whose first macrotile covers the target draws (4 of 4 rows decided)`;
attempt 20261114-060824, stage f2 (run.log): `SUMMARY: f2: H-FAULT23: a job at fx 2 or 3 mod 4
faults is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`.

**Results [HW].** No row faulted. Both baselines drew exactly with one header a target tile at
H-EVEN's slot (128 of 128, 960 of 960). The four poked rows drew wrong in whole tiles (28, 30, 576
and 576 wrong tiles) with every target tile's header at H-EVEN's slot (128 of 128 twice, 960 of 960
twice; R7-BLK 92, 94, 952 and 956), one header with flag bit 7 each, at H-LASTBLOCK's slot (119,
119, 383, 383), and the image's wrong tiles exactly those whose header lies past it or is
overwritten. At 768 x 640 the highest target slot (495) lies past the flag, so H-HIGHSLOT failed
there; at 256 x 256 the two are one slot. The frozen scorer re-run on the kept files is
byte-identical (fold/reproduce.out).

**What it shows.** [HW] Held out at fx 14, 15, 26 and 27 (2 and 3 mod 4), a block row of the first
macrotile takes 8 floor(fx / 2) region header slots (E950's H-EVEN, fitted on three dumps), not
R7-BLK's 16 floor(fx / 4); the rest of R7-BLK and block order hold. The list-end flag is on the
last target tile in block order, not on the highest target slot (E1011's open rival). [infer]
Words whose first macrotile covers the target's width draw at fx 2 or 3 mod 4 (H-COVER, 4 of 4,
formed post hoc on the 22 kept jobs); every kept fault at those fx had a later macrotile inside the
target.

**What it does not show.** Why words whose first macrotile ends inside the target fault (E509;
none ran here, by design), the stride's relation to the RT data, and fx 2 or 3 mod 4 with a second
macrotile column inside the target. sgx-pipe's ta.rs admits these four words and keeps refusing
other poked words (Q139).
