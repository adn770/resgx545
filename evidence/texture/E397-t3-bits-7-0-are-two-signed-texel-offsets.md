+++
id = "E397"
claim = "T3 bits 7:0 offset the copy's texel read by two signed 4-bit counts, bits 3:0 in y and 7:4 in x, clamped at the source's edge: at each of the 256 values every one of the 2048 pixels is the as-built image's texel at the offset place, and the 16 values run twice agree"
unit = "texture"
method = "probes/texture/copy-followup.toml (script copy-followup.sh, t3_low) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x32 copy of the every-value source with T3 = 0x00800800 with bits 7:0 replaced, every value once and sixteen twice; every pixel read back and fitted against the value-0 image"
tiers = ["HW"]
date = "2026-11-03"
data = ["texture-copy-followup"]
terms = ["T3.BITS7_0"]
+++
**Results.** 256 of 256 values fit exactly; the second run of 0, 1, 7, 8, 9, 15, 16, 17, 112, 127,
128, 136, 240, 247, 248, 255 gave the same images.
