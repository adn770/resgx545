+++
id = "E1105"
claim = "r26-vol on module E0CC4027 (Q114): with each of 19 sampler-word bits flipped one at a time on E567's twiddled 16 x 16 format 12 texture (T0 bits 14, 15, 16, 27, 28, 29, 30; T3 bits 8, 9, 10, 11, 12, 15, 18, 20, 21, 22, 27, 28: the bits a record ran on a twiddled texture without a fault), smp3d with the third coordinate at 0 and at 1.5 gives the same image at all 2048 pixels for every bit ('H-NOVOL (19 of 19 rows decided)', no cannot tell; the repeats of T0 27 and 30 equal their w 0 jobs), so none of them makes the third coordinate act; the controls passed: E567's ty0-3d-w0, -w15 and the repeat read its kept image (2b49c848...), TEXTYPE 2's rt2-3d-w5 and -w15 its two different kept images (79970597..., 480213ab...)"
unit = "texture"
method = "r26-vol (render/closing-r26-vol), stages vc and vb of the question-closing pass (round 26: closing26/DECISIONS-R26.md, session r26-vol of the round 26 plan (closing26/plan/rank-round26.md), sections 2.1 and 4, R26-2 (a), safe class), dataset render-closing-r26-vol; attempt out/20261115-225136 (scores score-vb.txt, score-vc.txt); on the laptop (host cedar over the travel cable, kernel 7.3.0-resgx545, module srcversion E0CC40275493F8AEAD8180B (linux fork 456404fcffe5; installed and loaded alike), stock firmware, tool ~/sgxfive-test-t24 (t24, sha256 fd15fce4ca75b3868fd42b7e5d639ae8a3096fc895543e25a707bac9fb5db040, built on the laptop from resgx545 1341034 by lead/build_tool24_laptop.sh), every job `probe --temps 32 --coords --pixels` of one program, one process of the kit runner (kit/run_stage.sh) in table order, a debugfs reset between jobs and the health fill and triangle (t10) at the stage's ends, every output kept gzipped; the rows are tables/vc.txt and tables/vb.txt, the programs bins/ (E567's case text of probes/texture/tx-types.toml and tx-types-risky.toml in tx_map.s, assembled by usse-asm built from resgx545 95445c7; the four control programs byte for byte E567's kept ones) and the frozen predictions predictions/vc.tsv and vb.tsv (gen/make.py)); freezes: FROZEN.sha256 78a3fb2416fce2b990f85ae514c7a3342dcbd9d5c8130de0637294e4e36fb47c (98 files), PREDICTIONS.sha256 552284819056d1eebb33ce4eee793c731b988591e20fef44fb2449680705ddce (2 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 95445c7d, resgx545:tools/closing/kit/lib_kit.sh at 95445c7d, resgx545:tools/closing/kit/run_stage.sh at 95445c7d, resgx545:tools/closing/kit/kitscore.py at 95445c7d, resgx545:tools/closing/kit/fake/sudo at 95445c7d, resgx545:tools/closing/kit/fake/timeout at 95445c7d, resgx545:tools/closing/kit/fake/df at 95445c7d, resgx545:tools/closing/kit/fake/modinfo at 95445c7d, resgx545:tools/closing/kit/fake/sha256sum at 95445c7d, resgx545:tools/closing/kit/fake/tool.sh at 95445c7d, resgx545:tools/closing/kit/fake/tool.py at 95445c7d, resgx545:tools/closing/kit/fake/ssh.py at 95445c7d, resgx545:tools/closing/scorekit.py at 95445c7d, resgx545:tools/closing/sessioncheck.py at 95445c7d, resgx545:probes/texture/tx-types.toml at 95445c7d, resgx545:probes/texture/tx-types-risky.toml at 95445c7d, resgx545:probes/texture/templates/tx_map.s at 95445c7d, data:texture/p1132-recomp/raw/tx-types/bins/tx-types__1.bin at e639458f, data:texture/p1132-recomp/raw/tx-types/bins/tx-types__4.bin at e639458f, data:texture/p1132-recomp/raw/tx-types-risky/bins/tx-types-risky__4.bin at e639458f, data:texture/p1132-recomp/raw/tx-types-risky/bins/tx-types-risky__5.bin at e639458f, data:texture/p1132/tx-types/ty0-3d-w0.txt.gz at e639458f, data:texture/p1132/tx-types/ty0-3d-w15.txt.gz at e639458f, data:texture/p1132/tx-types-risky/rt2-3d-w5.txt.gz at e639458f, data:texture/p1132/tx-types-risky/rt2-3d-w15.txt.gz at e639458f, data:texture/p1132/tx-types/ind-t0b27.txt.gz at e639458f, data:texture/p1132/tx-types/ind-t0b30.txt.gz at e639458f, data:render/closing-r25-sa64/lead/build_tool24_laptop.sh at e639458f, data:render/closing-r10-st1/lead/build_tool10.sh at e639458f, 134103452432f328eac27ec148499cc3149cf83b at built, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: df2e8b82d089fe6d91e4a72f46ccfb22127a167a4008a529b398c4dfba14b13b 134103452432f328eac27ec148499cc3149cf83b:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=E0CC40275493F8AEAD8180B; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-15"
data = ["render-closing-r26-vol:out/20261115-225136/vc/", "render-closing-r26-vol:out/20261115-225136/vb/", "render-closing-r26-vol:fold/"]
terms = ["TEXTYPE", "T0.BIT27", "T3.BIT10", "T3.BITS19_18", "T3.BITS28_27"]
+++
**What ran.** Stage vc (controls, gate of vb): c-w0 and c-w15, E567's ty0-3d-w0 and ty0-3d-w15
(smp3d on the twiddled 16 x 16 texture, T0 0x07fe0000, T1 0x0c00f00f, T2 0x5caf0000, T3
0x00800800, point, the third coordinate r26 at 0 and 1.5), c-cube-w5 and c-cube-w15 (E567's
rt2-3d-w5 and -w15, TEXTYPE 2), c-w0b (c-w0 again), each frozen on E567's kept pixel sha256.
Stage vb: for each of the 19 bits, ty0-3d-w0 and ty0-3d-w15 with that one bit of T0 (r20) or T3
(r23) flipped (38 jobs), and the w 0 jobs of T0 27 and 30 repeated. Frozen H-NOVOL (each bit's
two images equal at 2048 pixels, E567's w3d=ignore with the bit set) against H-VOL (they differ);
a bit is cannot tell when a job did not print 2048 pixels or its repeat differs from its w 0 job.
No fit set: every bit row is held out.

**Frozen verdict (as printed).** attempt 20261115-225136, stage vc (score-vc.txt): `SUMMARY: vc:
controls all passed`; stage vb (score-vb.txt): `SUMMARY: vb: H-NOVOL (19 of 19 rows decided)`,
`BITS where w acts (H-VOL): none`. The scores reproduce byte for byte (fold/reproduce.out).

**Results [HW].** Controls: c-w0, c-w15 and c-w0b 2b49c848... (E567's ty0-3d-w0 and -w15),
c-cube-w5 79970597... and c-cube-w15 480213ab... (E567's rt2-3d-w5 and -w15). Bits: every pair
equal at 2048 of 2048 pixels; vb-t0b27-w0r and vb-t0b30-w0r equal their w 0 jobs. Post hoc, not
frozen: the w 0 image of 13 bits (T0 14, 15, 16, 28, 29; T3 8, 9, 11, 12, 15, 20, 21, 22) is
c-w0's at 2048 pixels; T0 27 and 30 and T3 10, 18, 27 and 28 change it (0, 0, 8, 8, 0 and 0
pixels equal c-w0's), as E564, E566 and E567 saw. No fault, hang or stop.

**What it shows.** On this texture none of the 19 bits makes smp3d's third coordinate change the
image, whether the bit leaves the 2D image as it is or changes it; with E567's eight jobs (w
ignored with the control's words) no sampler-word bit that runs on a twiddled texture without a
fault names a volume. TEXTYPE 2 still reads w (the cube, E726), so a w that acts is seen by this
method. Q114's word sweep (R12-7 a's rule, bounded by R26-2 a to the bits that ran without a
fault) found none.

**What it does not show.** The bits never run in a sampler table or that fault (T0 0, 2, 31; T3
13, 14, 19, 24 to 26; T1's size bits; T2), which stay Q300's; other textures, sizes, formats or
filters; w values other than 0 and 1.5 (E567's sweeps cover 0 to 2 at the control's words only);
two bits at once. [infer] A volume layout, if the core has one, is not selected by any single one
of these bits.
