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
  overwriting it whether or not the sum carried (14 of 14 with `i0`, E471; 8 of 8 with `i0` and `i1`
  over four triples, one of which carries, E494, the other `i` registers keeping their values);
  `cie, iN` adds bit 0 of `iN` only (10 of 10 with `i0`: `iN` = 2 adds nothing, 0xffff and
  0xffffffff add 1; 8 of 8 with `i0` and `i1` and the values 0x10000, 0x80000000, 0x10001 and 1,
  E494); `coe` and `cie` on one `iN` write the
  carry of the sum that includes the added bit (14 of 14); two `imae` chained through `i0`, a `coe`
  then a `cie`, are an exact 64-bit accumulate of 16 × 16 products (10 of 10) (E471). `imae` has no
  negated source and no `i2` form for `coe` and `cie` (the assembler refuses them **[infer]**: no
  raw word was run).
- **`ima32.{u,s} d, a, b, c`** computes the low 32 bits of `a × b + c` **[HW]** (E469: 826 of 826
  cases, the corner cube of 343 included; `.s` gives the same bits as `.u`, with no saturation). Its
  operands a, b and c are sources 1, 2 and 3: sources 2 and 3 can be a register, a 7-bit immediate
  or a constant-bank register read as an integer (c0 reads 0, c56-c59 read 0xffffffff,
  c60 0x7fff7fff: E085), source 1 a register; the assembler refuses an immediate or a constant in
  source 1 **[infer]**, while pa, sa, o and i operands in source 1 and pa, sa, o, g and i operands
  in sources 2 and 3 assemble, and read 0 where `mov` reads 0 (40 of 40, E496: 31 of the 40 cases
  read 0 by both routes, so only `i0` to `i2` show a nonzero value). What ran: the immediates 0, 1,
  2, 3, 4, 5, 6, 7, 8, 15, 16, 17, 31, 32, 33, 63, 64, 65, 100, 125, 126 and 127 in source 2 and the
  same without 3 in source 3 (22 and 21 of the 128 values: E469, E495, so 'every 7-bit immediate' is
  **[infer]** for the others); the constants c0, c3, c13, c60 (and
  c45, c56 as source 3 only); the destinations r0, r9, r10, r18, r28, r30, r31, sa0, o0, i1 and i2,
  and **a pa0 destination is not written** (E496; the probe table's model had every destination take
  the result). So `add` is `ima32.u d, a, #1, c` and `mul` is
  `ima32.u d, a, b, c0`.
- **Operand order [HW]** (E597): `ima32.u d, i0, a, b, c` and `ima32.s` read their sources
  before the write in every one of the 15 partitions of d, a, b and c into registers (any of them
  alike, all four the same): d held the low word and i0 the high word of the 64-bit a × b + c (c
  sign-extended for `.s`) in 300 of 300 fills. Not run in a firmware task (the verifier refuses
  the form).
- **A 32-bit subtract [HW]** is `ima32.u d, b, c56, a`, which is `a - b` mod 2^32, and so is
  `ima32.u d, a, #1, b.neg` (E470: 80 of 80 through c56, 6 of 6 through c57, c58, c59 `.u` and c59
  `.s`). `.neg` on source 2 (`enc[40]`) or source 3 (`enc[39]`) negates that source in two's
  complement, `-(a × b) + c` and `a × b - c` (90 of 90 cases in nine probes; the readings
  "complement" and "ignored" fail in all of them and "fields swapped" in the eight probes with one
  negated source, 80 of 90 cases), with `.u` and `.s` on registers (E470) and on the immediates and
  constants of E495 (`.s` with #1.neg and #5.neg in source 2, #1.neg and #127.neg in source 3,
  c56.neg and c3.neg in source 2 and c56.neg in source 3; `.u` with #5.neg and #127.neg in source 2
  and #127.neg in source 3: 80 of 80). Source 1 has no `.neg` (the assembler's refusal **[infer]**).
  **The borrow comes with the high word [HW]:** `ima32.u d, i0, b, c56, a` leaves `a - b` in `d`
  and `b - [a < b]` in `i0` (75 of 75 cases, E501: `i0` over the 49 pairs of the values 0, 1,
  0xffff, 0x10000, 0x7fffffff, 0x80000000 and 0xffffffff, `i1` and `i2` over 13 pairs of them), so
  that `xor.testtanz.chan0 !c0, p0, b, i0` sets `p0` to `a < b` unsigned: two instructions instead
  of six (*The test group*), run on the 64 pairs of the eight values 0, 1, 0xffff, 0x10000,
  0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff (E501) and on 252 seeded pairs, 200 random among
  them, and with 0, 1 and 3 `nop`s between the two instructions on 48 of those pairs each (252 of
  252 and 48 of 48 three times, E527), registers only, the destination `r11`; that it is exact for
  every pair is **[infer]** from the arithmetic of the high word, which E525 shows for 200 random
  register triples. **A signed compare is two instructions too [HW]:** `ima32.s r11, i0, r2, c56,
  r1` then `xor.testtanz.chan0 !c0, p0, i0, #0` sets `p0` to `a < b` signed (164 of 164 pairs: the
  64 of the eight values and 100 random, E528; `c56` reads -1 signed, `i0` is the high word of the
  signed `a - b`, 0xffffffff for `a < b`), against the six of *The test group*; it was not padded
  and was not run beyond the 164 pairs (**[infer]** for the rest).
- **The extra `i` operand and `cie` of `ima32` [HW].** `ima32.u d, iK, a, b, c` (`enc[38]` set, `iK`
  in `enc[37:36]`) writes the low 32 bits of `a × b + c` to `d` and the high 32 bits to `iK`, the
  bits 63:32 of the exact 64-bit `a × b + c` on register operands (E525: 282 of 282 jobs, 42 corner
  triples, 0x12345678 × 0x9abcdef0 among them, and 200 random triples with `K` = 0, then `K` = 1 and
  2 over 20 random triples each; `.s` gives the signed high word with `c` sign-extended, 282 of 282,
  E526; E493's five `.u` triples, (3, 7, 100), (0xffffffff, 1, 1), (0xffffffff, 0xffffffff,
  0xffffffff), (0x10000, 0x10000, 0) and (0x80000000, 2, 0xffffffff), 15 of 15 cases with `K` = 0, 1
  and 2, and `b * 0xffffffff + a` for eight values of `b`, E501, are cases of it): the probe table's
  model, that the `i` registers keep their values, fits 0 of 15, and `iK` = the carry out of the
  32-bit add fits 6 of the 15 and 10 of the 282. A backend may lower a 32 × 32 + 32 high-word
  multiply to it for register operands; its cost was not measured. Raw words with the field
  `enc[37:36]` set and `enc[38]` clear, with `enc[38]` set and `iK` = 3 and with the bits 45, 44 and
  35 set changed neither `r10`, `i0` to `i2` nor `r14` to `r17`; with bit 46 set `r14` read 0x2255
  in 3 of 3 jobs, what the bit does is **[open]** (Q135). Immediates and constants other than c56
  with the extra operand, the extra operand together with `cie` or `.neg`, an `iK` that is also a
  source, a destination other than `r10`, the dual-issue form and `K` = 3 are **[open]** (Q135).
  `ima32 ... cie, iN` adds bit 0 of `iN` only **[HW]**: `i0` to `i2` with the values 0x10000,
  0x80000000, 0xfffffffe, 0x10001, 0x80000001, 2, 0x55555554 and 0xaaaaaaab (24 of 24, E494; and 10
  of 10 with 0, 1, 2, 0xffff and 0xffffffff in `i0`, E470; adding all of `iN` fits 0 of 24, E494).
  Dependent `ima32` need no gap: four in a row are exact (10 of 10, E470), and a reader (`ima32`,
  `mov` or `xor`) after 0, 1, 2, 3, 4, 5, 6 or 8 `nop`s sees the result, with or without `.nosched`
  on the writer (48 of 48, E495). `ima32` as a dual-issue secondary (two 16-bit lanes: *Dual
  issue*), `u16`/`z16` sources and `.rsN` on `ima32`, and `imae` with a repeat are **[open]**
  (Q127).
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
