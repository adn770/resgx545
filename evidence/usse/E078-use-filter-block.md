+++
id = "E078"
claim = "The USE filter block computes sat_u8((sum(tap * input) + bias) >> shift) on the byte it writes: eight signed taps at -3 to +4 from the centre in the first two words of a set's group (highest byte first), shift in bits 3:0 and a signed 16-bit bias in bits 19:4 of the third word; set 2 reads only three of its eight taps; sets 3 to 7 give 0 when the block is loaded; 0x0a9c bits 1:0 choose the fixed banks and 3 selects the loaded block"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/filter-taps.toml, filter-gain.toml, filter-control.toml and filter-sets.toml, fills whose pixel program runs one firh (u8, edge repeat) on preset input bytes, the transfer command's ten coefficient words and 0x0a9c poked per case, one run of each table; the model checked against every case"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-filter-taps", "usse-filter-gain", "usse-filter-control", "usse-filter-sets"]
terms = ["CR_USE_COEFFS0_A", "CR_USE_COEFFS0_B", "CR_USE_COEFFS0_BIAS", "CR_USE_COEFFS1_A", "CR_USE_COEFFS1_B", "CR_USE_COEFFS1_BIAS", "CR_USE_COEFFS2_A", "CR_USE_COEFFS2_B", "CR_USE_COEFFS2_BIAS", "CR_USE_COEFFS_MODE", "CR_USE_COEFFS_MODE.MODE", "transfer_cmd.load_use_coeffs", "video processor"]
+++

**What runs.** Each case is a fill whose pixel program runs `firh r10, r1, r2, r3, u8, rep, fcsN,
#s, #0` on twelve input bytes (r1 to r3, byte 0 first) and dumps r10. The transfer command's flag
word makes the firmware load the filter block (`xfer:17` bit 2 toggled) and its words `xfer:33` to
`xfer:41` hold three groups of three words, one group each for sets 0, 1 and 2; `xfer:32` is the
value of 0x0a9c. The cases put one byte of one word at a time (0x01, 0x02, 0x04, 0x40, 0x80, 0xff
and a scan of single bits) on an input of 0x40 or similar bytes, or load NV12-style words, or a ramp
of distinct bytes 1 to 36. The instruction writes byte 0 of r10 in these tables; the other three
bytes are a latch kept per instance slot (they read 0xffffff in all 8736 cases of these four tables
and are not used).

**Results.** One model fits every case that has one:

- The twelve bytes are a line; position `s + p` is read for the tap at p, an index off the line
  reads the nearest end byte (edge repeat).
- The group's first word holds the taps at p = -3, -2, -1, 0 in its bytes 3, 2, 1, 0, the second
  word p = +1, +2, +3, +4 in its bytes 3, 2, 1, 0; each is a signed byte.
- The third word's bits 3:0 are a right shift, its bits 19:4 a signed 16-bit bias added to the sum
  before the shift (arithmetic); the result is saturated to 0 to 255.
- Set 2 reads only three taps: p = -3 (first word byte 3), 0 (first word byte 0) and +3 (second word
  byte 1); its other five bytes change nothing.
- With the block loaded and 0x0a9c bits 1:0 = 3, sets 3 to 7 give 0 for every input and every word.

Counted: filter-taps 3744 cases with a model (sets 0 to 2) and 1404 for sets 3 to 5, all 0;
filter-gain 2244 of 2244; filter-sets 414 modelled (loaded sets 0 to 2: 102 from the NV12 and ramp
blocks, 312 centred at byte 4) and the 170 loaded cases of sets 3 to 7 all 0; filter-control 39
loaded cases of sets 0 to 2, modelled (its other 39 loaded cases, sets 3 to 5, all give 0 like the
sets 3 to 7 above). No modelled case differs from the model: 6441 of 6441. The bias is 16 bits:
reading a 20-bit signed field misfits 26 filter-taps cases and reading 17 to 19 bits misfits
filter-sets cases. A tap byte t gives t times the input byte at shift 0 (1 and 2 on 0x40 give 64 and
128; 0x80 and 0xff are negative and give 0). The NV12-style words (shifts 6, 7 and 5; bias fields
0xc845, 0x43ca and 0xdd65) give 0 for sets 0 and 2 on a zero input and 135 (0x87) for set 1, as the
model says.

0x0a9c (filter-control, 48 probes: bits 0x1, 0x2, 0x4, 0x8, 0x10, 0x100 and ~0 with sets 0 to 2
loaded as identity filters): only bits 1:0 count (0x4, 0x8, 0x10, 0x100 behave as 0). At 0 to 2,
sets 0 and 1 give the loaded filter and sets 2 to 5 fixed banks (E079); at 3 and at ~0 set 2 is the
loaded third group and sets 3 to 5 give 0. With no load (filter-sets `load0`) sets 0, 1, 6 and 7
give 0 and sets 2 to 5 give bank 0's fixed filters.

**Not shown.** One run of each table. Only `u8` and edge repeat were run here, and only byte 0 was
written. Whether the load lasts one job is not tested (every case loads or does not load in its own
job).
