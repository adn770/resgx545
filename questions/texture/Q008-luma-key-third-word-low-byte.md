+++
id = "Q008"
question = "what do bits 7:0 of the luma-key word that the TPU loads into 0x0868 do?"
unit = "texture"
phase = 6
evidence = ["E039"]
terms = ["CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET", "CR_TPU_LUMA_KEY_ALPHA", "T0.ALPHA_FROM_LUMA_KEY", "transfer_cmd.load_tpu_luma_key"]
+++

With T0 bit 31 set, a copy takes alpha from the three words that load 0x0860 to 0x0868 (E039).
The model fitted there, a weighted sum of R, G and B plus an offset compared against a
threshold in bits 15:8 of the third word, reproduces the alpha of every pixel in 74 of 77
hand-run copies, in both runs. Bits 7:0 of the third word do not enter it, and for the values
1 and 0x10 they change nothing, which is why the model leaves them out.

Three copies do not fit. With bits 7:0 at 64, 128 and 255 (the other bytes at their starting
values) the copy at 64 gives alpha_above at 1112 pixels and alpha_below at 936. The 936 all have
a luma (the sum shifted by 10) between 75 and 122 and the 1112 range from 33 to 208, so the
alphas are not monotone in the luma and no threshold separates them. The copies at 128 and 255
give alpha_above at all 2048 pixels, which a threshold of 128 on that luma does not allow.
The same three results came in both runs.

What the data supports: the low byte is not inert, and its effect depends on its value, at 1
and 0x10 nothing and from 64 up a lot. Candidates not excluded: a second threshold or a mask
applied to the luma, a field that gates the comparison (an enable that 64 turns on and 128
and 255 saturate), or a clamp on the sum. The model with a threshold from bits 7:0 instead of
15:8 was not fitted here.

To settle it: scan all 256 values of bits 7:0 with the other two words and the bytes of the
third at the starting values, printing every pixel as luma-key-bytes does, and fit alpha against
the luma for each value (a table of the 256 sets of cut points). Repeat with the threshold byte
at 0 and at 255, and with a source whose luma covers 0 to 255 evenly, so that a cut point shows
as a step.
