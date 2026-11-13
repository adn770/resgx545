+++
id = "Q177"
question = "does the offset that T0 address modes 4 to 7 add on the u axis, 8 max(W, H) + 52 dwords past the v rule's texel on every pixel of eleven twiddled textures of 4 x 4 to 64 x 64 (post hoc, E1000; the width's form of E983 and the height's each failed a held-out shape; 116, 180 and 308 at 8, 16 and 32 square, E957), hold on a held-out shape, format and type, and is mode 5's read past the texture on u (5 max(W, H) + 52 + t left, 6 max(W, H) + 52 + t right, post hoc, E983, E1000) a rule"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E565", "E033", "E932", "E957", "E983", "E1000"]
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
