+++
id = "Q009"
question = "what do T0 bits 20:17 do for mipmaps, when bits 26:21 = 0x3f enable the chain only for some of their values?"
unit = "texture"
phase = 6
evidence = ["E041"]
terms = ["T0.NO_MIPMAPS", "T0.BITS26_21", "T0.BITS20_19", "MIPMAPS_PRESENT"]
+++

The mip chain of a 16x16 twiddled texture is read at LOD 2.0 (tag 0x80, level 2) with T0 =
0x07fa0000, that is bits 26:21 = 0x3f and bits 20:17 = 0xd (E041). Varying the fields gives:

- bits 26:21 at 0x3f and bits 20:17 at 0xd, 0xc, 0x9 or 0x5: level 2 is read.
- bits 26:21 at 0x3f and bits 20:17 at 0x0, or 0xf (bit 18 set, T0 0x07fe0000): level 0.
- bits 20:17 at 0xd and bits 26:21 at 0, 1, 2, 3 or 7: level 0.

So bit 18 clear is not enough, since 0x0 reads level 0 although it has bit 18 clear. The values
that read level 2 each have a bit set among 20, 19 and 17 and bit 18 clear. A rule "the chain is
read when bit 18 is clear and bits 20:17 are not zero" fits the five values tried (0xf, 0x0 and
the four enabling ones) but is the fit, not a measurement: only 6 of the 16 values were run,
and bits 26:21 only at 0x3f and five lower values (not at the 58 others).

Not settled: whether the field is two flags (bit 18 clear and one of bits 20, 19, 17 set), an
encoding of a level count or a size, or the sum of fields in the same word as the filter bits;
and what bits 26:21 below 0x3f other than the five tried do (the data does not say that only
0x3f works). This table ran once.

To settle it: read LOD 2.0 over all 16 values of bits 20:17 with bits 26:21 at 0x3f, then over all
64 values of bits 26:21 with bits 20:17 at 0xd, two runs each, tagging the result by level as in the
probe texture-mipmaps-mip-t0-field. Then run bits 20:17 at each value against a chain of two, three
and four levels, to see whether the field counts levels.