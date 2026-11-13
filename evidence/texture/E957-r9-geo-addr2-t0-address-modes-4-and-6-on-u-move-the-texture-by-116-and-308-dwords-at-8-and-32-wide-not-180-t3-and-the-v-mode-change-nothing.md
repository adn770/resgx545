+++
id = "E957"
claim = "R9-geo stage addr2 (Q177; 11 probe fills of twiddled 32-bit textures at page 12 of a 32-page named scratch, the swept axis over 128 positions at one texel a step, no fault): E932's u reading replicates (addr-u4 H-MASK-V's index + 180 dwords, 2048 of 2048; addr-u5's per-position read) and the mode 0 control passed; at 8 x 8 and 32 x 32 in u modes 4 and 6 every rival failed (H-OFF180, H-OFFSCALE + 180 N^2 / 256, H-OFFNONE: 0 of 4 each): every pixel reads H-MASK-V's index + 116 dwords at 8 x 8 and + 308 at 32 x 32, in both modes (2048 of 2048 each; 8 N + 52 through 8, 16 and 32, post hoc [fitted]); T3 0, 0x800 and 0x800000 leave + 180 at 16 x 16 (H-T3-INERT 3 of 3); with v also in mode 4 the offset stays 180 and v repeats (H-OFF180 1 of 1, H-OFF360 and H-MASK-V refuted); frozen verdicts '... is not supported: 0 held, 4 FAILED' for the three size rivals, 'H-T3-INERT (u mode 4 at 16 x 16 under T3) (3 of 3 rows decided)', 'H-OFF180 (u and v mode 4) (1 of 1 rows decided)'"
unit = "texture"
method = "R9-geo stage addr2 of the question-closing pass, round 9 (S9-geo, decision R9-3 a of the seeds plan closing9/seeds/exp-seeds-r9.md section 4), on the laptop (host cedar), 2026-11-13, attempt out/20261113-081038 (dataset render-closing-r9-geo; the only attempt, 77 jobs in four stages, every job class ok, no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74, the one-shot test boot; installed = loaded, knobs at their defaults at every stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., bound by FROZEN.commits' built line to resgx545 4623753 userspace/libsgxfive/tools/sgxfive-test.c, sha256 703cbcea...), the session kit of resgx545 f32dfacc (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job; every row replayed before the freeze on the library mock built from the tool's source, none refused); frozen before the first job: FROZEN.sha256 ce1fd939..., PREDICTIONS.sha256 2693875c..., FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: `probe --temps 32 --coords --pixels --scratch-pages 32` of programs assembled by gen/make.py from the pinned tx_map.s: the swept coordinate (p - 64 + 1/2) / N with p = x | (y & 1) << 6, the other on texel N / 2's centre (the uv job: u = (x - 24 + 1/2) / 16, v = (y - 8 + 1/2) / 16), T0 0x07fe0000 with the modes in ADDRMODE_U (8:6) and ADDRMODE_V (5:3), T1 0x0c007007, 0x0c00f00f or 0x0c01f01f, T2 the immediate 0x5CAFC000 (the scratch address + 12 pages), T3 0x00800800 but on the T3 rows; addr-ctl-u0, addr-u4-rep and addr-u5-rep are r8-geo's programs byte for byte. Frozen per pixel (predictions/addr2/NAME.MODEL.txt by sha256), nothing fitted: H-MASK-V (E932's v reading on the swept axis: 4, 5 repeat, 6, 7 clamp; E561's index above 16), H-OFF180, H-OFFSCALE, H-OFFNONE, H-T3-INERT, H-OFF360 [infer], E932's per-position u5 read; the index read is the value less 0xD0000000 less 12288. Post hoc at the fold: out/fold/post_read.py"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-geo:out/20261113-081038/addr2/", "render-closing-r9-geo:out/fold/"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++
**What ran.** E932 read every u job of modes 4 to 7 at 16 x 16 as the v rule's index plus 180
dwords (post hoc) and left open why 180. Stage addr2 replicated two of E932's rows, ran u modes 4
and 6 at 8 x 8 and 32 x 32, u mode 4 under three other T3 words, and u and v both in mode 4, each
with frozen rivals for the offset, in a buffer whose every dword is named.

**Frozen verdict (as printed).** Replicates: `H-OFF180 (replicate addr-u4-rep) (1 of 1 rows
decided)`, `H-U5-E932 (replicate addr-u5-rep) (1 of 1 rows decided)`; sizes: H-OFF180, H-OFFSCALE
and H-OFFNONE each `is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`; `H-T3-INERT (u mode 4
at 16 x 16 under T3) (3 of 3 rows decided)`; `H-OFF180 (u and v mode 4) (1 of 1 rows decided)`,
H-OFF360 and H-MASK-V `0 held, 1 FAILED`. The control passed.

**Results [HW].** Index read less H-MASK-V's (out/fold/reproduce.out):

| jobs | texture | offset (dwords), every pixel |
|---|---|---|
| addr-u4-n8, u6-n8 | 8 x 8 | +116 (2048 of 2048 each) |
| addr-u4-rep, the three T3 rows, addr-uv4 | 16 x 16 | +180 |
| addr-u4-n32, u6-n32 | 32 x 32 | +308 |

**What it shows.** [HW] Modes 4 and 6 on u address the texture at a constant offset past its base
that grows with the size (116, 180 and 308 dwords at 8, 16 and 32), is the same in both modes, and
does not depend on T3 or on the v axis's mode; the u axis otherwise repeats (4) or clamps (6) as v
does. [fitted] The three offsets are 8 N + 52 dwords (32 N + 208 bytes); nothing holds that out.

**What it does not show.** Why the offset (a function of the width, the height or the size in
dwords: square textures only), sizes other than 8, 16 and 32, other formats and texture types, and
mode 5's reads past the texture beyond E932's replicate.
