<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### The test group: ALU operations with a test

Classes 9 and 15 run an ALU operation (`enc[19:14]`) and **test its result**: class 9 into a
predicate `p0`-`p3` (`enc[35:34]`), class 15 into a byte, word or dword mask (`.bmsk`,
`.wmsk`, `.dmsk`). With `enc[20]` clear the result itself is not written (`!` before the
destination) **[RE]**. The operations: the bitwise group and shifts, integer adds, subtracts
and multiplies on 8, 16 and 32 bits (`iadd8` ... `iaddu32`, the 8-bit ones with `.sat`), and
float adds, multiplies, min/max, derivatives, dot product and reciprocal-type operations,
with the operand formats of their own groups when `enc[50]` is set. The bitwise group, the
integer adds, subtracts and multiplies and `fadd`/`fsub`/`fmul` are measured as tests (*Test
channels* and the pages it links); the other operations, the one-source tests and the
`enc[50]` forms are **[open]**.

The test is `.test<S><J><Z>.<chan>`, from `enc[43:36]`:

| part | bits | values |
|---|---|---|
| sign test `S` | `enc[43:42]` | `t`, `n` (negative), `p` (positive) |
| join `J` | `enc[39]` | `o` (or), `a` (and) |
| zero test `Z` | `enc[41:40]` | `t`, `z` (zero), `nz` (not zero) |
| channel | `enc[38:36]` | `chan0`-`chan3`, `andall`, `orall`, `and02`, `or02` |

- **The tests [HW].** On 32-bit results tested on `chan0`: `z` and `nz` test the result for
  zero, `n` tests bit 31 and `p` is its complement (`>= 0`, so zero passes), and `t` is true
  in either join: `testtaz`/`testtanz` are "zero" and "not zero", an `o` join with a `t` side
  is always true (*The test sign `p`*, *`t` in the `a`/`o` joins of a test*). The firmware
  tests flags this way hundreds of times, and sign bits by shifting the flag to bit 31 first
  (`shl.testnat`); our state and vertex programs rely on `and.testtanz` of 0 and 0 leaving
  the predicate false (*Predicates*).
- **The 32-bit adds [HW]** are not full 32-bit adds: `iadd32`/`iaddu32` add source 1's low 16
  bits, sign- or zero-extended, to the 32-bit source 2, and `iaddu32`'s `n` is never true
  (*The 32-bit adds `iadd32` and `iaddu32`*).
- **The 16-bit operations [HW]:** `isub16`/`usub16` subtract both lanes, wrapping, and `chan0`
  tests the low lane (*`isub16`/`usub16` lanes*). `iadd16`, `uadd16`, `imul16`, `umul16`,
  `iadd8`, `isub8`, `imul8`, `fadd`, `fmul` and `fsub` test their lanes as the channels say, a
  16-bit lane on its full result before it is cut **[HW]** (*Test channels*).
- **Channels [HW]:** a test has one result per channel: bytes 0-3 for the 8-bit operations,
  the low and high halves as channels 0 and 2 for the 16-bit ones, the value as channel 0
  otherwise; a channel without a lane tests as a positive non-zero value. `chan0`-`chan3`
  pick one, `andall`/`orall` combine all four, `and02`/`or02` channels 0 and 2 (*Test
  channels*). The masks of class 15, `.partial` and `.quadlead` on tests are **[open]**.
- **The unsigned and unorm byte operations [HW]** (E092, E094). `uadd8`, `usub8`, `umul8`,
  `uadd16` and `umul16` work lane by lane, unsigned and wrapping, and `.sat` clamps a byte at
  255 (the Rogue ISR's `UADD8`, `UMUL8`, `UADD16`, `UMUL16`). The unorm8 operations clamp per
  byte: `fpadd8` is x + y up to 255, `fpsub8` x - y down to 0 (x86's `PSUBUSB`), and `fpmul8`
  round(x · y / 255), exactly rounded (the GL texture combiners' modulate on unorm8). A test sees
  each byte's unclamped result: `fpsub8` of 3 and 85 writes 0 but does not test as zero.

**In the firmware [RE].** 671 tests, every one on `chan0` and into a predicate, mostly `and` and
`xor` with the zero and non-zero tests, a few `shl`, `isub16`, `or` and `iaddu32`. Most discard the
result (`!c0`): test, then branch on the predicate.

<!-- @prog use_mtest18.s match='\.test' -->

<!-- @example usse xor.testtaz.chan0 r1, p2, r1, r3 -->

<!-- @example usse isub16.testpat.chan0 r1, p2, r3, #4 -->

<!-- @group usse class=9,15 -->
