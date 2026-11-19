<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### `ir0`-`ir2`, `tim` and `pc` as sources

*Spelling.* This section was measured with the earlier names of the
`mov16`/`mov32` special sources, which the probes' program texts and the published vectors
keep (their words are the record). The tools now spell them by
selector and bit 9 (*Input and special registers*):

| field (mov32; mov16 is twice it, plus the half) | earlier name | spelled now | reads (SGX545) |
|---|---|---|---|
| 128 | `ir0` | `ir0.0` | `ir0` |
| 129 | `ir1` | `ir0.1` | `ir0` (mov32), 0 (mov16) |
| 130 | `pc` | `ir1.0` | the ALU's `ir1`, 0 in a fill (E262, E263) |
| 131 | `tim` | `ir1.1` | 0 |
| 132 | `ir2` | `pc.0` | the fetch pc |
| 133 | (none) | `pc.1` | as `pc.0` (mov32), 0 (mov16) |
| 134 | (none) | `tim.0` | `EVENT_TIMER` |
| 135 | (none) | `tim.1` | the timer (mov32), 0 (mov16) |
| 136-255 | (none) | (undecoded) | 0 |

*Measured on the hardware (2026-10-24).* In a 64x32 fill's secondary program, `mov32` reads `ir0`
and `ir1` equal, `0x402` or `0x403`, and `ir2` from `0x15` to `0x1f`, varying from run to run;
`tim` and `pc` read 0, twice each (`pds-alu-inputs`, `pds-alu-specials`, recorded) **[HW]**. What
the
values mean is still open.

As `movs` sources (`pds-alu-specials`, recorded) the four specials are pairs of words, as a `ds0`
pair is: `.l` passes a whole 32-bit word and `.h` read 0 for all four, whatever the other
slots hold **[HW]**. Special 0 (`ir0.l`) is `ir0`, equal to the `mov32` copy in every run.
The others do not read what `mov32` reads under the same reference names: `ir1.l` and `ir2.l`
read 0, and `tim.l` a 32-bit down-counter (`0x0100_0000`-`0x0105_0000` at the start of the
program, different each run) that drops by 1 between back-to-back `movs` and by nearly the same
amounts across runs after the same `nop` gaps (3-6, 4-17, 7, 11-23, 31-40, 58-59 and 115-117
across 0, 1, 2, 4, 8, 16, 32 and 64 `nop`s, through `movs` and the ALU alike) **[HW]**: core
clocks, since the counter is `EVENT_TIMER` (*Input and special registers*) **[GPL]**.

The datapaths number the specials two ways (`pds-alu-specials-paths`, recorded) **[HW]**. The ALU's
first source, `mul`'s halves and `movs` agree: `ir0` is the input word, `ir1` reads 0 and `tim` is
the down-counter (`or ds0[n], tim, ...` reads it whole, `mul` with `tim.l`/`tim.h` its 16-bit
halves). `mov32` and `mov16`, with `pc` inserted in their numbering, read only `ir0` the same: their
`ir1` reads what `ir0` does, their `pc` and `tim` read 0 (`mov16` of `tim.l`/`tim.h` and `pc.l`
too), and their `ir2` the varying `0x15`-`0x1f`. `shl` and `abs` read `ir0` and `ir1` as the ALU
does (`ir1` 0), `not tim` the counter's complement; `tstz` of `ir1` tests nonzero, unlike the ALU's
`ir1` (it tests zero where `ir0` is 0, E262, so that it reads `ir0` **[infer]**), and `mov16` reads
`ir1.l` as 0 where `mov32` reads `ir1` as `ir0`'s value (`pds-alu-specials-paths2`, recorded)
**[HW]**.

Every special index of the source fields, swept with hand-encoded words (`pds-x-index-*`,
recorded; none hung) **[HW]**. The ALU's first source reads `ir0`, `ir1` (0 here) and the counter
at 64-66 and 0 above; `shl` reaches the counter too, at 130 after `ir0` and `ir1`, which the
decoder does not name; `mul`'s halves follow the ALU (`ir0`, `ir1`, the counter). `mov32` and
`mov16` number them their own way: special 0 is `ir0`, 2 reads 0, 4 a small count near the
instruction's own index (two `mov32`s in a row at instructions 20 and 21 read 23 and 24; what
the reference calls `ir2`), 6 the counter (which the reference does not name), and 8 and up 0;
`mov32` ignores the index's low bit (its `ir1` is `ir0` again), while `mov16` reads 0 at every
odd one. So of the reference's names for these fields only `ir0` matches the hardware: the
fields hold the reference's list in its order at every other index, the low bit (the word's
bit 9) apart, which is how the tools spell them now. The count is the fetch pc (8.11)
**[HW]**.

A `movs tim` loads the counter and stops it: the value written reads back unchanged through 64
`nop`s, and in every later job, of any client, until the GPU is reset; after a reboot it counts
again (`pds-timer-tim-count`, recorded) **[HW]**. Between probes, by hand through debugfs: the
driver's in-place reset (`sgx/reset`: halt, soft reset, firmware boot) restarts it, from
`0x0102_0000`-`0x0105_0000` as after power-on, while a POWER IDLE through the CCB (`sgx/idle`)
leaves it reading 0, in that job and the next ones, until a reset **[HW]**. The first word
printed (`movs tim, a, b, c, d`: `a`) loads it and the others do nothing; it keeps the word's
bits 24-0 (`pds-timer-tim-words`; the 25-bit reading was fitted to its first run and confirmed by a
case added for it) **[HW]**. Bit 24 is a run bit: a value with it set counts down from the
value less one, one with it clear stays where it was put; the counter that resets and power-on
leave has it set (`0x0102_0000`-`0x0105_0000`) **[HW]**. In runs by hand that no table or record
holds, an enabled count that reaches 0 hung the job: loads of `0x0100_0002`, `0x0100_0020` and
`0x0100_0040` each lost their job to the driver's recovery (Q057 asks for the recorded run). The
counter is the microkernel's tick timer, `EVENT_TIMER`
(GPL DDK, *Input and special registers*), so a probe that writes it stops or speeds up the
firmware's tick. It is not a PDS watchdog. The host reads the same register at 0x0acc
(`pds-timer-tim-host` under a host timeline of 0x0acc, E1152): the running count gave way to the
loaded 0x00abcde0 within one 5.8 us sample of the fill's job and read it to the timeline's end
and after the job, as the program's own `tim` reads did **[HW]**.
