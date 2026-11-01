+++
id = "E079"
claim = "With 0x0a9c bits 1:0 at 0, 1 or 2 the fixed sets 2 to 5 are interpolation filters: bank 0 gives the H.264 six-tap half-sample luma filter [1 -5 20 20 -5 1]/32 (set 2), [1 2 1]/4 (set 3), the MPEG-4 Part 2 eight-tap [-1 3 -6 20 20 -6 3 -1]/32 (set 4) and the six taps unscaled (set 5); bank 1 gives the VC-1 half-sample [-1 9 9 -1]/16 (sets 2, 3) and two roundings of about its quarter-sample [-4 53 18 -3]/64 (sets 4, 5); bank 2 gives [1 2 2 2 1]/8 (set 4) and [1 1 1 1]/4 (set 5); taps that fall off the line fold by edge repeat, mirror about the edge sample or mirror with the edge sample doubled"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/filter-banks.toml (and the impulse cases of probes/usse/filter-control.toml), fills whose pixel program runs one firh (u8, fcs2 to fcs5, edge mode rep, msc or mdc, centre #0, #2 or #4) on a pedestal of 0x80 in all twelve input bytes and on the pedestal with one byte raised by 0x20, 0x0a9c at 0, 1 or 2, one run; the change of the result is 0x20 times the byte's tap"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-filter-banks", "usse-filter-control"]
terms = ["CR_USE_COEFFS_MODE.MODE"]
+++

**What runs.** 110 probes of 13 cases (1430 cases): bank 0, 1 and 2 (0x0a9c at 0, 1, 2), sets 2 to
5, edge modes `rep`, `msc` and `mdc`, centred at byte 0, 2 and 4, plus two probes of bank 2 on a
pedestal of 0x20 (sets 2 and 3). The first case of each probe is the pedestal; the other twelve
raise input byte 0 to 11 by 0x20. The written byte is byte 0; the rest of the word is the latch,
0xffffff in every case.

**Results.** Centred at byte 4 with `rep` (no tap off the line), the change of the result for a byte
at positions -4 to +7 from the centre (the tap, times 0x20 over the divisor):

| bank / set | pedestal result | change by position | equals |
|---|---|---|---|
| 0 / 2 | 128 | 1 -5 20 20 -5 1 at -2..+3 | [1 -5 20 20 -5 1]/32 |
| 0 / 3 | 128 | 8 16 8 at -1..+1 | [1 2 1]/4 |
| 0 / 4 | 128 | -1 3 -6 20 20 -6 3 -1 at -3..+4 | [-1 3 -6 20 20 -6 3 -1]/32 |
| 0 / 5 | 255 | saturated, no change seen | the six taps unscaled (below) |
| 1 / 2, 1 / 3 | 128 | -2 18 18 -2 at -1..+2 | [-1 9 9 -1]/16 |
| 1 / 4 | 128 | -2 27 9 -1 at -1..+2 | about [-4 53 18 -3]/64 |
| 1 / 5 | 128 | -2 26 9 -2 at -1..+2 | about [-4 53 18 -3]/64, another rounding |
| 2 / 4 | 128 | 4 8 8 8 4 at -2..+2 | [1 2 2 2 1]/8 |
| 2 / 5 | 128 | 8 8 8 8 at -2..+1 | [1 1 1 1]/4 |
| 2 / 2, 2 / 3 | 0 | see E080 | |

Bank 0 set 5 on impulses of 0x40 at centre 0 (filter-control, sets 0 to 2 loaded as identity
filters) gives 255, 255, 0 and 64 for bytes 0 to 3, which is the six taps 20, 20, -5, 1 with the two
outer folded and no division. The same impulses give 32, 40, 0, 2 for bank 0 set 2 and 32, 40, 0, 6
for set 4, and 48, 16, 0, 0 for set 3; with bank 1 sets 2 and 3 32, 36, 0, 0 and sets 4 and 5 49,
18, 0, 0; with bank 2 set 2 and 3 0, 32 on bytes 0 and 1, set 4 40, 16, 8 and set 5 48, 16.

Centred at byte 0, the taps that fall off the line fold by the edge mode. For bank 0 set 2 (change
by bytes 0 to 3): `rep` 16 20 -5 1, `msc` 20 15 -4 1, `mdc` 15 21 -5 1. For bank 0 set 4: `rep` 16
20 -6 3 -1, `msc` 20 14 -3 2 -1, `mdc` 14 23 -7 3 -1. For bank 1 set 2: `rep` 16 18 -2, `msc` 18 16
-2, `mdc` 16 18 -2. Centred at byte 2 the six-tap set 2 has no tap off the line and the three modes
agree; set 4 has one (the tap -1 at -3): byte 0 changes by 2 and byte 1 by -6 under `rep` and `mdc`,
by 3 and -7 under `msc`. So `rep` replicates the edge byte (the codecs' picture padding), `msc`
mirrors about the edge sample (-1 onto +1, -2 onto +2) and `mdc` mirrors with the edge sample
doubled (-1 onto 0, -2 onto +1); `mdc` and `msc` differ from `rep` by a few counts in the folded
sums.

**Reading [infer].** The taps equal the public codec interpolation filters (H.264
clause 8.4.2.2.1, MPEG-4 Part 2 clause 7.6.2.1, VC-1's bicubic filters). The hardware data show the
taps, not the standard they serve.

**Not shown.** One run. 0x0a9c bit patterns above bits 1:0 behave as 0 (E078). The data do not
say why bank 1 has two roundings of one filter, or what bank 2's sets 2 and 3 are (E080). Only `u8`
was used.
