+++
id = "E955"
claim = "R9-geo stage cube2, sizes (Q284; 8 probe fills of TEXTYPE 2 point-sampled by smp3d, E726's cu-xn the control, no fault): with E923's face and (s, t) rule, the face-local index of 32 x 32 and 64 x 64 faces is E561's twiddle law (16 x 16 tiles in raster order with s first; at 64 bits 8, 9 = s4, s5 and 10, 11 = t4, t5): H-E561 held out on 3 of 3 new directions at 32 x 32 (1796, 1590 and 1596 of as many predicted pixels) and 3 of 3 at 64 x 64 (T1 0x4c03f03f, faces 4096 dwords apart; 1404, 1585, 1810), against E923's plain Morton (0 of 6) and a pairwise order of the bits above 7 (equal to E561's at 32, 0 of 3 at 64); 4 x 4 faces (T1 0x4c003003) sit 16 dwords apart with a 2-bit Morton index (H-NN 2 of 2, 1928 and 1889 pixels) against 64 apart (0 of 2); the control passed; frozen verdicts 'H-E561 at 32 x 32 held out (3 of 3 rows decided)', 'H-E561 at 64 x 64 held out (3 of 3 rows decided)', 'H-NN at 4 x 4 held out (2 of 2 rows decided)'"
unit = "texture"
method = "R9-geo stage cube2 of the question-closing pass, round 9 (S9-geo, decisions R9-3 a and S-2 a of the seeds plan closing9/seeds/exp-seeds-r9.md section 3), on the laptop (host cedar), 2026-11-13, attempt out/20261113-081038 (dataset render-closing-r9-geo; the only attempt, 77 jobs in four stages, every job class ok, no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74, the one-shot test boot; installed = loaded, knobs at their defaults at every stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., bound by FROZEN.commits' built line to resgx545 4623753 userspace/libsgxfive/tools/sgxfive-test.c, sha256 703cbcea...), the session kit of resgx545 f32dfacc (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job; every row replayed before the freeze on the library mock built from the tool's source, none refused); frozen before the first job: FROZEN.sha256 ce1fd939..., PREDICTIONS.sha256 2693875c..., FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: `probe --temps 32 --coords --pixels [--scratch-pages 32]` (32 on the 64 x 64 rows: six faces of 4096 dwords are 24 pages) of programs assembled by the session's gen/make.py from the pinned p1141 template tx_map.s in r8-geo's form (three coordinates, each a constant or (1 + x / 64 or 1 + y / 32) K + C, exact in f32; T0 0x07fe0000, T1 0x4c01f01f, 0x4c03f03f or 0x4c003003, the scratch address and E726's T3 0x00800800; one smp3d); bins/cube-ctl-xn.bin is E726's p1141-cube__4.bin byte for byte. Three new directions at 32 x 32, r8-geo's b1, b2, b3 at 64 x 64 and b1, b2 at 4 x 4. Frozen per pixel (predictions/cube2/NAME.MODEL.txt by sha256): r8-geo's q284_rule.json (E923, sha256 52162471...) for the face and (s, t), with the face-local index of each rival (gen/cube.py local: H-E561, H-MORTON, H-PAIRSWAP) and at 4 x 4 the faces 16 (H-NN) or 64 (H-PAD64) dwords apart; face ties and exact texel boundaries at a |ma| that is no power of two 'cannot tell'; a row holds only if every predicted pixel equals. sgx-pipe's cube::point_index (this fold, test first) takes faces of 4 and 64; crates/sgx-pipe/tests/texture_cube.rs replays the eight jobs, every predicted pixel matched"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-geo:out/20261113-081038/cube2/"]
terms = ["TEXTYPE"]
+++
**What ran.** E930 held E923's rule out at 16 x 16 and 8 x 8 faces and read 32 x 32 post hoc;
E951 showed that post hoc index is E561's twiddle law, and that a 64 x 64 face parts E561's law
from a pairwise order of the bits above 7. Stage cube2 ran three new directions at 32 x 32, three
at 64 x 64 and two at 4 x 4, every pixel frozen under each rival, with E726's cu-xn as the control.

**Frozen verdict (as printed).** `H-E561 at 32 x 32 held out (3 of 3 rows decided)`; `H-E561 at
64 x 64 held out (3 of 3 rows decided)`; `H-PAIRSWAP at 64 x 64 held out is not supported: 0 held,
3 FAILED`; `H-MORTON` 0 held, 3 FAILED at each size; `H-NN at 4 x 4 held out (2 of 2 rows
decided)`; `H-PAD64 ... 0 held, 2 FAILED`. The control passed (2048 of 2048 as E726 kept them).

**Results [HW].**

| jobs | faces | H-E561 or H-NN | the rivals |
|---|---|---|---|
| cube-n32-c1 to c3 | 32 x 32, 1024 apart | 1796, 1590, 1596 of as many | Morton 898, 690, 809 |
| cube-n64-b1 to b3 | 64 x 64, 4096 apart | 1404, 1585, 1810 of as many | pairwise 702, 790, 915; Morton 242, 229, 243 |
| cube-n4-b1, b2 | 4 x 4 | 1928, 1889 of as many (16 apart) | 64 apart 136, 1058 |

**What it shows.** [HW] A TEXTYPE 2 face of N x N is an N x N 32-bit twiddled texture by E561's
law, faces N * N dwords apart from N = 4 to 64, held out: E923's (s, t) and face order at every size
run, the 16 x 16 Morton inside a tile, the tiles in raster order with s first. sgx-pipe models
faces of 4 to 64.

**What it does not show.** Faces above 64 x 64, non-square faces (not legal for a cube),
mip-mapped cubes, other formats.
