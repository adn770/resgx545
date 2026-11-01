+++
id = "Q181"
question = "does the fill's transfer command load a colour-space set at all (xfer:17^=1 and xfer:18 to 22 made no difference for formats 28 and 29, E568), and if not, which path loads the set that the YUV conversion reads"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E568", "E037", "E040"]
terms = ["TEXFORMAT"]
+++

E568: eight YUV jobs read opaque black with or without the poke. Whether the set is not loaded or
the fill's transfer command ignores these words is not told apart. To settle it: a copy (as E037)
with the same words, and a fill with the poke read back from the transfer command's state.
