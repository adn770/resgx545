+++
id = "Q040"
question = "why does the end-of-tile emit write no pixel with EMIT2 bits 15:8 at 0x81 alone, when the other 255 values, those with bit 7 clear among them, write what 0x80 writes?"
unit = "pbe"
phase = 11
evidence = ["E046"]
terms = ["EMIT2.BITS15_8"]
+++

The fill's end-of-tile program emits with bits 15:8 of its EMIT2 word at 0x80. The table that sets
every value of the field (E046) gives the baseline image for 255 of the 256 values; 0x81 alone
writes no pixel, and all 2048 stay at the sentinel. So the field is not a valid bit with a count or
a mask below it: the values with bit 7 clear, 0x01 among them, write the image as 0x80 does, and so
do the other values with bit 0 set, such as 0x83 and 0xc1. One value out of 256 stopping the emit
fits a code compared with a fixed value, or a fault of the run, equally well.

What is open: whether 0x81 reproduces at all (the table ran once, on the fill only), whether it
stops the emit in other jobs, and what it is compared with.

To settle it: run 0x81 with its neighbours 0x01, 0x80, 0x83 and 0xc1 on the fill, the copy and the
triangle, twice each, every pixel read back. If 0x81 alone still writes nothing, flip the bits of
the emit's other words (the sideband and the PBE state words) one at a time with the field at 0x81:
a word that brings the image back names what the value is compared with.
