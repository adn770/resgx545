+++
id = "Q176"
question = "what position-dependent transform do T3 bits 10, 14, 18, 27 and 28 apply to the texel coordinates in smp (offsets that change every 32 or 64 pixels, E566), and why are the rows of bits 27 and 28 exact under 'after the source's height' at 64x16 and 64x32 but under no declared rule at a strided 32x32, and what do bits 11 and 12 select, given that they change nothing on a strided texture and every pixel of a twiddled chain texture"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E566", "E274", "E564", "E722"]
terms = ["T3.BIT10", "T3.BIT14", "T3.BITS19_18", "T3.BITS28_27"]
+++

E566 gives, for each of these bits on a strided 64x32 texture, the offsets as they run over the 2048
pixels (bit 10: column 0, -1, -2 ... every 32 pixels; bit 27: column -1, -2, -3 and row 31, 30, 29).
Not a constant offset, so Q078's "texel offset" reading does not cover them. E564 adds that bits 11
and 12, which change nothing on the strided texture, change every pixel of a twiddled 64x64 chain
texture (bit 11 cleared reads 2048 distinct names from level 0, bit 12 set one constant). To settle
it: for each bit decode the full (column, row) per pixel for the 64x32, 64x16 and 32x32 textures
and fit an affine map of (x, y) (a shear or a scale), then predict a fourth geometry before running
it; and run bits 11 and 12 on a strided and a twiddled texture of the same size.

Run in 11.39 (E722, 16 held-out jobs): the model "offset = sum of the level sizes below L,
address = (offset + index) << e" for bits 28:27 and 19:18 and bit 10 is exact on 13 of 13 jobs
that completed; "scale on the index only" fits 10 of 13, "strided chain by stride x height"
12 of 13. 3 jobs with the largest address extent (86016 to 174080 bytes) faulted; the largest
job that completed reads 65536 bytes (Q281; the 64 KiB cause, the probe's scratch size, is
[infer]). Only a 32-bit format and widths up to 128 were run. T3 bits 11, 12 and 14 were not run.
