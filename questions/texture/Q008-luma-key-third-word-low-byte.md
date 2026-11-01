+++
id = "Q008"
question = "how is the luma compared at the luma key's low cut (bits 7:0 of the word that loads 0x0868), where 8 pixels in 2 of 274 copies, 4/1024 above the cut, fall the other way, and what do bits 31:16 of the alpha word and the offset's precision do?"
unit = "texture"
phase = 6
evidence = ["E039", "E275"]
terms = ["CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET", "CR_TPU_LUMA_KEY_ALPHA", "T0.ALPHA_FROM_LUMA_KEY", "transfer_cmd.load_tpu_luma_key"]
+++

Bits 7:0 of the third word are the low end of a luma band (E275): a pixel whose luma lies from
the low byte to the threshold (bits 15:8) takes alpha_below, every other pixel alpha_above. All
256 values at threshold 128 and nine at thresholds 0 and 255 follow this, every pixel of 272 of
274 copies; E039's three misfits (64, 128, 255) are this band. So what the low byte does is
answered.

What is open: the rounding at the low cut. With the luma taken as (S + r) >> 10 for any r from 12
to 35 the low cut fits 272 copies; at low bytes 119 and 122 eight pixels each, with S 4 above the
cut (low x 1024 + 4), take alpha_above, which would need r below -4 while the copy at low 33
needs r of 12 or more. The high cut fits E039's r of 0 to 19. Whether the two cuts use
different roundings, or the sum has more terms, is not shown.

To settle it: a source whose pixels place S on every value within ±16 of the cuts at 119, 120
and 122 (a ramp in one channel with the other two fixed), at both the low and the high cut.

Not run in 11.15: the settle plan needs a copy source whose pixels place the luma sum on every value
within 16 of the cuts at 119, 120 and 122 (a ramp in one channel); the copy tool's sources are a
fixed pattern and the every-value permutation, with no ramp. Status: narrowed, not answered;
missing: a ramp source option.
