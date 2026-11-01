+++
id = "E266"
claim = "EMIT2 bits 15:8 count what the end-of-tile emit stores of a 32x16 tile in units of four pixels: at 0 the job writes no pixel, at each odd value it hangs, at an even value v up to 0x80 (the value the library writes) it writes 4v pixels of every tile and leaves the rest unwritten, and above 0x80 it writes the whole tile with 40 to 2524 of 4096 pixels changed, other words and 0x00000000 among them"
unit = "pbe"
method = "the probes pbe-emit-words-bits15-8 (all 256 values) and pbe-emit-words-followup-bits15-8 (twelve of them) of probes/pbe/emit-words.toml and emit-words-followup.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with eot_words.s in the end-of-tile slot, whose four extra instructions (r2 = r2 & AND | OR through r4 and r5) set bits 15:8 of r2 (EMIT2) before the emits, pix_colour.s writing 0x00ff8040 over the background 0xff203040; every pixel read back"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["pbe-emit-words", "pbe-emit-words-followup"]
terms = ["EMIT2.BITS15_8", "SIDEBAND.BIT9"]
+++

**What runs.** The end-of-tile program `eot_words.s` is the library's (use_eot.s): four movs the
host patches with the PBE words of the 64x64 target into r0-r3, then the two emits. Between them
it computes `r2 = r2 & 0xffff00ff | v << 8`, so EMIT2 bits 15:8 take the value v and every other
bit stays as built (EMIT2 0x001f8000 at 64x64). The plain image, with the field at 0x80, holds
3034 pixels of the background and 1062 of the triangle colour. The target is 0xdeadbeef before
each job. The target has eight 32x16 tiles.

**Results** of the first run, all 256 values:

- 0: the job completes and writes no pixel (`no pixel written`).
- Every odd value, 1 to 0xff (128 values): the job hangs and the context is lost.
- Every even value v from 2 to 0x7e: the job completes, every pixel written holds the plain
  image's value, and each of the eight tiles holds exactly 4v written pixels (64 in all at v =
  2, 128 at 4, 2048 at 0x40, 4032 at 0x7e); the rest keep the sentinel.
- 0x80: the plain image.
- Every even value from 0x82 to 0xfe: every pixel is written, and 40 (0x82) to 2524 (0xfe) of
  4096 differ from the plain image, mostly more as the value grows (not always: 0xb8, 0xbc, 0xc2
  and 0xd4 change fewer than the value before); the changed pixels hold the two colours in other
  places, other words (0xffff00ff and 0x00008200 at 0x82, for instance) and 0x00000000 (none at
  0x82, 8 at 0x84, 291 at 0xfe).

Where the 4v pixels lie in a tile (x, y within the 32x16 tile): at v = 2 columns 2, 3, 18 and 19
of rows 0 and 8; at v = 4 columns 0-3 and 16-19 of rows 0 and 8; at v = 8 columns 0-7 and 16-23;
at v = 16 rows 0 and 8 whole; at v = 32 rows 0, 1, 8 and 9; at v = 64 rows 0-3 and 8-11. So the
tile is stored as two halves of eight rows written side by side, and the count fills them from
their first row **[infer]**.

The follow-up run repeated 0, 1, 2, 4, 0x10, 0x40, 0x7e, 0x80, 0x81, 0x82, 0xc0 and 0xfe: the same
outcome for each up to 0x80 (no pixel at 0, the hangs at 1 and 0x81, identical images), while
the images above 0x80 differ from the first run's in 1 (0x82), 253 (0xc0) and 1224 (0xfe) of
4096 pixels. The first run's hangs (128 here, 7 in E267's probe) are known from the runner's
records of each case ("job hung, context lost"); its kernel log wrapped and was not kept (the
dataset's manifest says so), so the recoveries are seen only in the follow-up's kernel log.

**What it shows.** The field is a count, in units of four pixels, of what one emit stores of its
tile: 0x80 is the 512 pixels of a 32x16 tile, a value below it stores part of the tile, and a
value above it stores more units than the tile has, which then land over its pixels with values
not of the tile, values that change from run to run **[infer]**. Bit 8 set hangs the job
whatever the other bits, which fits a count of pairs of units or a unit that must be whole
**[infer]**. With bit 9 of the sideband (E239) the
emit completes the tile; nothing here shows what the PBE does with a count that leaves the tile
part-stored, beyond the unwritten pixels.
