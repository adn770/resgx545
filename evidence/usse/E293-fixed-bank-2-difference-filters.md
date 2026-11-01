+++
id = "E293"
claim = "With 0x0a9c at 2, firh's fixed sets 2 and 3 are zero-sum difference filters: set 2 is [1 -4 4 -1]/8 at -1 to +2 and set 3 is [1 -2 1/2 1/2] at -2 to +1, seen on a line lifted above 0 so that the negative taps show"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/filter-bank2.toml, fills whose pixel program runs firh r10, r1, r2, r3, u8, rep, fcs2 or fcs3, #4, #0 with the filter block loaded at 0x0a9c = 2 (xfer:17 bit 2, xfer:32 = 2), on a line of 0x40 with the positive tap's byte at 0xc0 (byte 5 for set 2, byte 2 for set 3), then every other byte raised and lowered by 0x20 in turn; 46 cases, one run"
tiers = ["HW"]
date = "2026-11-02"
data = ["usse-filter-bank2"]
terms = ["CR_USE_COEFFS_MODE.MODE"]
+++

**What runs.** E080 saw bank 2's sets 2 and 3 only on flat pedestals, where the result is 0 and a
negative tap cannot lower it. Here the line is 0x40 everywhere but at the byte of a positive tap
E080 found (+1 for set 2, -2 for set 3, centre at byte 4), which is 0xc0, so the result starts
above 0. Each other byte is then raised by 0x20, and in a second pass lowered by 0x20.

**Results.** The written byte (byte 0 of r10; the other three are the latch, 0x5a5a5a in this
run):

| set | lifted line | change for a byte raised by 0x20 (by position from the centre) |
|---|---|---|
| 2 | 0x40 | +4 at -1, -16 at 0, -4 at +2, none elsewhere |
| 3 | 0x80 | -64 at -1, +16 at 0, +16 at +1, none elsewhere |

Lowering a byte by 0x20 gives the opposite change at the same positions, and nothing elsewhere.
With the lift (0x80 at the positive tap) the taps are, over the divisor:

- set 2: 1/8 at -1, -4/8 at 0, 4/8 at +1 (the lift: 0x80 x 4/8 = 0x40), -1/8 at +2: [1 -4 4 -1]/8;
- set 3: 1 at -2 (the lift: 0x80 x 1 = 0x80), -2 at -1, 1/2 at 0 and 1/2 at +1: [1 -2 1/2 1/2].

Both sum to zero, as E080's 0 on every pedestal requires, and agree with E080's steps (4 and 16
for set 2, 32, 16 and 16 for set 3 on the pedestals). In 128ths with a shift of 7, the tap
vectors within 5 of [16 -64 64 -16] and [128 -256 64 64] that some bias fits on every case of
usse-filter-banks and this table are 7 per set; the simulator gives a result where all 7 agree
(E292).

**Not shown.** One run, `u8` and edge repeat only, centred at byte 4.
