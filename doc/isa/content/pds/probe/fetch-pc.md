<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### The fetch pc, read everywhere

*Measured on the hardware (2026-11-02; `probes/pds/fetch-pc.toml`, recorded runs).* `pc.0` read
by `mov32` into a temporary of its own, 16 reads a program, each case three times (E261)
**[HW]**:

- **Back to back**, after 0-3 `nop`s: index + 3 at every read but two consecutive ones at
  index + 2, at instructions 26-27 in ten of twelve runs, whatever the `nop`s before, and at
  19-20 in two.
- **After 0-14 `nop`s** between reads, rising and falling: index + 3, with lags of one at a
  few reads, and + 1 once (the first read of a long program in one run). A `nop` takes one slot.
- **After each kind of instruction** (`mov16`, `mov64`, `mov128`, `add`, `mul`, `shl`, `not`,
  `abs`, `tstz`, `alum`, `rfence`, `rwfence`, `movs douta`, `mov32`, `bra` to the next):
  index + 3, + 2 after `add` and `mov32` in every run, and in one run also after `mov64` and
  `alum`, with + 1 at its first read.
- **Across branches and a call**, the three runs alike: + 2 at the first read, at the targets
  of branches over 1 and 3 `nop`s, in the called routine, after its return and at the target
  past it; + 3 at the target of a branch to the next instruction (the read after it + 2) and
  of one over 7 `nop`s (and the read after it).
- **After a load** with `nop`s instead of a fence, and after `rfence` and `rwfence`: + 1 to + 3.

No read was more than 3 or less than 1 ahead. Where the fetch falls behind is mostly a fixed place
in the program: the back-to-back lag stays at instructions 26-27 whatever the `nop`s before it,
which with the 36-dword data segment are dwords 62-63, the last two before a 64-dword boundary; the
branch program gives the same values in all three runs, and the `nop`-gap programs do but at their
first read and one read of one run. Some runs differ (two of twelve back to back, some first reads,
the third kinds run and the loads) **[infer]**. The simulator models `pc.0` as index + 3, matched by
a hardware value up to 2 below (*Input and special registers*; Q062).
