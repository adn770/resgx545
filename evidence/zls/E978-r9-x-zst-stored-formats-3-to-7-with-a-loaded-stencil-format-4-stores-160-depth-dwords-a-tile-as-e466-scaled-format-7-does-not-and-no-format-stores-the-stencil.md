+++
id = "E978"
claim = "r9-x stage zst (12 jobs): with E466's x ramp and a stencil buffer of each dword's index loaded (bits 1 and 13) and stored (bit 17), at 64 x 32 (4 tiles) and 96 x 48 (9 tiles), format 4 changed 640 and 1440 depth dwords (160 a tile, the frozen H-SCALE from E466, held 2 of 2), format 7 784 and 2064 (frozen 12 a tile: failed), formats 3 and 5 2560 and 5760 (640 a tile), format 6 2048 and 4608 (512 a tile), and no format from 3 to 7 changed a dword of the stencil store; both format-0 controls passed (depth 512 a tile, stencil store E467's copy, 128 a tile)"
unit = "zls"
method = "r9-x (render/closing-r9-x), stage zst of the question-closing pass (round 9, decision R9-2 (a), plan closing9/rank/rank-round9.md R9-D (Q120; Q121 not run)), dataset render-closing-r9-x; attempt out/20261113-081821 (zst 08:22:42 Mac time; driver log run.log; its freeze FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37; scores score-zst.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/STAGE.py)); freezes: FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37 (216 files), PREDICTIONS.sha256 b0d34b59ae03da1b4c3261fc7dc44b929c7ba8e8c18f8f2a972d87c5e266da7c (91 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at f32dfacc, resgx545:tools/closing/kit/lib_kit.sh at f32dfacc, resgx545:tools/closing/kit/run_stage.sh at f32dfacc, resgx545:tools/closing/kit/kitscore.py at f32dfacc, resgx545:tools/closing/kit/fake/sudo at f32dfacc, resgx545:tools/closing/kit/fake/timeout at f32dfacc, resgx545:tools/closing/kit/fake/df at f32dfacc, resgx545:tools/closing/kit/fake/modinfo at f32dfacc, resgx545:tools/closing/kit/fake/sha256sum at f32dfacc, resgx545:tools/closing/kit/fake/tool.sh at f32dfacc, resgx545:tools/closing/kit/fake/tool.py at f32dfacc, resgx545:tools/closing/kit/fake/ssh.py at f32dfacc, resgx545:tools/closing/scorekit.py at f32dfacc, resgx545:tools/closing/sessioncheck.py at f32dfacc, data:texture/p1141/templates/tx_map.s at 2d666bfa, data:texture/p1141/support/build.py at 2d666bfa, data:texture/p1141/support/texmodel.py at 2d666bfa, data:texture/p1141/support/specs.json at 2d666bfa, data:texture/p1141/gen/cases.json at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 2d666bfa, data:texture/p1141/stage-bins/p1141-t0b27__4.bin at 2d666bfa, data:texture/p1132/tx-t3/s64x32-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s32x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x16-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b10.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b12.txt.gz at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b12.txt.gz at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__0.bin at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__14.bin at 2d666bfa, data:isp/coverage-envelope/far/raw/1401720.txt.gz at 2d666bfa, data:isp/coverage-envelope/far/raw/1401724.txt.gz at 2d666bfa, resgx545:crates/sgx-pipe/src/zls.rs at f32dfacc, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/zst/", "render-closing-r9-x:fold/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** tri --tri-full --tri-z 0.25,0.75,0.25 with --depth, --stencil --stencil-fill index
--stencil-store, the control word E466's with G the tiles across minus one and bits 1 and 13 (the
stencil load), formats 0, 3, 4, 5, 6 and 7 at both sizes; depth, stencil and stencil-store dumps
kept.

**Frozen verdict (as printed).** attempt 20261113-081821, stage zst (run.log): `SUMMARY: zst: H-NONE
is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`; attempt 20261113-081821, stage zst
(run.log): `SUMMARY: zst: H-SCALE is not supported: 2 held, 2 FAILED, 0 cannot tell of 4`.

**Results [HW].** Depth dwords changed (64 x 32 / 96 x 48): format 0 2048 / 4608 (control), 3 2560 /
5760, 4 640 / 1440, 5 2560 / 5760, 6 2048 / 4608, 7 784 / 2064; stencil-store dwords changed: format
0 512 / 1152 (control), formats 3 to 7 0.

**What it shows.** With a stencil buffer, format 4 stores 160 dwords a tile at both sizes, as E466's
1024 x 768 count scaled per tile; formats 3 and 5 store 640 a tile (512 + 128, [infer] depth and
stencil together), 6 512 a tile, 7 a count that is not a whole number a tile at 96 x 48. None of
them writes the stencil-store buffer.

**What it does not show.** The layouts are not decoded (the dumps are kept for it); formats 3 to 7
without a loaded stencil and other sizes did not run. Q121 (the stencil's byte order and test) needs
ISP word 2 with the ZLS stencil buffers, which tool t4 cannot set (`tri --isp2`, a tool change).
