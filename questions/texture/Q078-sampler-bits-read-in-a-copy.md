+++
id = "Q078"
question = "what do T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27 select, given a copy that reads one texel, a sheared read, coordinates scaled by 2 and 4, smaller images after the source, and values of no texel?"
unit = "texture"
kind = "hw"
value = "high"
phase = 11
evidence = ["E274", "E397", "E566", "E564"]
terms = ["T3.BIT10", "T3.BIT14", "T3.BITS19_18", "T3.BITS28_27", "T0.BIT27", "T3.BITS7_0"]
+++

Flipped one at a time in a copy (E274): T3 bits 3:0 and 7:4 offset the texel read in y and x by
a signed 4-bit count, clamped at the edge; bit 10 reads texel (0, 0) for every pixel; bit 14
reads (x + 32, y + x); bits 18 and 19 scale the coordinates by 2 and 4 (19 then faults past the
source); bits 27 and 28 read a half-size image 32 rows on and a quarter-size one 40 rows on,
at the source's stride; bit 13 faults; T0 bit 27 gives values of no texel at every pixel.

Narrowed in 11.14 (E397): T3 bits 7:0 are two signed 4-bit texel offsets at every value: bits 3:0 in
y and 7:4 in x, clamped at the edge, all 256 values exact over 2048 pixels and sixteen of them
again. Answered: bits 7:0 in the copy (a fetch).

What is open: whether bits 7:0 are a texel offset at every value (only single bits were set) and
in a sampler (smp) as well as a fetch; what bits 18-19 and 27-28 are (a level select and a scale
for strided textures fit, a reading only); bit 10's single texel (a border or a clamp to a
constant); bit 14's shear; T0 bit 27's format.

To settle it: T3 bits 7:0 at every value in the copy; bits 18-19 and 27-28 at each of their
values with a strided chain of tagged levels written after the source; T0 bit 27 over the coded
source of E270 with the pixels fitted by pbe_words.py correlate.

Narrowed in 11.32 (E566, E564). In smp on a strided 64x32 texture T3 bits 0 to 3 and 4 to 7 are the
row and column offsets at every value tried (30 single-nibble values and 16 combinations, 46 of 46
under both declared orders of the offset and the address mode), so they are an offset in a sampler
as well as in a fetch; the held-out values prefer the offset before the address mode (6 of 24
against 1 of 24), neither model complete. Bits 8, 9, 20, 21 and 22 change nothing there, as do 11
and 12; but on a twiddled 64x64 chain texture bit 11 cleared and bit 12 set change every pixel
(E564), so those two act on a twiddled texture. Bits 10, 14, 18, 27 and 28 give offsets that change
with the pixel position (a transform of (x, y), not a constant offset), and T3 bit 13 faults the
job again; they are carried by Q176 with bits 11 and 12. T0 bit 27 on the strided texture reads
values that are no name of the buffer. What stays open is the transform of bits 10, 14, 18, 27 and
28 (Q176), what bits 11 and 12 select, and T0 bit 27's format.
