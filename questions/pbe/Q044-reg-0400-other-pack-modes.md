+++
id = "Q044"
question = "does CR_REG_0400 bit 25 invert the stored pixel's byte 3 or its alpha, and do the register's other bits act in pack modes other than ARGB8888?"
unit = "pbe"
phase = 11
evidence = ["E029", "E028", "E031"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "SIDEBAND.PACKMODE"]
+++

Bit 25 of the word that loads 0x0400 inverts bits 31:24 of every pixel a fill, a copy or the
triangle writes, background and triangle alike; no other bit of the word, nor 0, changes a pixel,
and over a source holding every value exactly the 128 values of the word's top byte with bit 25 set
change the image (E029, E028). Every one of these jobs stores ARGB8888, where bits 31:24 are the
alpha channel, so the data cannot tell an inversion of the alpha channel from an inversion of the
stored dword's top byte. The end-of-tile emit's pack modes store the colour in other orders too:
ABGR8888 (mode 1), BGRA8888 (mode 2) and RGB565 (mode 3) (E031).

What is open: what bit 25 inverts in a layout where alpha is not the top byte, and whether the other
bits, which change nothing in ARGB8888, act in another layout. The glossary's reading of the
register as a control of the pixel output conversion rests on bit 25 alone.

To settle it: render the triangle with the emit's pack mode at 1, 2 and 3, each with the register's
word as the job builds it, with bit 25 flipped, with each other bit flipped, at 0 and at 0xffffffff,
two runs each, every stored pixel read back. In BGRA8888 the alpha sits in bits 7:0: an alpha
inversion flips those and a byte-3 inversion flips bits 31:24. In RGB565, with two pixels to a
dword, a byte-3 inversion flips the high byte of every second pixel.
