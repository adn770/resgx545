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
- **`imae`**: `.usat`/`.ssat` saturate the 32-bit result (`.ssat` signed), `.rsN` shifts it right
  by N, source 2 typed `u16` is its half **sign**-extended and `z16` zero-extended, **`coe, iN`
  writes the carry out to `iN` and `cie, iN` adds bit 0 of `iN`** (probe `usse-integer-imae-modes`);
  `ima32`'s `cie, iN` adds bit 0 of `iN` only, as `imae`'s does (E470, E471: 10 of 10 each).

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
with the immediates, the constants, `.neg` on sources 2 and 3, a subtract in one instruction and
the one-bit `cie`, and **`imae`'s carry out and carry in** write and take exactly 0 or 1, in one
instruction or two, chained to a 64-bit accumulate **[HW]** (E469, E470, E471).

**Undecided:** `imae` with both `.rsN` and saturation, or with a repeat, a `u16`/`z16` source or a
`.rsN` shift and its carries; `ima32`'s extra `i` operand after the destination (Q127); when a
repeated `idiv`'s result becomes visible to its own later iterations.
