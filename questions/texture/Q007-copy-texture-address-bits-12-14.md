+++
id = "Q007"
question = "where do the copy's source, its destination and the page before the source lie, given that T2 bits 12, 13 and 14 read those buffers rather than the source's continuation?"
unit = "texture"
phase = 6
evidence = ["E036", "E041", "E273"]
terms = ["T2.TEXADDR"]
+++

T2 is an address in every bit from 2 up (E036, E273). Its odd images come from the memory around
the source (E273): flipping bit 12 reads the 4 KiB before the source, zeros and a few words such
as 0x3f800000, so the source's address has bit 12 set; with the source moved 4 rows down the read
starts 4096 bytes before the moved source; bit 14, and bit 13 with a source of 16 rows, read the
destination's sentinel and write it back, which is the "nothing written" of E036, and bit 14 with
a 16-row source faults. So the original question is answered: bit 12 is an address bit read from
another page, bit 14 copies the destination onto itself.

What is open: the inference rests on where the library places the buffers, which the run does not
print; and what the page before the source holds (0x04000004 at its first texel read).

To settle it: print the source, destination and scratch addresses with the job (a tool option),
and fill the page before the source with a counting pattern, then repeat the bit-12 and bit-14
flips.
