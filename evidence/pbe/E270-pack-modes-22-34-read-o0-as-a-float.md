+++
id = "E270"
claim = "Pack modes 22 and 34 read o0 as an IEEE single: at 727 of the triangle's 1062 pixels (665 or 730 in a few cases), mode 22 stores 0x00000088 for zero, negative and NaN values, 0xc0000088 for every positive value from 1/128 to 2.0 and 0xfff00088 for values of 1e13 and up; mode 34 stores 0x60800000 there, with bits 31:20 of the single in bits 11:0 for the values of 1e13 and up that are not NaN (0x7f807f80, a NaN, gives 0x7f9), and at 215 other pixels (149 at 2.0 and 1/128) bits 30:20 of the single in bits 21:11 for positive values from 1/128 to 2.0; read at the triangle's pixels, no stored bit of either mode copies a bit of o0 across the coded colours, while mode 26, the control, stores R >> 3, G >> 3 and B >> 2 at every pixel; the rest of each image changes with the job before it"
unit = "pbe"
method = "probes/pbe/pack-colours.toml (pack modes 0, 22, 26 and 34 over seven coded colours, 0x80ff8040, 0 and 0xffffffff) and probes/pbe/pack-floats.toml (modes 0, 22 and 34 over ten singles; one run) on the laptop, linux fork with the debug option on, and the follow-up run of pack-colours: the 64x64 triangle with eot_plain.s and the sideband 0x200 plus the mode, the shader writing the case's word to o0 over the background 0xff203040; every pixel read back; tools/usse-asm/pbe_words.py correlate, at the triangle's pixels of each run's mode 0 image"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pbe-pack-colours", "pbe-pack-floats", "pbe-pack-colours-followup"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE"]
+++

**What runs.** E032 found one value, 0x00000088 in mode 22 and 0x60800000 in mode 34, at 727 of
the triangle's 1062 pixels for the colour 0x80ff8040, and backgrounds that varied. The coded
colours give each bit of o0 its own pattern over seven cases (bit b set in case j when bit j of b
+ 1 is), so a stored bit that copies a bit of o0 names it. `pbe_words.py correlate` reads each
case at the pixels where the run's mode 0 image holds the triangle (E031's 1062), splitting a
16-bit mode's dwords into their two pixels, takes the commonest value there and fits each of its
bits against o0. Mode 26 is the control, a mode whose packing E032 read for one colour.

**Results, mode 26 and mode 0.** Mode 0 stores o0 unchanged. Mode 26 stores one value at all 1062
triangle pixels in every case of both runs (0x554a, 0x658c, 0x79ef, 0x81f0, 0x021f, 0, 0, 0x421f,
0, 0xffff), and the correlator fits every bit: bits 4:0 copy o0 bits 23:19, bits 9:5 bits 15:11
and bits 15:10 bits 7:2, that is R >> 3, G >> 3 and B >> 2. E032's 0x10 in bits 14:10 is the blue
of 0x80ff8040 (0x40 >> 2).

**Results, mode 22**, the commonest value at the triangle, at 727 of its 1062 pixels:

| o0 | the 727 | o0 | the 727 |
|---|---|---|---|
| 0x55555555, 0x66666666, 0x78787878 | 0xfff00088 | 0.25, 0.5, 0.75, 1.0, 2.0 | 0xc0000088 |
| 0x7f807f80, 0x7fff8000, 0xffffffff (NaN) | 0x00000088 | 0.1, 0.996, 1/128 | 0xc0000088 |
| 0x80000000, 0, 0x80ff8040, -0.5 | 0x00000088 | | |

The correlator fits bits 7:0 and 19:8 as constants and bits 31:20 to no bit of o0. At 0.5
(pack-floats) the value holds 665 pixels, not 727.

**Results, mode 34.** The 727 pixels hold 0x60800000 | f, f = 0x555, 0x666, 0x787 and 0x7f9 for
0x55555555, 0x66666666, 0x78787878 and 0x7f807f80, and 0 for every other value. For the first
three f is bits 31:20 of the single; 0x7f807f80 is a NaN whose bits 31:20 are 0x7f8, not 0x7f9,
and the other NaN, 0x7fff8000, gives 0, so the NaNs do not follow that rule (mode 22 files both
with zero). In pack-floats the 727 are 665 at 0, 2.0 and 1/128 and 730 at -0.5. 215 other
triangle pixels hold, for 1/128, 0.1, 0.25, 0.5, 0.75, 0.996, 1.0 and 2.0, 0x001e0000,
0x001ee000, 0x001f4000, 0x001f8000, 0x001fa000, 0x001fb800, 0x001fc000 and 0x00200000: bits 30:20
of the single (0x3c0, 0x3dc, 0x3e8, 0x3f0, 0x3f4, 0x3f7, 0x3f8, 0x400) in bits 21:11; at 1/128
and 2.0 only 149 of them do, the rest holding other words. At 0 and -0.5 those pixels hold other
values. In the coded run the same 215 pixels hold bits 30:20 of o0 in bits 21:11 for the four
largest values too (0xaaaaad55 for 0x55555555), with further bits above and below. The
correlator fits the 727's bits 10:0 to no bit of o0.

Both modes leave triangle pixels that are neither group, and the background, whose values follow
the case before: in the coded run mode 22's cases 0 to 2 hold 0x088fffff in about 830 dwords of
the image and the later cases 0x08800000 in about 1525. The follow-up run of pack-colours
repeated each case's value at the triangle, at 727 pixels but 665 in four cases (three of mode 22,
one of mode 34) and 730 in one, and not the counts of the rest. The singles ran once.

**What it shows.** Neither mode packs bits of o0 as a colour (the correlator fits no stored bit to
an o0 bit, where it fits mode 26's channels exactly), and both follow o0 as a float: positive
against zero, negative and NaN, and its exponent and top mantissa bits. That they are float
formats whose other channels come from other output registers, which the shader leaves unwritten,
would explain the varying rest **[infer]**.
