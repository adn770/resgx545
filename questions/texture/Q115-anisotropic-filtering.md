+++
id = "Q115"
question = "does the sampler filter anisotropically on this core, and which bits of the texture words or the smp operands select it and its ratio?"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E041", "E342", "E564", "E720", "E723"]
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

Narrowed in 11.32 (E564, not answered). A ratio sweep (2 to 32) of explicit gradients with bilinear
filters was compared with one bilinear tap at the level the footprint picks; the declared control
(ratio 8) did not match that formula either (1528 of 2048 pixels), so the baseline is not
established and no image can be called one tap or more. Of 15 bit flips at ratio 8, eleven (T0 bits
14, 15, 16, 28, 29 and T3 bits 8, 9, 15, 20, 21, 22) leave the image unchanged and so are not an
enable of this image; four change every pixel (T3 bit 11 cleared, T3 bit 12 set, T0 bits 27 and 30)
and read other state: names of level 0, one constant, and values that are no name of the buffer. No
anisotropic filtering was identified, and the failed control means none was ruled out. What is open:
whether the hardware has it, and a baseline the control can pass first.

Run in 11.39 (E720): the bilinear form of the baseline is two-stage xy (x then y, +32 and a 6-bit
shift at each stage), 8 of 8 held-out jobs exact against 0 of 8 for the joint form. This lifts
the "fit by a search on 6 jobs" caveat for the form and the rounding, not for the weight
precision: the 8 jobs have weights on the 1/64 grid (precision 64, 128 and 256 give identical
images), so the truncation to 1/64 rests on the landed vectors and the 11.32 jobs. Anisotropy is
unchanged and open. With the sRGB bit the bilinear order is not known (E723; the sRGB stage rule is
E982, answered by E1038).
