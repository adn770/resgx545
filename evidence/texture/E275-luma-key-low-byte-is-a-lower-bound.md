+++
id = "E275"
claim = "Bits 7:0 of the luma-key word that loads 0x0868 are the lower bound of a luma band: the copy writes alpha_below where low byte <= luma <= threshold and alpha_above elsewhere, at every pixel of 272 of 274 copies (all 256 values of the low byte at threshold 128, nine values at thresholds 0 and 255); in the other two (low byte 119 and 122) 8 pixels each, whose weighted sum is 4/1024 above the low cut, fall the other way; RGB is the source's in every copy"
unit = "texture"
method = "the hand-run script of probes/texture/luma-cuts.toml (section low-byte) on the laptop, linux fork with the debug option on: the 64x32 copy over the every-value source with T0 bit 31 and the three luma-key words loaded (xfer:17 bit 1; 0x02020106, 0x00210064 and 0xff00TTLL), every pixel read back; the cuts of each copy found by tools/usse-asm/tex_words.py (cuts) against the luma of E039's weights, and the band model checked pixel by pixel (tex_words.py band); one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-luma-cuts"]
terms = ["CR_TPU_LUMA_KEY_ALPHA", "CR_TPU_LUMA_KEY_ALPHA.LOW", "CR_TPU_LUMA_KEY_ALPHA.THRESHOLD", "CR_TPU_LUMA_KEY_ALPHA.BELOW", "CR_TPU_LUMA_KEY_ALPHA.ABOVE", "CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET", "T0.ALPHA_FROM_LUMA_KEY", "transfer_cmd.load_tpu_luma_key"]
+++

**What runs.** E039's model computes, per pixel, S = 262 R + 514 G + 100 B + 512 x 33 and the
luma S >> 10, and writes alpha_above (bits 31:24 of the third word) where the luma exceeds the
threshold (bits 15:8) and alpha_below (bits 23:16) elsewhere; it fitted 74 of 77 copies and left
out bits 7:0, which broke it at 64, 128 and 255. Here the low byte takes every value with the
threshold at 128, alpha_above 0xff and alpha_below 0, and nine values with the threshold at 0
and at 255. The every-value source's lumas run from 32 to 208, in steps (no luma between 58 and
74, for instance).

**Results.** In all 274 copies RGB is the source's at every pixel.

- Low byte 0 to 32: alpha 0 for lumas 32 to 122, 0xff for 139 to 208: E039's image.
- Low byte 33 and up, threshold 128: the lumas below the low byte take 0xff as well; at 34 the
  lumas 32 and 33; at 56 those up to 55; at 64 and up to 75 those up to 57 (no luma between);
  at 101 those up to 100; from 123 on every pixel, as no luma lies between the low byte and 128.
- Threshold 0: alpha 0xff at every pixel for all nine low bytes. Threshold 255: alpha 0 at every
  pixel for low bytes 0 to 32; 0xff below the low byte and 0 from it up for 64, 96, 128 and 192
  (at 128 the lumas up to 122 take 0xff, 139 up take 0); 0xff at every pixel for 255.
- The band model, alpha_below where low <= (S + r) >> 10 and S >> 10 <= threshold, gives every
  pixel of 272 copies for any r from 12 to 35 (`tex_words.py band`; at 11 the copy at low 33
  misfits, at 36 those at 76 and 98); at low bytes 119 and 122, 8 pixels each, with S 4 above the
  cut (121860 = 119 x 1024 + 4 and 124932 = 122 x 1024 + 4), take alpha_above, which no r >= 0
  gives.

**What it shows.** The key is a band: the third word holds both ends, bits 7:0 the low one and
bits 15:8 the high one, and a pixel whose luma lies inside takes alpha_below. E039's values 1 and
0x10 changed nothing because no luma of that source lies below 32; 64 left a band of 75 to 122,
the 936 pixels it found; 128 and 255 an empty band. The few pixels at the low cut suggest that
the low comparison does not use quite the sum of the high one (another rounding) **[infer]**.
