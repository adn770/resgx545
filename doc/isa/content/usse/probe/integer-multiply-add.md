<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### Integer multiply-add modes

*Measured on the hardware (2026-10-22).* The later probes (table `integer.toml`) **[HW]**:

- **`idiv d, a, b, drcN`** writes the **unsigned quotient to `d` and the remainder to `d + 1`**,
  `0xffffffff` to both for `b = 0`; the results arrive once `wdf drcN` returns (without the
  wait the remainder was still missing at the next store) (probe `idiv`).
- **`ima16` with 8-bit formats** reads, in each 16-bit lane, the byte `.low` or `.high` of that
  lane's half of `b` and `c`: `u8` unsigned, `s8` signed, `o8` the byte minus 128; `a` stays
  `u16` (probe `usse-integer-ima16-8bit`).
- **`ima8 d, a, b, c, x, y, z, xa, ya, za`** computes **`x + y × z` per byte**, the colour
  selectors `x`, `y`, `z` for bytes 0-2 and the alpha ones for byte 3 (`s0`, `s1`, `s2` = `a`,
  `b`, `c`; `.comp` = 255 − the byte), wrapping, or clamping to 255 with `.sat` (probe
  `ima8`).
- **`imae`**: `.usat`/`.ssat` saturate the 32-bit result (`.ssat` signed), `.rsN` shifts it right by
  N, source 2 typed `u16` is its half **sign**-extended and `z16` zero-extended, **`coe, iN` writes
  the carry out to `iN` and `cie, iN` adds bit 0 of `iN`** (probe `usse-integer-imae-modes`);
  `ima32`'s `cie, iN` adds bit 0 of `iN` only, as `imae`'s does (E470, E471: 10 of 10 each; E494:
  `ima32` 24 of 24 with `i0` to `i2` and the values 0x10000, 0x80000000, 0xfffffffe, 0x10001,
  0x80000001, 2, 0x55555554 and 0xaaaaaaab, `imae` 8 of 8 with `i0` and `i1`).

- **`idiv` repeats** 1 to 16 times, the count enc[47:44] + 1 (enc[47], outside every field
  before, is its high bit): iteration k divides `a + k` by `b + k`, the quotient to `d + k` and
  the remainder to `d + k + 1`, so after the last iteration `d` to `d + n - 1` hold the
  quotients and `d + n` the last remainder; a divisor 0 gives `0xffffffff` for both. The 21
  cases (three input sets, counts 1 to 16, other destinations) in which no iteration reads a
  register an earlier one writes match this exactly. In the nine in which one does, every such
  read saw what an iteration ten or more before it wrote, and the register's old value where the
  writer ran nine or fewer iterations before (probes `usse-idiv-enc47-grid`,
  `usse-idiv-enc47-repeat-sets`, E367).

*Later probes (2026-11-08).* **`ima32` is the low 32 bits of `a × b + c`**, `.u` and `.s` alike,
with the immediates, the constants, `.neg` on sources 2 and 3, a subtract in one instruction and the
one-bit `cie`, and **`imae`'s carry out and carry in** write and take exactly 0 or 1, in one
instruction or two, chained to a 64-bit accumulate **[HW]** (E469, E470, E471). In a second batch,
with the same forms: **`ima32.u d, iK, a, b, c` writes the high 32 bits of the product with the
addend to `iK`** (15 of 15 cases of five `.u` register triples, E493, then 282 of 282 jobs of
generic register triples, 200 of them random, and the signed form in 282 of 282, E525, E526; the
probe table's model had the `i` registers keep their values, 0 of 15), a borrow follows in one more
instruction, `ima32.u r10, iK, r2, c56, r1` leaving `a - b` and `b - [a < b]` (75 of 75, E501) and
an unsigned compare of two registers being that and `xor.testtanz.chan0 !c0, p0, r2, i0` (64 of 64
pairs of the eight values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000, 0x80000001 and 0xffffffff,
E501; 252 of 252 seeded pairs and 48 of 48 with each of 0, 1 and 3 `nop`s between, E527), and a
signed compare from `ima32.s` and `xor.testtanz.chan0 !c0, p0, i0, #0` (164 of 164 pairs, E528); 17
more seven-bit immediates, `.neg` on `.s` immediates and constants, and a dependent reader after 0
to 6 and 8 `nop`s are exact (E495); the operand banks `pa`, `sa`, `o`, `g` and `i` are accepted and
read 0 where `mov` reads 0 (31 of 40 cases), and the six r-bank destinations run, r0, r9, r18, r28,
r30 and r31, `sa0`, `o0`, `i1` and `i2` take the result while `pa0` does not (E496); `imae coe, iN`
writes the iN named for `i0` and `i1` (E494).

**Undecided:** `imae` with both `.rsN` and saturation, or with a repeat, a `u16`/`z16` source or a
`.rsN` shift and its carries; `ima32` with `cie` or `.neg` and the extra operand, or with immediates
and constants other than c56 there, its dual-issue secondary form, its selector 3 and what bit 46 of
its word does to `r14` (Q135, Q127); when a repeated `idiv`'s result becomes visible to its own
later iterations.
