+++
id = "E988"
claim = "r10-st1 stage st1 (16 jobs of 18, tool t10, `tri --isp2`): against a loaded stencil (CR_ISP_ZLSCTL 0x0017300e) ISP word 2's test reads, for pixel (x, y), byte j of its tile slot's 512 with j the depth's in-tile index y0 x0 y1 x1 y2 x2 y3 x3 x4: H-DEPTHORD held out 13 of 13 rows, the image and every stored stencil byte of the target's pixels (8 rows reading bit k of j for every pixel through the bytes fill, the bytes:1 carry row, two lane rows of 0x03020100 and two 40 x 20 edge rows); EQUAL against reference 0 drew exactly the pixels whose byte and mask are 0 and stored them inverted (the pass operation), the others copied; H-RASTER 0, H-F2ORD 3 (rows where its order agrees) and H-NOLOAD 0 of 13; the controls passed (always 2048, never 0, without --isp2 2048); post hoc, at 40 x 20 the bytes past the target are the loaded ones but in E831's band, where the test acts as inside (1248 of 1248 in both edge rows)"
unit = "zls"
method = "r10-st1 (render/closing-r10-st1), stage st1 of the question-closing pass (round 10, decisions R10-4 (a) and R10-6 (a), plan closing10/seeds/exp-seeds-r10.md section 5 (stage st1)), dataset render-closing-r10-st1; attempt out/20261113-103934 (st1 10:39:34 Mac time; driver log run.log; its freeze FROZEN.sha256 3327dc6be2f95aa7a790e0b456cdf29f2c212ea6345b0a0b529ceb4bb58b6841; scores score-st1.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, built from resgx545 a581c06 by lead/build_tool10.sh, whose printed recipe line names closing-r10-zls: the copy is byte for byte), every job one process of the kit runner, a debugfs reset and the health pair between jobs, every output and dump kept; the rows are tables/st1.txt, the predictions predictions/st1.tsv (gen/st1.py)); freezes: FROZEN.sha256 3327dc6be2f95aa7a790e0b456cdf29f2c212ea6345b0a0b529ceb4bb58b6841 (41 files), PREDICTIONS.sha256 9ea349f57a1fcc6f540662cd79e17707d11ee0965b1a919f731a026b8b42ecc1 (1 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 287031c6, resgx545:tools/closing/kit/lib_kit.sh at 287031c6, resgx545:tools/closing/kit/run_stage.sh at 287031c6, resgx545:tools/closing/kit/kitscore.py at 287031c6, resgx545:tools/closing/kit/fake/sudo at 287031c6, resgx545:tools/closing/kit/fake/timeout at 287031c6, resgx545:tools/closing/kit/fake/df at 287031c6, resgx545:tools/closing/kit/fake/modinfo at 287031c6, resgx545:tools/closing/kit/fake/sha256sum at 287031c6, resgx545:tools/closing/kit/fake/tool.sh at 287031c6, resgx545:tools/closing/kit/fake/tool.py at 287031c6, resgx545:tools/closing/kit/fake/ssh.py at 287031c6, resgx545:tools/closing/scorekit.py at 287031c6, resgx545:tools/closing/sessioncheck.py at 287031c6, data:render/closing-r9-x/tables/zst.txt at 1324301b, resgx545:crates/sgx-pipe/src/zls.rs at 287031c6, resgx545:userspace/libsgxfive/src/render.c at 287031c6, resgx545:userspace/libsgxfive/tools/sgxfive-test.c at 287031c6, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-st1:out/20261113-103934/st1/", "render-closing-r10-st1:fold/"]
terms = ["CR_ISP_ZLSCTL", "ISP2", "ISP2.SCMP_MODE", "ISP2.SOP3", "ISP0.SREF", "ISP0.ISP2_PRESENT", "CR_ISP_STENCIL_LOAD_BASE", "CR_ISP_STENCIL_STORE_BASE"]
+++
**What ran.** Every row `tri --tri-full --depth --stencil --stencil-store --pixels` at 64 x 32 (two
rows 40 x 20, `--depth-pages 16`) with E978's control 0x0017300e (the stencil loaded, depth and
stencil stored, G 1) and `--isp2 V`: ISP word 0 0x01d00300 (reference 0, the depth test always), V =
mode << 25 | 5 << 16 | m << 8 | 0xff. Fills: `bytes` (byte b of the buffer holds b & 0xff) with m =
1 << k, k 0 to 7; `bytes:1` with m 0x02; 0x03020100 with m 0x01 and 0x02; at 40 x 20 `bytes` with m
0x01 and 0x10. Controls: mode 7, mode 0, and no --isp2. Post hoc: fold/q071_look.py
(fold/q071_look.out, its edge-row lines).

**Frozen verdict (as printed).** attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1:
H-DEPTHORD (13 of 13 rows decided)`; attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1:
H-F2ORD is not supported: 3 held, 10 FAILED, 0 cannot tell of 13`; attempt 20261113-103934, stage
st1 (run.log): `SUMMARY: st1: H-INERT is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`;
attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1: H-NOLOAD is not supported: 0 held, 13
FAILED, 0 cannot tell of 13`; attempt 20261113-103934, stage st1 (run.log): `SUMMARY: st1: H-RASTER
is not supported: 0 held, 13 FAILED, 0 cannot tell of 13`.

**Results [HW].** Every held-out row: the drawn pixels are those whose byte (j + S) & 0xff has the
mask's bits 0, 1024 of 2048 at 64 x 32 (400 and 480 of 800 at 40 x 20), none extra, and the stored
stencil byte of every target pixel the loaded one inverted where drawn and copied where not (2048 of
2048 bytes; 800 of 800). The raster order drew 512 extra pixels on every row, the 16-bit format's
order 512 extra on 10 rows (it agrees on bit 0, bit 7 and lane 0), the no-load rival 1024 pixels
short. Past the 40 x 20 target, the stored bytes are inverted exactly where x + 0.5 < 1.25 W, y +
0.5 < 1.25 H and the test passes (250 and 170 bytes) and the loaded ones elsewhere.

**What it shows.** Q121's two clauses: the stencil store and load hold a pixel's stencil at the
depth's in-tile index, one byte a pixel, 512 bytes a tile slot at the depth's pitch, every lane
(E985 read lane 0 from E978's copies), and the stencil test of ISP word 2 (E284's fields) reads that
loaded byte, its pass operation's result stored in its place. The test runs over E831's band past an
edge target as the depth store does.

**What it does not show.** The other compare modes and operations against a loaded stencil (E284 ran
them against the background stencil), the depth-fail operation with a loaded stencil, a test with
depth writes, other pitches and sizes than 64 x 32 and 40 x 20.
