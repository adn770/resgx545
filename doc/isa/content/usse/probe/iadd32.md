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
**[HW]** (E472, probes `usse-compare32x-iadd32-ovf-testnat`, `usse-compare32x-iadd32-ovf-testpat`,
`usse-compare32x-iaddu32-carry-testtanz`): `iadd32`'s `n` and `p` read the sign of `sext16(r1) + r2`
with `r2` signed, so r1 = 0x7fff with r2 = 0x7fffffff leaves `n` clear and `p` set (12 pairs, of
which 5 overflow the signed 32-bit sum: the true sum fits 12 of 12, the wrapped one 7), and the
nonzero test of `iaddu32` sees the carry out of bit 31, so r1 = 1 with r2 = 0xffffffff is nonzero (8
of 8, the wrapped sum fits 5 or 7; one pair, (1, 0xffffffff), decides it for both extensions of r1,
the two others with a wrapped sum of zero only for zero-extension). The probe table's model tested
the wrapped sum. Whether `z` of an overflowed `iadd32` sum or `iaddu32`'s `p` and `z` do the same is
not shown. With source 1 = `#0` a test through source 2 reads that register's 32 bits exactly: `n`,
`p`, `z` and `nz` of `iadd32` (8 of 8 values each), `nz` of `iaddu32` (8 of 8) and its `n`, never
true (8 of 8).

**Undecided:** whether `iaddu32` zero- or sign-extends a source 1 above 0x7fff (the pairs that would
tell read nonzero under both), `testtaz` of an overflowed `iadd32` sum, which no pair run
separates (`testpat` of it is separated), and `testtaz` and `testpat` of `iaddu32` (Q126).
