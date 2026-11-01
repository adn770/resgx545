+++
id = "E030"
claim = "The end-of-tile emit's sideband with bit 9 clear hangs the triangle job, in all four sizes tried and in both runs; with bit 9 set, bits 8:6 at each of 1 to 7 change no pixel of the ARGB8888 image and none of the RGB565 image; pack mode 3 stores RGB565; bit 13 stores the same colours at 1182 other places"
unit = "pbe"
method = "probes/pbe/sideband.toml on the laptop, linux fork with the debug option on: the 64x64 triangle (32x16, 32x32 and 64x16 for bit 9 clear) with the default end-of-tile program replaced, its sideband set per probe, the shader writing one colour to o0 over the background 0xff203040; two runs of the table, the second is the follow-up run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["pbe-sideband", "pbe-sideband-followup"]
terms = ["SIDEBAND.BIT9", "SIDEBAND.BITS8_6", "SIDEBAND.PACKMODE", "SIDEBAND.MEMLAYOUT"]
+++

**What runs.** The triangle job (E023) runs with the end-of-tile program replaced by one that
emits the tile with a sideband word chosen by the probe; the shader writes 0x00ff8040 (or
0x80ff8040 in the pack-mode-3 controls) to o0. The target is 0xdeadbeef before the job. The
sideband 0x200 (bit 9 set, pack mode 0) is the control; the tool reads the 64x64 image back and
counts the dwords of each value.

**Results.**

- Sideband 0x200: the image holds the background 0xff203040 in 3034 dwords and the triangle
  colour 0x00ff8040 in 1062, ARGB8888, as 0x240 to 0x3c0 and 0x2200 below.
- Sideband 0x0 (bit 9 clear): the job hangs and the context is lost, at 64x64, 64x16, 32x32
  and 32x16 alike. Both runs of the table agree.
- Bits 8:6 at 1 to 7 (sideband 0x240, 0x280, 0x2c0, 0x300, 0x340, 0x380, 0x3c0): each image is
  identical to the 0x200 image, pixel for pixel (0 of 4096 dwords differ), in both runs.
- Pack mode 3 (0x203): the image holds RGB565, 0xfc08 for the triangle and 0x2188 for the
  background, two pixels to a dword (0x2188 pairs in 1496 dwords, 0xfc08 pairs in 510, mixed
  pairs in 24 and 18 other), and half of the target keeps the sentinel (2048 dwords). With bits
  8:6 at 1 to 7 (0x243 to 0x3c3, shader colour 0x80ff8040) all seven images are identical to
  the 0x203 image, both runs.
- Bit 13 (0x2200): the same multiset of colours as 0x200 (3034 and 1062 dwords) at different
  places: 1182 of 4096 dwords differ from the 0x200 image, identically in both runs. The
  layout is a rearrangement of the pixels; calling it twiddled is an inference **[infer]**,
  a Morton order of the pixel index reproduces 3052 of 4096 places only, so the rule is not
  settled.

Two-emit probes (the same tile emitted twice with two sidebands): with 0x200 first
the image is ARGB8888 for a second sideband of 0x0, 0x3 or 0x200; with 0x203 first it is
RGB565 for a second sideband of 0x0, 0x3, 0x200 or 0x203; with 0x0 first the job hangs. Bit 9
clear in the last emit alone does not hang; the data does not say which of the two sidebands
the pixel back end uses.

**Not shown.** What bits 8:6 do at all: they change no pixel of these two modes with this job.
Bits 12:10 and 14 to 31 are not swept. The layout of bit 13 as a formula.
