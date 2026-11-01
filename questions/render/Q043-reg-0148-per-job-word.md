+++
id = "Q043"
question = "what does bit 0 of CR_REG_0148, which the firmware loads for every render, partial render and transfer, change, when no bit of the word changes a triangle, five copies, a fill or a copy?"
unit = "render"
phase = 11
evidence = ["E056", "E163", "E160", "E015", "E028", "E252", "E302"]
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
