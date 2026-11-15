+++
id = "Q181"
question = "does the fill's transfer command load a colour-space set at all (xfer:17^=1 and xfer:18 to 22 made no difference for formats 28 and 29, E568), and if not, which path loads the set that the YUV conversion reads"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E568", "E037", "E040", "E1097"]
terms = ["TEXFORMAT"]
+++

E568: eight YUV jobs read opaque black with or without the poke. Whether the set is not loaded or
the fill's transfer command ignores these words is not told apart. To settle it: a copy (as E037)
with the same words, and a fill with the poke read back from the transfer command's state.

Narrowed 2026-11-15 (E1097, round 23's r23-pk on t22, no frozen verdict): E568's poke went through
a dangling poke set (E568's correction); on t22 the colour-space words are echoed as sent, and
every YUV fill read E037's conversion of its texel at 2048 of 2048 pixels, poked or not. Post
hoc, the set is kept from one job to the next across the runner's debugfs reset: E037's copy
without the load, run after a loaded copy, read the loaded copy's hash, not black. The first
poked fill of the session already converted, so a fill's transfer command loads the set [infer],
but no fill ran on a set known to be unloaded. To settle it: a copy that loads set 0 with zeros
(E037: black), then the poked fill (the conversion if a fill loads), then the same fill unpoked
(the conversion kept), frozen in that order.
