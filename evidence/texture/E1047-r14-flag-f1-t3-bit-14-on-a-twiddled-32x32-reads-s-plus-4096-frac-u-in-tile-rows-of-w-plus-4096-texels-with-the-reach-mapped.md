+++
id = "E1047"
claim = "r14-flag stage f1 (5 probe fills on E566's twiddled 32 x 32 32-bit texture in the tx_map form, t14 with a 1 MiB scratch (probe --scratch-pages 256) that maps E1033's two fault pages; 3 planned faults, none happened): T3 bit 14 reads, on every pixel of all three bit-14 fills, the dword of column s + floor(4096 frac(u)) (s the wrapped bit-clear column) in E561's 16 x 16 tiles with a tile row of W + 4096 = 4128 texels; frozen 'H-TWP4128 (3 of 3 rows decided)', 'H-TWP4096', 'H-TWP4096-NS' and 'H-FAULTANY' 'not supported: 0 held, 3 FAILED', 'H-MOVE0' '0 held, 1 FAILED'; H-TWP4128 was fitted post hoc on E1033's two fault pages, so f1-tw32 and f1-small (E1033's inputs rerun) are in sample and only f1-zero (u = 0) is held out; both bit-clear references passed"
unit = "texture"
method = "r14-flag (render/closing-r14-flag), stage f1 of the question-closing pass round 14, the flagged session: decision R14-5 (a) of closing14/DECISIONS-R14.md with the user's OK for these planned faults only, R14-4 (a) for t14, plan closing14/plan/rank-round14.md sections 2 and 3; folded with the lead's confirmation, the user's standing instruction to proceed at the recommendations, dataset render-closing-r14-flag; attempt out/20261114-060824 (f1 06:08:25 Mac time; driver log run.log; its freeze FROZEN.sha256 1d702048e64b9cc43bc424c558f2ab799b00c2b50d2d715ec541c672bc90dcd8; scores score-f1.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tools ~/sgxfive-test-t14 (t14, sha256 aa550b94585aaf6eb5d9b7927d320ad31ea8d1e206b8c5e99e4435c7f0a83859, built from resgx545 c58f9f9 by lead/build_tool14.sh) for the rows and ~/sgxfive-test-t10 (t10, 9bedc2d6..., from a581c06) for the health pair, every job one process of the kit runner (kit/run_stage.sh at resgx545 c58f9f9), a debugfs reset before every row, a reset and the strict health fill and triangle after any fault (none happened), no debugfs knob written, every output and kernel slice kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv (gen/make.py)); freezes: FROZEN.sha256 1d702048e64b9cc43bc424c558f2ab799b00c2b50d2d715ec541c672bc90dcd8 (111 files), PREDICTIONS.sha256 f74107b52cdf9eff8e47688c6b05c0238f98bdb7f8c658e36a0545c03e821044 (26 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at c58f9f9c, resgx545:tools/closing/kit/lib_kit.sh at c58f9f9c, resgx545:tools/closing/kit/run_stage.sh at c58f9f9c, resgx545:tools/closing/kit/kitscore.py at c58f9f9c, resgx545:tools/closing/kit/fake/sudo at c58f9f9c, resgx545:tools/closing/kit/fake/timeout at c58f9f9c, resgx545:tools/closing/kit/fake/df at c58f9f9c, resgx545:tools/closing/kit/fake/modinfo at c58f9f9c, resgx545:tools/closing/kit/fake/sha256sum at c58f9f9c, resgx545:tools/closing/kit/fake/tool.sh at c58f9f9c, resgx545:tools/closing/kit/fake/tool.py at c58f9f9c, resgx545:tools/closing/kit/fake/ssh.py at c58f9f9c, resgx545:tools/closing/scorekit.py at c58f9f9c, resgx545:tools/closing/sessioncheck.py at c58f9f9c, data:texture/p1141/templates/tx_map.s at 3309b5fd, data:texture/p1141/support/build.py at 3309b5fd, data:texture/p1141/support/texmodel.py at 3309b5fd, data:texture/p1141/support/specs.json at 3309b5fd, data:texture/p1132/tx-t3/tw32-ctl.txt.gz at 3309b5fd, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__33.bin at 3309b5fd, data:render/closing-r10-tex/gen/pins.py at 3309b5fd, data:render/closing-r10-tex/gen/tex.py at 3309b5fd, data:render/closing-r10-tex/gen/addr.py at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/cases.tsv at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-ref-a.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-ref-b.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-tw32.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-tw32.dmesg.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-small.txt.gz at 3309b5fd, data:render/closing-r13-flag/out/20261113-220930/f1/f1-small.dmesg.gz at 3309b5fd, data:render/closing-r10-geo/gen/q139_fit.py at 3309b5fd, data:render/closing-r10-geo/gen/q139model.py at 3309b5fd, data:render/closing-r10-geo/gen/q139even.py at 3309b5fd, data:render/closing-r10-geo/score/lib_dump.py at 3309b5fd, data:render/closing-r10-geo/score/pbdump_dump.py at 3309b5fd, data:render/closing-r10-geo/score/region_tiles_dump.py at 3309b5fd, data:render/closing-r10-geo/out/20261113-103256/q139c/q139c-ctl-256x256.txt.gz at 3309b5fd, data:render/closing-r10-geo/out/20261113-103256/q139c/q139c-ctl-256x256.tri.param.bin.gz at 3309b5fd, data:render/closing-r10-geo/out/20261113-103256/q139c/q139c-ctl-256x256.tri.tadata.bin.gz at 3309b5fd, data:render/closing-r9-lgeo/out/20261113-080029/q139b/q139b-ctl-768x640.txt.gz at 3309b5fd, data:render/closing-r9-lgeo/out/20261113-080029/q139b/q139b-ctl-768x640.tri.param.bin.gz at 3309b5fd, data:render/closing-r9-lgeo/out/20261113-080029/q139b/q139b-ctl-768x640.tri.tadata.bin.gz at 3309b5fd, data:ta/mtile-fields/output.txt at 3309b5fd, data:ta/mtile-fields-risky/output.txt at 3309b5fd, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built, c58f9f9c87aa3f8370d2b66917898550d86f6879 at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 9cef7a202fc8267fa04ab6986145b69fd4ab18beafbe6fdb5e65dd009a00b612 c58f9f9c87aa3f8370d2b66917898550d86f6879:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r14-flag:out/20261114-060824/f1/", "render-closing-r14-flag:fold/"]
terms = ["T3.BIT14"]
+++
**What ran.** E1033's form (E566's tx_map: scratch dword i reads 0xD0000000 | i; the texture, T1
0x0C01F01F, at the scratch's first dword; `probe --temps 32 --coords --pixels`) with t14's
`--scratch-pages 256`: the scratch spans 1 MiB, so E1033's fault pages (scratch + 0x21000 and +
0x40000) lie inside it and a read there names its dword. Rows in run order: f1-ref-a (control:
E566's tw32-ctl program byte for byte), f1-tw32 (E566's tw32-t3b14, u in (1, 2)), f1-ref-b
(control: u = x / 4096, bit 14 clear), f1-small (the same with bit 14), f1-zero (held out: u = 0
on every pixel, bit 14, v on row y's centre). The three bit-14 rows were the stage's planned rows
(`expectfault`, `#limit 3`).



**Frozen verdict (as printed).** attempt 20261114-060824, stage f1 (run.log): `SUMMARY: f1:
H-FAULTANY: T3 bit 14 on a twiddled 32 x 32 texture, 256 scratch pages is not supported: 0 held, 3
FAILED, 0 cannot tell of 3`; attempt 20261114-060824, stage f1 (run.log): `SUMMARY: f1: H-MOVE0: T3
bit 14 on a twiddled 32 x 32 texture, 256 scratch pages is not supported: 0 held, 1 FAILED, 0 cannot
tell of 1`; attempt 20261114-060824, stage f1 (run.log): `SUMMARY: f1: H-TWP4096: T3 bit 14 on a
twiddled 32 x 32 texture, 256 scratch pages is not supported: 0 held, 3 FAILED, 0 cannot tell of 3`;
attempt 20261114-060824, stage f1 (run.log): `SUMMARY: f1: H-TWP4096-NS: T3 bit 14 on a twiddled 32
x 32 texture, 256 scratch pages is not supported: 0 held, 3 FAILED, 0 cannot tell of 3`; attempt
20261114-060824, stage f1 (run.log): `SUMMARY: f1: H-TWP4128: T3 bit 14 on a twiddled 32 x 32
texture, 256 scratch pages (3 of 3 rows decided)`.

**Results [HW].** No row faulted; both controls drew their frozen images (E566's kept tw32-ctl,
the tile law's column 0, as E1033's references did at 16 pages). Every pixel of the three bit-14
fills names a scratch dword (READING lines of score-f1.txt): f1-tw32 dwords 1024 to 131071,
f1-small 0 to 67071, f1-zero 0 to 66133; H-TWP4128 gives 2048 of 2048 pixels of each. The rivals:
H-TWP4096 (the same column, a tile row of 4096 texels) 1024 of 2048 on each (the tile rows below
16 part them), H-TWP4096-NS (no bit-clear column) 32, 1024 and 1024, H-MOVE0 (f1-zero: the
bit-clear image) 1024. The frozen scorer re-run on the kept files is byte-identical
(fold/reproduce.out).

**What it shows.** [HW] On a twiddled 32 x 32 32-bit texture, point sampled in repeat mode, T3
bit 14 widens the tile layout: the read is texel (s + floor(4096 frac(u)), t) of a texture laid out
in 16 x 16 tiles with 258 tiles a tile row, so every texel row from 16 on lies 64.5 KiB further on
than the bit-clear layout puts it, and a u in (1, 2) is taken by its fraction (f1-tw32: column
16 + 2112 = 2128 at q = 16). That explains E566's and E1033's faults: the reads lie past a 64 KiB
scratch (up to 512 KiB on). [infer] With E1003's strided reading (the texel plus floor(4096
clamp(u, 0, 1))) the bit adds 4096 texels to the width the address is formed with; a strided
texture's row pitch is its stride, so only the column moves there.

**What it does not show.** The form was fitted post hoc on E1033's two fault pages and held out by
one row only (f1-zero; f1-tw32 and f1-small rerun the fitted inputs, their images new but their
inputs not): whether the pitch is W + 4096 or a constant 4128 (only W = 32 ran), whether u past 1
takes its fraction or is clamped at another width, other sizes and formats, filtered samples,
address modes other than repeat. sgx-sim's tex.rs models this geometry only and refuses the rest
(Q078).
