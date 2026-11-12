+++
id = "E904"
claim = "r7-rp stages q291g and q291 (Q291, 27 jobs with t6): the pixel tasks past the target run over the ZLS store's band and nowhere else, with the attribute iterated linearly there: with E898's position-store program (each valid instance stores its iterated pa0 and pa1 and its lane at the scratch slot of its place in its 32 x 16 tile), E437's position pair (pa0 = x + 0.5, pa1 = y + 0.5) and one tile touched a job, the set of slots that held a valid instance's store was rule A's band cut to the tile and the triangle (x + 0.5 < 1.25 W, y + 0.5 < 1.25 H; H-BAND) in 12 of 12 held-out rows (18 x 12, 24 x 8, 12 x 12, 20 x 8, 26 x 10 and 10 x 6 on one tile; W 34, 36, 44 and 50 at H 16 and H 18 and 24 at W 32 with the triangle cut to one tile: 330, 300, 225, 250, 384, 84, 160, 208, 368, 480, 192 and 448 slots), against 0 of 12 for H-TARGET (the target's pixels only) and H-TILE (the whole tile), and every stored pa0 and pa1 was f32(x + 0.5) and f32(y + 0.5) of the slot past the target too (H-LIN, 12 of 12 rows); the vertex pair (E606: pa0 the clip z, pa1 the clip x iterated) gave the band at 20 x 12, 18 x 12 and 24 x 8 (3 of 3) with clip x within E661's tolerance; the fit pair 20 x 12 stored 375 slots twice; the depth twins (E885's depth row at 20 x 12, 18 x 12, 24 x 8, 12 x 12 and 10 x 6) stored rule A's sets, 375, 330, 300, 225 and 84 dwords (5 of 5); the gate row (32 x 16, all 512 slots, each its position and lane), the pix_pa0 image and the cut-triangle and vertex controls passed; frozen verdict 'Q291 H-BAND held: held-out P 12 held, 0 FAILED, 0 cannot tell of 12; rivals H-TARGET 0, H-TILE 0; values H-LIN held (12 held ...); fit pair held; vertex pair H-BAND 3 held ..., values E661 held (3 held ...); depth twins rule A 5 held ...'"
unit = "zls"
method = "r7-rp stages q291g and q291 of the question-closing pass, round 7 (decisions R7-2 a; plan closing7/a/exp-pixel-r7.md sections 1.2 and 3.3), dataset render-closing-r7-rp, on the laptop (host cedar), 2026-11-12, one attempt out/20261112-205431 (started 20:54:31 Mac time, run-r7r.log; 143 jobs in nine stages, s0 first, the session gate, which passed 4 of 4: the default 64 x 64 triangle exact with t4, t6 and t7 and E831's z-ctl-34x18-y storing 924 with t4), kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, installed = loaded, knobs at their defaults at every stage start, read only), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a; tools ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a), round 6's t6 (built from resgx545 d9b2969, sha256 97df5c0ebf5bff2786a59b302e9a8a722bad36f0ef2f5dba11b6f2957f4ad98c) and t7, built by the lead on the build host from resgx545 1c64f3a, which allows odd widths (lead/build_tool7.sh, source pinned in TOOL7SRC.sha256, sha256 f2df4f99add18f011a3607dc3a73ac42cdfab3ec730d1e1f8cd7621761643375 in TOOL7.sha256, the slot run/freeze_r7.sh tool7 filled once, checked on the laptop before every stage); tables, predictions, models, scorers and runner frozen before the first job (FROZEN.sha256 33237f0d..., PREDICTIONS.sha256 c4be8ddd...; FROZEN.commits pins the resgx545 files read at 1c64f3a and data 830641e6); every stage ran to its end with health ok after it, no stop, no lead decision during the run and no reboot. Scored by the frozen score/score_r7.py in the run (out/ATT/score-STAGE.txt); at the fold (2026-11-12) the same scorer re-run on the kept files gave output byte-identical to the kept one for every stage (p7-rd's once its first line, the absolute path of the kept p7-rdc directory, names the run's tree), and the 944 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out). Rows: E606's iteration job with the new shader, `probe --tri pixpds:12 --temps 32 --pixels --width W --height H --slot pixel=pix_posstore.bin PDS.bin` with t6 (no row needed t7); pix_posstore.bin is E898's landed template probes/pds/templates/pix_posstore.s assembled with the landed usse-asm (the session's bins/, hash-pinned), PDS E437's kept position pair (q291_pos.bin) for set P and the landed pds_iter_nofetch.s with DOUTI0 0x20400800 for set V (q291_vtx.bin, with `--vtx-coords 2 --slot vtxuse=vtx_attr_zx.bin`); the program reads only g23 to g25 (E808), so every row touches one tile: the target fits one tile, or the triangle is cut to one with `--tri-v` (its right angle on the tile's corner: no pixel or quad of another tile covered); stage q291g, the gate (32 x 16 `--tri-full`, every slot known), ran first and passed, so q291 ran; read: the changed scratch dwords, four a slot, the valid set being the slots whose dword 1 changed, compared by exact set equality with each rival's set (r3_geo.py's band for H-BAND; the 12 held-out P rows all separate H-BAND from both rivals, tested before the freeze); secondary and not gating: dword 0's set grown to whole 2 x 2 quads. Every job class ok"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-rp:out/20261112-205431/q291g/", "render-closing-r7-rp:out/20261112-205431/q291/", "render-closing-r7-rp:out/20261112-205431/s0/", "render-closing-r7-rp:bins/", "render-closing-r7-rp:fold/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E730 found the band in which the ZLS store keeps depth past the target, E831,
E885 and E903 its rule (rule A). Whether the pixel tasks that make that depth also run there, with
their attributes iterated, could not be read through the image, which ends at the target. E898's
program stores, per valid instance, pa0, pa1 and a lane tag at the scratch slot of its place in its
tile (g24 << 5 | g23), so a job's stored slots are the pixels whose instances ran. With E437's
position pair every stored value checks its own slot. Rows: one tile a job (sizes up to 32 x 16,
or a triangle cut to one tile of a larger target), three rival sets per row, and the depth store of
the same sizes as twins.

**Frozen verdict (as printed).** `Q291 H-BAND held: held-out P 12 held, 0 FAILED, 0 cannot tell of
12; rivals H-TARGET 0, H-TILE 0; values H-LIN held (12 held, 0 FAILED, 0 cannot tell of 12); fit
pair held; vertex pair H-BAND 3 held, 0 FAILED, 0 cannot tell of 3, values E661 held (3 held, 0
FAILED, 0 cannot tell of 3); depth twins rule A 5 held, 0 FAILED, 0 cannot tell of 5; headline: Q291
H-BAND (the attribute band is the depth band, x + 0.5 < 1.25 W, y + 0.5 < 1.25 H) (12 of 12 rows
decided)`; the gate: `q291g gate PASS: 512 slots of 32 x 16, each its slot's position and lane
(E808, E437)`.

**Results [HW].** Valid slots per row (`out/20261112-205431/score-q291.txt`):

| rows | size | valid slots | H-BAND | H-TARGET | H-TILE |
|---|---|---|---|---|---|
| gate, controls (P full tile, cut 64 x 16 and 32 x 32, V) | 32 x 16 | 512 | 512 | 512 | 512 |
| fit, two runs | 20 x 12 | 375 | 375 | 240 | 512 |
| held out | 18 x 12 | 330 | 330 | 216 | 511 |
| held out | 24 x 8 | 300 | 300 | 192 | 500 |
| held out | 12 x 12 | 225 | 225 | 144 | 434 |
| held out | 20 x 8 | 250 | 250 | 160 | 483 |
| held out | 26 x 10 | 384 | 384 | 260 | 512 |
| held out | 10 x 6 | 84 | 84 | 60 | 264 |
| held out, cut in x | 34 x 16 | 160 | 160 | 32 | 512 |
| held out, cut in x | 36 x 16 | 208 | 208 | 64 | 512 |
| held out, cut in x | 44 x 16 | 368 | 368 | 192 | 512 |
| held out, cut in x | 50 x 16 | 480 | 480 | 288 | 512 |
| held out, cut in y | 32 x 18 | 192 | 192 | 64 | 512 |
| held out, cut in y | 32 x 24 | 448 | 448 | 256 | 512 |
| held out, V | 20 x 12 | 375 | 375 | 240 | 512 |
| held out, V | 18 x 12 | 330 | 330 | 216 | 511 |
| held out, V | 24 x 8 | 300 | 300 | 192 | 500 |

(H-TILE is the triangle's raster over the whole tile, so below 512 where the full-screen triangle's
hypotenuse crosses the tile.) Every row's set equalled H-BAND's slot for slot, not only in count.

In every row each valid slot held f32(x + 0.5) and f32(y + 0.5) of its own pixel (P) or a clip x
linear in x within E661's 23 units of 2^-23 (V), and the lane tag (x & 1) | (y & 1) << 1; every
in-target slot held its position; dword 0, written by every instance that ran, grew the valid set to
whole 2 x 2 quads in every row (secondary). The `pix_pa0` control image was f32(x + 0.5) at 240 of
240 pixels. The depth twins stored 375, 330, 300, 225 and 84 dwords with extents (25, 15), (22, 15),
(30, 10), (15, 15) and (12, 7), rule A's sets, no tile-area dword left at the pre-fill.

**What it shows.** The tile pass runs pixel tasks for the pixels of the band past the target and
for no pixel past the band: the valid instances are exactly rule A's band cut to the triangle, as
the depth store keeps them, at every size run, on one tile and across a tile edge in x and in y.
Their iterated attributes continue linearly past the target, the position pair and the vertex
pair's clip x alike, with no clamp at the target's edge. [infer] The band is a clip of the
rasterised area (E730's guard band), shared by depth and colour work, and the colour store alone
ends at the target.

**What it does not show.** Sizes of one tile and triangles cut to one tile (the program reads no
per-tile register); the float depth format; the iterated pa0 and pa1 of two programs only; whether
the colour of those pixels is written anywhere (the PBE ends at the target).
