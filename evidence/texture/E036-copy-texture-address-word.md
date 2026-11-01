+++
id = "E036"
claim = "In the copy's texture word T2, bits 2 to 11 and 13 move the source address by 2^n bytes (the first pixel written is the source texel that far in), bit 12 reads other data, bit 14 completes the job with nothing written, bits 15 to 31 and the values 0 and 0xffffffff fault; bits 1:0 are not address bits (they give colours that are no source texel); over the every-value source, whose texels repeat every 1024 bytes, bits 10 and 11 change nothing"
unit = "texture"
method = "sweeps of probes/texture/state-words.toml, copy-tex-bg and copy-every-tex-bg (1123 cases each, 64x32 copy, plain and every-value source; word tex:2), on the laptop, linux fork with the debug option on"
tiers = ["HW"]
date = "2026-11-01"
data = ["texture-state-words"]
terms = ["T2.TEXADDR"]
+++

**What runs.** The copy builds the four texture words of its source, T0 to T3, and the sweep flips
each bit of T2 (`tex:2`) and sets it to 0 and to 0xffffffff, one copy per case, comparing the
target to the unflipped copy's (hash 0x9b1c0be484ac0d25 for the plain source, 0x88c655df5891e325
for the every-value source). The first pixels below fit a plain source that holds, at column x and
row y of 64x32 texels, 0xa5000000 | y << 16 | x << 8 | ((x + y) & 0xff), read off the cases
themselves, so the first pixel of a changed target names the source texel it read.

**Results**, plain source, first pixel of the target:

- Bits 2 to 7: 0xa5000101, 0xa5000202, 0xa5000404, 0xa5000808, 0xa5001010, 0xa5002020: the
  texels at x = 1, 2, 4, 8, 16, 32 of row 0, that is the source address plus 4, 8, ... 128
  bytes. Bits 8 to 11 give the texels at y = 1, 2, 4, 8 (0xa5010001, 0xa5020002, 0xa5040004,
  0xa5080008): rows are 256 bytes apart. Bit 13 gives 0xa5200020, row 32, the pattern
  continued past the 32 rows of the source.
- Bit 12 gives 0x04000004, not row 16 (which would be 0xa5100010): at +4096 bytes the copy reads
  data that is not the source's continuation. Over the every-value source the same word is
  read and 1024 of the 2048 pixels change.
- Bit 14: the job completes and nothing is written (the target is the sentinel, hash
  0xfc8ce806207f8325), in both sources.
- Bits 15 to 31 flipped, 0 and 0xffffffff: the job faults and the context is lost, both
  sources.
- Bit 1: the first pixel is 0xa52a2a00, bit 0: 0xa52a200a. Neither fits that pattern (the
  low byte would be x + y), and bit 2's 0xa5000101 does: bits 1:0 do not move the source by
  one or two bytes, and each of the two flips changes all 2048 pixels (2040 over the every-value
  source, where a few pixels coincide), with its own target hash (0xc9964303ae0e3325 for bit 1,
  0x9f9d55383efd5b25 for bit 0). That the bit-1 target is one colour over its whole area and
  the bit-0 target eight colours in runs is consistent with these counts but the data does not
  show the targets, only their hashes and first pixels.

Over the every-value source the first pixel for bits 2 to 9 is a texel whose high byte is
1, 2, 4, 8, 16, 32, 64 and 128: the texels of that source repeat every 256 texels, 1024
bytes, so bits 10 and 11 (offsets 1024 and 2048 bytes: 0 of 2048 pixels differ) read the same
texel as the unflipped copy.

**Not shown.** What is at +4096 bytes (bit 12); why bit 14 completes without writing while
bit 15 faults; how a changed address reads bits 1:0 (colours with no source texel).
