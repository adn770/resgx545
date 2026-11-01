+++
id = "E268"
claim = "Bit 25 of the word that loads CR_REG_0400 inverts the stored alpha channel wherever the pack mode puts it: bits 31:24 in ARGB8888 (mode 0) and ABGR8888 (mode 1), bits 7:0 in BGRA8888 (mode 2), and nothing in RGB565 (mode 3), which stores no alpha; bits 11:0 of the word (each flipped from 0x80), the word at 0 and the other bits change no pixel in any of the four modes"
unit = "pbe"
method = "probes/pbe/reg-0400-modes.toml (pbe-reg-0400-modes-0 to -3) on the laptop, linux fork with the debug option on, and its follow-up run: the 64x64 triangle with the end-of-tile program eot_plain.s and the sideband 0x200 plus the pack mode, the shader writing 0x80ff8040 over the background 0xff203040, the render command's word 11 (the word that loads 0x0400, 0x80 as the library builds it) at 16 values per mode; every pixel read back"
tiers = ["HW"]
date = "2026-11-02"
data = ["pbe-reg-0400-modes", "pbe-reg-0400-modes-followup"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "CR_REG_0400.BITS11_0", "hw_render_details.reg_0400", "SIDEBAND.PACKMODE"]
+++

**What runs.** E029 found that bit 25 of the word inverts bits 31:24 of every stored pixel in
ARGB8888, where they are the alpha. Here the same triangle is stored in pack modes 0 to 3
(E031: ARGB8888, ABGR8888, BGRA8888, RGB565), and the render command's word 11 is 0x80 (case 0),
0x80 with bit 25 flipped, with each of bits 0 to 11 flipped, 0 and 0xffffffff. The register takes
bit 25 and bits 11:0 (E251).

**Results.** In each mode the baseline is E031's image. Pixels that differ from it:

| mode | bit 25 flipped and 0xffffffff | stored values, baseline to case |
|---|---|---|
| 0, ARGB8888 | 4096 | 0xff203040 to 0x00203040, 0x80ff8040 to 0x7fff8040 |
| 1, ABGR8888 | 4096 | 0xff403020 to 0x00403020, 0x804080ff to 0x7f4080ff |
| 2, BGRA8888 | 4096 | 0x403020ff to 0x40302000, 0x4080ff80 to 0x4080ff7f |
| 3, RGB565 | 0 | the RGB565 image, unchanged |

Each of bits 0 to 11 flipped and the word at 0: 0 pixels differ, in all four modes. Each table
of the follow-up run gave the same images.

**What it shows.** The bit inverts the alpha channel, not a fixed byte of the stored word: in
BGRA8888 the inverted byte is bits 7:0, where that mode stores the alpha, and RGB565, with no
alpha, is unchanged. Bits 11:0 do nothing with these jobs, the low byte included, which the
library sets to 0x80 with alpha 0x80 in the shader colour.
