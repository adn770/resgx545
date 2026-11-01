+++
id = "E123"
claim = "Three models, one each for bilin, firv and firh, fit every video-filter case they were fitted to (bilin 636 of 636, firv 1068 of 1068 with a known latch, firh 2411 of 2411 with #s of -4 or more), while the 563 firh cases with #s below -4 are recorded only and the dumped registers repeat in the follow-up run in 4835 of 4836 cases"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/video-filters.toml, 134 probes of fills whose pixel program presets r1 to r8 from the case, runs one video instruction (some tables first run mov or firh instructions) and stores r10 to r17 and r1 to r8; two runs of every probe (the second is the follow-up run); the three models checked against every case, comparing only the bytes the instruction writes"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-video-filters", "usse-video-filters-followup"]
terms = ["video processor"]
+++

**What runs.** The table has 134 probes and 4836 cases: bilin 636 cases in 30 probes, firv 1207 and
firh 2993 (of which 19 are the latch tables, which are not fitted). Each case is a fill whose pixel
program presets r1 to r8 to the case's words A to H (r1 is A) and r10 to r17 to 0xA0A1A2A3 and up in
steps of 0x04040404, runs the instruction under test and stores r10 to r17 and r1 to r8 to scratch.
The instructions are `bilin r10, r3, r1, r2` (first source r3, second r1, third r2), `firv r10, r1,
r2, r3` and `firh r10, r1, r2, r3, fmt, edge, fcsN, #s, #k`, with formats u8, s8 and o8, the flags
`planar` or `interleaved`, `src01` or `src23`, `dst01` or `dst23`, `rnd`, `+src2.2`, `latch` and
`scale`, and the edge modes rep, msc and mdc. `fcs0` to `fcs7` name the eight filter coefficient
sets of firh, `#s` is the line offset of its first tap and `#k` the destination byte, the latch is
the per-instance history that firv adds and firh leaves in its other destination bytes, and the
tables named amp, cross and izero are the groups of firv cases described next. The amp and cross
tables of firv first run four firh (centre 0, bytes 0 to 3) on a constant word so that the latch
holds 0x00 or 0x40 in every byte; the izero tables of the latch cases first write 0 to i0 to i2.
Every probe ran twice: the first run and the follow-up run of the same table. Each model was fitted
to the bytes the instruction writes: for bilin bytes 0 and 1 (`dst01`) or 2 and 3 (`dst23`) of r10,
for firv all four bytes, for firh byte `#k` of its destination. The other bytes of a firh
destination are not results (see the latch below).

**Results.**

*Run to run.* Of the 4836 cases, 4835 give the same words in all sixteen dumped registers in both
runs. The one that differs is firv-all case 11 (see firv): r10 reads 0xff00ff40 in the first run and
0xff00ff00 in the follow-up run. The dumped registers of every bilin and firh case, and of every
other firv case, repeat exactly; the pixels of one firh case do not (c11-latch-pixel case 1 reads
0x26262600, 0x27272700, 0xa4a4a400 and 0xa5a5a500 on 64 pixels each in the first run, and
0xa6a6a600, 0xa7a7a700, 0x24242400 and 0x25252500 in the follow-up run).

*bilin: 636 of 636 in both runs.* With W the first source (r3), P the second (r1) and Q the third
(r2), wx the low three bits of W's byte 0 (src01) or 2 (src23) and wy the low three bits of byte 1
(src01) or 3 (src23), n = 1 for planar and 2 for interleaved, each output byte j (0 or 1) is

    ((8-wy) * ((8-wx) * P[j] + wx * P[j+n]) + wy * ((8-wx) * Q[j] + wx * Q[j+n])) >> 6

and with `rnd` the sum gets 32 added before the shift (round half up). The result goes to byte j
(`dst01`) or byte 2+j (`dst23`); `src01` and `src23` only choose which weight bytes are read, the
data bytes stay bytes 0 and 1 of P and Q. Bits above the low three of a weight byte change nothing
(154 cases have such bits set in a weight byte the instruction reads; 220 have them in some byte of
W, and the statement rests on the 154). u8 uses the bytes as they are, s8 sign-extends them and o8
takes the byte minus 128; the result is clamped to 0 to 255 in all three (a negative blend of s8 or
o8 inputs reads 0, and o8 is not offset back). The 240 rounding cases (three formats, with and
without `rnd`, 40 cases each) fit: without `rnd` the blend is truncated, with `rnd` an exact half
reads the upper integer. The 636 cases do not separate a single truncation at the end from a
truncation after each of the two blends: the two forms give the same bytes on every case.

The part of the model that is more than a single neighbour blend is wy. Forcing it to 0 still fits
602 of the 636 cases, because most cases have wy = 0, and misfits the 34 cases that have wy non-zero
and differing second and third sources. So the first weight blends a byte with its neighbour in the
same source (planar or interleaved, in eighths, truncating unless `rnd`), and the second weight
blends the two results between the second and third sources.

*firv: 1068 of 1068 modelled cases, 105 more at a latch of zero, 33 of 34 at the latch 00 ff 00 ff.*
Output byte j (0 to 3) is the sum of the byte j of source 0 times the signed byte 0 of source 2 and
the byte j of source 1 times the signed byte 1 of source 2 (cross tables: 260 cases, source bytes
and taps each 0 to 3, all fit), plus with `+src2.2` the byte 2 of source 2 as a signed byte, plus
with `latch` the latch byte j, then shifted right (arithmetic) by byte 3 of source 2 with `scale`,
then clamped to 0 to 255, in u8, s8 (sign-extended inputs) and o8 (inputs minus 128) alike. Detail:

- `+src2.2` is signed: byte 2 of 0x80, 0xc0 and 0xff (six cases, in the amp tables) read as unsigned
  misfits those six.
- The shift amount is the whole byte, with no limit (32, 63, 64, 65, 96, 127, 128, 192 and 255 were
  run and read as a shift beyond the width). Taking it modulo 64, 32, 16 or 8 misfits 5, 9, 11 and
  17 cases. `scale` changes the result in 65 cases and in 39 of those the result is not 0; the latch
  is added before the shift (firv-all case 12, shift 0x40, reads 0 where the other 15 cases of the
  table read the latch).
- s8 and o8: 207 and 142 cases fit; 97 and 14 of them give a non-zero result, the rest 0 through the
  clamp.
- `latch` with a known latch (amp tables, latch bytes 0x00 or 0x40 from four preceding firh): 98
  of 98 fit. Without a preceding firh the latch is history: 105 cases (firv-latch-pix, the two izero
  tables, ped-firv-latch and ped-firv-all) fit a latch of zero: 103 read 0 on every byte, one
  (firv-all-izero case 11) reads 0x40404040 through its +src2.2 byte of 0x40 and one (ped-firv-latch
  case 1, taps 0x40 on 0x40 inputs) reads 0xffffffff, clamped; and the 34 cases of firv-latch and
  firv-all read 0xff00ff00 for every input (the taps are 0 there), which fits with the latch bytes
  0, 255, 0, 255 added. That value is read off the result, not set by the case.
- The one firv case that does not fit is firv-all case 11 (`+src2.2` with byte 2 = 0x40, no taps):
  the model gives 0xff40ff40, the first run reads 0xff00ff40 and the follow-up run 0xff00ff00. It is
  the only case of firv-all with a non-zero byte 2 and a zero shift, and its two runs differ; it is
  left unsettled.

*firh: 2411 of 2411 cases with #s of -4 or more, both runs.* The twelve bytes of r1, r2 and r3 (byte
0 first) are one line; the tap at position p reads line byte #s + p, the result is written to byte
#k and clamped to 0 to 255. u8, s8 and o8 read as for firv. Per fixed set (cases with #s of -4 or
more):

| set | cases | taps (position) | divisor | rounding |
|---|---|---|---|---|
| fcs0, 1, 6, 7 | 641, 89, 89, 89 | none | | result 0 |
| fcs2 | 679 | 1 -5 20 20 -5 1 (-2..+3) | 32 | half up (bias 16 to 19) |
| fcs3 | 365 | 1 2 1 (-1..+1) | 4 | half up (bias 2 or 3) |
| fcs4 | 345 | -1 3 -6 20 20 -6 3 -1 (-3..+4) | 32 | exact half down (bias 12 to 15) |
| fcs5 | 114 | the fcs2 taps | 1 | none, clamped at 255 |

The bias is the number added before the shift, the range is what the cases allow; the rounding
tables (256 cases each for fcs2, fcs3 and fcs4, steps of one in the input) have the exact halves,
and fcs4 reads the lower integer on its 38 exact halves (32 of them in its rounding table) where
fcs2 and fcs3 read the upper one. The three edge modes: rep 2269 cases, msc 71 and mdc 71; msc
mirrors about the edge byte (-1 reads +1) and mdc mirrors with the edge byte doubled (-1 reads 0),
both at #s = 0 only and in 54 cases with a non-zero set (fcs2, 27 each); the other 17 and 27 per
mode are fcs0, which reads 0 in any mode. The written byte #k = 0, 1, 2 and 3: 2164, 88, 88 and 71
cases, of which the fcs2 cases are 27 for each of k = 1, 2 and 3 on a pedestal of 0x80; the rest of
the k cases use fcs0.

*#s below -4: recorded only.* 563 cases have #s from -16 to -5: 90 fit the model, 473 do not. Of the
90, 44 are fcs0 cases, which read 0 whatever #s; of the 519 cases that can tell the sets apart, 46
fit (all fcs3, at #s -16 and -15) and none of the 111 fcs2 cases fits. Both runs read the same
bytes. The cases at #s = -16 and -15 fit in 67 of 112 and 23 of 41; at -14 to -5 none of 41 each
fit. For the ramp of bytes 0x10 to 0xc0 in steps of 0x10 (fcs2, rounding table of the negative #s)
the model reads 16 at every #s and the hardware reads 186, 216, 96, 0, 6 and then 0 for #s -16, -15,
-14, -13, -12 and -11 to -5. The result does not change with r4 to r8 (varied in the same table).
The edge folding of taps that fall far off the line is therefore not the model's at these #s.

*The other bytes of a firh destination.* Across the 2974 firh cases that are not the latch tables
(2411 fitted and 563 with #s below -4), the three bytes other than #k are all 0 in 2706, hold 0xff
in 187 and hold 0x3e or 0x80 in 81; they are never the destination's previous contents. The latch
tables show where they come from: four firh with k = 0 to 3 on a word of 0x40 into r11 (r11 reads
0x40404040), then one firh k = 0 on zero into r10, give r10 = 0x40404000, and the same with 0x5a
gives 0x5a5a5a00. So the other bytes are the last results of the firh of the same instance slot, one
per byte position, whatever the destination register was. In the merge table (four firh into r10 to
r13 with k = 0 to 3 and input bytes 0x11, 0x22, 0x33, 0x44) r11 and r12 hold the earlier bytes
(0x2211 in r11, 0x332211 in r12) and, in 1 of 9 cases for r11 and 4 of 9 for r12, also a byte from
the previous pixel's firh (0x44 in byte 3): the latch outlives the pixel. The 9 cases read
identically in both runs.

**Not shown.** The firh sets 0, 1, 6 and 7 give 0 everywhere they were run, but no case of this
table loads a filter block; the loaded block is E078's subject. The mirrored edge modes were run
only at #s = 0 and only with fcs0 (0) and fcs2. The rounding of fcs4 is only bounded: a bias from 12
to 15 of 32 fits every case and the data do not choose within it. The mix of 0x00 and 0xff in the
unwritten bytes depends on what ran before in the slot, and the table does not control that. Why #s
below -4 differs is not shown (the line may reach past the three sources, but varying r4 to r8
changed nothing). The bilin dest bytes that the instruction does not write were not compared.
