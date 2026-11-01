+++
id = "Q010"
question = "which field of the copy's T1 word is bit 28, that setting it writes opaque black whatever the source and the luma-key words?"
unit = "texture"
phase = 6
evidence = ["E037", "E039", "E046"]
terms = ["transfer_cmd.load_tpu_luma_key", "CR_TPU_LUMA_KEY_ALPHA"]
+++

The case flips bit 28 of the copy's T1 word (`tex:1^=0x10000000`) with the transfer
command's luma-key load flag raised (`xfer:17^=0x2`). It is in three sweep tables of
`probes/texture/tpu-csc.toml`: `copy-border-t13` (the three words at marker colours
0xff123456, 0xff654321 and 0xffabcdef), `copy-tpu-diff-init-values` (the starting values of
E039) and `copy-tpu-diff-other-values` (0x40ff7f10, 0x7fff0020, 0x00ff0080), the last two over
the every-value source.

In all three tables, in the first run and in the follow-up run (E037, E039): the job completes,
all 2048 pixels differ from the baseline, the first pixel is 0xff000000, and the target hash is
0xd3522437a14b6325. That hash is the hash E037 gives for a target of 0xff000000 in all 2048
pixels (opaque black), and E046 gives it for the 32 and 33 values of the copy's DOUTI0 field,
so the image is opaque black by hash identity; the pixels of these three cases were not
printed. The marker colours of `copy-border-t13` are not in the image, and the three luma-key
word sets do not matter (three different word sets, one image).

Not settled: why bit 28 of T1 gives opaque black regardless of the source and the words, and
which field of T1 the bit belongs to. The hash identity was checked, not the pixels.

To settle it: run the case with `--pixels` on, to compare the pixels to the 0xff000000 image;
run it alone first in a fresh context, then after a case that loads non-zero colour-space
words and the luma-key words, to see whether the preceding case matters; run it with T0 bit 31
clear as well.
