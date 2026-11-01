<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Integer multiply-add: `imae`, `ima16`, `ima32`, `ima8`, `idiv`

Four classes **[RE]**: 21 `imae` (16 × 16 + 32), 20 `ima16` (16-bit), 26 `ima32` (32-bit) and
`idiv`, 19 `ima8` (four 8-bit lanes with colour-style selectors). They carry the multiply
flags (`.skipinv`, `.nosched`, `.end`, a three-bit repeat) and a two-bit predicate (`ima32`
and `idiv` the full one).

- **`imae.{u,s} d, a.{low,high}, b.{low,high}, c, u32`** computes `d = a16 × b16 + c`, the halves
  zero-extended for `.u` **[infer]** and sign-extended for `.s` **[HW]** (6 cases; E471: `.s`
  multiplies the halves as signed values and adds `c` as an unsigned 32-bit number, a formula
  fitted after the six cases): the firmware's
  addition idiom is a multiply-add by an immediate 1 of a 16-bit value, 205 times, and its address
  arithmetic multiplies indices by structure sizes the same way. **[HW]** `.usat`/`.ssat` saturate,
  `.rsN` shifts the result right, a `u16` source 2 is sign-extended and a `z16` one zero-extended
  (*Integer multiply-add modes*). `coe, iN` writes the carry out of the 32-bit sum to `iN`, 0 or 1,
  overwriting it whether or not the sum carried (14 of 14); `cie, iN` adds bit 0 of `iN` only (10 of
  10: `iN` = 2 adds nothing, 0xffff and 0xffffffff add 1); `coe` and `cie` on one `iN` write the
  carry of the sum that includes the added bit (14 of 14); two `imae` chained through `i0`, a `coe`
  then a `cie`, are an exact 64-bit accumulate of 16 × 16 products (10 of 10) (E471). `imae` has no
  negated source (the assembler refuses it **[infer]**: no raw word was run).
- **`ima32.{u,s} d, a, b, c`** computes the low 32 bits of `a × b + c` **[HW]** (E469: 826 of 826
  cases, the corner cube of 343 included; `.s` gives the same bits as `.u`, with no saturation). Its
  operands a, b and c are sources 1, 2 and 3: sources 2 and 3 can be a register, a 7-bit immediate
  (0 to 127) or a constant-bank register read as an integer (c0 reads 0, c56-c59 read 0xffffffff,
  c60 0x7fff7fff: E085), source 1 only a register (the assembler refuses anything else in source 1
  **[infer]**). The runs used the immediates 0, 1, 2, 3 and 127, the constants c0, c3, c13, c60 (and
  c45, c56 as source 3 only) and temporaries (r bank) as registers, and the destination r10: other
  banks are **[open]** (Q127). So `add` is `ima32.u d, a, #1, c` and `mul` is
  `ima32.u d, a, b, c0`.
- **A 32-bit subtract [HW]** is `ima32.u d, b, c56, a`, which is `a - b` mod 2^32, and so is
  `ima32.u d, a, #1, b.neg` (E470: 80 of 80 through c56, 6 of 6 through c57, c58, c59 `.u` and c59
  `.s`). `.neg` on source 2 (`enc[40]`) or source 3 (`enc[39]`) negates that source in two's
  complement, `-(a × b) + c` and `a × b - c` (90 of 90 cases in nine probes; the readings
  "complement" and "ignored" fail in all of them and "fields swapped" in the eight probes with one
  negated source, 80 of 90 cases). It was run with `.u` and `.s` on registers and with `.u` only on
  an immediate and a constant; `.s` with `.neg` on those two was not run. Source 1 has no `.neg`
  and `ima32 ... coe` does not assemble, both the assembler's refusals **[infer]**: no carry out of
  `ima32` is known, so the borrow of a 32-bit compare is software (*The test group*).
- **`ima32 ... cie, iN` [HW]** adds bit 0 of `iN` only (10 of 10 with iN = 0, 1, 2, 0xffff and
  0xffffffff in `i0`; the probe table's model added all of `iN`, which fits 4 of 10; an iN with bit
  0 clear and a high bit set, and an iN other than `i0`, were not run). Dependent `ima32` need no
  gap: four in a row are exact (10 of 10, E470). The optional `i` register after the destination,
  and `ima32` as a dual-issue secondary (two 16-bit lanes: *Dual issue*), are **[open]** for the
  carry flags and the 32-bit result (Q127).
- **`ima16`** multiplies 16-bit values, its sources read as `u16`, `u8`, `s8` or `o8` with a
  half select. With `u16, u16` it computes `a × b + c` (or `- c`) in each 16-bit lane,
  wrapping **[HW]** (*`ima16` lanes and source formats*); with `u8`, `s8`, `o8` each lane reads
  the `.low`/`.high` byte of its own half **[HW]** (*Integer multiply-add modes*).
  The firmware has two, both `.s` with a negated source.
- **`idiv d, a, b, drcN`** writes the unsigned quotient to `d` and the remainder to `d + 1`,
  asynchronously: `wdf drcN` waits for them **[HW]** (*Integer multiply-add modes*). Its repeat
  count has four bits, enc[47:44] + 1: iteration k divides `a + k` by `b + k`, its quotient
  to `d + k` and its remainder to `d + k + 1`, which the next quotient overwrites **[HW]**
  (E367).
- **`ima8`** computes `x + y × z` per byte from its selectors (`s0`, `s1`, `s2` and their alpha
  forms), wrapping or with `.sat` clamping **[HW]** (*Integer multiply-add modes*).

<!-- @example usse imae.u r2, r4.low, #1.low, r2, u32 -->

<!-- @example usse ima32.u r1, r2, r3, r4 -->

<!-- @group usse class=19-21,26 -->
