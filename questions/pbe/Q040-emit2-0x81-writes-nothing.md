+++
id = "Q040"
question = "what do EMIT2 bits 15:8 count, given that 4v pixels of each tile are stored for an even v up to 0x80, odd values hang and values above 0x80 change the image, what do EMIT2 bits 6:0 and 31 select, and is bit 29 a rotation by 180 degrees or an anti-transpose?"
unit = "pbe"
phase = 11
evidence = ["E046", "E265", "E266", "E267"]
terms = ["EMIT2.BITS15_8", "EMIT2.BIT28", "EMIT2.BIT29", "EMIT2.BIT30"]
+++

The table E046 took for EMIT2 bits 15:8 varied the pixel-event program's data dword 8, its
end-of-render mask: E046's 0x81 is that dword at 0, which makes the program skip every tile's
end-of-tile task; at 0x2 the same, at 0x4 only the last tile's (E265). So the original question,
why 0x81 alone writes nothing, is answered, and it said nothing about EMIT2.

The real field, set in the end-of-tile program, is a count (E266): 0 stores nothing, every odd
value hangs the job, an even value v up to 0x80 stores 4v pixels of every 32x16 tile (two
halves of eight rows from their first row), and values above 0x80 store the whole tile with up
to 2524 of 4096 pixels changed. EMIT2 bits 6:0 change the image with words of the task's own
registers among the pixels, as an offset into the place the colours are read from would; bit 7
does not change it. Bit 28 stores the image mirrored in x, bit 29 rotated by 180 degrees, and
bit 30 each tile's 2x2 box average into its top-left 16x8 pixels, every pixel in both runs
(E267); the old glossary hint of a downscale, rotate or flip field (Rogue, AGX) fits these
EMIT2 bits. Bit 31 stores a triangle of another shape in the same colours.

What is open: why bit 8 of the count hangs (a count of pairs, or a unit that must be whole),
what the PBE stores beyond 0x80, the unit and range of the offset in bits 6:0 (one bit at a
time was set), and what bit 31 selects. The triangle is symmetric about x = y, so bit 29's
image is also the anti-transpose and bit 28's also a rotation by 90 degrees; the bits' combined
values were not run.

To settle it: bits 6:0 at every value with the shader writing a known word to each output
register o0-o15 and the task's temporaries preset, so that each pixel names the register it
came from; bits 31:28 at each of their 16 values with a shader that writes the pixel's own x
and y (an image with no symmetry), so the place each pixel lands names the transform and tells
the rotation from the anti-transpose; the count above 0x80 with the same shader.
