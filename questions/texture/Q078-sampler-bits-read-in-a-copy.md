+++
id = "Q078"
question = "what do T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27 select, given a copy that reads one texel, a sheared read, coordinates scaled by 2 and 4, smaller images after the source, and values of no texel?"
unit = "texture"
phase = 11
evidence = ["E274"]
terms = ["T3.BIT10", "T3.BIT14", "T3.BITS19_18", "T3.BITS28_27", "T0.BIT27", "T3.BITS7_0"]
+++

Flipped one at a time in a copy (E274): T3 bits 3:0 and 7:4 offset the texel read in y and x by
a signed 4-bit count, clamped at the edge; bit 10 reads texel (0, 0) for every pixel; bit 14
reads (x + 32, y + x); bits 18 and 19 scale the coordinates by 2 and 4 (19 then faults past the
source); bits 27 and 28 read a half-size image 32 rows on and a quarter-size one 40 rows on,
at the source's stride; bit 13 faults; T0 bit 27 gives values of no texel at every pixel.

What is open: whether bits 7:0 are a texel offset at every value (only single bits were set) and
in a sampler (smp) as well as a fetch; what bits 18-19 and 27-28 are (a level select and a scale
for strided textures fit, a reading only); bit 10's single texel (a border or a clamp to a
constant); bit 14's shear; T0 bit 27's format.

To settle it: T3 bits 7:0 at every value in the copy; bits 18-19 and 27-28 at each of their
values with a strided chain of tagged levels written after the source; T0 bit 27 over the coded
source of E270 with the pixels fitted by pbe_words.py correlate.
