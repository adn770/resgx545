+++
id = "Q078"
question = "does T3 bit 14 on a twiddled texture read texel (s + floor(4096 frac(u)), t) of a layout of 16 x 16 tiles with W + 4096 texels a tile row at other sizes and formats (E1047: every pixel of three fills of E566's 32 x 32 32-bit texture, fitted post hoc on E1033's fault pages and held out by u = 0 only), is the tile row W + 4096 or 4128 texels, is u past 1 taken by its fraction or clamped at another width, and what does the bit do to a filtered twiddled sample?"
unit = "texture"
kind = "hw"
value = "high"
phase = 11
evidence = ["E274", "E397", "E566", "E564", "E722", "E723", "E968", "E975", "E1003", "E1027", "E1033", "E1047"]
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
held-out fills; the bilinear part answered by E1038), and bits 10, 18-19 and 27-28, whose transform is
E722's level and scale model held out on 13 of 13 fills that completed (the spec gives it with its
limits, which stay there). Bit 14 is narrowed by E968: on E566's kept strided jobs the read is the
dword plus 32 plus 64 per column at W = S = 64, six frozen forms held out offline at 64 x 16 (2048
of 2048) and all refuted at W = 32, S = 64 (0 of 2048); post hoc, dword + floor(S * S * u) with u
clamped to [0, 1] fits all three jobs. What stays: bits 11 and 12, bit 14 held out at other widths
and strides (W != S, a width that is no power of two, u past both ends) and on a twiddled texture.
The round 9 session r9-x's stage t3 runs both (bit 14 with u inside and past the texture, bits 11
and 12 on a strided and a twiddled texture).

Note 2026-11-13 (E975). r9-x held E968's bit-14 rivals out on six strided geometries: the
column-centre form (R-U) failed all six, i + floor(S * S * clamp(u, 0, 1)) held four and failed the
two where S * S is not 4096 (W 32 at strides 128 and 32). Post hoc, every pixel of the six reads the
bit-clear dword plus floor(4096 * clamp(u, 0, 1)), whatever S and W: a rule to hold out (another S,
a twiddled texture, v varying). Bits 11 and 12 changed nothing on a strided texture again, and
E564's twiddled bit-11 and bit-12 images replicated byte for byte; their read-out is not decoded.
Open: bit 14's constant held out, and bits 11 and 12 on a twiddled chain.

Narrowed 2026-11-13 (round 10, session r10-tex, decision R10-2 a; E1003; the question line
is rewritten to what stays). Bit 14 on a strided texture is answered for point
samples: the read is the bit-clear texel plus floor(4096 clamp(u, 0, 1)) texels, held out on six
geometries (strides 16 and 256, u off the grid and past both ends, v varying, a 16-bit format, where
the count is texels, not dwords); sgx-sim models it. What stays: bit 14 on a twiddled texture
(E566's fault) and filtered, and bits 11 and 12 on a twiddled chain.

Note 2026-11-13 (round 11 offline, decision R11-8 a; closing11/plan/rank-round11.md finding 8,
closing11/plan/c8-q078/; no record: a decode written after reading the only two jobs, post hoc).
E564's twiddled 64 x 64 chain under the counting fill names every dword, and E561's tile law over
E722's offset chain maps the 5461 names one to one: with T3 bit 11 cleared every pixel reads level
0's texel (x, y) (2048 of 2048; the control reads levels 3 and 4), with bit 12 set dword 5460, the
1 x 1 level 6 (2048 of 2048); a stride read, an offset chain from 0 and a bit-10 clone score 8, 1
and 0 of 2048. r9-x's t3 images are E564's byte for byte (replicates, not held out). Not parted by
these images: a forced level, mips off and a LOD bias (bit 11: -3.5 or less; bit 12: +2.5 or
more), the last level and a constant dword, nearest and bilinear. E564 and E975 take appended
corrections that say so. A later row: bit 11 cleared at LOD 0 to 6, bit 12 with T0's maximum
level below 6 and at LOD 0, bits 12:11 = 10, a 32 x 32 chain. [infer] A 2-bit LOD-mode field (00
level 0, 01 the gradient's level, 11 the coarsest) fits the three values seen; 10 is untested.

Narrowed 2026-11-13 (round 13, session r13-tex, decision R13-1 a; E1027; the question line is
rewritten to what stays; not retired: R13-9 needs r13-flag's F1 for bit 14 on a twiddled texture).
Answered: T3 bits 12:11 select the level on a twiddled chain whatever the LOD: 00 level 0 (9 of 9
held-out rows, LOD 0 to 6, a 32 x 32 chain, mips off), 01 the LOD's level, 11 and 10 the last level
T0's max level allows (3 of 3 and 1 of 1); a LOD bias and a constant address failed. Bit 14 under a
bilinear sample on a strided texture moves the footprint by E1003's count (1 of 1). What stays: bit
14 on a twiddled texture.

Narrowed 2026-11-13 (round 13, session r13-flag stage f1, decision R13-3 a; E1033). Bit 14 on a
twiddled 32 x 32 texture faulted both rows run: E566's own job again (u past 1) and a held-out row
with u = x / 4096, where E1003's strided move would be 0 to 63 texels; the fault pages were 132 KiB
and 256 KiB past the scratch, past every mapping of the job. The three frozen move models (the move
in the twiddled index, the plan's H-TWMOVE; in the texel column, unwrapped or wrapped) each
predicted an image there and failed 2 of 2; H-FAULTANY held 2 of 2. So the twiddled clause is
narrowed to where the read goes (only each job's first faulting page is known); not retired (R13-9:
no held-out row decodes the address).

Narrowed 2026-11-14 (round 14, session r14-flag stage f1, decisions R14-4 (a) and R14-5 (a); E1047;
the question line is rewritten to what stays; not retired). It read "where does T3 bit 14 send a
twiddled read, where it faults the job past every mapping whatever the move E1003 measured (E566,
E1033), given that on a strided texture it moves a point sample by floor(4096 clamp(u, 0, 1))
texels (E1003) and a bilinear footprint as a whole (E1027)?". With a 1 MiB scratch (t14) no row
faulted and every pixel of the three bit-14 fills named its dword: the read is texel (s +
floor(4096 frac(u)), t), s the wrapped bit-clear column, of a layout of 16 x 16 tiles with W + 4096
texels a tile row (H-TWP4128, 2048 of 2048 on each; a tile row of 4096 texels, a column without s,
the bit-clear image at u = 0 and "every twiddled read faults" failed). E566's and E1033's faults
are the reads past a 64 KiB scratch. Why it is not retired (R14-6): the form was fitted post hoc on
E1033's two fault pages, and of its three rows only u = 0 is held out; f1-tw32 and f1-small rerun
the fitted inputs (their images new, their inputs not), and only W = 32 ran, so W + 4096 is not
parted from a constant 4128, nor the fraction of u past 1 from a clamp at another width. sgx-sim's
tex.rs models the 32 x 32 geometry and refuses the rest. To retire: the form held out at two other
widths (16 x 16 and 64 x 64, say) with u past 1, then filtered.
