+++
id = "Q046"
question = "do SIDEBAND bits 8:6 change what the end-of-tile emit stores under multisampling or in the pack modes that store part of a colour, when at 1 to 7 they change no pixel of an ARGB8888 or RGB565 triangle?"
unit = "pbe"
phase = 11
evidence = ["E030", "E031", "E210"]
terms = ["SIDEBAND.BITS8_6", "SIDEBAND.PACKMODE", "CR_ISP_MSAA"]
+++

With bit 9 of the end-of-tile emit's sideband set, bits 8:6 at each of 1 to 7 give images identical,
pixel for pixel, to the image with the field at 0, in pack mode 0 (ARGB8888) and in pack mode 3
(RGB565), in both runs (E030). The pack modes themselves are wider than these two: some store 16- or
8-bit subsets of the colour, some whole colours into part of the target, and a few values nobody has
decoded (E031). The triangle of E030 is single-sampled, and the multisample modes of `CR_ISP_MSAA`
change the image (E210).

What is open: whether the field does anything at all. The glossary's reading, a sub-format,
downscale or rotation field with 0 for plain output, is a hypothesis: a downscale could only show
where a tile holds more samples than pixels, a sub-format only in a pack mode with variants, and a
rotation or flip only in where a tile lands.

To settle it: run the triangle with bits 8:6 at 0 to 7 under `CR_ISP_MSAA` bits 1:0 at 1 and 2,
with the sample positions set as in E210, in each pack mode that stores a subset of the colour
(E031), and on a target of several tiles in pack mode 0, two runs each, every stored pixel read
back and compared with the field at 0.
