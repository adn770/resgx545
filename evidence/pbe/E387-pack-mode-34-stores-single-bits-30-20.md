+++
id = "E387"
claim = "Pack mode 34 stores bits 30:20 of an IEEE single in bits 21:11, for the words found where 2.0, 1.0, 0.5, 0.25 and 0.3 land, and for 0.5 + y/128 at 689 of the 704 pixels holding such a word in run 1 and 695 of 709 in run 2 (the others hold another row's word); mode 22 stores 3 in bits 31:30 for 1.0 and 0x3ff in bits 19:10 for 2.0; but every pixel of a shader that writes o0-o3 shows, in mode 0 as in 22 and 34, the value of o0 at some pixels and of another output register at others (mode 0: o0 at 981, o1 at 512 of the triangle's place), and outside the triangle's pixels the words differ from run to run, so which register each field of a pixel reads is not settled"
unit = "pbe"
method = "probes/pbe/pack-floats-channels.toml and pack-floats-ramps.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x64 triangle with eot_plain.s and sideband 0x200 plus the mode (0, 22, 34), pds_iter_xy.s, the shader writing o0-o3 four singles, each alone, x + 0.5 and y + 0.5, and x/128, 0.5 + y/128, 0.3, 0.9 (fmad from pa0, pa1); two runs; every pixel read back"
tiers = ["HW"]
date = "2026-11-03"
data = ["pbe-pack-floats-channels", "pbe-pack-floats-ramps"]
terms = ["SIDEBAND.PACKMODE"]
+++
**Results.** Mode 0 (the control) stores o0 where it lands and, at other pixels, o1-o3: with o0-o3
= 1.0, 2.0, 0.5, 0.25, 981 pixels hold 1.0 and 512 hold 2.0; with o1 alone 2.0, 435 hold 2.0 (E081's
displaced output registers). Mode 34 holds 0x00200000, 0x001fc000, 0x001f8000, 0x001f4000 where
those values land (2.0, 1.0, 0.5, 0.25: bits 30:20 in bits 21:11) and 0x001f4800 and
0x001f9000-style words where 0.3 and 0.5 + y/128 land; bits 10:0 hold 0x304 at most pixels. With o1 = 0.5 + y/128 alone, of the pixels holding a word that
is some row's bits 30:20 in bits 21:11, 689 of 704 (run 1) and 695 of 709 (run 2) hold their own
row's.
Mode 22 holds 0xc0000000 where o0 = 1.0 alone lands (730 pixels) and 0x000ffc00 where o1 = 2.0
alone lands (628). The two runs of the ramp probe differ outside the commonest words.

**Not shown.** Which output register each field of a 64- or 128-bit format reads: the triangle's
pixel task is given one output dword a pixel (Q023), so the other registers land on other pixels.
