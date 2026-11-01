+++
id = "E521"
claim = "iaddu32 writes the low 16 bits of source 1, zero-extended, plus source 2, mod 2^32: its source 1 is zero-extended in the value it writes, in 16 distinct pairs of two datasets run before 11.28, seven of which a sign extension would write otherwise (bit 15 of the low half of r1 set): (r1, r2) = (0x8000, 0x8000) writes 0x10000 (a sign extension writes 0), (0xffff, 1) 0x10000, (0xffffffff, 1) 0x10000, (0x7fffffff, 1) 0x10000, (0xffffffff, 2) 0x10001, (0x7c23a2bd, 0x47b003f0) 0x47b0a6ad and (0xb99ede85, 0x87261f80) 0x8726fe05, and the nine others agree with both; the zero extension fits 16 of 16 and the sign extension the nine with bit 15 of the low half clear"
unit = "usse"
method = "read from the readbacks of two datasets that were run before 11.28, no new run: usse/decoder-vectors/usse-decoder-vectors-iaddu32-taz (14 cases, the value in r10 and in scratch dword 0) and usse/integer/usse-integer-iaddu32-value (4 cases, o0, two of them repeating pairs of the first), found while replaying the vectors on sgx-sim for phase 11.28 (the simulator already wrote the zero-extended value, which no record had checked); the pairs were counted from the converted vector files (16 distinct pairs in the 18 cases)"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-decoder-vectors", "usse-integer"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** `iaddu32.testtaz.chan0 r10, p0, r1, r2` (the value in r10, o0 or scratch dword 0).
Nothing was run for this record.

**Results.** The value is (r1 & 0xffff) + r2 mod 2^32 in every case. The nine pairs that a sign
extension writes the same: (0, 0) 0, (1, 1) 2, (0x80000000, 0xffffffff) 0xffffffff, (0x10000,
0xffffffff) 0xffffffff, (2, 0x7fff) 0x8001, (0x80000000, 0x80000000) 0x80000000, (0x12345678,
0x11111111) 0x11116789, (0xa9fe10c8, 0xdab59ba2) 0xdab5ac6a, (0x50cb1943, 0x83bab235) 0x83bacb78.
The seven that it writes otherwise (sign extension in brackets): (0x8000, 0x8000) 0x10000 (0),
(0xffff, 1) 0x10000 (0), (0xffffffff, 1) 0x10000 (0), (0x7fffffff, 1) 0x10000 (0), (0xffffffff, 2)
0x10001 (1), (0x7c23a2bd, 0x47b003f0) 0x47b0a6ad (0x47afa6ad), (0xb99ede85, 0x87261f80) 0x8726fe05
(0x8725fe05).

**What it shows.** [HW] The value iaddu32 writes zero-extends source 1, where iadd32 sign-extends it
(0x337a70a2 + 0xb01b9c1d = 0xb01c0cbf is iadd32's). This answers the extension of Q126 for the value
of `iaddu32`: E498 asked for "a different observable, the value iaddu32 writes", and these readbacks
were already in the data.

**What it does not show.** Whether the test reads the same extension as the value (no pair of E498
separates it); `iaddu32` with a repeat, with an immediate or a constant in source 2, or with other
destinations. The pairs come from two probes written before the question was asked, not from a table
for it.
