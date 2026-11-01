+++
id = "Q115"
question = "does the sampler filter anisotropically on this core, and which bits of the texture words or the smp operands select it and its ratio?"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E041", "E342"]
terms = ["TEXFORMAT"]
+++

The filter fields of T0 are the minification, magnification and mip filters, nearest or linear
(E041, E342); no record or glossary row names an anisotropy control. Q078 asks what the unexplained
bits T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27 select, but nothing in the records ties any of
them to an anisotropic filter.

Open: whether the hardware has anisotropic filtering at all, and if so its enable, its maximum ratio
and what it reads (more taps along the longer axis of the pixel's footprint).

To settle it: a textured triangle at a steep angle sampled by a USSE program, the T words'
unexplained bits flipped one at a time (the method of E274 in a copy) and the filtered image
compared with the plain linear one for taps spread along one axis.
