+++
id = "Q177"
question = "which dword do texture types 1, 3 and 4 read, each byte halved, in u address modes 4 to 7 at a size other than 16 x 16 and 32 x 32 (E1055's two-point fit 39 W + 52 + (x mod W), 40 W + 20 for type 4, failed at 8 x 8, 64 x 64 and 64 x 16, E1065; post hoc type 1 reads W H + 7 W + 52 + (x mod W) at five sizes, mode 5 7 W + 51, modes 6 and 7 mode 4's last column, type 4 at 64 x 64 two 32-wide blocks), and what is the half, and what lies behind the held-out constants of the twiddled type (8 max(W, H) + 52 inside, 5, 6, 7 and 4 max(W, H) + 52 on the sides, above and below, 4 log2 max(W, H) at the corners)"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E565", "E033", "E932", "E957", "E983", "E1000", "E1017", "E1026", "E1039", "E1055", "E1065"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++

E565: none of clamp, nomask (the unwrapped coordinate in the twiddle) or border (a constant) fits
the u axis of modes 4 to 7. To settle it: decode the dword index per position for modes 4 to 7 in a
texture whose neighbouring memory is written with names (a buffer of 24 pages, the texture in the
middle), and with the u range wider than 64 positions; test whether the u address uses a different
mask than the v address; and sweep the v axis at a pitch of one texel (E565's v sweep had a pitch of
two).

Narrowed 2026-11-13 (round 8, session r8-geo; E932). The v axis is answered at a pitch of one
texel: modes 4 and 5 repeat, 6 and 7 clamp (E565's reading held out, 4 of 4). On the u axis none
of the frozen rivals (the v rule, the unwrapped twiddle into the next block, a border constant)
fits, but post hoc every read is the v rule's index plus 180 dwords: in modes 4, 6 and 7 on every
pixel, here at page 12 and in E565's kept jobs at base 0 and page 1 (fitted, no held-out row), so
the memory read 'past the texture' is the texture's own layout moved by 720 bytes. What stays: a
held-out row for the offset (another size, format and texture type), what sets 180, and what mode
5 reads past the texture on u.

Narrowed 2026-11-13 (round 9, session r9-geo, decision R9-3 a; E957; the question line is
rewritten to what stays). E932's u reading replicated (+180 at 16 x 16, mode 5's reads as E932's).
The offset depends on the size: +116 dwords at 8 x 8 and +308 at 32 x 32, in modes 4 and 6 alike,
every pixel; none of the frozen rivals (180 at every size, 180 N^2 / 256, none off 16) held. T3
(0, 0x800, 0x800000) and the v axis's own mode 4 leave it at 180, and v then repeats as its rule
says. Post hoc the three offsets are 8 N + 52 dwords [fitted]. What stays: why that offset (width,
height or size: only square textures were run), a held-out size, other formats and texture types,
and mode 5 past the texture.

Narrowed 2026-11-13 (round 10 offline, decision R10-1 a; E983; the question line is rewritten to
what stays). It read "what sets the offset that T0 address modes 4 to 7 add on the u axis (...),
and what mode 5 reads past the texture on u". E565's kept 32 x 8 jobs in modes 4, 6 and 7 read the
v rule's dword plus 308 on every pixel, the width's 8 W + 52, where the height's (116) and the
square's (180) forms miss every pixel; the rows ran before E957's fit but no rival was frozen by
hash before the reading (SEMI). Post hoc, mode 5 reads 5 W + 52 + t left of the texture and 6 W +
52 + t right of it (t the texel row), and dwords 20 to 23 by corner with v outside too. What stays:
a held-out non-square size (the seeds plan's stage addr3, closing10/seeds/exp-seeds-r10.md section
2), other formats and types, and mode 5's form held out.

Note 2026-11-13 (round 10, session r10-tex, decision R10-2 a; E1000; the question line is
rewritten to what stays: E983's width form is refuted). On textures of W != H every frozen rival for
the offset failed a held-out shape: 8 x 32
and 16 x 64 read the height's 8 H + 52 (308 and 564), 64 x 16 and E565's 32 x 8 (E983's form) the
width's, 64 x 64
in modes 4 and 6 read 564 and 4 x 4 84; mode 5 followed the longer side past the texture too. Post
hoc every read of the eleven jobs is 8 max(W, H) + 52 dwords past E561's index, mode 5's 5 max(W,
H) + 52 + t left and 6 max(W, H) + 52 + t right [fitted]. What stays: a held-out row for max(W, H),
why that offset, and other formats and texture types.

Narrowed 2026-11-13 (round 11 offline, decision R11-1 a; E1017; the question line is rewritten to
what stays, the question is not retired). It read "does the offset that T0 address modes 4 to 7 add
on the u axis, 8 max(W, H) + 52 dwords past the v rule's texel on every pixel of eleven twiddled
textures of 4 x 4 to 64 x 64 (post hoc, E1000; the width's form of E983 and the height's each failed
a held-out shape; 116, 180 and 308 at 8, 16 and 32 square, E957), hold on a held-out shape, format
and type, and is mode 5's read past the texture on u (5 max(W, H) + 52 + t left, 6 max(W, H) + 52 +
t right, post hoc, E983, E1000) a rule". Of the 31 kept twiddled u mode 4 to 7
jobs outside E1000's, 27 are squares and 4 are E565's 32 x 8, where max(W, H) is W: none parts the
max form from the width's, so 8 max(W, H) + 52 stays fitted. In mode 5 the frozen rule
(closing11/plan/c2-texture/rule_a.py) held on every
pixel with t inside the texture, and missed the 384 pixels of each uv5 job with s inside and t
outside, which read a
constant per side plus s (7 M + 52 + s above, 4 M + 52 + s below, post hoc); E983's corner dwords
20 to 23 are the 32 x 8 texture's, 16 x 16 reads 16 to 19. sgx-sim keeps refusing modes 4 to 7 on
u, naming this question. What stays: a held-out H > W shape outside E1000's (16 x 64 or 64 x 16
parts the corner bases (W + H) / 2 and 12 + M / 4, 40 against 28; 8 x 64 parts max from W), mode
5 above and below where M is not W, why these constants, other formats and texture types.

Narrowed 2026-11-13 (round 13, session r13-tex, decision R13-1 a; E1026; the question line is
rewritten to what stays, the question is not retired: every frozen corner form failed). Held out:
8 max(W, H) + 52 past E561's index at 32 x 64, 8 x 64 and 128 x 32 in modes 4 and 6 and 32 x 64 in
mode 7 (7 of 7; the width's form failed 5, the height's 2), in texels on a u16 32 x 64; with u and v
in mode 5 the side, above and below reads follow max(W, H) (5 M, 6 M, 7 M and 4 M + 52 plus the
row or column) and the inside the index plus 8 M + 52, at 64 x 16 and 16 x 64. The corners read a
base plus 0 to 3; the base is 24 at both shapes, which no frozen form gave ((W + H) / 2, 12 + M / 4,
12 + W / 4). The strided type reads modes 4 to 7 as mode 0 (E565's bd-st rows, read at the fold).
What stays: the corner base held out, the constants' reason, types 1, 3 and 4.

Narrowed 2026-11-14 (round 14, session r14-tex, decision R14-1 a; E1039; the question line is
rewritten to what stays, the question is not retired: the types clause read neither frozen form).
It read "what is the base of mode 5's corner dwords past the texture (16 at 16 x 16, 20 at 32 x 8,
24 at 64 x 16 and 16 x 64; post hoc 4 log2 max(W, H), E1026), why does a u mode 4 to 7 add 8
max(W, H) + 52 texels and mode 5 its side constants, and do texture types 1, 3 and 4 take these
modes". Answered: the corner base is 4 log2 max(W, H), held out at 8 x 8, 32 x 32, 128 x 32, 32 x
128, 128 x 128 and 256 x 32 against a cap at 24, a floor at 16 and E1026's three failed forms, the
other regions of mode 5 by max(W, H) at the same six shapes (sgx-sim models every region past the
texture on 32-bit twiddled textures). Types 1, 3 and 4 with u mode 4 at 16 x 16 read neither their
mode 0 image (the strided type's reading) nor it plus 180 (the twiddled type's): every pixel is a
named dword past the texture (675 to 691 for types 1 and 3, 659 to 675 for type 4) with each byte
halved, rounded up, the same on every row (post hoc). "Why these constants" no row can decide: it
is reworded to the held-out formulas [infer] (R14-6 a, the lead confirms). What stays: types 1, 3
and 4 in u modes 4 to 7 (a held-out row of the halving reading, other sizes, modes 5 to 7).

Narrowed 2026-11-14 (round 15, session r15-tex, decisions R15-1 a and R15-5 a; E1055). Held out on
ten rows with passing controls: types 1, 3 and 4 read every pixel in u modes 4 to 7 as a named dword
with each byte halved, rounded up, the 32 rows alike, at 32 x 32 in mode 4 and at 16 x 16 in modes
5, 6 and 7 (not the mode 0 image, not an unhalved name); at 16 x 16 in mode 4 the name is 676 + (U
mod 16) over U = -24 to 39 (the column inside the texture, not the unwrapped one); modes 5 to 7 do
not read mode 4's image (the question line is rewritten to what stays). Post hoc: at 32 x 32 mode 4
reads 1300 + (x mod 32) on all three types (39 W + 52 at both sizes for types 1 and 3 [infer]); at
16 x 16 modes 6 and 7 read mode 4's last column on every pixel and mode 5 one other name (163 or 164
for type 1, 371 to 628 for type 4); the 32 x 32 mode 0 references read 32 t + s (types 1 and 3 the
width, type 4 its block). The halves leave each name or the one 256 apart. sgx-sim reads mode 4 on
these types at 16 x 16 and 32 x 32 and refuses modes 5 to 7. What stays: the size form held out (a
third size), mode 5's constant and modes 6 and 7 held out, what the half is (a blend with zero
[infer]) and which of the two names is read.

Narrowed 2026-11-14 (round 16, session r16-tex, decision R16-7 a; E1065; the question line is
rewritten to what stays, the question is not retired). **E1055's two-point fit of the name failed
at the new sizes**: types 1 and 3's N = 39 W + 52 + (x mod W) 0 of 3 rows (8 x 8, 64 x 64, 64 x
16), type 4's 40 W + 20 + (x mod W) 1 of 2 (held at 8 x 8, failed at 64 x 64), the quadratic
through the same two sizes 0 of 5, modes 6 and 7 at 64 x 64 as mode 4's last column of that fit 0
of 2. Held out and holding: every pixel of the nine mode 4 to 7 rows is a halved name, the rows
alike (9 of 9), mode 5 one value on every pixel (2 of 2), the mode 0 references a raster of the
width on type 1 (3 of 3) and 32 t + s on type 4 at 8 x 8. Post hoc (fitted, not held out): type 1
reads W H + 7 W + 52 + (x mod W) at 8, 16, 32 and 64 and at 64 x 16 (the product, not max(W, H)
squared), mode 5 reads 7 W + 51 (107, 163, 499), modes 6 and 7 at 64 x 64 mode 4's last column;
type 4 reads 340 at 8 x 8 and at 64 x 64 3347 + (x mod 32), then 4371 + (x mod 32) from column 32
(E941's 32 x 32 blocks 1024 dwords apart). sgx-sim keeps the two measured names at 16 x 16 and 32
x 32 and refuses the other sizes naming E1065. What stays: the size form held out (a round that
runs W H + 7 W + 52 on new sizes, 16 x 64 for W against max(W, H), type 3 and type 4's block
form), what the half is, and which of the two names is read.
