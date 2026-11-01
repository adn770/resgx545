+++
id = "Q044"
question = "what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them changes a stored pixel in pack modes 0 to 3, and does bit 25 act on the other pack modes?"
unit = "pbe"
phase = 11
evidence = ["E029", "E028", "E031", "E251", "E268", "E385"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "SIDEBAND.PACKMODE"]
+++

Answered in its main part (E385): the low byte of the word that loads CR_REG_0400 is the threshold of
ARGB1555's one-bit alpha (pack mode 4): with an alpha ramp over x the stored bit is set above the
low byte and clear below it (0x00, 0x40, 0x80, 0xc0, 0xff, every triangle pixel, two runs). The
threshold was run in mode 4 only, and bit 25 in modes 4, 5 and 8 (it inverts the alpha in modes 4
and 5 and changes nothing in mode 8; E268 covers modes 0 to 3). Bits 11:8 change nothing in modes 0
and 4 and bits 7:0 nothing in mode 0.

What is left: an alpha equal to the low byte (no pixel had it); the low byte in the other modes with
one or more alpha bits, and bit 25 in the pack modes not run; what bits 11:8 do, if anything.
