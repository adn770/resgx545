+++
id = "E366"
claim = "A mov to destination bank 6 with neither index bit set (numbers 0, 4, 8, 16, 64 and 124, printed i.) changes no temporary r0-r25, internal register i0-i2, index register or pixel o0 a fill reads back (one run of each number), and no primary attribute pa0-pa15 or secondary attribute sa0-sa31 (read for numbers 0, 4 and 64 only, three runs each); the marker appears in none of the stored o0-o7; numbers 1, 2 and 3 write i.l, i.h (from the low half) and both; no other number whose low two bits are 0 was run"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/destination-bank6.toml (bank6_dump.s: r0-r25 and i0-i2 preset, i.l and i.h 0, then r1 = 0x00030002 and the mov as a raw word, then every register read back, the index registers as r[il + #0] and r[ih + #0]; attr_dump.s for o0-o7) and destination-bank6-moved.toml (copy_dump.s: pa0-pa15, sa0-sa31, o1-o7 and i0-i2 moved to temporaries and stored); each case against a control with the same marker and no bank 6 write; one run of each of numbers 0, 4, 8, 16, 64, 124, 1, 2 and 3 in the three destination-bank6 probes (temps, attributes, outputs), and three runs of numbers 0, 4 and 64 in the moved probes (the only readings of pa and sa that count, see Results)"
tiers = ["HW"]
date = "2026-11-03"
data = ["usse-destination-bank6", "usse-destination-bank6-moved"]
terms = []
+++

**What runs.** `mov.skipinv` with destination bank 6 and number n, source r1 holding the marker
0x00030002, as a raw word (the decoder prints every number whose low two bits are 0 as `i.`).
The marker's halves, 2 and 3, would make `r[il + #0]` and `r[ih + #0]` read r2 and r3 if it
reached an index register.

**Results.**

| number (runs) | r0-r25, i0-i2 | i.l, i.h | pa0-pa15, sa0-sa31 | pixel o0 |
|---|---|---|---|---|
| 0, 4, 64 (1 + 3) | as the control | 0, 0 | as the control | as the control |
| 8, 16, 124 (1) | as the control | 0, 0 | not read | as the control |
| 1 (`i.l`) (1) | as the control | 2, 0 | not read | as the control |
| 2 (`i.h`) (1) | as the control | 0, 2 | not read | as the control |
| 3 (`i.lh`) (1) | as the control | 2, 3 | not read | as the control |

The marker appears in no register read back for numbers 0 to 124, and in none of the stored o0-o7
dwords of the outputs probe (ten cases). Only the pixel o0 is the same in all ten cases (1432
pixels of 0xff203040 and 616 of 0xff00ff00); the o0-o7 dwords the instances stored, and the o1-o7
read through moves, are not: of the 12 moved-high cases (a control and numbers 0, 4, 64, three
runs), three (run 1 number 4, run 2 number 4, run 3 number 0) read other values in o1, o2, o3 and
o5 (and o6, o7 in two; for example 0x1554d4ab, 0x01222038 and 0x585c50de in o2), the other nine
read the fill 0x3e003000 (the run 1 control also reads 0xff203040 in o4). The marker is not among
them and the three cases are not one number, so the values are what earlier jobs left in the
output registers (E373), not this write; there is no repeated control to say how often a control
would differ. Every job completed.

The attributes probe (attr_dump.s, `stad` from pa0-pa15 and sa0-sa15) stored r1, the marker, in all
32 dwords of all ten cases, the control included, so it reads nothing; pa and sa were read
through moves (copy_dump.s) only for numbers 0, 4 and 64 (a store whose data is pa or sa is Q097).

**Not shown.** Registers no form of ours reads (the global bank's write path, the MOE state);
numbers other than these six; pa and sa for numbers other than 0, 4 and 64. [infer] The
simulator takes the write as a no-op for these six numbers only and stops on any other number
whose low two bits are 0.
