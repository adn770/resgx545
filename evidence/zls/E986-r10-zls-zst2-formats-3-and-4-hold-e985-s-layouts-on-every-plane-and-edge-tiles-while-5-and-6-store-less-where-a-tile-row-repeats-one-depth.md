+++
id = "E986"
claim = "r10-zls stage zst2 (26 jobs, the stencil loaded and stored): E985's layouts held out byte for byte on 13 of 16 rows, formats 3 and 4 on every plane (E978's x ramp with stencil fills 0x00000000, 0xffffffff and 0xa5a5a5a5, a y ramp, the plane z = x / 2W + y / 2H from 0.012 to 0.988, and 40 x 20's edge tiles) and formats 5 and 6 on that plane; formats 5 and 6 stored fewer dwords and held no frozen model where each tile row holds one depth (the y ramp: 988 and 212 changed dwords) and format 6 at the edge tiles (1364 of 2048, constant past the target); the raster and 16-bit stencil orders failed 7 of 7 and format 6's in-tile order 3 of 3; no format 3 to 7 wrote the stencil store (21 of 21); format 7 stored 48 dwords under a constant stencil and 784 under the index one; the five controls passed, z2x-f0 byte for byte E978's z120-ctl-s"
unit = "zls"
method = "r10-zls (render/closing-r10-zls), stage zst2 of the question-closing pass (round 10, decision R10-4 (a), plan closing10/seeds/exp-seeds-r10.md section 5), dataset render-closing-r10-zls; attempt out/20261113-102039 (zst2 10:20:39 Mac time; driver log run.log; its freeze FROZEN.sha256 9b2abee89bbac2ffa239877c9bb6d68f131d5dcf0763c1e58cbeff6baf9a80ed; scores score-zst2.txt); on the laptop (host cedar, kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (linux fork 2a650d74), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, built from resgx545 4623753), every job one process of the kit runner, a debugfs reset and the health pair between jobs, every output and dump kept; the rows are tables/zst2.txt, the predictions predictions/zst2.tsv (gen/zst2.py, E985's frozen rules as code)); freezes: FROZEN.sha256 9b2abee89bbac2ffa239877c9bb6d68f131d5dcf0763c1e58cbeff6baf9a80ed (60 files), PREDICTIONS.sha256 27b5b614decf201f2ea70b566948e52dc554d435b46f6af4f2d22a8ed954918d (4 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at 9849dab7, resgx545:tools/closing/kit/lib_kit.sh at 9849dab7, resgx545:tools/closing/kit/run_stage.sh at 9849dab7, resgx545:tools/closing/kit/kitscore.py at 9849dab7, resgx545:tools/closing/kit/fake/sudo at 9849dab7, resgx545:tools/closing/kit/fake/timeout at 9849dab7, resgx545:tools/closing/kit/fake/df at 9849dab7, resgx545:tools/closing/kit/fake/modinfo at 9849dab7, resgx545:tools/closing/kit/fake/sha256sum at 9849dab7, resgx545:tools/closing/kit/fake/tool.sh at 9849dab7, resgx545:tools/closing/kit/fake/tool.py at 9849dab7, resgx545:tools/closing/kit/fake/ssh.py at 9849dab7, resgx545:tools/closing/scorekit.py at 9849dab7, resgx545:tools/closing/sessioncheck.py at 9849dab7, data:render/closing-r9-x/out/20261113-081821/zst/z120-ctl-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f3-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f3-s.stencil.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f4-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f4-s.stencil.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zst/z120-f6-s.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/out/20261113-081821/zls/z242-a-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-z2/out/20261113-082522/z2/z2-a-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-z2/out/20261113-082522/z2/z2-b-f0.depth.1.bin.gz at 1324301b, data:render/closing-r9-x/tables/zst.txt at 1324301b, data:render/closing-r9-x/tables/zls.txt at 1324301b, data:render/closing-r9-k1/lead/build_tool9.sh at 1324301b, resgx545:crates/sgx-pipe/src/zls.rs at 9849dab7, 4623753f2cc5b9a34b357736801a4c6e66138bf9 at built, 97447b04b38cadac7733f0cd12503e2ef207a3bf at built; tools: TOOLSRC.sha256: 703cbceaae8cdff3eda280b7ef89f3c5ef14ba7d378dd269bc66ef714aaead69 4623753f2cc5b9a34b357736801a4c6e66138bf9:userspace/libsgxfive/tools/sgxfive-test.c; TOOLSRC.sha256: 5de429431a93ddbdcd9c20141f5c286dcc5cc72265f95d662279e09b655a3f50 97447b04b38cadac7733f0cd12503e2ef207a3bf:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=B60AB0B475DD1E8972419B5; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r10-zls:out/20261113-102039/zst2/", "render-closing-r10-zls:fold/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_STENCIL_LOAD_BASE", "CR_ISP_STENCIL_STORE_BASE"]
+++
**What ran.** Four depth planes at 64 x 32 (G 1), each with its format-0 reference (a control:
E831's 2048 dwords and E467's 512 stencil-store dwords): x, E978's ramp `--tri-full --tri-z
0.25,0.75,0.25`, in formats 3, 4 and 7 with three constant stencil fills plus z2x-f4 (E978's
z120-f4-s, a control); y (`--tri-z 0.25,0.25,0.75`) and d (the triangle (0,0) (128,0) (0,64) at
depths 0, 1, 1) in formats 3 to 7; e, the x ramp at 40 x 20 (`--depth-pages 16`) in formats 3 and 6.
Every row loads an index or constant stencil (bits 1 and 13) and stores it (bit 17), depth less with
writes. Post hoc: fold/look.py (fold/look.out).

**Frozen verdict (as printed).** attempt 20261113-102039, stage zst2 (run.log): `SUMMARY: zst2:
H-E978 (no stencil store) (21 of 21 rows decided)`; attempt 20261113-102039, stage zst2 (run.log):
`SUMMARY: zst2: H-E985 is not supported: 13 held, 3 FAILED, 0 cannot tell of 16`; attempt
20261113-102039, stage zst2 (run.log): `SUMMARY: zst2: H-E985/H-F2ORD is not supported: 0 held, 7
FAILED, 0 cannot tell of 7`; attempt 20261113-102039, stage zst2 (run.log): `SUMMARY: zst2:
H-E985/H-RASTER is not supported: 0 held, 7 FAILED, 0 cannot tell of 7`; attempt 20261113-102039,
stage zst2 (run.log): `SUMMARY: zst2: H-F6ITI is not supported: 0 held, 3 FAILED, 0 cannot tell of
3`.

**Results [HW].** Controls: 2048 depth and 512 stencil-store dwords on each format-0 reference (40 x
20: 2048, its stencil count a reading, 512), z2x-f4 640 and E985's f4 layout, z2x-f0 equal to E978's
z120-ctl-s dump. Held (every predicted byte, every changed dword predicted whole): z2x-f3 and z2x-f4
under the three fills (10240 and 2560 bytes), z2y-f3, z2y-f4, z2d-f3, z2d-f4, z2d-f5, z2d-f6,
z2e-f3. Not held: z2y-f5 (988 changed dwords; 741 of 10240 predicted bytes), z2y-f6 (212; 68 of
8192), z2e-f6 (1364; 2181 of 8192; block 0 whole, the other three 316, 332 and 204). z2d-f5 is
byte-identical to z2d-f3, z2y-f5 is not to z2y-f3. Format 7: 48 changed dwords under each constant
fill, none equal to format 4's of the same fill at its offset; 784 under the index fill in the y and
d planes, 320 of them equal to format 4's. Stencil store: 0 changed dwords on all 21 rows of formats
3 to 7.

**What it shows.** Formats 3 and 4 are E985's layouts whatever the depth plane and the stencil
bytes, edge tiles included: a 5-byte record a pixel (the float with its sign set, then the stencil
byte) and format 4's records of 0xf0 and four stencil bytes. Formats 5 and 6 are format 3's and
E985's float layout when every pixel of a tile row has its own depth, and store less when a row
repeats one depth or a tile holds the constant background [infer: a compressed form keyed by the
row's or the tile's values]. Format 7 depends on the stencil data [infer: compressed as well]. None
of 3 to 7 writes the stencil store.

**What it does not show.** The compressed layouts of formats 5 and 6 and format 7's, which the first
dwords in fold/look.out only begin to show; formats 3 to 7 without a stencil buffer at these sizes;
a load of formats 3 to 7.
