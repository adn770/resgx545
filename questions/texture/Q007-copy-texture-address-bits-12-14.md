+++
id = "Q007"
question = "what does bit 12 of the copy's texture address word read, and why does bit 14 complete with nothing written while bit 15 faults?"
unit = "texture"
phase = 6
evidence = ["E036", "E041"]
terms = ["T2.TEXADDR"]
+++

The copy's source texture address is the word T2 (E036). Flipping bits 2 to 11 and bit 13 moves
the first source texel read by 2^n bytes, as an address would. Three bits do not follow that.

Bit 12 (`tex:2^=0x1000`) is an offset of 4096 bytes, which is inside the 8192-byte source (64x32
texels of 4 bytes, so row 16). A source address would give the texel of row 16, 0xa5100010 in
the plain pattern. The first pixel written is 0x04000004 instead, the job completes, and all
2048 pixels differ from the baseline (target hash 0x333baa84526172ab). Over the every-value
source 1024 of the 2048 pixels differ (hash 0x6290812a2f44452b), the first again 0x04000004.
Bit 13 (+8192 bytes) does give the pattern continued past the source, so only bit 12 breaks the
rule among the low bits.

Bit 14 (`tex:2^=0x4000`) completes the job (`job: ok`) with every pixel left at the sentinel
(hash 0xfc8ce806207f8325), in both sources. Bit 15 (`tex:2^=0x8000`), every higher bit, 0 and
0xffffffff fault the job and lose the context, with the same sentinel hash. So the address
range the unit accepts ends between bit 14 (accepted, nothing written) and bit 15 (rejected by
a fault).

Not settled: what 0x04000004 is (a word of the scratch buffer, of the render's own state, or a
value the unit makes up), and whether the nothing-written result of bit 14 is a copy of zero
pixels or a copy to somewhere else. The state-words table ran once in this campaign, so
whether the bit 12 pixels repeat is not known either.

To settle it: run bit 12 and bit 14 with the buffer at +4096 and +16384 bytes filled with a
counting pattern (the host's counting fill of E041), read the whole target and the buffer
back, and match the first pixels to dwords of the buffer. Repeat the same flips with the source
at another address, to see whether 0x04000004 moves with it, and read the target of bit 14 and
of the buffer for writes outside the 64x32 target.
