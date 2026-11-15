<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
### The 32-bit adds `iadd32` and `iaddu32`

*Measured on the hardware (2026-10-22).* **`iadd32` and `iaddu32` are not full 32-bit adds**
**[HW]**: they add **source 1's low 16 bits**, sign-extended (`iadd32`) or zero-extended
(`iaddu32`), to the 32-bit source 2, modulo 2^32. `0x12345678 + 0x11111111` gives `0x11116789` and
`iadd32 0xffff + 1` gives 0, while `#1 + r` is the plain increment the firmware uses **[RE]** (an
`iaddu32` of the immediate 1 and a register). The test reads the sum: `z` and `n` as usual
for `iadd32` (but see the true sum below); `iaddu32` is unsigned, its `n` is never and its `p`
always true, also for `0x80000000`
(probes `usse-integer-iadd32-value`, `usse-integer-iaddu32-value`, `usse-integer-iaddu32-imm`,
`usse-integer-iadd32-src1-imm`, `usse-integer-iadd32-z`, `usse-integer-iadd32-n`,
`usse-integer-iadd32-p`, `usse-integer-iaddu32-tests`, `usse-integer-iaddu32-np`).

*Later probes (2026-11-08).* **A test reads the true 33-bit sum, not the wrapped 32-bit one**
**[HW]** (E472, E498; probes `usse-compare32x-iadd32-ovf-testnat`,
`usse-compare32x-iadd32-ovf-testpat`, `usse-compare32x-iaddu32-carry-testtanz`,
`usse-iaddu32-pairs-*`): `iadd32`'s `n` and `p` read the sign of `sext16(r1) + r2` with `r2` signed,
so r1 = 0x7fff with r2 = 0x7fffffff leaves `n` clear and `p` set (12 pairs in E472, of which 5
overflow the signed 32-bit sum: the true sum fits 12 of 12, the wrapped one 7; and 16 pairs in E498,
where the true sum fits 16 and the wrapped one 15, the one pair that separates them, (0xffff,
0x80000000), being one of the 5). `iadd32`'s `z` and `nz` read the zero of the same sum with r1
**sign-extended** (E498: 16 of 16, the pairs (0x8000, 0x8000) and (0xffff, 1) read zero, a
zero-extended r1 fits 11; with r2 signed the sum stays within +-2^32, so the true and the wrapped
sum agree in zero-ness on 16 of 16 pairs, and (1, 0xffffffff) reads zero). The nonzero test of
`iaddu32` sees the carry out of bit 31, so r1 = 1 with r2 = 0xffffffff is nonzero: E472's 8 pairs,
and E498's 16, where `testtaz` is true for (0, 0) only and `testtanz` for the other 15 (the sum with
its carry fits under either extension of r1, the wrapped sum under neither, and so does 'zero if
both operands are zero': the 16 pairs do not separate the two); `iaddu32`'s `p` is always true and
its `n` never (16 of 16 pairs each). The probe table's model tested the wrapped sum. With source 1 =
`#0` a test through source 2 reads that register's 32 bits exactly: `n`, `p`, `z` and `nz` of
`iadd32` (8 of 8 values each), `nz` of `iaddu32` (8 of 8) and its `n`, never true (8 of 8).

The value `iaddu32` writes zero-extends source 1 **[HW]** (E521, from the readbacks of two earlier
probes, `usse-decoder-vectors-iaddu32-taz` and `usse-integer-iaddu32-value`: 16 distinct pairs,
seven that a sign extension writes otherwise, such as (0x8000, 0x8000) giving 0x10000), with source
2 `#1`, `#127` and `c56` and into `i0` as well, and under a write mask `.xy` or `.xyzw`, which
repeats the test as on the other forms (E1061, held out). The combined conditions of the test
field and the `o` join read on these adds as on the bitwise group (E1062, held out).

With one writer quad alone writing `sa0` (a branch on `pa0`, E513's), the value read back is the
same
zero-extended sum, 8 of 8 dwords in 6 of 6 rows (E1106, held out; E1061's sa0 row, every instance
writing, mixed other pairs' values).

**Undecided:** which extension the test of `iaddu32` reads for a source 1 above 0x7fff: the sums
that would tell it are nonzero under both readings, so no test of those pairs settles it (Q126).
