+++
id = "E979"
claim = "r9-x stage far (11 jobs): with one vertex at +2^22, +2^23, +2^24 or -2^25 pixels in x, -2^22, +2^23, -2^24 or -2^25 in y (the other coordinate up to 2^23), or two at +-2^23 or +-2^24, and the rest inside a 64 x 64 target (tool unit 1/32), the coverage equals the exact rule of E606/E607 at every pixel outside E684's 1e-3 pixel band in 10 of 10 rows (frozen H-EXACT held); a clamp to the 24.8 range (H-SAT) failed the 5 rows where it differs, a two's-complement wrap of 24.8 (H-WRAP) failed 8 of 8 where it differs, nothing drawn (H-CULL) failed 10 of 10; E684's far21d0 rerun drew its 208 pixels (control); no job faulted"
unit = "isp"
method = "r9-x (render/closing-r9-x), stage far of the question-closing pass (round 9, decision R9-2 (a), plan closing9/rank/rank-round9.md R9-E (Q199, Q261)), dataset render-closing-r9-x; attempt out/20261113-081821 (far 08:24:00 Mac time; driver log run.log; its freeze FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37; scores score-far.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/STAGE.py)); freezes: FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37 (216 files), PREDICTIONS.sha256 b0d34b59ae03da1b4c3261fc7dc44b929c7ba8e8c18f8f2a972d87c5e266da7c (91 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at f32dfacc, resgx545:tools/closing/kit/lib_kit.sh at f32dfacc, resgx545:tools/closing/kit/run_stage.sh at f32dfacc, resgx545:tools/closing/kit/kitscore.py at f32dfacc, resgx545:tools/closing/kit/fake/sudo at f32dfacc, resgx545:tools/closing/kit/fake/timeout at f32dfacc, resgx545:tools/closing/kit/fake/df at f32dfacc, resgx545:tools/closing/kit/fake/modinfo at f32dfacc, resgx545:tools/closing/kit/fake/sha256sum at f32dfacc, resgx545:tools/closing/kit/fake/tool.sh at f32dfacc, resgx545:tools/closing/kit/fake/tool.py at f32dfacc, resgx545:tools/closing/kit/fake/ssh.py at f32dfacc, resgx545:tools/closing/scorekit.py at f32dfacc, resgx545:tools/closing/sessioncheck.py at f32dfacc, data:texture/p1141/templates/tx_map.s at 2d666bfa, data:texture/p1141/support/build.py at 2d666bfa, data:texture/p1141/support/texmodel.py at 2d666bfa, data:texture/p1141/support/specs.json at 2d666bfa, data:texture/p1141/gen/cases.json at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 2d666bfa, data:texture/p1141/stage-bins/p1141-t0b27__4.bin at 2d666bfa, data:texture/p1132/tx-t3/s64x32-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s32x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x16-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b10.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b12.txt.gz at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b12.txt.gz at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__0.bin at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__14.bin at 2d666bfa, data:isp/coverage-envelope/far/raw/1401720.txt.gz at 2d666bfa, data:isp/coverage-envelope/far/raw/1401724.txt.gz at 2d666bfa, resgx545:crates/sgx-pipe/src/zls.rs at f32dfacc, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/far/"]
terms = []
+++
**What ran.** tri --tri-unit 5 --tri-v (vertices on the 1/32 grid) --pixels on a 64 x 64 target, one
job per row, the plan's whole-pixel unit refused by the tool (unit 5 reaches +-2^24 and -2^25
pixels; +2^25 and 2^26 not reachable) and its tie rows dropped (README.md deviation 2); control
far-ctl is E684's case 1401720 in its own unit.

**Frozen verdict (as printed).** attempt 20261113-081821, stage far (run.log): `SUMMARY: far: H-CULL
is not supported: 0 held, 10 FAILED, 0 cannot tell of 10`; attempt 20261113-081821, stage far
(run.log): `SUMMARY: far: H-EXACT (10 of 10 rows decided)`; attempt 20261113-081821, stage far
(run.log): `SUMMARY: far: H-SAT is not supported: 5 held, 5 FAILED, 0 cannot tell of 10`; attempt
20261113-081821, stage far (run.log): `SUMMARY: far: H-WRAP is not supported: 2 held, 8 FAILED, 0
cannot tell of 10`.

**Results [HW].** Determined pixels matching H-EXACT: 4096 of 4096 or all but the 13 to 16 band
pixels in every row (drawn 312 to 3320). H-SAT matched where it equals H-EXACT (x22p, x23p, y22n,
y23p, 2a) and failed x24p, x25n, y24n, y25n, 2b (by 462 to 1268 pixels); H-WRAP failed every row
past 2^23 (x23p, x24p, x25n, y23p, y24n, y25n, 2a, 2b); H-CULL failed all ten.

**What it shows.** The vertex range is not clamped or wrapped at 2^23 pixels: up to 2^24 pixels both
ways and -2^25 pixels, one or two vertices, the ISP draws the exact triangle outside a 1e-3 pixel
band, and no job faulted. [infer] The vertex format holds at least 26 bits of signed whole pixels or
the clip-space path never forms a 24.8 word.

**What it does not show.** +2^25 pixels and beyond were not reachable with the tool; the band's
width as a function of distance (Q261's first half) is not measured (band pixels are undetermined,
not scored); sub-grid fractions and ties at far vertices are not shown.
