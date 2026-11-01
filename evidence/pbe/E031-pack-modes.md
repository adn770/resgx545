+++
id = "E031"
claim = "Of the 64 pack modes of the end-of-tile sideband, 41 store the shader's colour as ARGB8888 (mode 0 and 40 others), mode 1 as ABGR8888, mode 2 as BGRA8888 and mode 3 as RGB565; modes 4, 5, 6, 7, 8, 15, 18, 20, 24, 25, 27 and 28 store subsets in 16 or 8 bits, modes 9, 10, 12 and 13 store whole 32-bit colours into part of the target, mode 14 faults, and modes 22, 26 and 34 store other values; all but 22 and 34 repeat in two runs, and mode 14 faults in both"
unit = "pbe"
method = "probes/pbe/pack-modes.toml (packmode-00 to packmode-63) on the laptop, linux fork with the debug option on: the 64x64 triangle with the end-of-tile sideband set to 0x200 plus the mode, the shader writing 0x80ff8040 to o0 over the background 0xff203040, the target 0xdeadbeef before the job; two runs, the second is the follow-up run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["pbe-pack-modes", "pbe-sideband", "pbe-pack-modes-followup"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE"]
+++

**What runs.** One triangle job per pack mode, 0 to 63; E030 has the sideband's other bits. The
tool reads back the 64x64 target (4096 dwords) and counts the dwords of each value. The
triangle covers 1062 pixels. Written as ARGB8888 the target holds 3034 dwords of background and
1062 of the triangle colour.

**Results.** Stored values, triangle colour first and background second:

| modes | triangle | background | format, and the dwords left at the sentinel |
|---|---|---|---|
| 0, 11, 16, 17, 19, 21, 23, 29 to 33, 35 to 63 | 0x80ff8040 | 0xff203040 | ARGB8888, none left |
| 1 | 0x804080ff | 0xff403020 | ABGR8888, none |
| 2 | 0x4080ff80 | 0x403020ff | BGRA8888, none |
| 3 | 0xfc08 | 0x2188 | RGB565 (16 bits), 2048 |
| 4 | 0xfe08 | 0x90c8 | ARGB1555 (alpha 0x80 stores 1), 2048 |
| 5 | 0x8f84 | 0xf234 | ARGB4444, 2048 |
| 6 | 0x80f1 | 0xff25 | A8 with RGB332, 2048 |
| 7 | 0x80ff | 0xff20 | A8 with R8, 2048 |
| 8 | 0x80 | 0xff | one byte: A8, 3072 |
| 15, 18, 20, 27, 28 | 0x8040 | 0x3040 | the low 16 bits of the colour, 2048 |
| 24, 25 | 0x40 | 0x40 | one byte, B8, 3072 |

The sixteen-bit modes show as pairs: mode 3, for instance, holds 0x21882188 in 1496 dwords,
0xfc08fc08 in 510 and mixed pairs in the rest. The names of the formats are read from the
values; the data shows only the bit patterns.

- Modes 9 and 10 store the whole 32-bit colours (0xff203040 and 0x80ff8040) with 3072 and 2048
  dwords of the target left at the sentinel: a quarter and a half of the target written.
- Modes 12 and 13 do the same with 2048 and 3072 dwords left at the sentinel, and write past
  the target: 1536 dwords at an 8-byte stride (offsets 0 to 0x2ff8) for mode 12 and 2816 at a
  16-byte stride (0 to 0xaff0) for mode 13 land in the 64 KiB scratch buffer beyond the
  target's guard page, holding the same two colours. The pixels of these modes are probably
  8 and 16 bytes wide **[infer]**.
- Mode 14 faults the job and the context is lost, in both runs; its scratch shows 1716 dwords
  (1718 in the follow-up run) written, mostly at a 32-byte stride, before the fault. The scratch
  dwords of modes 12 and 13 are identical in the two runs.
- Modes 22, 26 and 34 are in E032.

Run to run: the images of modes 0 to 13, 15 to 21, 23 to 33 and 35 to 63 are identical in
the two runs, dword for dword; mode 14 faults in both. Modes 22 and 34 differ between the
runs in 531 and 602 dwords (E032).

**Not shown.** Why the modes between 35 and 63 and the unlisted ones repeat mode 0: the
data shows they store as ARGB8888 with this shader, not that they are the same mode. Other
colours, alpha values, and the interplay with the 0x0400 inversion (E029) were not run.
