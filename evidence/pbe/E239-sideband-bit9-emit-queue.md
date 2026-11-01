+++
id = "E239"
claim = "On a target of one tile (32x16) bit 9 clear still hangs the job, and an end-of-tile program that emits the tile twice stores the first emit's tile and leaves the next job's image wrong at 1977, 2107, 2164 or 2165 of 4096 places according to the second sideband (the probe's colour, or RGB565 words when the second sideband has pack mode 3), in both runs; that the second emit is carried out during the next job, and that bit 9 is therefore not tile-relative addressing, are readings"
unit = "pbe"
method = "the probes pbe-sideband-0000-32x16, pbe-sideband-0200-32x16 and the eight pbe-sideband-two-* probes of probes/pbe/sideband.toml, on the laptop with the linux fork and the debug option on, each probe fenced (the 64x64 baseline triangle compared with its clean image before the probe and again after it), run twice (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["pbe-sideband", "pbe-sideband-followup"]
terms = ["SIDEBAND.BIT9", "SIDEBAND.PACKMODE", "Pixel Back End (PBE)"]
+++

**What runs.** E030 found that an end-of-tile emit with bit 9 clear hangs the triangle job. Here
the target is one tile (32x16, so a tile offset of 0) and the end-of-tile program emits the tile
twice. In `eot_two_0200.s` the first emit has sideband 0x0200 and no `.end` or `.freep`, the
second ends the program with the probe's sideband; `eot_two_0203.s` has 0x0203 first and
`eot_two_0000.s` has 0x0000 first. The shader writes 0x00ff8040 to o0 over the sentinel
0xdeadbeef. The eight probes are the pairs (first, second) 0200/0200, 0200/0000, 0200/0003,
0203/0200, 0203/0000, 0203/0003, 0203/0203 and 0000/0200. After each probe the baseline
triangle, a 64x64 job with the default end-of-tile program, was drawn and compared with its
clean image.

**Results.** Both runs agree on every case.

- One tile, one emit: sideband 0x0 hangs (32x16, and 32x32 and 64x16 as E030 has it); sideband
  0x200 on 32x16 draws the tile, 135 dwords of 0x00ff8040 over 377 of the background 0xff203040.
- Two emits, first with bit 9 set: the job completes. With 0x0200 first the image is the
  ARGB8888 tile of the one-emit case for each of the second sidebands 0x0200, 0x0000 and 0x0003.
  With 0x0203 first the image is RGB565 (0xdeadbeef in 256 dwords, 0x21882188 in 181, 0xfc08fc08
  in 60, 0x2188fc08 in 9, 6 other) for each of the second sidebands 0x0200, 0x0000, 0x0003 and
  0x0203. So the pack mode of the stored tile is the first emit's.
- Two emits, first with bit 9 clear (0x0000 then 0x0200): the job hangs; the baseline drawn after
  it was clean.
- The baseline after a probe that completed was not clean:

| first | second | baseline after: wrong pixels of 4096 | first wrong pixel |
|-------|--------|--------------------------------------|-------------------|
| 0x200 | 0x200 | 1977 | (4, 1) 0x00ff8040 |
| 0x203 | 0x200 | 1977 | (4, 1) 0x00ff8040 |
| 0x200 | 0x000 | 2107 | (0, 0) 0x00ff8040 |
| 0x203 | 0x000 | 2107 | (0, 0) 0x00ff8040 |
| 0x200 | 0x003 | 2165 | (0, 0) 0xfc08fc08 |
| 0x203 | 0x003 | 2165 | (0, 0) 0xfc08fc08 |
| 0x203 | 0x203 | 2164 | (0, 0) 0x21882188 |

The count and the first wrong value depend on the second sideband alone, not on the first. A
second sideband with pack mode 3 leaves RGB565 words in the baseline's image; the others leave
the probe's colour 0x00ff8040. All baselines before a probe were clean (0 of 4096), which is
what the fence checks.

**What it shows.** The probe's second emit is not part of the probe's own image: the first emit
stores the tile, and the second is carried out when the next job's first tile comes **[infer]**,
in its own pack mode, over that job's pixels. A one-tile target hangs with bit 9 clear as
64x64 does, so the hang does not come from a tile offset that bit 9 would fix, and bit 9 is not
tile-relative addressing **[infer]**. Reading
bit 9 as marking an emit the PBE counts against a tile fits the hangs (the only emit of a tile
without it never completes the tile) and the carried-over second emit **[infer]**.

**Not shown.** Whether a later job after the baseline is also wrong, or whether the queue
recovers after one job with bit 9 clear in the second emit: each probe is fenced, and a hung job
is followed by a clean baseline before the next probe. Whether the count of emits per tile is a
queue depth is not shown; no probe reads the PBE's state. Unfenced runs were not made.
