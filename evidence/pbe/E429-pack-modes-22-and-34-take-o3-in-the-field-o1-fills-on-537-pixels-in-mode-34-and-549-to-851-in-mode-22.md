+++
id = "E429"
claim = "In the room setup of E406, pack mode 34 stores bits 30:20 of o3's single in bits 21:11 on 537 pixels for each of 0.75, 1.0, 1.5, 2.0 and 4.0 (3 of 3 runs: 0x001fa304, 0x001fc304, 0x001fe304, 0x00200304, 0x00204304), and mode 22 sets the field of bits 19:10 to 0x3ff (0x088ffc00) on 851 pixels at o3 of 1.0, 2.0 and 4.0 (549 to 567 at 0.75 and in two ramps); o2 alone reaches a few pixels only (8 in mode 34, 12 in mode 22)"
unit = "pbe"
method = "probes/pbe/pack-floats-o23.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the shader of pix_xy_op.s (pixel x + 0.5 in pa0, y + 0.5 in pa1) writing o0 to o3 with the eot slot of eot_plain.s at sideband 0x216 (mode 22) and 0x222 (mode 34), ISP word 0 bit 26 (blk 1 = 0x5d00200) and render details dword 9 bit 0 (rd:9=1), the setup of E406: o2 and o3 alone at 0.75, 1.0, 1.5, 2.0 and 4.0, both at 1.0, o0 to o3 at 1.0, 2.0, 1.5 and 0.75, ramps of o2 and o3 (x/64, 0.5 + y/128, both together), 17 cases three times in each mode (102 jobs), every pixel read"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["pbe-pack-floats-o23"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE"]
+++

**Results** (64x64 target, the triangle's 1062 pixels; values per pixel as stored; the counts are
the pixels that hold the value, the same in all three runs unless said):

- Mode 34, o3 alone: 0x001fa304 (o3 = 0.75), 0x001fc304 (1.0), 0x001fe304 (1.5), 0x00200304 (2.0)
  and 0x00204304 (4.0), each on 537 pixels; the single's bits 30:20 are 0x3f4, 0x3f8, 0x3fc, 0x400
  and 0x408, which sit in bits 21:11 (the field E406 found o1 in). With o3 as a ramp (x/64, 0.5 +
  y/128) the field takes many values (the data hold them). o2 alone at 1.0, 1.5, 2.0 and 4.0 gives
  no pixel with a field value among the four commonest values (3 of 3 runs), and 0x00210304 on 8
  pixels.
- Mode 22, o3 alone: 0x088ffc00 on 851 pixels at 1.0, 2.0 and 4.0 (847 at 1.5 in one run), on 549
  at 0.75, 559 at x/64 and 567 at 0.5 + y/128: the field of bits 19:10 (o1's) is saturated at
  every value from 0.5. o2 alone: 0xc0000000 (the field of bits 31:30, o0's) on 61 pixels at 1.0,
  2.0 and 4.0 and no 0x088ffc00 among the four commonest values.
- With o0 to o3 at 1.0, 2.0, 1.5 and 0.75 mode 22 gives 0xc00ffc00 on 1119 pixels, mode 34
  0x00200000 on 1063 and 0x00200304 on 827.

Runs differed on a few cells (o2 = 0.75 and 1.5 in mode 22, o2 = 0.5 + y/128 in mode 34, o3 = 1.5
in mode 22: counts moving by 4 to 100 pixels); the data hold every count.

**What it shows.** The fields are fed by the pixel task's other output dwords: o3 reaches the field
o1 fills in both modes, on 537 pixels in mode 34 and 549 to 851 in mode 22, and o2 reaches o0's
field in mode 22 on 61 pixels at 1.0 and over [infer: with the room setup the four outputs of a
pixel are stored through two fields' worth of lanes]. Mode 34's field is exactly bits 30:20 of the
single at the five values (E387 and E406 had 1.0, 2.0 and a ramp). Mode 22's field is saturated at
the unsaturated values tried (0.75, 0.5 + y/128), so what it encodes between 0.25 (zero, E406) and
0.5 is not found.

**What it does not show.** Which pixels take o3 (no parity of x or y separates them) and why, the
constants 0x88 and 0x60800000, and the pixels at 0. Q012 stays open.
