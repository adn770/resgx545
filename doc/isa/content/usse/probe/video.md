<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Video `adif`, `adifsum`, `bilin`, `firv`, `firh`

*Measured on the hardware (2026-10-22).* **`adif d, a, b` = `|a − b|` per byte; `adifsum d,
s0.low|high, a, b` = the sum of the four byte differences plus that 16-bit half of `s0`**, as a
32-bit value; a repeat advances the destination and the sources **[HW]** (probe
`usse-video-ops-adif`).

*Filter probes (2026-10-25).* The three filters, from impulse responses, pedestals and amplitude
sweeps (table `probes/usse/video-filters.toml`, probes `x-*`, every result recorded).
Every formula below fits every recorded case unless it says otherwise. Bytes are numbered
from the least significant; `x.bN` is byte N of `x`.

**Data formats.** `u8`, `s8` and `o8` only change how the data bytes are read: as they are,
as signed bytes, or as the byte minus 0x80. **Every result byte is unsigned, saturated to
0-255** **[HW]**, whatever the format, so a negative result reads 0.

**`bilin d, w, a, b, fmt, planar|interleaved, srcPQ, dstPQ[, rnd]` is a bilinear filter**
**[HW]** (636 cases). With `fx` = (`w.bP` & 7)/8 and `fy` = (`w.bQ` & 7)/8, the weights in
eighths (`src01` takes them from bytes 0-1 of `w`, `src23` from bytes 2-3; the bits above
the low three are ignored):

- `v_k` = `a.bk` + `fy` · (`b.bk` − `a.bk`), each byte of `a` towards the same byte of `b`;
- result byte `j` (0, 1) = `v_j` + `fx` · (`v_n` − `v_j`), `n` = `j` + 1 (`planar`) or
  `j` + 2 (`interleaved`);
- truncated, or rounded half up with `rnd`; written to bytes 0-1 (`dst01`) or 2-3 (`dst23`)
  of `d`, the other two bytes zero.

**`firv d, a, b, c, fmt[, +src2.2][, latch][, scale]` is a two-tap vertical filter, one per
byte column** **[HW]** (750 cases): result byte `k` = `a.bk` · `c.b0` + `b.bk` · `c.b1`, the
two taps signed bytes; `+src2.2` adds `c.b2`, `scale` shifts the sum right by `c.b3`, and
`latch` adds byte `k` of the *firh latch* (below); the order of `latch` and `scale` together
was not measured.

**`firh d, a, b, c, fmt, edge, fcsN, #s, #k` is a horizontal FIR filter along one 12-byte
line** **[HW]** (1711 cases): the line is `a.b0`-`a.b3`, `b.b0`-`b.b3`, `c.b0`-`c.b3`, the
kernel of set `fcsN` is centred on position `s`, and the result, Σ tap · sample plus a
bias, shifted right by 7 and saturated, is written to byte `k`. The sets are fixed at boot
(we know of no way to load them):

| set | taps, centre at `s` | sum | bias |
|-----|---------------------|-----|------|
| `fcs2` | [4 −20 80 80 −20 4] from `s` − 2: [1 −5 20 20 −5 1]/32, H.264 | 128 | 64-79 |
| `fcs3` | [32 64 32] from `s` − 1: [1 2 1]/4 | 128 | 64-95 |
| `fcs4` | [−4 12 −24 80 80 −24 12 −4] from `s` − 3 | 128 | 48-63 |
| `fcs5` | [1 −5 20 20 −5 1] from `s` − 2, not normalised (no shift) | 32 | 0 |
| `fcs0`, `fcs1`, `fcs6`, `fcs7` | all zero | 0 | |

Positions off the line follow `edge`: `rep` repeats the end sample, `msc` mirrors without
repeating it (−1 reads 1), `mdc` mirrors with it (−1 reads 0). **The bias column** is the
range that fits every case; `fcs4`'s is below a half **[HW]**, so it does not simply round.
`s` from −4 to 15 behaves so; **below −4 only `c.b3` ever counts** (all three `fcs3` taps at
−16 and −15, 96/128 at −14, 32/128 at −13, nothing from −12 to −5) and no rule per tap fits
**[open]**; `r4`-`r8` are never read (probes `x-c9-*`, `x-c10-*`).

**The firh latch.** `firh` writes all four bytes of `d`: byte `k` is its result, the other
three come from a hidden 32-bit latch that every `firh` updates at byte `k` **[HW]**. So four
`firh` with `#k` 0-3 build a whole word, each destination getting the bytes merged so far
(0x11, 0x2211, 0x332211, 0x44332211); `firv`'s `latch` reads it; `firv` and `bilin` never write
it. **The latch belongs to an instance slot, not to a pixel** **[HW]**: a fill where every pixel
writes its own number reads back 32 values, those of the last pixels each slot ran, and a slot
carries the latch from one pixel to the next and from one task, and one client, to the next,
as `i0`-`i2` do (*Internal registers*). At power-up it holds garbage: the first run gave every
pixel 0x00 or 0xff bytes until `firh` probes with `#k` 1-3 had written them. With two to five
instructions between `firh`s, a destination can catch a later `firh`'s byte, which fits a latch
shared by instances interleaved on one slot **[infer]** (probe
`usse-video-filters-c11-latch-merge`). A program
that relies on the latch should write all four bytes first.

**Undecided:** `firh` below `#−4`; the exact biases; how the coefficient sets are loaded, and
whether `fcs0`, `fcs1`, `fcs6` and `fcs7` are only empty; the timing of the latch under
interleaving.
