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
- **The 32-bit adds [HW]** are not full 32-bit adds: `iadd32`/`iaddu32` add source 1's low 16 bits,
  sign- or zero-extended (`iadd32` sign-extends: E498; `iaddu32`'s extension is **[open]**, Q126),
  to the 32-bit source 2, and a test of some of them applies to the true 33-bit sum, not the wrapped
  one (E472, E498; the probe table's model tested the wrapped sum): `iadd32`'s `n` and `p` read the
  sign of the true sum sext16(r1) + r2 (r1 = 0x7fff with r2 = 0x7fffffff leaves `n` clear; 12 pairs
  in E472, 5 of which separate the readings, and 16 in E498, where only (0xffff, 0x80000000), one of
  those 5, does), `iadd32`'s `z` and `nz` read the zero of that sum with r1 sign-extended (16 pairs:
  (0x8000, 0x8000) and (0xffff, 1) read zero, which a zero-extended r1 does not give, 11 of 16; no
  pair can tell the true sum from the wrapped one: with r2 signed the sum stays within +-2^32, so
  they agree in zero-ness on 16 of 16 pairs, and (1, 0xffffffff) reads zero), `iaddu32`'s `p` is
  always true and its `n` never (16 of 16 pairs each) and its `z` is true for the pair (0, 0) only:
  the sum with its carry out of bit 31 is zero for no other pair of the 16 under either extension of
  r1 (nor is 'both operands zero': the 16 pairs do not separate the two), so 1 + 0xffffffff is
  nonzero, and the wrapped sum reads zero for pairs that are nonzero (E498 lists the 16 pairs).
  Whether `iaddu32` extends source 1 by zero or by sign is **[open]** (Q126): no test tells it. With
  source 1 = `#0` the test reads source 2's 32 bits exactly: `n`, `p`, `z` and `nz` (8 of 8 values
  each) (*The 32-bit adds `iadd32` and `iaddu32`*).
- **The test field is two parts, ANDed under the `a` join [HW]** (E499): `enc[43:40]` holds taz =
  bit 40, tanz = bit 41, nat = bit 42 and pat = bit 43 (the assembler's `.test<S><J><Z>` writes one
  condition of the two parts at a time). Run as raw words, with enc[39] = 1 (join `a`) and chan0 in
  all 732 words, the zero part is tanz if bit 41 is set, else taz if bit 40, the sign part is pat if
  bit 43 is set, else nat if bit 42, and the test is true when the parts present are all true: `and`
  with r1, r2 over the 15 values of the field and six input pairs (90 of 90, a rule read out of
  those cases, the plain AND of the set conditions fitting 69 and the OR 57), then predicted on
  `or`, `xor` and `rol` with registers and `and` and `xor` with #7 (450 of 450, 90 cases each, join
  `a` and chan0 only). Bit 43 is the bit that `~` sets in `and r10, r1, ~r2`; set in the sixteen
  test words the assembler writes (`and`, `or`, `xor`, `rol`, with r2 or #7, testtaz and testtanz)
  it is the `pat` condition ANDed with the test, not an invert (96 of 96; the invert of source 2,
  the probe table's model, fits 53 of 96): so a test word has no `~`, taz with pat is taz, and tanz
  with pat is the one-instruction "greater than zero" test that the assembler does not write.
  **[infer]** The rule is not run for the `o` join (enc[39] = 0) with a two-part field, the shifts
  `shl`, `shr` and `asr`, `or` and `rol` with #7, the chan fields other than chan0 and the other
  classes' tests, and that no other bit of a test word inverts a source is not run (Q137).
- **Tests with an immediate [HW]** act on the 32-bit result (E473): `shr.testtanz.chan0 !c0, p0, r,
  #n` is "r >> n is nonzero", with n of 32 and over giving zero (80 of 80), `xor.testtaz` is "r ^ n
  is zero" over all 32 bits (18 of 18), and `and`, `or`, `xor` and `rol` with `testtanz` and `asr`
  and `shl` with `testnat` test their 32-bit result (48 of 48). The immediate of a test is seven
  bits. The assembler refuses `~` in the three test forms tried (`and.testtanz ... ~#7` and `~r2`,
  `xor.testtaz ... ~#7`), while `and r10, r1, ~#7` assembles; `or`, `rol` and `xor ~r2` were not
  tried as text. The reason is in the test field below: the bit that `~` sets in the non-test forms
  is the `pat` bit of a test word (E499). To test `x & ~mask`, a compiler computes the inverted
  value first (`and r11, r1, ~#7`, then a test of r11).
- **A 32-bit compare [HW]** of two registers ran as two instructions for the unsigned a < b and six
  for the signed one. Unsigned: with `ima32.u r11, i0, r2, c56, r1` (`r11` = a - b, `i0` = b - [a <
  b]: the high word of the extra operand, E493, which ran for b * 0xffffffff + a over eight values
  of b) and `xor.testtanz.chan0 !c0, p0, r2, i0`, `p0` is a < b (64 of 64 pairs of the eight values
  0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff, 28 of them with a < b;
  E501; unsigned only, not padded, with the destination r11: other pairs, other operands and a
  signed `.s` form were not run, and that `b xor (b - [a < b])` is nonzero exactly when a < b for
  them is **[infer]** from the arithmetic). Signed: with `t = ima32.u r11, r2, c56, r1` (a - b), the
  signed one is bit 31 of `(((a ^ b) & (a ^ t)) ^ t)`, tested by `shr.testtanz.chan0 !c0, p0, rX,
  #31` (64 of 64 pairs of the same eight values, unpadded, and 16 pairs with 1, 3 and 6 nops after
  the `ima32`, 48 of 48; E472, E497); the six-instruction unsigned formula, bit 31 of `((~a & b) |
  (~(a ^ b) & t))`, was also exact on the 64 pairs (E472, 16 of 16 with three nops after the
  `ima32`). A signed compare through the high word was not run (the high word of `.s` is **[open]**,
  Q135). `ima32` has no test field **[infer]** (the assembler refuses a test on it).
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
