+++
id = "E930"
claim = "R8-geo stage cube (Q284; 13 probe fills of TEXTYPE 2 point-sampled by smp3d, E726's cu-xn as the control, no fault): the cube-face (s, t) rule frozen offline (E923, q284_rule.json 52162471...) held out on 4 of 4 new off-axis programs at 16 x 16 (6777 of 6777 predicted pixels, all six faces between them) and, with the same rule at N = 8 (texel floor((q + 1) / 2 * 8), 3-bit Morton, faces 64 dwords apart), on 3 of 3 programs at 8 x 8 faces; at 32 x 32 faces (faces 1024 dwords apart, the frozen part held) it failed 3 of 3 (718, 783 and 921 of 1436, 1585 and 1810 pixels); frozen verdicts 'the frozen q284 rule held out (4 of 4 rows decided)' and 'the rule with N = 8, 32 held out is not supported: 3 held, 3 FAILED, 0 cannot tell of 6'; post hoc, every predicted pixel of the three 32 x 32 jobs (4831 of 4831) reads the rule's index with the fifth bits of s and t in the other order (bits 8 and 9 swapped against a 5-bit Morton) [fitted]"
unit = "texture"
method = "R8-geo stage cube of the question-closing pass, round 8 (decisions R8-2 a and R8-4 a; plan closing8/rank/rank-round8.md R8-2 (a) and (b)), on the laptop (host cedar), 2026-11-13, attempt out/20261113-015842 (dataset render-closing-r8-geo; the first attempt, out/20261113-015816, ran nothing: the lead passed SGX_TARGET_SSH_OPTS where the kit reads SGX_TARGET_HOST_KEY_ALIAS, so staging failed, and the lead's run log inside the session directory was a new file the freeze refused), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, installed = loaded, knobs at their defaults at the stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), the session kit of resgx545 d97c4739 (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job, every job class ok, no stop, no lead decision); frozen before the first job: FROZEN.sha256 2687abf3..., PREDICTIONS.sha256, FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: `probe --temps 32 --coords --pixels` of programs assembled by the session's gen/make.py from the pinned p1141 template tx_map.s (render/closing-r4-render4x's cubegen form: three coordinates, each a constant or (1 + x / 64 or 1 + y / 32) K + C, all exact in f32, the T words 0x07fe0000, T1 0x4c00f00f / 0x4c007007 / 0x4c01f01f for 16, 8 and 32 (E725's width and height fields), the scratch address and 0x00800800, one smp3d); bins/cube-ctl-xn.bin is E726's p1141-cube__4.bin byte for byte. Frozen per pixel (predictions/cube/NAME.txt by sha256 in predictions/cube.tsv): the rule's dword, a face tie (two equal largest magnitudes) and an exact texel boundary at a |ma| that is no power of two 'cannot tell'; a row holds only if every predicted pixel equals. Post hoc at the fold, not frozen: out/fold/post_read.py"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-geo:out/20261113-015842/cube/", "render-closing-r8-geo:out/fold/"]
terms = ["TEXTYPE"]
+++
**What ran.** E923 fitted the faces' (s, t) on E726's eight jobs, froze it by hash and held it out
offline on E844's two jobs (4090 of 4096, the 6 misses exact texel ties). Q284 asked for faces of
other sizes and a hardware row. Stage cube ran E726's cu-xn program as the control (its 2048 pixels
known), four new off-axis programs at 16 x 16 ((a): one constant coordinate of magnitude 0.625 or
0.6875 and two ramps, the dominant axis changing inside each image, all six faces between them),
and three of those directions at 8 x 8 and at 32 x 32 faces ((b): the rule with N for 16, faces N *
N dwords apart, frozen). The stage's six other jobs are E931's.

**Frozen verdict (as printed).** `the frozen q284 rule held out (4 of 4 rows decided)`; `the rule
with N = 8, 32 held out is not supported: 3 held, 3 FAILED, 0 cannot tell of 6`. The control
passed (2048 of 2048 as E726 kept them).

**Results [HW].**

| job | face size | predicted pixels as the rule | not predicted (face tie, texel tie) |
|---|---|---|---|
| cube-off-a1 to a4 | 16 | 1600, 1685, 1682, 1810 of as many | 9 + 439, 79 + 284, 120 + 246, 6 + 232 |
| cube-n8-b1 to b3 | 8 | 1760, 1817, 1881 of as many | 9 + 279, 79 + 152, 6 + 161 |
| cube-n32-b1 to b3 | 32 | 718 of 1436, 783 of 1585, 921 of 1810 | 9 + 603, 79 + 384, 6 + 232 |

Every pixel holds a texel tag (0xD000xxxx). At 32 x 32 the face (the index divided by 1024) is the
rule's in every predicted pixel; the misses differ from the rule's index by 256 or 512.

**Post hoc, not frozen [fitted].** With bit 8 of the face-local index taken from bit 4 of the
coordinate the rule puts in the odd bits and bit 9 from the other (the 16 x 16 interleave below,
the fifth bit pair in the other order), all 4831 predicted pixels of the three 32 x 32 jobs read
that index (out/fold/post_read.py). Read another way, a 32 x 32 face is four 16 x 16 twiddled
blocks of 256 dwords in an order the 16 x 16 rule does not give [infer]. Fitted on these three
jobs; nothing holds it out.

**What it shows.** [HW] E923's (s, t) rule holds on hardware rows never used for its fit: four new
off-axis 16 x 16 programs, all faces, and at 8 x 8 faces with the rule's N = 8 form, faces 64
dwords apart. Faces of 32 x 32 sit 1024 dwords apart, but their local index is not the 5-bit
Morton the rule extends to.

**What it does not show.** The 32 x 32 index held out (the swapped fifth bits are fitted), faces of
other sizes (4, 64 and up), non-square faces, ties (E931) and the edges' filtering (E931).
