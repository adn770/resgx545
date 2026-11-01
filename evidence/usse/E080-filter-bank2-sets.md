+++
id = "E080"
claim = "Fixed bank 2's sets 2 and 3 give 0 on a pedestal of 0x80 and of 0x20 and, with one byte raised by 0x20, set 2 shows 4 at -1 and 16 at +1 (taps 1/8 and 4/8) and set 3 shows 32 at -2 and 16 at the centre and at +1 (taps 1, 1/2, 1/2); the results clamp at 0, so negative taps are not seen, and the table has no lifted case, so [1 -4 4 -1]/8 for set 2 is consistent but not measured"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/filter-banks.toml, bank 2 (0x0a9c = 2) sets 2 and 3 with edge repeat centred at byte 4, on a pedestal of 0x80 and on one of 0x20 (the -low probes), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-filter-banks"]
terms = ["CR_USE_COEFFS_MODE.MODE"]
+++

**What runs.** The bank probes of E079 for bank 2 sets 2 and 3: the pedestal case and twelve
cases that raise one input byte by 0x20, with the filter centred at byte 4, on pedestals of
0x80 and 0x20.

**Results.** The pedestal gives 0 for both sets on both pedestals, so the taps sum to zero or
below. Raising a byte by 0x20 (written byte 0):

- Set 2: 4 for the byte at -1, 16 for the byte at +1, 0 for every other byte, on both
  pedestals.
- Set 3: 32 for the byte at -2, 16 for the byte at 0 and 16 for the byte at +1, 0 for every
  other byte, on both pedestals.

These are 0x20 times a tap of 1/8 and 4/8 (set 2), and of 1, 1/2 and 1/2 (set 3). A byte
with a negative tap cannot be seen because the pedestal's result is already 0 and a
negative step clamps there. A zero-sum difference filter [1 -4 4 -1]/8 at -1..+2 (set 2)
fits what is seen (+4 at -1, +4 times 4 at +1, the negative taps at 0 and +2 hidden by the
clamp); the data do not measure the -4 and -1.

The edge modes at centre 0 move these steps: set 2 gives 16 (byte 1) under `rep` and `mdc` and 20
under `msc`; set 3 gives 16 (byte 1) under `rep`, 48 under `mdc` and 16 and 32 (bytes 0 and 2)
under `msc`. At centre 2 `rep`, `msc` and `mdc` agree (set 2: 4 at byte 1, 16 at byte 3; set 3:
32, 16, 16 at bytes 0, 2, 3).

**Not shown.** The negative taps of both sets (this table has no case that lifts the
result above 0 first) and set 3's tap at -1. One run.
