+++
id = "E932"
claim = "R8-geo stage addr (Q177; 9 probe fills of E565's 16 x 16 twiddled texture at page 12 of a 24-page scratch whose every dword is named, the swept axis over 128 positions at one texel a step, no fault): on the v axis modes 4 and 5 repeat and modes 6 and 7 clamp (H-MASK-V, E565's v reading, held out at a pitch of one texel: 4 of 4, 2048 of 2048 pixels each); on the u axis H-MASK-V, H-NOMASK-PAGE and H-BORDER all failed 4 of 4; the mode 0 control read the repeat image at page 12 (PASS); frozen verdicts 'H-MASK-V on the v axis (4 of 4 rows decided)' and, on u, '0 held, 4 FAILED' for each rival; post hoc, every u job's index is H-MASK-V's plus 180 dwords inside the texture (256 of 256) and on all 2048 pixels in modes 4, 6 and 7, as in E565's kept u jobs at base 0 and page 1 (bd-u4, u6, u7, hb-u4: 2048 of 2048 each) [fitted]; mode 5 outside the texture reads other dwords"
unit = "texture"
method = "R8-geo stage addr of the question-closing pass, round 8 (decision R8-2 a; plan closing8/rank/rank-round8.md R8-5), on the laptop (host cedar), 2026-11-13, attempt out/20261113-015842 (dataset render-closing-r8-geo; the first attempt, out/20261113-015816, ran nothing: the lead passed SGX_TARGET_SSH_OPTS where the kit reads SGX_TARGET_HOST_KEY_ALIAS, so staging failed, and the lead's run log inside the session directory was a new file the freeze refused), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, installed = loaded, knobs at their defaults at the stage start), tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), the session kit of resgx545 d97c4739 (kit/run_stage.sh with run/hooks.sh, a debugfs reset before each job, every job class ok, no stop, no lead decision); frozen before the first job: FROZEN.sha256 2687abf3..., PREDICTIONS.sha256, FROZEN.commits; scored by the frozen score/score.py (out/ATT/score-STAGE.txt), re-run at the fold on the kept files with byte-identical output, every kept file decompressing to the raw sha256 the laptop logged (out/fold/reproduce.sh, reproduce.out). Jobs: `probe --temps 32 --coords --pixels --scratch-pages 24` of programs assembled by gen/make.py from the pinned tx_map.s: the swept coordinate -4 + (p + 1/2) / 16 with p = x | (y & 1) << 6 (128 positions on each pair of rows), the other 0.53125 (texel 8's centre), T0 0x07fe0000 with the mode in ADDRMODE_U (8:6) or ADDRMODE_V (5:3), T1 0x0c00f00f, T3 0x00800800 (E565's), T2 the immediate 0x5CAFC000, which the probe loads as the scratch address + 0xC000 (page 12; the tool's --scratch-at is tri's only, the plan's [check] 4). Frozen per pixel (predictions/addr/NAME.MODEL.txt, sha256 in predictions/addr.tsv), nothing fitted: H-MASK-V (the swept axis wraps as E565's v: 4, 5 repeat, 6, 7 clamp), H-NOMASK-PAGE (Morton of the texel mod 16 plus 256 per 16-texel block on), H-BORDER (inside the twiddled texel, outside one constant); the index read is the value less 0xD0000000 less 12288. Post hoc at the fold, not frozen: out/fold/post_read.py, which also reads E565's kept u jobs (texture/p1132/tx-border) the same way"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-geo:out/20261113-015842/addr/", "render-closing-r8-geo:out/fold/", "texture-p1132-tx-border"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++
**What ran.** E565 found the v axis of modes 6 and 7 clamping and of 4 and 5 repeating (at a pitch
of two texels), and the u axis reading indices past the texture in every one of modes 4 to 7 (+324
to +366 in one row), which no rule fitted. Stage addr placed E565's texture in the middle of a
named buffer, so that any read decodes to its dword, and swept u (v inside) and v (u inside) over
128 positions at one texel a step in modes 4 to 7, with mode 0 on u as the control.

**Frozen verdict (as printed).** `H-MASK-V on the v axis (4 of 4 rows decided)`; on u `H-MASK-V
on the u axis is not supported: 0 held, 4 FAILED, 0 cannot tell of 4`, H-NOMASK-PAGE and H-BORDER
the same; on v H-NOMASK-PAGE and H-BORDER `0 held, 4 FAILED`. The control passed.

**Results [HW].** v jobs: every pixel H-MASK-V's index. u jobs, index read minus H-MASK-V's (post
hoc, out/fold/post_read.py):

| job | inside the texture | all 2048 pixels |
|---|---|---|
| addr-u4, u6, u7 | +180 on 256 of 256 | +180 on 2048 of 2048 |
| addr-u5 | +180 on 256 of 256 | +180 on 256; outside 140 and 156 less the texel's index |

E565's kept u jobs, read the same way: bd-u4, bd-u6, bd-u7 and bd-hb-u4 (the texture at page 1)
H-MASK-V's index + 180 on 2048 of 2048 each, bd-u5 on 512 (its inside and nothing else).

**What it shows.** [HW] On the v axis modes 4 and 5 repeat and 6 and 7 clamp at a pitch of one
texel too: E565's v reading held out. [infer, fitted] On the u axis modes 4 to 7 address the
texture 180 dwords (720 bytes) past its base, at three bases and every texel row run; 4 repeats
and 6 and 7 clamp there as on v, and 5 does something else past the texture. E565's indices 'past
the texture' are this offset, not a wider mask.

**What it does not show.** Why 180 (its dependence on the size, the format and the type was not
varied: one 16 x 16 twiddled texture), what mode 5 reads past the texture on u, held-out rows for
the offset, both axes in modes 4 to 7 at once.
