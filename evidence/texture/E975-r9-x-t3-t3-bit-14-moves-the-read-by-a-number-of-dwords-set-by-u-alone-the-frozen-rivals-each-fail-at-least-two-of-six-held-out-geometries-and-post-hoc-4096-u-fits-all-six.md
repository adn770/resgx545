+++
id = "E975"
claim = "r9-x stage t3 (19 jobs): with T3 bit 14 set in smp on named memory, on six held-out strided geometries (W 16, 32, 48 at strides 32, 64, 128, u off the texel centres and past the texture) each with its bit-14-clear reference (the references equal texmodel's image, 6 of 6), the frozen rival H-UCOL (the control column's centre, E968's R-U) failed 6 of 6, H-U01 (i + floor(S * S * clamp(u, 0, 1))) held 4 and failed 2 (W 32 at S 128 and at S 32), H-URAW held 3; post hoc (fold/t3_post.py, not frozen) every pixel of all six rows reads the reference's dword plus floor(4096 * clamp(u, 0, 1)) (12288 of 12288), S and W notwithstanding; T3 bits 11 and 12 on E566's strided 64 x 32 left the control image (replicates, 2 of 2) and E564's twiddled an-t3b11 and an-t3b12 replicated byte for byte; all three controls passed"
unit = "texture"
method = "r9-x (render/closing-r9-x), stage t3 of the question-closing pass (round 9, decision R9-2 (a), plan closing9/rank/rank-round9.md R9-A (Q078)), dataset render-closing-r9-x; attempt out/20261113-081821 (t3 08:18:22 Mac time; driver log run.log; its freeze FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37; scores score-t3.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74, installed and loaded alike), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner (kit/run_stage.sh), a debugfs reset and the health fill and triangle between jobs, every output and dump kept gzipped; the rows are tables/STAGE.txt, the frozen predictions predictions/STAGE.tsv and predictions/STAGE/ (gen/STAGE.py)); freezes: FROZEN.sha256 11292e03289f1a5147c6510706dd248eae88a906bd316f1938cfd06fbfd75c37 (216 files), PREDICTIONS.sha256 b0d34b59ae03da1b4c3261fc7dc44b929c7ba8e8c18f8f2a972d87c5e266da7c (91 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at f32dfacc, resgx545:tools/closing/kit/lib_kit.sh at f32dfacc, resgx545:tools/closing/kit/run_stage.sh at f32dfacc, resgx545:tools/closing/kit/kitscore.py at f32dfacc, resgx545:tools/closing/kit/fake/sudo at f32dfacc, resgx545:tools/closing/kit/fake/timeout at f32dfacc, resgx545:tools/closing/kit/fake/df at f32dfacc, resgx545:tools/closing/kit/fake/modinfo at f32dfacc, resgx545:tools/closing/kit/fake/sha256sum at f32dfacc, resgx545:tools/closing/kit/fake/tool.sh at f32dfacc, resgx545:tools/closing/kit/fake/tool.py at f32dfacc, resgx545:tools/closing/kit/fake/ssh.py at f32dfacc, resgx545:tools/closing/scorekit.py at f32dfacc, resgx545:tools/closing/sessioncheck.py at f32dfacc, data:texture/p1141/templates/tx_map.s at 2d666bfa, data:texture/p1141/support/build.py at 2d666bfa, data:texture/p1141/support/texmodel.py at 2d666bfa, data:texture/p1141/support/specs.json at 2d666bfa, data:texture/p1141/gen/cases.json at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-a.txt.gz at 2d666bfa, data:texture/p1141/stage-bins/p1141-t0b27__4.bin at 2d666bfa, data:texture/p1132/tx-t3/s64x32-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s32x32-t3b14.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x16-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b10.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-t3/s64x32-t3b12.txt.gz at 2d666bfa, data:texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/g-bl-st-b.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-ctl.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b11.txt.gz at 2d666bfa, data:texture/p1132/tx-lod/an-t3b12.txt.gz at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__0.bin at 2d666bfa, data:texture/p1132-recomp/raw/tx-t3bits/bins/tx-t3bits__14.bin at 2d666bfa, data:isp/coverage-envelope/far/raw/1401720.txt.gz at 2d666bfa, data:isp/coverage-envelope/far/raw/1401724.txt.gz at 2d666bfa, resgx545:crates/sgx-pipe/src/zls.rs at f32dfacc, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/t3/", "render-closing-r9-x:fold/"]
terms = ["T3.BIT14", "T3.BIT10"]
+++
**What ran.** Six bit-14 jobs on strided textures (b14-w16s64, b14-w32s128, b14-w32s32, b14-w48s64,
b14-u01, b14-u02w16) each followed by the same program with bit 14 clear (`-ref`), E566's s64x32-ctl
and s64x32-t3b14 reruns (controls), E566's s64x32-t3b11 and -t3b12 (replicates), E564's an-ctl
(control), an-t3b11 and an-t3b12 (replicates). Every program is E566's tx_map form (probe --coords
--pixels, scratch dword i = 0xD0000000 | i), the scratch pages sized to every rival's reads.

**Frozen verdict (as printed).** attempt 20261113-081821, stage t3 (run.log): `SUMMARY: t3: H-CTL (2
of 2 rows decided)`; attempt 20261113-081821, stage t3 (run.log): `SUMMARY: t3: H-E564 (2 of 2 rows
decided)`; attempt 20261113-081821, stage t3 (run.log): `SUMMARY: t3: H-TEXMODEL (6 of 6 rows
decided)`; attempt 20261113-081821, stage t3 (run.log): `SUMMARY: t3: H-U01 is not supported: 4
held, 2 FAILED, 0 cannot tell of 6`; attempt 20261113-081821, stage t3 (run.log): `SUMMARY: t3:
H-UCOL is not supported: 0 held, 6 FAILED, 0 cannot tell of 6`; attempt 20261113-081821, stage t3
(run.log): `SUMMARY: t3: H-URAW is not supported: 3 held, 3 FAILED, 0 cannot tell of 6`.

**Results [HW].** Controls t3-ctl, t3-b14ref and an-ctl: 2048 of 2048 pixels each. References: 2048
of 2048 under texmodel, six of six. Bit-14 rows (frozen): H-UCOL 0 of 2048 on every row; H-U01 2048
on w16s64, w48s64, u01 and u02w16, 0 on w32s128 and w32s32; H-URAW as H-U01 except 1024 on u02w16
(the pixels past the texture, where u passes 1). Post hoc: the offset kept - reference takes 64
values (33 on u02w16) and equals floor(4096 * clamp(u, 0, 1)) at every pixel of the six rows. Bits
11 and 12 (strided): 2048 of 2048 equal to the control. an-t3b11 and an-t3b12: 2048 of 2048 equal to
E564's kept images (2048 and 1 distinct values).

**What it shows.** The read under T3 bit 14 is the bit-clear dword plus a number of dwords set by u
alone, clamped to [0, 1], not by the stride or the width: the S * S of E968 and of H-U01 equals 4096
in every row where it held, and failed where S * S is not 4096. [infer] The constant 4096 (16 KiB of
32-bit texels) is what the post hoc reading names; it is not held out. Bits 11 and 12 do nothing on
a strided texture and reproduce on the twiddled chain.

**What it does not show.** No frozen rule held on all six rows; R-4096 was formed after the run and
needs a held-out row (another texel size, a twiddled texture, a v-dependent case). The twiddled
bit-11 and bit-12 reads are replicates, not decoded. tw32-t3b14 (E566's fault) was not rerun.

**Correction 2026-11-13:** E1003 (r10-tex stage t3b) held the post hoc reading out on six more
strided geometries, one of them a 16-bit format, where the read moved by floor(4096 * clamp(u, 0,
1)) texels (2048 dwords at u near 1), not dwords: the claim's "plus floor(4096 * clamp(u, 0, 1))"
counts texels, which are dwords on this record's 32-bit rows only. The measurements are unchanged.

**Correction 2026-11-13:** Round 11 offline (closing11/plan/c8-q078/, post hoc: the replicates
are E564's images byte for byte, not held out). The "read-out not decoded" of the twiddled bit 11
and bit 12 images is overtaken: with T3 bit 11 cleared every pixel reads level 0's texel (x, y),
with bit 12 set dword 5460, the 1 x 1 level of the chain (E564's appended correction). What sets
the level (a forced level, mips off or a LOD bias) is not parted by these images. The
measurements are unchanged.
