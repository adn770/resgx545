+++
id = "Q011"
question = "why do the plain and every-value copies differ in pixel count for xfer:0 bits 24 to 30 and =0, and xfer:7 bit 1?"
unit = "transfer"
phase = 6
evidence = ["E028"]
terms = ["transfer_cmd"]
+++

A 1429-case flip table of the transfer command runs over two sources, the plain pattern and the
every-value source (E028). The two agree case for case in class. In 13 of the 22 changed cases
the pixel count is the same in both. Nine differ:

- word 0 with any of bits 24 to 30 flipped, and word 0 set to 0: 2047 of 2048 pixels differ
  from the baseline over the plain source and 2040 over the every-value one. In each source
  the eight cases give the same first pixel (0xa51f3f20 for plain, against 0xa5000000 expected;
  0xff6648dc for every-value, against 0x000d6539).
- word 7 bit 1: 2047 plain and 2044 every-value, first pixels 0xa5081018 and 0x107d3509.

In both sources the first pixel is neither the expected one nor the sentinel (0xdeadbeef, which
word 0 set to 0xffffffff leaves in all 2048 pixels). The pixels that still agree with the
baseline are 1 of 2048 over the plain source and 8 (or 4, word 7) over the every-value one.

A coincidence of a few pixels with the baseline is what a target that does not follow the
source would give, and the every-value source repeats colours more often than the plain
pattern; a function of the pixel's value would instead be a map the data does not show. No run
reads the target's pixels against the source, so the data does not tell the two apart (E028
says the same). Nor is it known which pixel agrees in the plain copy.

To settle it: run word 0 bit 24 (one flip stands for the seven, and word 0 = 0) and word 7
bit 1 over both sources with `--pixels`, compare the whole target with the source texel by
texel, and fit it as a shifted or strided read and as a per-channel function of the value.
Then check that the fit predicts 2047 and 2040 (word 0) and 2047 and 2044 (word 7).
