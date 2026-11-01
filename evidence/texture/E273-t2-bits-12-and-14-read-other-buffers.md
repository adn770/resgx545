+++
id = "E273"
claim = "The copy's T2 bits 12 and 14 read memory outside the source like every other address bit: flipping bit 12 reads the 4 KiB before the source (mostly zeros, 0x3f800000, 0x1000; the first pixel 0x04000004), so the source's address has bit 12 set; with the source 16 rows long bit 13 reads the destination's sentinel and bit 14 faults, with it 32 rows long bit 14 reads the sentinel and completes, so bit 14's empty image is the destination's own sentinel read back; bit 13 as built leaves 448 and 256 sentinel pixels in the two rounds (plain source), 224 and 296 (every-value source), as a read of a destination the copy is overwriting would"
unit = "texture"
method = "the hand-run script of probes/texture/copy-words.toml (section t2-bits) on the laptop, linux fork with the debug option on: the 64x32 copy (and 64x16, --height 16) over the plain and the every-value source, as built and with the source 4 rows down (--sy 4), with tex:2 bits 11, 12, 13 or 14 flipped; two rounds, every pixel read back and matched to the source pattern; --sx 16 was rejected by the library (the source is the copy's width)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["texture-copy-words"]
terms = ["T2.TEXADDR"]
+++

**What runs.** E036 flipped each bit of T2 once without the pixels: bits 2 to 11 and 13 moved the
first texel read as an address would, bit 12 gave the first pixel 0x04000004, bit 14 completed
with the target left at its sentinel, bit 15 up faulted. The plain source holds 0xa5000000 |
y << 16 | x << 8 | (x ^ y) at texel (x, y), 256 bytes a row; the destination is filled with
0xdeadbeef before the job.

**Results**, both rounds alike but the sentinel counts of bit 13 as built (pixels of 2048, or
1024 at 64x16; first/second round):

| source | bit 11 | bit 12 | bit 13 | bit 14 |
|---|---|---|---|---|
| plain, as built | rows 8-39 | 1013 zeros, 0x3f800000 | rows 32-63, 448/256 sentinel | sentinel |
| plain, --sy 4 | rows 12-43 | 768 zeros, then rows 0 on | rows 36-67 | sentinel |
| plain, 64x16 | rows 8-23 | 1013 zeros, as at 64x32 | sentinel | job faults |
| every-value | the baseline | 1024 changed | 224/296 sentinel | sentinel |

Bit 14 completes the 32-row jobs (the target left at its sentinel) and faults the 16-row ones.

The --sy 4 case of bit 12 shows rows 0 onwards of the pattern after 768 zeros: reading starts
3072 bytes before the source's first row, which is 1024 bytes into the buffer (4 rows), so it
starts 4096 bytes before the shifted source. The every-value source repeats every 1024 bytes,
so half of the bit-12 image, read from the source's own first half, matches.

Bit 13 as built reads the rows from 32 on, which lie past the 32-row source; that the sentinel
count varies between the rounds (448 against 256, 224 against 296) fits a read of the
destination while the copy is writing it, the count depending on how far the writes have gone
**[infer]**.

**What it shows.** T2 is an address throughout, bits 12 and 14 included; their odd images come
from the buffers around the source. The source's address has bit 12 set, so the flip goes back
4 KiB into a page holding other words (0x3f800000, the background depth 1.0, among them)
**[infer]**; bit 14, and at 64x16 bit 13, land in the destination, whose sentinel the copy reads
and writes back, so nothing is seen written; at 64x16 bit 14 lands past every buffer and
faults **[infer]**. Where the buffers lie is the library's allocation, not shown by the run.
