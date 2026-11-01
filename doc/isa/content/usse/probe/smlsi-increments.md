<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `smlsi` increments

*Measured on the hardware (2026-10-22).* `smlsi #I0, #I1, #I2, #I3, ...` sets four signed 8-bit
increments **[RE]**: before `mov.repeat2 r20, r10`, **`I0` is the destination's increment and `I2`
the source's** (0 repeats a register, 2 skips one); `I1` and `I3` change nothing there **[HW]**
(probe `usse-repeat-smlsi`). **On a three-source repeat (`fmad.repeat2`)
`I1` is source 0's increment, `I2` source 1's and `I3` source 2's** **[HW]** (probe
`usse-moe-smlsi-three-sources`); `mov`'s source is source 1. With the firmware's `0, 0, 0, 1` at
every task
entry **[RE]** a following `mov` repeat would hold its destination and its source still; the
firmware repeats nothing itself; its 1 is taken to step fetch destinations **[infer]** (*Loads and
stores*).

*Measured on the hardware (2026-11-08).* On `stad.repeatN [rb,...], rs` the base is source 0 and
the data source 2, so by the same rule **`I1` is the base register's increment and `I3` the data
register's** **[HW]** (E483, 12 of 12 cases with 16 valid pointers): with `0, 0, 0, 1` the data
steps by one and the pointer stays, one post-incremented `rb` for the whole repeat (`stad.repeat4
[r40,#1++]` stores `r2`-`r5` at four consecutive dwords); `0, 0, 0, 2` stores every second
register, `0, 0, 0, 0` the same register N times, `0, 1, 0, 1` and `0, 2, 0, 1` step the pointer
by one and by two registers; `I0` and `I2` changed nothing to a store, varied only together
(`1, 0, 1, 1` and `1, 1, 1, 1`). Without an `smlsi` both step by one. The first and the third
increment alone were not run on a store.

The first recorded run of `usse-moe-smlsi-three-sources` began with a case `(1, 1, 1, 1)` that the
table
no longer has: each of its readbacks is the previous case's, and with that shift every case
fits the rule above.

**Undecided:** swizzle mode, the limits, how long the state lasts, and which increment a fetch
uses.
