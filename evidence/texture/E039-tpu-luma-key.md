+++
id = "E039"
claim = "With T0 bit 31 set, a copy reads its texture as RGB, passes RGB through and takes alpha from the three words that load 0x0860 to 0x0868: alpha_above if a weighted sum of R, G and B plus an offset exceeds a threshold, else alpha_below; one model fits 74 of the 77 hand-run copies exactly, in both runs, and the 3 others, with bits 7:0 of the third word at 64, 128 and 255, fit none of its thresholds; T0 bit 31 is the only bit of T0, T1 and T3 whose effect depends on the three words repeatably, in both runs (six other cases differ between the tables, not repeatably)"
unit = "texture"
method = "hand-run script probes/texture/templates/tpu-csc.sh (luma-key-bytes, luma-key-fields, luma-key-modes; 77 copies of the every-value source with --pixels) and sweeps copy-tpu-diff-init-values and copy-tpu-diff-other-values of probes/texture/tpu-csc.toml (103 cases each), on the laptop, linux fork with the debug option on; two runs, the second is the follow-up run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["texture-tpu-csc", "texture-tpu-csc-followup"]
terms = ["CR_TPU_LUMA_KEY_RG", "CR_TPU_LUMA_KEY_B_OFFSET", "CR_TPU_LUMA_KEY_ALPHA", "T0.ALPHA_FROM_LUMA_KEY", "transfer_cmd.load_tpu_luma_key"]
+++

**What runs.** The 64x32 copy over the every-value source with T0 bit 31 set and the load flag
of the three words (xfer:17 bit 1) raised. The words xfer:29, xfer:30 and xfer:31 load
0x0860, 0x0864 and 0x0868; the starting values are 0x02020106, 0x00210064 and 0xff008000.
luma-key-bytes replaces each of their 12 bytes by 1, 64, 128 and 255 (48 copies),
luma-key-fields scans the fields named below (26 copies), luma-key-modes runs a plain copy and
the mode with the words absent, at the starting values, at zeros and at 0x01020304,
0x05060708, 0x80402010 (5 copies; the 3 with the load are in the 77 below, with 48 and 26).
Every pixel is printed. The two sweeps flip every bit of T0, T1
and T3 with the words at the starting values and at 0x40ff7f10, 0x7fff0020, 0x00ff0080.

**Model.** Written in the fields the fit uses: wR is bits 9:0 and wG bits 25:16 of the first
word, wB bits 9:0 and the offset bits 23:16 of the second, the threshold T bits 15:8, alpha_below
bits 23:16 and alpha_above bits 31:24 of the third:

    S = wR * R + wG * G + wB * B + 512 * offset + rnd
    alpha = alpha_above if (S >> 10) > T else alpha_below

**Results.**

- RGB is the source's in every pixel of every copy. The model, applied to the source's R, G
  and B, reproduces the alpha of every pixel in 74 of the 77 copies, in both runs, with the same
  rounding constant for all: rnd between 0 and 19 (of 1024), from the 69 copies in which the
  two alphas differ and the threshold falls within the sums (the other 5 are consistent and
  do not test it). The starting values are the limited-range BT.601 luma weights (262, 514, 100
  in 1024ths) with a 16.5 offset, keyed at 128: alpha 0 below and 0xff above.
- The three copies outside the model have bits 7:0 of the third word at 64, 128 and 255. The
  copy at 64 gives alpha_above at 1112 pixels and alpha_below at 936, the latter all with a
  luma (S >> 10) between 75 and 122 while the former range from 33 to 208, so no threshold on
  that luma separates them; 128 and 255 give alpha_above at all 2048 pixels, which a threshold
  of 128 does not (luma below 128 should give alpha_below). The value 1 fits the model, and
  so does the copy at 0x80402010 (bits 7:0 = 0x10), alpha_above 0x80 at all 2048 pixels,
  which the model allows but does not test.
- The sweeps: with the words at their starting values and at the others, the images differ at one
  bit only deterministically: T0 bit 31, hash 0xa8c1785e10ca73e5 at the starting values and
  0xcfa65fc4f12b6325 at the others, in both runs (the second set has bits 7:0 of the third word at
  0x80 and the two alphas swapped; 0xcfa65fc4f12b6325 is also the hash of the copy with the words at
  zeros). Six other cases differ between the two tables in both runs (T0 bits 20 and 21, T1 bits 5
  and 6, T3 bits 14 and 18), but their hashes change from run to run in at least one table: they are
  not repeatable differences. T1 bit 28 (`tex:1^=0x10000000`, with the luma-key load flag raised),
  in `copy-border-t13` and in both sweep tables completes with all 2048 pixels differing, the first
  pixel 0xff000000 and the target hash 0xd3522437a14b6325, the hash of an opaque black target
  (E037), in both runs and whatever the three words hold (Q010).
- Without the load flag the mode gives the image of the starting values (alpha 0 at 1112
  pixels and 0xff at 936, hash 0xa8c1785e10ca73e5): the block holds the starting values until
  something loads it. Zeros give alpha 0 everywhere.

**Not shown.** What bits 7:0 of the third word do; the rounding constant and the 16.5 offset
beyond the interval above; any other T0 bit with the words.
