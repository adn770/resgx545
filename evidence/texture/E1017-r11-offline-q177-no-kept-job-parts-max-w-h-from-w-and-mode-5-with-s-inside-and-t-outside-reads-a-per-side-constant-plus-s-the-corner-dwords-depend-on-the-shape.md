+++
id = "E1017"
claim = "Round 11 offline (Q177; no run): of the 31 kept twiddled jobs with T0 u mode 4 to 7 outside E1000's own (p1132 tx-border 16, r8-geo addr 4, r9-geo addr2 11), 27 are squares and 4 are E565's 32 x 8 (max(W, H) = W), so none parts E1000's 8 max(W, H) + 52 from the width's 8 W + 52 (only E1000's fit jobs 8 x 32 and 16 x 64 do): the max form stays fitted, and the 32 x 8 jobs refute only the height's (2048 of 2048 each under max and W, 0 under H); in mode 5 the rule frozen by hash before scoring (closing11/plan/c2-texture/rule_a.py, sha256 1dc23918...) scored 512 of 896 pixels on both uv5 jobs (bd-uv5 16 x 16, bd-hb-ns-uv5 32 x 8): every pixel with s inside and t inside or with s outside and t inside held, and the 384 with s inside and t outside missed, a case its text left unpredicted [HW, held out offline]; post hoc those read 7 M + 52 + s above (t < 0) and 4 M + 52 + s below (t >= H) the texture, M = max(W, H) = W in both, 384 of 384 on both jobs [fitted]; with s and t both outside, E983's corner dwords 20 to 23 hold at 32 x 8 (1152 of 1152) and fail at 16 x 16 (0 of 1152), which reads 16 to 19 (+0 above left, +1 above right, +2 below left, +3 below right; the dump's first line was seen before the freeze, disclosed): a corner base of (W + H) / 2 or 12 + M / 4 fits both shapes [fitted, two shapes]"
unit = "texture"
method = "Offline, no run (round 11, decision R11-1 a of closing11/plan/rank-round11.md, finding 6; the planner's check closing11/plan/c2-texture/, part A). Data: every kept twiddled job whose T0 u mode is 4 to 7 (p1132 tx-border's 16 such jobs, texture/p1132/tx-border/*.txt.gz; r8-geo's addr-u4 to addr-u7, render-closing-r8-geo out/20261113-015842/addr/; r9-geo's addr2 jobs, render-closing-r9-geo out/20261113-081038/addr2/), the other 21 tx-border jobs being u modes 0 to 3, v-only or strided, and p1132's and p1141's specs.json and cases.json holding no other. rule_a.py (standard library) declares H-MAX (modes 4, 6 and 7, and mode 5 with s inside: index + 8 M + 52, M = max(W, H); mode 5 with s outside and t inside: 5 M + 52 + t left, 6 M + 52 + t right), its rivals H-W and H-H (W or H for M), and for the corners C-CONST (dwords 20 to 23, E983's reading) and C-ROW; the index is E561's tile law (render/closing-r10-tex/gen/addr.py index()). FREEZE.log gives its hash at 2026-11-13T11:05:06Z and everything read before it, including the first 12 lines of bd-uv5's dump, whose header named the corner values 16 and 17 (so C-CONST was known to fail at 16 x 16 before the freeze, disclosed). score_a.py scores every job and names those that part max from W or H; probe_uv5.py and probe_uv5b.py print the uv5 reads by region, post_a.py the post hoc forms. This fold re-ran all five with python -I and got byte-identical outputs"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["texture-p1132-tx-border", "render-closing-r8-geo:out/20261113-015842/addr/", "render-closing-r9-geo:out/20261113-081038/addr2/", "cited-scratch:closing11/plan/c2-texture/"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++
**What was done.** E1000 found, post hoc, that the offset modes 4, 6 and 7 add on the u axis of a
twiddled texture is 8 max(W, H) + 52 dwords and that mode 5's reads beside the texture use max(W,
H) too, after every frozen single-side rival failed a held-out shape; no row held the max form
out. The round 11 planner searched the kept data for jobs that part max(W, H) from W or H and
scored the max form, frozen with its rivals, on all of them; mode 5's reads with v outside the
texture were scored against E983's corner reading.

**Results [HW].** score_a.out: 27 of the 31 jobs are squares (8, 16 and 32 a side), where the
three forms agree on every pixel. The four 32 x 8 jobs bd-hb-ns-uv4 to uv7 (E565's, read by E983)
have max(W, H) = W: H-MAX and H-W hold 2048 of 2048 on uv4, uv6 and uv7, H-H 0. No job outside
E1000's fit (8 x 32, 16 x 64, 64 x 16) parts max from W.

Mode 5 (probe_uv5.out, probe_uv5b.out), by region of the texel (s, t):

| region | bd-uv5 (16 x 16) | bd-hb-ns-uv5 (32 x 8) | frozen |
|---|---|---|---|
| s, t inside | index + 180 | index + 308 | held |
| s outside, t inside | 5 M + 52 + t left, 6 M + 52 + t right | the same | held |
| s inside, t < 0 | 164 + s (7 M + 52 + s) | 276 + s | not predicted, missed |
| s inside, t >= H | 116 + s (4 M + 52 + s) | 180 + s | not predicted, missed |
| corners | 16, 17, 18, 19 | 20, 21, 22, 23 | C-CONST 0 and 1152 of 1152 |

The corner dword is constant over its whole quadrant (288 pixels each), +0 above left, +1 above
right, +2 below left, +3 below right in both shapes.

**What it shows.** [HW, held out offline] Mode 5 with s inside the texture and t outside does not
read the inside offset: it reads a constant per side plus s. The corner dwords are not fixed: they
change with the shape. [fitted] 7 M + 52 + s above and 4 M + 52 + s below (384 of 384 on both
jobs, post_a.out; the height's 7 H + 52 = 108 at 32 x 8 is excluded, W and M not parted, W = M on
both); a corner base c of 16 at 16 x 16 and 20 at 32 x 8, which (W + H) / 2 and 12 + M / 4 both
give. E1000's 8 max(W, H) + 52 stays fitted: nothing kept holds it out against the width.

**What it does not show.** A held-out row for max(W, H) against W (a texture with H > W outside
E1000's two); which corner base (a 16 x 64 or 64 x 16 texture parts them, 40 against 28); mode 5
above and below at a shape where M differs from W; why 52, 8, 7, 5, 6 and 4 per texel of the
longer side; other formats and texture types. sgx-sim keeps refusing modes 4 to 7 on u (Q177).
