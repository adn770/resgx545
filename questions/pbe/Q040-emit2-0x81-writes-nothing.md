+++
id = "Q040"
question = "what do EMIT2 bits 15:8 count, given that 4v pixels of each tile are stored for an even v up to 0x80, odd values hang and values above 0x80 change the image, and what do EMIT2 bits 6:0 select?"
unit = "pbe"
phase = 11
evidence = ["E046", "E265", "E266", "E267", "E382"]
terms = ["EMIT2.BITS15_8", "EMIT2.BIT28", "EMIT2.BIT29", "EMIT2.BIT30"]
+++

The table E046 took for EMIT2 bits 15:8 varied the pixel-event program's data dword 8, its
end-of-render mask: E046's 0x81 is that dword at 0, which makes the program skip every tile's
end-of-tile task; at 0x2 the same, at 0x4 only the last tile's (E265). So the original question,
why 0x81 alone writes nothing, is answered, and it said nothing about EMIT2.

The real field, set in the end-of-tile program, is a count (E266): 0 stores nothing, every odd
value hangs the job, an even value v up to 0x80 stores 4v pixels of every 32x16 tile (two
halves of eight rows from their first row), and values above 0x80 store the whole tile with up
to 2524 of 4096 pixels changed.

The other bits are known better since E382, which ran a shader that names each pixel by its own
x and y, so the place a pixel lands names the transform. Bits 29:28 rotate the stored image by
90, 180 and 270 degrees at 1, 2 and 3 (every one of 1062 pixels, two runs): bit 28 is a rotation
by 90 degrees, not the mirror in x that E267 read from a triangle symmetric about x = y, and bit
29 alone a rotation by 180 degrees. Bit 31 scales the image by two, the pixel at (X, Y) coming
from (X/2, Y/2), after the rotation when bits 29:28 are set (1728 of 1728 named pixels). Bit 30
(and every value with it set, 0x4-0x7 and 0xc-0xf) stores no word that names a pixel; E267's 2x2
box average into each tile's top-left 16x8 pixels stands, as an inference, because its image
fitted every pixel in both runs. Bit 7 does not change the image.

Bits 6:0 change the image, and a fit says how: reading each tile's pixels from an offset into the
order x0, y0, x1, x2, x3, y1, y2 of each 16x8 block explains 928 to 1053 of about 1050 named
pixels at 1, 2, 4, 8 and 16, 1035 at 3, 798 at 32 and 530 at 64, and 8 at 127; the misfits lie
where an offset would carry out of a block. The offset and its order are a fit [infer], not a
read-out. Counts 0x82-0xfe change 39 to 2742 pixels, mostly at the first places of each tile's
order.

What is open: why bit 8 of the count hangs (a count of pairs, or a unit that must be whole), what
the PBE stores beyond 0x80, what bits 6:0 are (the unit, the range and the order of the offset are
a fit, and 127 does not fit it), and what bit 30 does to a named image (an average of four names
none).

To settle it: bits 6:0 at every value, with the shader writing a known word to each output
register o0-o15 and the task's temporaries preset, so that each pixel names the register it came
from; bit 30 with a shader whose pixels differ in one byte only, so that the average of four can
be told from a pick; the count above 0x80 with the shader that names pixels.
