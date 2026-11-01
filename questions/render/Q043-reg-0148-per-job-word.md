+++
id = "Q043"
question = "what does bit 0 of CR_REG_0148, which the firmware loads for every render, partial render and transfer, change, when no bit of the word changes a triangle, five copies, a fill or a copy?"
unit = "render"
phase = 11
evidence = ["E056", "E163", "E160", "E015", "E028", "E252", "E302", "E412", "E406"]
terms = ["CR_REG_0148"]
+++

The firmware loads register 0x0148 from render details dword 9 at every 3D kick (E163), at a partial
render (E160) and from the transfer command (E015). The register keeps only bit 0 (E252). Render
details dword 9 at 0xffffffff and with each of its 32 bits alone changes no pixel of the triangle
job, and four values change none of the five-copy job; after each job the register reads 1 exactly
when bit 0 was set (E302, one run). The transfer command's word for the register changes no fill and
no copy at any of 34 values (E302, from the transfer kernel-word sweep, one run). Six address forms
wrote nothing to a scratch page (E056).

What is open: what bit 0 enables. The glossary's reading, a mode of a feature these clients leave
off, stays a hypothesis.

To settle it: bit 0 set in jobs that use what the clients here leave off: a render with depth
and stencil buffers loaded and stored, a multisampled render, a render that overflows into
partial renders, a copy with filtering, each against its control, every pixel and the visibility
counters read back.

Narrowed in 11.15 (E412, three runs each): bit 0 of the word at 0 and at 1 gives the same image,
stored pages and times in a render with depth and stencil stored, in 4x renders in modes 1 and 2, in
a 1024x768 render and in one that overflows the parameter buffer (0x24 and 0x30 pages, the same
wrong-pixel counts), all with shaders that write o0 only. With the tagged shader of E406 it is not
inert: bit 0 set keeps o1 from landing on other pixels (tags 1, 3, 5, 7 where the plain job shows 1
to 7, 3 of 3). Not run: a copy with filtering
(no filtered copy in the transfer tool). Status: narrowed, not answered.
