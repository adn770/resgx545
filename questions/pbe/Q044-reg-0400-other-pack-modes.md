+++
id = "Q044"
question = "what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them changes a stored pixel in pack modes 0 to 3, and does bit 25 act on the other pack modes?"
unit = "pbe"
phase = 11
evidence = ["E029", "E028", "E031", "E251", "E268"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "SIDEBAND.PACKMODE"]
+++

Bit 25 of the word that loads 0x0400 inverts the stored alpha channel, wherever the pack mode
puts it: bits 31:24 in ARGB8888 and ABGR8888, bits 7:0 in BGRA8888, and nothing in RGB565, which
stores no alpha (E268). So the first half of the question (byte 3 or alpha) is answered: alpha.
The register takes bit 25 and bits 11:0 (E251); each of bits 0 to 11 flipped from the 0x80 the
library writes, and the word at 0, change no pixel in pack modes 0 to 3 (E268), as E029 found
for ARGB8888 over fills and copies.

What is open: what bits 11:0 control. No job here varies the alpha of the stored pixels (the
shader colour's alpha is 0x80, the low byte's value), so a field that tests alpha would not show.
Bit 25 under the pack modes with one or two alpha bits (ARGB1555, ARGB4444, A8) is not run.

To settle it: a triangle whose pixels carry alpha 0 to 0xff (a ramp over x) with the low byte at
0, 0x40, 0x80, 0xc0 and 0xff, in pack modes 0 and 4 (ARGB1555), where a threshold would decide
the stored alpha bit; bits 11:8 flipped with the same ramp; bit 25 in pack modes 4, 5 and 8.
