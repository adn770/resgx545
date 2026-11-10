<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Test channels

*Measured on the hardware (2026-10-22).* **A test gives one result per channel, and the channel
field picks one or combines them** **[HW]** (probe `usse-test-channels-chan-tests`, 360 cases):

- an 8-bit operation (`iadd8`, ...) has four channels, **bytes 0-3**, each tested on its own
  (`n` is the byte's bit 7);
- a 16-bit operation has **the low half as channel 0 and the high half as channel 2**;
- a 32-bit or float operation has its value as channel 0;
- **a channel with no lane tests as a positive non-zero value**: `z` and `n` false, `nz` and `p`
  true. That is why the first probes saw `chan1`-`chan3` clear the predicate on a zero test;
- `chan0`-`chan3` take one channel, **`andall`/`orall` all four** (and/or), **`and02`/`or02`
  channels 0 and 2**.

*Later probes (2026-10-22).* **`imul16`, `umul16`, `iadd16` and `uadd16` test their lanes as
channels 0 and 2 on the full product or sum, before it is cut to 16 bits**: `0x100 × 0x100`
writes 0 but does not test as zero, nor does `uadd16`'s `0xffff + 1` or `iadd16`'s
`-0x8000 + -0x8000`. `fmul` and `fsub` test channel 0 like `fadd`, and `isub8`/`imul8` a byte per
channel **[HW]** (probe `usse-test-channels-lanes-other`).

A float test of an exact zero product tests the hardware's `+0`: `fmul` of 0 and -3 gives `+0`,
not IEEE's `-0` **[HW]** (probe `x-misc`).

*Later probes (2026-11-08).* **On a 32-bit result the raw `and` test words with the chan field 1 to
7 and the `a` join do not read as `chan0` as a table** **[HW]** (E530: six field values and six
input pairs in each of seven tables, the prediction that the field is ignored having failed), and
they read as this rule says **[infer]** (252 of 252 cases; the rule was applied after the data, it
predates the runs and was not predicted for them): `chan1`-`chan3` test a channel with no lane, and
`andall`, `orall`, `and02` and `or02` (chan4 to chan7) combine channel 0 with such channels, so a
test of a 32-bit value must name `chan0`. The same on 8-bit and 16-bit lane operations with raw
words is not run (Q137).

**Undecided:** the mask forms of class 15 (`.bmsk`/`.wmsk`/`.dmsk`); float tests of `-0`,
infinities and NaNs; the one-source tests (`frcp`, `frsq`, `flog`, `fexp`); `fsubflr`, `fdp`,
`fmin`, `fmax`, `fdsx`, `fdsy`, `uadd8`, `usub8`, `umul8` and the `fp*8` operations as
tests; and the operand formats of the `enc[50]` forms.
