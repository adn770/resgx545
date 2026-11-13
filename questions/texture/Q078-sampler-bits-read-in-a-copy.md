+++
id = "Q078"
question = "what do T3 bits 11 and 12 select, given that they change nothing on a strided texture and every pixel of a twiddled chain texture (E564, E566), and does bit 14's sheared read, dword + floor(S * S * u) with u clamped to [0, 1] (held out offline where the width is the stride, refuted in its frozen forms at W = 32, S = 64, and fitted post hoc on all three strided jobs, E968), hold at other widths and strides, and what does it do on a twiddled texture, where it faulted (E566)?"
unit = "texture"
kind = "hw"
value = "high"
phase = 11
evidence = ["E274", "E397", "E566", "E564", "E722", "E723", "E968"]
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

Run in 11.39 (E722, 16 held-out jobs): the model "offset = sum of the level sizes below L,
address = (offset + index) << e" for bits 28:27 and 19:18 and bit 10 is exact on 13 of 13 jobs
that completed; "scale on the index only" fits 10 of 13, "strided chain by stride x height"
12 of 13. 3 jobs with the largest address extent (86016 to 174080 bytes) faulted; the largest
job that completed reads 65536 bytes (Q281; the 64 KiB cause, the probe's scratch size, is
[infer]). Only a 32-bit format and widths up to 128 were run. T3 bits 11, 12 and 14 were not run.

**Correction 2026-11-11:** Q176 is merged into this question (retired as folded into Q078; a fold is
not an answer), and its question is now a clause of the one above. Its question was: what
position-dependent transform do T3 bits 10, 14, 18, 27 and 28 apply to the texel coordinates in smp
(offsets that change every 32 or 64 pixels, E566), why are the rows of bits 27 and 28 exact under
'after the source's height' at 64x16 and 64x32 but under no declared rule at a strided 32x32, and
what do bits 11 and 12 select, given that they change nothing on a strided texture and every pixel
of a twiddled chain texture.

Its text (the paragraph that follows the same E722 paragraph as above): E566 gives, for each of
these bits on a strided 64x32 texture, the offsets as they run over the 2048 pixels (bit 10: column
0, -1, -2 ... every 32 pixels; bit 27: column -1, -2, -3 and row 31, 30, 29), not a constant offset.
E564 adds that bits 11 and 12, which change nothing on the strided texture, change every pixel of a
twiddled 64x64 chain texture (bit 11 cleared reads 2048 distinct names from level 0, bit 12 set one
constant). To settle it: for each bit decode the full (column, row) per pixel for the 64x32, 64x16
and 32x32 textures and fit an affine map of (x, y), then predict a fourth geometry before running
it; and run bits 11 and 12 on a strided and a twiddled texture of the same size. Q176's evidence
(E566, E274, E564, E722) and terms were already in this question's lists.

Narrowed 2026-11-13 (round 9 offline, decisions X-1 a and X-6 a; the question line is reworded,
the question is not retired). It read "what do T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27
select, given a copy that reads one texel, a sheared read, coordinates scaled by 2 and 4, smaller
images after the source, and values of no texel; what position-dependent transform of the texel
coordinates do bits 10, 14, 18, 27 and 28 apply in smp (offsets that change every 32 or 64 pixels,
E566), why are the rows of bits 27 and 28 exact under 'after the source's height' at 64x16 and
64x32 but under no declared rule at a strided 32x32, and what do bits 11 and 12 select, given that
they change nothing on a strided texture and every pixel of a twiddled chain texture?". Dropped:
T0 bit 27, which E723 answers for point samples (a texel byte decoded sRGB to half, 4 of 4
held-out fills; the bilinear part is Q282), and bits 10, 18-19 and 27-28, whose transform is
E722's level and scale model held out on 13 of 13 fills that completed (the spec gives it with its
limits, which stay there). Bit 14 is narrowed by E968: on E566's kept strided jobs the read is the
dword plus 32 plus 64 per column at W = S = 64, six frozen forms held out offline at 64 x 16 (2048
of 2048) and all refuted at W = 32, S = 64 (0 of 2048); post hoc, dword + floor(S * S * u) with u
clamped to [0, 1] fits all three jobs. What stays: bits 11 and 12, bit 14 held out at other widths
and strides (W != S, a width that is no power of two, u past both ends) and on a twiddled texture.
The round 9 session r9-x's stage t3 runs both (bit 14 with u inside and past the texture, bits 11
and 12 on a strided and a twiddled texture).
