+++
id = "E032"
claim = "Pack modes 22, 26 and 34 store one value per triangle pixel and none of the three is a pair of luma and chroma: mode 26 stores R >> 3 in bits 4:0, G >> 3 in bits 9:5 and 0x10 in bits 14:10; mode 22 stores 0x00000088 and mode 34 stores 0x60800000 in 727 of the triangle's 1062 pixels, neither explained; the backgrounds of 22 and 34 take scattered values that change from run to run; with o1 to o3 written, even mode 0 spills them into other pixels' places"
unit = "pbe"
method = "probes/pbe/pack-modes.toml on the laptop, linux fork with the debug option on: packmode-22, -26 and -34, and packmode4-00, -09, -10, -12, -13, -14, -22, -26 and -34 (the shader writes o1, o2 and o3 as well: 0x11223344, 0x55667788, 0x99aabbcc); the 64x64 triangle, o0 0x80ff8040 over the background 0xff203040; two runs"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["pbe-pack-modes", "pbe-pack-modes-followup"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE"]
+++

**What runs.** The pack-mode probes of E031 for the three modes it leaves open, and the same
modes with the shader writing o1 to o3 as well. Each job runs twice (the follow-up run is the
follow-up run).

**Results, o0 only.**

- Mode 26: triangle 0x421f in 510 dwords (two pixels each) and background 0x40c4 in 1496,
  2048 dwords left at the sentinel. For the triangle colour (R 0xff, G 0x80) the value is
  R >> 3 = 0x1f in bits 4:0, G >> 3 = 0x10 in bits 9:5 and 0x10 in bits 14:10; for the
  background (R 0x20, G 0x30) 0x04, 0x06 and 0x10 give 0x40c4. Blue does not enter. This
  repeats in both runs.
- Mode 22: 727 dwords hold 0x00000088, in both runs; the other dwords of the target hold
  0x08800088, 0x08800000, 0x088ffc00 and others (first run: 1323, 1269, 341 and 436 other),
  and the follow-up run gives a different mix (0x08800000 in 1560, 0x08800088 in 1322, 0x00000000
  in 307, 180 other). 531 of 4096 dwords differ between the two runs.
- Mode 34: 727 dwords hold 0x60800000 in both runs, and the rest scatter (0x60800304,
  0x00000304, 0x00000000 and 546 other in the first run; the follow-up run's mix differs); 602 of
  4096 dwords differ between the runs.
- The 727 pixels of 22 (0x00000088) and of 34 (0x60800000) all lie inside the triangle (the
  triangle of the plain ARGB8888 image has 1062 pixels), in both runs. Each is one value per
  pixel: no dword holds an interleaved pair, as a 4:2:2 packing would.
- Neither value matches the luma or chroma of the triangle colour or of the background in the
  studio or the full range (BT.601 luma of the triangle colour is 152 or 159, of the
  background 55 or 45).

**With o1 to o3 written.** Mode 0 stores o1's word, 0x11223344, in 615 dwords (608 in the second
run) and o2's 0x55667788 in 5, where the plain mode 0 stores only the two colours: the extra
output lands in other pixels' places in the tile **[infer]**, so these probes cannot tell a mode
that reads o1 to o3 from that spill. Modes 9 and 10 gain o1 in 306 and 342 dwords; mode 12 gains
o1 (766 dwords, 815 in the follow-up run) and 13 gains o2 and o3 (396 and 146); the scratch of mode
13 then holds 0x11223344 and 0x55667788 too (385 and 202 dwords), the scratch of mode 12 only the
two colours, and mode 14 faults again. Every probe of this family varies from run to run in tens
to hundreds of dwords (for example mode 12: 487 dwords differ), the stable parts being the
colours, the sentinel counts and the strides.

**Not shown.** What modes 22 and 34 encode, and why only 727 of the 1062 triangle pixels hold the
value; how the output registers map to the tile. Only one triangle colour and one background
colour were run, so a chroma or luma rule that the data cannot see is not excluded.
