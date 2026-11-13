+++
id = "E989"
claim = "r10-st1 rows q071-b0 and q071-l1 (2 jobs): with CR_ISP_ZLSCTL's bits that E411 flipped singly to no effect flipped together under a stencil test (0xf8e6a00e: bits 15, 21 to 23 and 27 to 31 set, 12, 16 and 20 cleared, from E988's 0x0017300e), H-INERT failed 2 of 2: each row drew all 2048 pixels where its base row drew 1024, and stored 0xff at every byte of the 512 stencil dwords of the target's tiles, as a test reading 0 and inverting it would; the depth dump and the loaded stencil buffer are byte for byte the base rows'"
unit = "isp"
method = "r10-st1 (render/closing-r10-st1), stage st1 of the question-closing pass (round 10, decision R10-4 (a) of closing10/rank/rank-round10.md (Q071's stencil clause, riding stage st1)), dataset render-closing-r10-st1; attempt out/20261113-103934 (st1 10:39:34 Mac time; driver log run.log; its freeze FROZEN.sha256 3327dc6be2f95aa7a790e0b456cdf29f2c212ea6345b0a0b529ceb4bb58b6841; scores score-st1.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06 by lead/build_tool10.sh), every job one process of the kit runner, a debugfs reset and the health pair between jobs, every output and dump kept; the rows q071-b0 and q071-l1 of tables/st1.txt, the predictions predictions/st1.tsv (gen/st1.py)); freezes: FROZEN.sha256 3327dc6be2f95aa7a790e0b456cdf29f2c212ea6345b0a0b529ceb4bb58b6841 (41 files), PREDICTIONS.sha256 9ea349f57a1fcc6f540662cd79e17707d11ee0965b1a919f731a026b8b42ecc1 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 287031c6, resgx545:tools/closing/kit/lib_kit.sh at 287031c6, resgx545:tools/closing/kit/run_stage.sh at 287031c6, resgx545:tools/closing/kit/kitscore.py at 287031c6, resgx545:tools/closing/kit/fake/sudo at 287031c6, resgx545:tools/closing/kit/fake/timeout at 287031c6, resgx545:tools/closing/kit/fake/df at 287031c6, resgx545:tools/closing/kit/fake/modinfo at 287031c6, resgx545:tools/closing/kit/fake/sha256sum at 287031c6, resgx545:tools/closing/kit/fake/tool.sh at 287031c6, resgx545:tools/closing/kit/fake/tool.py at 287031c6, resgx545:tools/closing/kit/fake/ssh.py at 287031c6, resgx545:tools/closing/scorekit.py at 287031c6, resgx545:tools/closing/sessioncheck.py at 287031c6, data:render/closing-r9-x/tables/zst.txt at 1324301b, resgx545:crates/sgx-pipe/src/zls.rs at 287031c6, resgx545:userspace/libsgxfive/src/render.c at 287031c6, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 287031c6, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-st1:out/20261113-103934/st1/", "render-closing-r10-st1:fold/"]
terms = ["CR_ISP_ZLSCTL", "ISP2", "ISP2.SOP3"]
+++
**What ran.** q071-b0 is E988's st1-b0 (the `bytes` fill, EQUAL against reference 0 with mask 0x01,
pass operation invert) and q071-l1 E988's st1-lane1 (fill 0x03020100, mask 0x02), each with the
control 0xf8e6a00e in place of 0x0017300e: r10-x's zbits mask (E411's inert bits all flipped at
once), the load, store and pitch fields unchanged. Frozen: H-INERT, the image and the stencil-store
dump equal to the base row's. Post hoc: fold/q071_look.py (fold/q071_look.out).

**Frozen verdict (as printed).** attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1:
H-DEPTHORD (13 of 13 rows decided)`; attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1:
H-F2ORD is not supported: 3 held, 10 FAILED, 0 cannot tell of 13`; attempt 20261113-103934, stage
st1 (run.log): `SUMMARY: st1: H-INERT is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`;
attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1: H-NOLOAD is not supported: 0 held, 13
FAILED, 0 cannot tell of 13`; attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1: H-RASTER
is not supported: 0 held, 13 FAILED, 0 cannot tell of 13`.

**Results [HW].** q071-b0: 2048 pixels drawn against st1-b0's 1024 (the 1024 pixels of lanes 1 and 3
added), stencil store 0xffffffff at all 512 dwords of the four tile slots and 0xdeadbeef past them;
q071-l1: 2048 against 1024 (lanes 2 and 3 added), the same store. The depth dump (0x3f800000
throughout) and the stencil load buffer equal the base rows'.

**What it shows.** One or more of bits 12, 15, 16, 20 to 23 and 27 to 31 change the stencil test:
with all of them flipped the test acts as if the stencil were 0 (every EQUAL-to-0 test passes and
the invert stores 0xff), not on the loaded byte [infer: the load of the stencil or the test's input
is switched off]. So these bits are not inert under a stencil test, which E411's single flips
without a test could not see.

**What it does not show.** Which bit or bits do it (the flips were together), whether the depth path
changes (the depth test was always and depth writes off), and what the bits do without a stencil
load.
