+++
id = "E470"
claim = "A 32-bit subtract is one ima32: ima32.u d, b, c56, a computes a - b mod 2^32 because c56-c59 read as 0xffffffff through the integer multiplier (80 of 80 cases through c56, 6 of 6 through each of c57 .u, c58 .u, c59 .u and c59 .s, and 8 of 8 with an all-ones register); a .neg on source 2 (enc[40]) or source 3 (enc[39]) of ima32, negates that source in two's complement, -(a * b) + c and a * b - c (90 of 90 cases in nine spellings: registers in .u and .s, and in .u an immediate and a constant; of the three other readings, complement fits 0 or 1 of 10 and ignored 0 to 4 in every probe, and swapped 1 or 2 of 10 in the eight probes with one negated source, 80 of the 90 cases, where it is told apart: the probe with both sources negated cannot tell it); a chain of four dependent ima32 is exact with no gap between them (10 of 10); and the carry-in of ima32, cie, iN, adds bit 0 of iN only (10 of 10; adding all of iN fits 4 of 10, adding its low 16 bits 4)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/ima32-neg.toml (dump.s), 18 probes and 230 cases (the imae probes of the same first table are E471); two runs of each probe, the first by probe.py over the table (outside the data, where usse-ima32-neg-sub-c56 and sub-reg ran first, alone, and fitted before compare32 ran) and the second by the campaign runner (the dataset): the same readback in all 230 cases"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-ima32-neg"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPCONSTANT", "REGTYPE.FPINTERNAL"]
+++

**What runs.** `ima32.u r10, r2, c56, r1` (r10 = r2 * c56 + r1, c56 = 0xffffffff = -1, so a - b with
a = r1 and b = r2) over 80 pairs of corner values and others, and the same through c57, c58, c59
(`.u`, and c59 `.s`) over 6 pairs each, and with the all-ones in a register (8): the control that
tells "the constant bank reads 0 in ima32" (fits 8 of the 80) from the subtract. The `.neg` probes
run, on ten triples each, `ima32.{u,s} r10, r1, r2, r3.neg` and `r2.neg, r3` (four probes, `.u` and
`.s`, registers), and in `.u` only: both negated, `#1` in source 2 with `r3.neg`, `#1.neg` in
source 3, `c56.neg` in source 3 and in source 2 (five probes). Every operand is a temporary
(r1-r3) or c56 or `#1`, and iN is i0 only. `usse-ima32-neg-cie-width`
presets i0 with `mov i0, r4` (0, 1, 2, 0xffff, 0xffffffff) and runs `ima32.u r10, r1, r2, r3, cie,
i0`; `usse-ima32-neg-chain` runs `t = a - b; u = t - c; v = u + b; w = v + c` as four ima32 in a
row.

**Results (campaign run).**

| probe | cases | model fits | the other readings fit |
|---|---|---|---|
| sub-c56 | 80 | 80 (a - b mod 2^32) | "reads 0": 8; "reads 0xffff": 24 |
| sub-c57u, c58u, c59u, c59s | 6 each | 24 | - |
| sub-reg | 8 | 8 | - |
| c56-src3 | 8 | 8 (a * b - 1) | - |
| nine .neg probes | 10 each | 90 | complement 0 to 1, ignored 0 to 4, swapped 1 to 2 of 10 (10 of 10 in the both-negated probe: no information) |
| cie-width | 10 | 4 (adds all of i0) | bit 0 only: 10; low 16 bits: 4 |
| chain | 10 | 10 | - |

`ima32.u d, a, #1, b.neg` is `a - b` as well (the `#1`-in-source-2, `r3.neg` probe, 10 of 10), so
the subtract has two spellings, one constant-bank read and one `.neg`.

**What it shows.** [HW] The cheapest exact 32-bit subtract is one `ima32`: `ima32.u d, b, c56, a`
(or `ima32.u d, a, #1, b.neg`); no carry out of it is known (below). `.neg` on `ima32` exists on
sources 2 and 3 and is a plain negation; that source 1 has none rests on the assembler's refusal
[infer] (E469's list of refusals). The carry-in is one
bit, which is the shape of a carry flag written by `imae coe` (E471).

**What it does not show.** [infer] `ima32 ... coe` does not assemble, which is the assembler's
refusal and not a hardware result; no raw word with a carry-out bit was run, so whether `ima32` has
a carry out is not known, and the borrow is the software one of E472. `.neg` with the `.s` type was
run on sources 2 and 3 of registers only (the `.s` probes); the constant and immediate spellings are
`.u`, and `.s` with `.neg` on an immediate or a constant was not run. The `cie` cases ran iN = 0, 1,
2, 0xffff and 0xffffffff in i0: among "adds iN & mask" the mask 1 is the only one that fits, but iN
with bit 0 clear and a high bit set (0x10000, 0x80000000) and an iN other than i0 were not run. None
of these cases is yet a vector. [infer] From reading `crates/sgx-sim/src/usse.rs` at 8665d77
(sgx-sim was not run): its `ima32` stops on a negated source and on the extra operand, and adds the
whole of `iN` for `cie`.

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged; three of the statements
under 'What it shows' and 'What it does not show' are corrected by 11.25 runs. (1) 'No carry out of
it is known' and 'the borrow is the software one of E472': `ima32` has a second result, the high 32
bits of a * b + c, through the extra operand (`ima32.u d, iK, a, b, c`, 15 of 15 cases of five
register triples, E493), and `ima32.u r10, iK, r2, c56, r1` leaves a - b mod 2^32 in r10 and b - [a
< b] in iK (75 of 75 cases over the pairs of the values 0, 1, 0xffff, 0x10000, 0x7fffffff,
0x80000000 and 0xffffffff for i0, and 13 pairs for i1 and i2), so that an unsigned compare is two
instructions on the 64 pairs of the eight values of E472 (E501); [infer] what the model called `coe`
is this operand for `a * 1 + c`. The six-instruction formula of E472 stays exact for the signed
compare. (2) '`.s` with `.neg` on an immediate or a constant was not run': E495 ran seven `.s` forms
(#1.neg and #5.neg in source 2, #1.neg and #127.neg in source 3, c56.neg and c3.neg in source 2,
c56.neg in source 3) and three `.u` ones, 80 of 80, each two's-complement negation. (3) 'iN with bit
0 clear and a high bit set and an iN other than i0 were not run': E494 ran i0, i1 and i2 with the
eight values 0x10000, 0x80000000, 0xfffffffe, 0x10001, 0x80000001, 2, 0x55555554 and 0xaaaaaaab (24
of 24, bit 0 only). The immediates, banks and destinations of E469's list ran in E495 and E496.
