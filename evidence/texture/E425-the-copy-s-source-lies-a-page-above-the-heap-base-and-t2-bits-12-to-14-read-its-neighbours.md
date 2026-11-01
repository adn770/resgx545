+++
id = "E425"
claim = "With the copy's tool printing its addresses and a counting page before the source (0xB0000000 | dword), the source of the 64x32 copy lies at 0x3e002000 (the page before it at 0x3e001000), its destination at 0x3e005000 (0x3e006000 with the source moved 4 rows down, 0x3e004000 at 64x16), and T2 flipped by 0x2000, 0x3000 and 0x4000 reads 0x3e000000 (first dword 0x04000004, then zeros and a few other dwords), the counting page and the destination's second page: 28 of the 30 cases identical pixel for pixel in 3 of 3 runs and the other 2 (64x16, T2 flipped by 0x4000) faulting in 3 of 3"
unit = "texture"
method = "probes/texture/copy-addresses.toml (copy-addresses.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: sgxfive-test copy --print-addrs --page-before --pixels at 64x32 (plain and every-value source), with the source 4 rows down (--sy 4) and with a 16-row target, each with tex:2 as built and flipped by 0x1000, 0x2000, 0x3000 and 0x4000, three runs: 90 copies, every pixel read back"
tiers = ["HW"]
date = "2026-11-07"
data = ["texture-copy-addresses"]
terms = ["T2.TEXADDR"]
+++

**What ran.** The copy's source buffer now has a page of its own before the source, dword i
holding 0xB0000000 | i (--page-before), and the tool prints where the buffers lie (--print-addrs).
The plain source holds 0xa5000000 | y << 16 | x << 8 | (x ^ y); the destination starts at
0xdeadbeef.

**Where things lie.** At 64x32 the counting page is at 0x3e001000, the source (8 KiB) at
0x3e002000 and the destination (8 KiB) at 0x3e005000; with --sy 4 the source buffer is longer and
the destination at 0x3e006000; with a 16-row target at 0x3e004000. Without the counting page
E273's source was at 0x3e001000, the page below it the first page of the general heap, 0x3e000000.

**Results** (plain source, as built; the other shapes and the every-value source in the data; the
30 cases gave the same 2048 or 1024 pixels in all three runs, except the two that fault):

- T2 bit 12 flipped (source + 0x1000, 0x3e003000): the second half of the source, first pixel
  0xa5100010.
- Bit 13 flipped (source - 0x2000, 0x3e000000): rows 0 to 15 read the page at the heap's base,
  first dword 0x04000004, then 1013 zeros and 10 other dwords, and rows 16 to 31 the counting page
  (1024 counting pixels): E273's 'page before the source' is that page.
- Bits 13 and 12 flipped together (0x3000, source - 0x1000, 0x3e001000): 1024 counting pixels
  (first 0xb0000000), then the source's first 16 rows.
- Bit 14 flipped (source + 0x4000, 0x3e006000 = the destination's second page): 2048 sentinels
  (the destination is copied onto itself); with the 16-row target that address is unmapped and the
  job faults (64x16, 3 of 3).

**What it shows.** E273's odd images are plain address arithmetic on the buffers' placement: T2 is
an address in the bits 12 to 14 flipped here (the other bits were not tried), bit 12 and 13 reach
the neighbouring pages of the source buffer and the heap's first page, bit 14 the destination: the
question of where the copy's buffers lie is answered.
