+++
id = "E981"
claim = "r9-z2 stage z2 (10 jobs, 256 x 128, G 7): with the viewport's z offset (state-block word 10) at -0.25, so a modelled depth of -0.75 to -0.25, format 0 stored 0.0 at every dword and formats 1 and 2 stored 0 at every dword with and without bit 19 (byte-identical dumps), so the four frozen rivals collapse there (each held 4 of 8 rows: ramp b's four); with the offset at +0.25 the stored depth ran 0.00059 to 0.2994 (not the modelled -0.25 to +0.25, never 0 or negative), and formats 1 and 2 match min(floor(z * 2^24), 0xffffff) and its >> 8 at every dword with and without bit 19 (byte-identical), missing round(z * 0xffffff), the rivals' encoding, at 8803 of 32768 dwords; both format-0 controls passed (32768 dwords)"
unit = "zls"
method = "r9-z2 (render/closing-r9-z2), stage z2 of the question-closing pass (round 9, decision R9-3 (a), plan closing9/rank/rank-round9.md R9c-F (Q101)), dataset render-closing-r9-z2; attempt out/20261113-082522 (z2 08:25:22 Mac time; driver log run.log; its freeze FROZEN.sha256 9c2c54cd0412ab17a349f7e8b65d5a8c23a7d7a67cadc3ec1b0c4456accbe5e4; scores score-z2.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5, stock firmware, tool ~/sgxfive-test-t9 (sha256 7a28be3952fb310170e861da0622d890a2e215cb761d6f21bc9321223e1b40ce, built from resgx545 97447b04 by lead/build_tool9.sh, whose header still names r9-k1: the frozen byte copy), every job one process of the kit runner, a debugfs reset and the health pair between jobs, every output and dump kept; the rows are tables/z2.txt, the predictions predictions/z2.tsv (gen/z2.py)); freezes: FROZEN.sha256 9c2c54cd0412ab17a349f7e8b65d5a8c23a7d7a67cadc3ec1b0c4456accbe5e4 (39 files), PREDICTIONS.sha256 2045d072f582c36cdf31b99499006ef50bca5803a85b90dcd8407bb8b9016bcc (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 02ae0a0e, resgx545:tools/closing/kit/lib_kit.sh at 02ae0a0e, resgx545:tools/closing/kit/run_stage.sh at 02ae0a0e, resgx545:tools/closing/kit/kitscore.py at 02ae0a0e, resgx545:tools/closing/kit/fake/sudo at 02ae0a0e, resgx545:tools/closing/kit/fake/timeout at 02ae0a0e, resgx545:tools/closing/kit/fake/df at 02ae0a0e, resgx545:tools/closing/kit/fake/modinfo at 02ae0a0e, resgx545:tools/closing/kit/fake/sha256sum at 02ae0a0e, resgx545:tools/closing/kit/fake/tool.sh at 02ae0a0e, resgx545:tools/closing/kit/fake/tool.py at 02ae0a0e, resgx545:tools/closing/kit/fake/ssh.py at 02ae0a0e, resgx545:tools/closing/scorekit.py at 02ae0a0e, resgx545:tools/closing/sessioncheck.py at 02ae0a0e, resgx545:crates/sgx-pipe/src/zls.rs at 02ae0a0e, 97447b04b38cadac7733f0cd12503e2ef207a3bf at built; tools: TOOLSRC.sha256: 5de429431a93ddbdcd9c20141f5c286dcc5cc72265f95d662279e09b655a3f50 97447b04b38cadac7733f0cd12503e2ef207a3bf:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-z2:out/20261113-082522/z2/", "render-closing-r9-z2:fold/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** Two ramps (the triangle over (0,0) (512,0) (0,256) at depths 0, 1, 0, the z offset
poked to +0.25 or -0.25), each stored in format 0 and in formats 1 and 2 without and with bit 19,
depth less with writes; dumps kept. Post hoc: fold/look.py (fold/look.out).

**Frozen verdict (as printed).** attempt 20261113-082522, stage z2 (run.log): `SUMMARY: z2: H-ABS is
not supported: 4 held, 4 FAILED, 0 cannot tell of 8`; attempt 20261113-082522, stage z2 (run.log):
`SUMMARY: z2: H-B19 is not supported: 4 held, 4 FAILED, 0 cannot tell of 8`; attempt
20261113-082522, stage z2 (run.log): `SUMMARY: z2: H-CLAMP is not supported: 4 held, 4 FAILED, 0
cannot tell of 8`; attempt 20261113-082522, stage z2 (run.log): `SUMMARY: z2: H-WRAP is not
supported: 4 held, 4 FAILED, 0 cannot tell of 8`.

**Results [HW].** Format-0 controls: 32768 dwords changed each. Ramp b: format 0 all 0x00000000 at y
= 0 (256 of 256) and at every dword read; formats 1 and 2 0 at every dword, bit 19 or not. Ramp a:
format 0 from 0.0005859 (x 0) to 0.2994 (x 255) at y = 0; formats 1 and 2 = the floor rule at 32768
of 32768 and 16384 of 16384 dwords, bit 19 or not; the frozen rivals (all round-based) 23965 of
32768 and 15600 of 16384.

**What it shows.** A depth below 0 made after the clip reaches the store as 0 in every format
[infer: clamped to 0 before the store, as E287's compare of a negative depth as 0], so bit 19 cannot
meet a negative integer depth this way, and over 0 to 0.3 bit 19 changes no dword of formats 1 and 2
(E490's finding, at a new range). The integer rows follow E977's floor rule, a second held set at a
new geometry (post hoc here: the frozen rivals used round).

**What it does not show.** What the poke of word 10 does to the depth plane is not shown (ramp a's
0.6 t is a post hoc reading); a negative float reaching the integer conversion, and bit 19 with
format 0 below 0, did not run. The route of the plan (--tri-z outside [0, 1]) is clipped by the MTE
(E287) and was not used.
