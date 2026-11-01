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
line** **[HW]** (1711 cases, then every `firh` vector with its job, E292): the line is
`a.b0`-`a.b3`, `b.b0`-`b.b3`, `c.b0`-`c.b3`, the kernel of set `fcsN` is centred on position
`s`, and the result, Σ tap · sample plus a bias, shifted right and saturated, is written to byte
`k`. The sets come from the USE filter block, which the job loads or not (E078): a transfer
command with load flag bit 2 loads `CR_USE_COEFFS_MODE` and three groups of three words, one
per set 0, 1 and 2; a group's first word holds the signed taps at −3..0 (bytes 3..0), its
second +1..+4, its third the shift (bits 3:0) and a signed 16-bit bias (bits 19:4).
`CR_USE_COEFFS_MODE` bits 1:0 pick what sets 2-5 are:

| mode | `fcs0`, `fcs1` | `fcs2` | `fcs3`-`fcs5` | `fcs6`, `fcs7` |
|---|---|---|---|---|
| 0 | the loaded groups 0, 1 | fixed bank 0 | fixed bank 0 | 0 |
| 1, 2 | the loaded groups 0, 1 | fixed bank 1, 2 | fixed bank 1, 2 | not 0, taps open (E298) |
| 3 | the loaded groups 0, 1 | group 2, taps −3, 0 and +3 only | 0 | 0 |

A job that loads nothing runs with mode 0 and every group zero, whatever the job before it
loaded (`usse-filter-sets` load0 cases after loaded ones). The fixed banks, in 128ths, shift 7
(bank 0 E079; banks 1 and 2 E079, E080, E293):

| bank / set | taps from `s` − | taps | bias |
|---|---|---|---|
| 0 / `fcs2` | 2 | [4 −20 80 80 −20 4]: [1 −5 20 20 −5 1]/32, H.264 | 64-79 |
| 0 / `fcs3` | 1 | [32 64 32]: [1 2 1]/4 | 64-95 |
| 0 / `fcs4` | 3 | [−4 12 −24 80 80 −24 12 −4] | 48-63 |
| 0 / `fcs5` | 2 | [1 −5 20 20 −5 1], no shift | 0 |
| 1 / `fcs2`, `fcs3` | 1 | about [−8 72 72 −8]: [−1 9 9 −1]/16 | |
| 1 / `fcs4` | 1 | about [−9 106 36 −5] | |
| 1 / `fcs5` | 1 | about [−6 105 37 −7] | |
| 2 / `fcs2` | 1 | about [16 −64 64 −16]: [1 −4 4 −1]/8 | |
| 2 / `fcs3` | 2 | about [128 −256 64 64]: [1 −2 ½ ½] | |
| 2 / `fcs4` | 2 | about [16 32 32 32 16]: [1 2 2 2 1]/8 | |
| 2 / `fcs5` | 2 | about [32 32 32 32]: [1 1 1 1]/4 | |

The bias column of bank 0 is the range that fits every case; `fcs4`'s is below a half
**[HW]**, so it does not simply round. Banks 1 and 2 are known to a fitted family
**[infer]**: every tap vector within 5 per tap of E079's changes times 4 (E293's taps for bank
2's `fcs2` and `fcs3`), with its own bias range, that fits all their cases (`usse-filter-banks`,
`usse-filter-control`, `usse-filter-bank2`; `tools/usse-asm/firh_banks.py`). The simulator gives
a result only where the whole family agrees, and counts it as fitted, not as a hardware check:
the families come from the same vectors (E292).

Positions off the line follow `edge`: `rep` repeats the end sample, `msc` mirrors without
repeating it (−1 reads 1, 12 reads 10), `mdc` mirrors with it (−1 reads 0, 12 reads 11), up to
position 18; **from position 19 every mode reads 0** **[HW]** (a loaded identity filter on a ramp
line, every centre, E298). **The centre is −4 to 27**: the field's values written `#−16` to
`#−5` are centres 16 to 27 **[HW]**, which gives every case below `#−4`: all three `fcs3` taps at
`#−16` and `#−15` (centres 16, 17), 96/128 at `#−14`, 32/128 at `#−13`, nothing from `#−12`
(probes `x-c9-*`, `x-c10-*`; 1126 vectors). `r4`-`r8` are never read.

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
that relies on the latch should write all four bytes first. The bytes a task did not write
read what the slot's last task left (for example 0xffffff, 0, 0x5a5a5a or 0x80803e in the
runs): the simulator checks the byte `firh` wrote and takes the others as any value, and stops
on a byte the task wrote but it could not compute (E292).

**Undecided:** `fcs6` and `fcs7` under banks 1 and 2; the exact taps of banks 1 and 2 within
their families, and whether the families hold on lines outside the fit; the timing of the latch
under interleaving.
