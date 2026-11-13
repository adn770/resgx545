+++
id = "Q177"
question = "what do T0 address modes 4 to 7 read along the u axis of a 16x16 twiddled texture (indices 324 to 366 past the 256 texels, a period of 6 or 16 positions), given that on the v axis 6 and 7 clamp and 4 and 5 repeat, and what memory lies past the texture"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E565", "E033", "E932"]
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
