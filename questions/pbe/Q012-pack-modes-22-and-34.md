+++
id = "Q012"
question = "what float formats are pack modes 22 and 34, given that both read o0 as an IEEE single (sign, NaN and exponent) and store it at some of the triangle's dwords while the rest change with the job before?"
unit = "pbe"
phase = 6
evidence = ["E032", "E270", "E387", "E406", "E429"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE"]
+++

Over seven coded colours and ten singles (E270), read at the triangle's pixels, no stored bit of
either mode copies a bit of o0 (mode 26, the control, gives R >> 3, G >> 3 and B >> 2), and both
follow o0 as a float. At 727 of the triangle's pixels (665 or 730 in a few cases) mode 22 holds
0x00000088 for zero, negative and NaN values, 0xc0000088 for positive values from 1/128 to 2.0
and 0xfff00088 for values of 1e13 and up; mode 34 holds 0x60800000 with bits 31:20 of the single
in bits 11:0 for the large values that are not NaN (the NaN 0x7f807f80 gives 0x7f9), and at 215
others (149 at 1/128 and 2.0) bits 30:20 of the single in bits 21:11 for positive values from
1/128 to 2.0. So the first part of the old question (one value whatever the colour, E032) is
narrowed: the value depends on o0 as a float, E032's single colour was a negative one.

Narrowed in 11.14 (E387): mode 34 stores bits 30:20 of a single in bits 21:11 (exactly for 2.0, 1.0,
0.5, 0.25, 0.3 and a ramp 0.5 + y/128) and mode 22 3 in bits 31:30 for 1.0 and 0x3ff in bits 19:10
for 2.0; but with o0-o3 written every mode, 0 included, shows o0 at some pixels and o1-o3 at others
(mode 0: 1.0 at 981, 2.0 at 512 pixels), the triangle's pixel task having one output dword per pixel
(E081, Q023), and the rest differs between runs. Which register each field of a pixel reads waits on
a pixel task with room for four output dwords.

What is open: the formats themselves (the meaning of the constant bits 0x88 and 0x60800000, why a
group of 727 and one of 215 dwords, which dword holds which pixel), and where the varying rest
comes from; a format whose other channels come from o1 to o3, which these shaders leave unwritten,
would explain it.

To settle it: the shader writing o0 to o3 with four different singles (and each alone set), every
pixel read back, both modes; a ramp of singles over x (o0 = x / 64) to place each dword's value by
pixel.

Narrowed in 11.15 (E406, the setup of ISP word 0 bit 26 or 27, CR_REG_0148 bit 0 and one data row,
two runs): under it o1 to o3 stop landing on other pixels (room for four output dwords is the
reading [infer]), and the pack-floats probes give one value per case on the triangle's pixels in 12
of 16 mode 0 cases, where the plain job gave one value in four cases of 16, two in six and 32 in
two (E387), so the varying rest of E387 was the shader's registers landing on other pixels. On the
triangle's pixels pack mode 22 puts o0 in bits 31:30 and o1 in bits 19:10, but every value that set
a field was saturated (o0 = 1.0 alone 0xc0000000, o1 = 2.0 alone 0x000ffc00, all four 0xc00ffc00,
and x + 0.5, y + 0.5), so the fields are placed and what they encode is not shown [infer]; o2 and
o3 at 0.5 and 0.25 give 0. Mode 34 stores bits 30:20 of o1's single in bits 21:11 (o1 = 2.0 alone
0x00200000; a mid-range ramp fits on 1017 of 1062 pixels, the others lower by two to four in the
field), and o0 = 1.0, o2 and o3 alone store 0. The constants 0x88 and 0x60800000 sit on pixels the
triangle does not cover [infer]. Still open: why o2 and o3 feed nothing at the values tried (o2 at
1.0, 0.5 and 0.3, o3 at 0.25, 0.5 and 0.9), what the mode 22 fields encode at unsaturated values,
the 45 and 43 pixels at 0 in the mode 22 ramps, the 45 or so pixels of the mode 34 ramp that
differ, and the fields at other values. Status: narrowed, not answered.

Narrowed in 11.16 (E429, 102 jobs, the room setup of E406): o3 reaches the field o1 fills in both
modes (mode 34: bits 30:20 of o3's single in bits 21:11 for 0.75, 1.0, 1.5, 2.0 and 4.0 on 537
pixels, 3 of 3 runs; mode 22: 0x088ffc00 on 851 pixels from 1.0 and on about 550 at 0.75 and in
the ramps), and o2 reaches o0's field in mode 22 on 61 pixels at 1.0 and
over; o2 feeds nothing in mode 34 beyond 8 pixels. Still open: which pixels take o3 and why, what
mode 22's fields encode between 0.25 and 0.5, the constants 0x88 and 0x60800000. Status: narrowed,
not answered.
