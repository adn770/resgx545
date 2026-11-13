+++
id = "E977"
claim = "r9-x stage zls (16 jobs): stored depth format 1 is min(floor(z * 2^24), 0xffffff) of the format-0 float at every dword (frozen H-FLOOR held 3 of 3: 32768, 76800 and 3200 dwords at 256 x 128 G 7 over z 0 to 0.5, 320 x 240 G 9 and 80 x 40 G 2 over 0.5 to 1; H-ROUND, round(z * 0xffffff) of E466, failed 0 of 76800 and 0 of 3200 and held only below 0.5) and format 2 is the same >> 8 in E490's 16-bit layout at all three pitches (H-E490/H-FLOOR 3 of 3, the 512-dword slot spacing refuted); a load of format 1 or 2 compares the loaded dword as a float (H-RAW held 2 of 2: 0x00400000 failed less against 0.125, 0x3fff3fff passed less against 0.5; the integer back-conversion failed both); a loaded NaN (0x7fc00000) passed less and failed greater against 0.5, and infinity passed less and failed greater (IEEE held 3 of 4, failing on NaN under less); all four controls passed"
unit = "zls"
method = "r9-x (render/closing-r9-x), stage zls of the question-closing pass (round 9, decision R9-2 (a), plan closing9/rank/rank-round9.md R9-C (Q242, Q243)), dataset render-closing-r9-x; attempt out/20261113-081821 (zls 08:21:06 Mac time; driver log run.log; its freeze FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37; scores score-zls.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/STAGE.py)); freezes: FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37 (216 files), PREDICTIONS.sha256 b0d34b59ae03da1b4c3261fc7dc44b929c7ba8e8c18f8f2a972d87c5e266da7c (91 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at f32dfacc, resgx545:tools/closing/kit/lib_kit.sh at f32dfacc, resgx545:tools/closing/kit/run_stage.sh at f32dfacc, resgx545:tools/closing/kit/kitscore.py at f32dfacc, resgx545:tools/closing/kit/fake/sudo at f32dfacc, resgx545:tools/closing/kit/fake/timeout at f32dfacc, resgx545:tools/closing/kit/fake/df at f32dfacc, resgx545:tools/closing/kit/fake/modinfo at f32dfacc, resgx545:tools/closing/kit/fake/sha256sum at f32dfacc, resgx545:tools/closing/kit/fake/tool.sh at f32dfacc, resgx545:tools/closing/kit/fake/tool.py at f32dfacc, resgx545:tools/closing/kit/fake/ssh.py at f32dfacc, resgx545:tools/closing/scorekit.py at f32dfacc, resgx545:tools/closing/sessioncheck.py at f32dfacc, data:texture/p1141/templates/tx_map.s at 2d666bfa, data:texture/p1141/support/build.py at 2d666bfa, data:texture/p1141/support/texmodel.py at 2d666bfa, data:texture/p1141/support/specs.json at 2d666bfa, data:texture/p1141/gen/cases.json at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 2d666bfa, data:texture/p1141/stage-bins/p1141-t0b27__4.bin at 2d666bfa, data:texture/p1132/tx-t3/s64x32-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s32x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x16-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b10.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b12.txt.gz at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b12.txt.gz at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__0.bin at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__14.bin at 2d666bfa, data:isp/coverage-envelope/far/raw/1401720.txt.gz at 2d666bfa, data:isp/coverage-envelope/far/raw/1401724.txt.gz at 2d666bfa, resgx545:crates/sgx-pipe/src/zls.rs at f32dfacc, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/zls/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** Q242: one triangle over (0,0) (2W,0) (0,2H) at depths 0, 1, 0 (rising) or 1, 0, 1
(falling), stored with E466's control (G the tiles across minus one) in format 0, then 1, then 2,
depth less with writes, each dump kept; Q243: one render loading a constant-filled depth buffer
(bits 1 and 14) into a separate store, 64 x 32, a flat triangle under less or greater, the reading
the drawn count; control z243-ctl loads 0.75 under less (E467).

**Frozen verdict (as printed).** attempt 20261113-081821, stage zls (run.log): `SUMMARY: zls:
H-E490/H-FLOOR (3 of 3 rows decided)`; attempt 20261113-081821, stage zls (run.log): `SUMMARY: zls:
H-E490/H-ROUND is not supported: 1 held, 2 FAILED, 0 cannot tell of 3`; attempt 20261113-081821,
stage zls (run.log): `SUMMARY: zls: H-FLOOR (3 of 3 rows decided)`; attempt 20261113-081821, stage
zls (run.log): `SUMMARY: zls: H-IEEE is not supported: 3 held, 1 FAILED, 0 cannot tell of 4`;
attempt 20261113-081821, stage zls (run.log): `SUMMARY: zls: H-INFZERO is not supported: 0 held, 2
FAILED, 0 cannot tell of 2`; attempt 20261113-081821, stage zls (run.log): `SUMMARY: zls: H-INT is
not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; attempt 20261113-081821, stage zls (run.log):
`SUMMARY: zls: H-NANPASS is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; attempt
20261113-081821, stage zls (run.log): `SUMMARY: zls: H-RAW (2 of 2 rows decided)`; attempt
20261113-081821, stage zls (run.log): `SUMMARY: zls: H-ROUND is not supported: 1 held, 2 FAILED, 0
cannot tell of 3`; attempt 20261113-081821, stage zls (run.log): `SUMMARY: zls: H-SLOT512/H-FLOOR is
not supported: 0 held, 3 FAILED, 0 cannot tell of 3`; attempt 20261113-081821, stage zls (run.log):
`SUMMARY: zls: H-SLOT512/H-ROUND is not supported: 0 held, 3 FAILED, 0 cannot tell of 3`.

**Results [HW].** Format-0 controls: 32768, 76800 and 4608 dwords changed (every dword of the tiles,
E831). Format 1: H-FLOOR 32768/32768, 76800/76800, 3200/3200; H-ROUND 32768/32768 (z below 0.5),
0/76800, 0/3200. Format 2: H-E490/H-FLOOR 16384/16384, 38400/38400, 1600/1600; H-E490/H-ROUND 16384,
34365, 1443; the 512 spacing 1024, 2048, 494. Loads (drawn of 2048): ctl 2048; f1-less 0; f2-less
2048; nan-less 2048; nan-gt 0; inf-less 2048; inf-gt 0.

**What it shows.** The 24-bit format stores floor(z * 2^24) clamped to 24 bits, the 16-bit one its
>> 8, with E490's 16-bit layout at pitches other than 33 and on a target with edge tiles (within the
target): E466's round(z * 0xffffff) agrees with it only where the dumps lay (0.25 to 0.4166 and
below 0.5 on the rising ramp). A load of an integer format does not convert back: the depth test
reads the stored dword as a float32, and the pass/fail of all six load rows matches an unsigned
compare of the bit patterns [infer: a float compare of non-negative values, NaN ordered above every
finite value].

**What it does not show.** Values past the target in edge tiles for the integer formats were not
scored; the loads ran at one size and one address (the moved base of Q243 stays); a loaded NaN under
equal and the other compare modes did not run.
