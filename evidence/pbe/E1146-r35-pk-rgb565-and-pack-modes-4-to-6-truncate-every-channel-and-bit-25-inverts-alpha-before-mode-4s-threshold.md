+++
id = "E1146"
claim = "r35-pk on module 7CE8E38E (Q302), every control passed, a colour ramp whose channels take every byte value on the 64 x 64 triangle (each pixel's colour unique): RGB565 (pack mode 3) and pack modes 4 (ARGB1555), 5 (ARGB4444) and 6 (A8 with RGB332) truncate every narrowed channel (H-RZ on every dword of 2 of 2 rows in each mode; H-RN, H-RNE and H-SCALE not supported, 0 held, 2 FAILED in each); the 40 ARGB8888-like modes other than 0 and mode 11 store mode 0's image (H-AS0 40 of 40 and 2 of 2, H-AS0-PART refuted); modes 9, 10, 12 and 13 store whole colours of the image in the target and, 12 and 13, in the scratch past it (H-WHOLE 2 of 2 each); bit 25 with the low bytes 0x40 and 0xc0 inverts the alpha field in modes 0, 5 and 6 (H-1136 4 of 4 each) but not as frozen in mode 4 (H-LOWDEP 4 of 4): there post hoc the alpha bit is set where 255 - alpha is at or above the low byte, the threshold taking the inverted alpha"
unit = "pbe"
method = "r35-pk (render/closing-r35-pk), stages s0, r1, r2, r3, pw of the question-closing pass (round 35: R35-1 (a), R35-4 (a), the round-35 plan, section 3.3 (Q302); safe class, no planned fault or hang, #limit 0 in every stage; record E1146 reserved by the frozen README), dataset render-closing-r35-pk; attempt out/20261118-090046 (scores score-pw.txt, score-r1.txt, score-r2.txt, score-r3.txt, score-s0.txt); on the laptop host cedar at home, kernel 7.3.0-resgx545, module srcversion 7CE8E38EDB97FC5EA4F6C90 (installed and loaded alike), stock firmware, tool ~/sgxfive-test-t10 (t10, sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, resgx545 a581c06), every job `sgxfive-test-t10 probe --temps 32 --pixels --tri pixel --width 64 --height 64 [--vtx-coords 2] --cmd 11=WORD --sideband 0x200|MODE --slot eot=eot_plain.bin [--slot pixpds=pds_iter_xy.bin:12 --slot vtxuse=vtx_coords.bin] PROGRAM` after a debugfs reset (the colour form: E031's program, o0 = 0x80ff8040 over the background 0xff203040; the ramp form: src/ramp_xy.s, with pa0 = x + 0.5 and pa1 = y + 0.5 (E382) X and Y as integers by adding 2^22, o0 = the XOR of X << 0, 8, 16, 20, 25 and Y << 4, 11, 19, 22, 29), word 11 being pixelbe, the word that loads CR_REG_0400, every pixel read back and every scratch dword changed, no knob and no register write; the rows tables/STAGE.txt from gen/make.py, the frozen predictions predictions/STAGE.tsv, every model's image computed from the stage's own mode 0 reference row; the narrow rule score/score.py narrow, frozen; the post-hoc readings fold/posthoc.py and posthoc.txt, not frozen; the sgx-pipe replay crates/sgx-pipe/tests/closing_r35_pk.rs offline; freezes: FROZEN.sha256 68b73b243a9707fec3707400e65cf92ef71f71c8593fd3b415ec99406f6b1d1e (79 files), PREDICTIONS.sha256 fcb38b57d539234e882f3cc4561aa3681e03815ad0ea22de9eb462a0617b16f7 (19 files); FROZEN.commits pins: resgx545:tools/closing/kit/session.py at eea6d2ab, resgx545:tools/closing/kit/lib_kit.sh at eea6d2ab, resgx545:tools/closing/kit/run_stage.sh at eea6d2ab, resgx545:tools/closing/kit/kitscore.py at eea6d2ab, resgx545:tools/closing/kit/fake/sudo at eea6d2ab, resgx545:tools/closing/kit/fake/timeout at eea6d2ab, resgx545:tools/closing/kit/fake/df at eea6d2ab, resgx545:tools/closing/kit/fake/modinfo at eea6d2ab, resgx545:tools/closing/kit/fake/sha256sum at eea6d2ab, resgx545:tools/closing/kit/fake/tool.sh at eea6d2ab, resgx545:tools/closing/kit/fake/tool.py at eea6d2ab, resgx545:tools/closing/kit/fake/ssh.py at eea6d2ab, resgx545:tools/closing/scorekit.py at eea6d2ab, resgx545:tools/closing/sessioncheck.py at eea6d2ab, data:pbe/emit-transforms/pbe-emit-transforms-xy/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-00/bins/eot_plain.bin at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-00/bins/pbe-pack-modes-packmode-00__0.bin at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-03/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-04/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-05/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-06/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-07/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-09/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-10/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-12/raw.txt at 1f5ebe6b, data:pbe/pack-modes/pbe-pack-modes-packmode-13/raw.txt at 1f5ebe6b, data:pbe/reg-0400-alpha/pbe-reg-0400-alpha-bit25-mode5/raw.txt at 1f5ebe6b, data:pbe/reg-0400-alpha/pbe-reg-0400-alpha-mode0/raw.txt at 1f5ebe6b, data:pbe/reg-0400-alpha/pbe-reg-0400-alpha-mode4/bins/pds_iter_xy.bin at 1f5ebe6b, data:pbe/reg-0400-alpha/pbe-reg-0400-alpha-mode4/bins/vtx_coords.bin at 1f5ebe6b, a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f at built; tools: TOOLSRC.sha256: 23e1fa76d10bb4e7cfadb0985ac110d4681e4113f2f55f17dd81bdd4b2fe183b a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f:userspace/libsgxfive/tools/sgxfive-test.c; the runner expects: run/session.env SRCV_EXPECT=7CE8E38EDB97FC5EA4F6C90; stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-18"
data = ["crates/sgx-pipe/tests/closing_r35_pk.rs", "render-closing-r35-pk:out/20261118-090046/s0/", "render-closing-r35-pk:out/20261118-090046/r1/", "render-closing-r35-pk:out/20261118-090046/r2/", "render-closing-r35-pk:out/20261118-090046/r3/", "render-closing-r35-pk:out/20261118-090046/pw/", "render-closing-r35-pk:fold/"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE", "CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "CR_REG_0400.BITS11_0"]
+++
**What ran.** r35-pk (closing29/r35-pk README, pre-run), 92 jobs: s0 (9 controls: the ramp in
mode 0 at 0x80, its image by construction; the ramp in mode 4, the alpha bit split 127 clear, 128
set, E1136; E031's colour images of modes 3, 4, 5, 6, 7, 9 and 10), r1 (a mode 0 reference, then
modes 3, 4, 5, 6, 9, 10 and 11 at 0x80, twice, the second in reverse order), r2 (a reference, the
40 ARGB8888-like modes other than 0 at 0x80), r3 (a reference, modes 4, 5, 6 at 0x80, then modes
0, 4, 5 and 6 at 0x02000040 and 0x020000c0, twice) and pw (a reference, E031's images of modes 12
and 13, the ramp in 12 and 13 twice). The ramp: on the 1062 triangle pixels every colour unique
and each byte lane all 256 values, 2 to 6 pixels each. Modes 14, 22, 26, 34 not run. Frozen, with
every model's image computed from the stage's own mode 0 row: H-RZ (truncate), H-RN (round half
up, saturated), H-RNE (half to even), H-SCALE (round(v (2^w - 1) / 255)) for modes 3 to 6 (fit:
E385's mode 5 alpha and E031's mode 6 green, both H-RZ only); H-AS0 against H-AS0-PART; H-WHOLE
(every dword written, the scratch included, one of the image's values) against H-NARROW; H-1136
(bit 25 inverts the alpha field, E1135; the low byte thresholds mode 4's alpha bit, E1136, after
the inversion of the bit) against H-LOWDEP.

**Frozen verdict (as printed).** Every control PASS; s0 `cannot tell: no row decided` (controls
only), every gate open. r1: `H-RZ m03 (heldout) (2 of 2 rows decided)`, and so `m04`, `m05`,
`m06`; `H-RN`, `H-RNE`, `H-SCALE` in each of the four modes `is not supported: 0 held, 2 FAILED, 0
cannot tell of 2`; `H-AS0 (heldout) (2 of 2 rows decided)`; `H-WHOLE m09` and `m10 (2 of 2 rows
decided)`. r2: `H-AS0 (heldout) (40 of 40 rows decided)`, `H-AS0-PART ... 0 held, 40 FAILED`. r3:
`H-1136 m00`, `m05`, `m06 (heldout) (4 of 4 rows decided)`, `H-1136 m04 (heldout) is not
supported: 0 held, 4 FAILED`, `H-LOWDEP m04 (heldout) (4 of 4 rows decided)`. pw: `H-WHOLE m12`
and `m13 (2 of 2 rows decided)`. The frozen narrow rule: `NARROW`, clauses (d) H-RZ, (a) modes 4,
5, 6 H-RZ, the ARGB8888-like class H-AS0 on 42 of 42, modes 9, 10, 12, 13 H-WHOLE, (e) not decided
(mode 4 H-LOWDEP). fold/reproduce.out reproduces every score byte for byte.

**Results [HW].** Every narrowed channel of modes 3 to 6 stores v >> (8 - w) for every byte
value v (RGB565: 5, 6, 5 bits; ARGB1555: RGB 5 bits each; ARGB4444: 4 bits; RGB332 under the
alpha byte). Every replicate pair is equal dword for dword (fold/posthoc.txt). Mode 4 with bit
25, the low 15 bits of every pixel as at 0x80, the alpha bit:

| word | alpha bit set for | clear for |
|---|---|---|
| 0x00000080 | 128 to 255 | 0 to 127 |
| 0x02000040 | 0 to 191 | 192 to 255 |
| 0x020000c0 | 0 to 63 | 64 to 255 |

Modes 9, 10, 12, 13 (post hoc): 9 writes 1024 dwords holding 120 triangle colours, 10 2048 with
714, 12 every second dword of the target (714) and 1536 scratch dwords at an 8-byte stride (152,
pixel rows 40 to 54), 13 every fourth (120) and 2816 at 16 bytes (792, rows 20 to 54); no raster
map tried fits.

**What it shows.** RGB565 and the 16-bit pack modes 4 to 6 drop a channel's low bits, never
round. The ARGB8888-like modes store o0 as mode 0 does over every byte value, so with E1135 they
differ from mode 0 only in bit 25. Modes 9 to 13 store whole colours, never narrowed. Bit 25
inverts the alpha before it is packed: in mode 4 the threshold of E1136 then reads 255 - alpha
(set where 255 - alpha >= the low byte), which at the low byte 0x80 is the same image as
inverting the stored bit, as E385 and E1135 read it [infer: one inversion ahead of every pack
step]; in modes 0, 5 and 6 the low byte changes nothing with bit 25 either.

**What it does not show.** Mode 14 (it faults, E031); where modes 9, 10, 12 and 13 put each
pixel (the layout and what they write past the target); the fields 1 to 7 of sideband bits 8:6 in
modes 4 to 6 and the ARGB8888-like modes; modes 22, 26 and 34 (Q012); the low byte with bit 25 in
mode 4 at values other than 0x40, 0x80 and 0xc0.
