+++
id = "E469"
claim = "ima32.u and ima32.s compute the low 32 bits of a * b + c on full 32-bit operands, and every route to its three sources agrees: 826 of 826 cases fit, among them the 343 combinations of the corner values 0, 1, 0xffff, 0x10000, 0x7fffffff, 0x80000000 and 0xffffffff as a, b and c (.u), 147 of them signed (.s gives the same bits as .u, with no saturation), 22 sums that land just below, on and just above 2^16 and 2^32, the add lowering ima32.u d, a, #1, c (49 cases, a + c mod 2^32) and immediates 0, 2, 3 and 127 in source 2 (56), immediates 0, 1, 2 and 127 in source 3 (45) and in both (21), c0 as source 3, the mul lowering (49, the low 32 bits of a * b), and the constants c3, c13, c45, c56 and c60 as source 3 (40) and c0, c3, c13 and c60 as source 2 (40) read as the integers of E085"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/ima32-full.toml (dump.s: r1-r3 preset, ima32 under test, r10 stored to scratch and shown as the pixel), 24 probes, 826 cases; each probe ran twice, the first by probe.py over the whole table (outside the data, not kept with it), the second by the campaign runner, probe by probe (the dataset): the same verdict in every probe and the same readback in all 826 cases; the three short probes (carry, bimm1, c0-mul, 120 cases) also ran once alone before everything else, with the same bits"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-ima32-full"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPCONSTANT"]
+++

**What runs.** `ima32.u r10, r1, r2, r3` (or `.s`, or with an immediate or a constant-bank register
in source 2 or source 3) with r1, r2 and r3 set by moves, then r10 stored to scratch. Every probe
lists, for each case, the low 32 bits of `a * b + c` as the model and competing readings that the
case values separate: the 16-bit halves of the operands combined as `imae` does, two 16-bit lanes
as `ima16` does, saturation, and "the constant bank reads 0 in ima32". The dataset's raw.txt of a
probe has one `probe-case` line per case (826 in all).

**Results (campaign run, 826 of 826).**

| probe | cases | what | fits the model |
|---|---|---|---|
| u-cube | 343 | 7 x 7 x 7 corner values, `.u` | 343 |
| s-cube | 147 | a, b over the 7 corners and c in 0, 1, 0xffffffff, `.s` | 147 |
| carry | 22 | a * b + c just below, on and above 2^16 and 2^32 | 22 |
| bimm1 | 49 | `ima32.u d, a, #1, c` (the add lowering) | 49 |
| bimm0, bimm2, bimm3, bimm127 | 14 each | `#0`, `#2`, `#3`, `#127` in source 2 | 56 |
| bimm1-s | 14 | `ima32.s d, a, #1, c` | 14 |
| cimm0, cimm1, cimm2, cimm127 | 8, 21, 8, 8 | an immediate in source 3 | 45 |
| bothimm | 21 | immediates in sources 2 and 3 | 21 |
| c0-mul | 49 | `ima32.u d, a, b, c0` (the mul lowering) | 49 |
| c3, c13, c45, c56, c60 -src3 | 8 each | constant as the addend | 40 |
| c0, c3, c13, c60 -src2 | 10 each | constant as the multiplier | 40 |

Some of the values: 0xffffffff * 0xffffffff = 0x00000001, 0xffff * 0xffffffff = 0xffff0001,
0x7fffffff * 0xffffffff = 0x80000001, 0x80000000 * 0xffffffff = 0x80000000, 0x10000 * 0x10000 =
0, 0x10000 * 0xffff = 0xffff0000: the product is not cut to 16 bits and not saturated, and the
carries across bit 16 and out of bit 31 (the part above bit 31 is dropped) are exact. `.s` and
`.u` differ in no case. c0 reads 0 as source 3 and c3 = 0x3f800000, c13 = 0x44800000, c45 =
0x3c003c00, c56 = 0xffffffff and c60 = 0x7fff7fff read as those integers (the constants of E085 are
the same through the integer multiplier as through a mov or a store).

**What it shows.** [HW] `ima32` is a full 32-bit multiply-add whose result is the low 32 bits,
`add` is `ima32.u d, a, #1, c` and `mul` is `ima32.u d, a, b, c0`, with the immediate of source 2 or
3 and the constant bank usable as sources. The `[infer]` of usse_isa.md 6.5 for the formula can go.

**What it does not show.** Which operands ran. Immediates: 0, 1, 2, 3 and 127 in source 2, and 0, 1,
2 and 127 in source 3; none between 4 and 126, so that every 7-bit immediate reads as itself is
[infer] from five values. Constants: c0, c3, c13 and c60 in source 2, and c0, c3, c13, c45, c56 and
c60 in source 3 (c45 and c56 only as source 3). Every register operand was a temporary (r1-r3, in
the r bank) and the destination was r10 throughout: `pa`, `sa`, `o`, `i` and `g` operands and other
destinations were not run (Q127). The `i` register after the destination is not run, nor `ima32` as
a dual-issue secondary (two 16-bit lanes). One instance per pixel only; the pixel and the scratch
word agreed in all 826 cases.

[infer] The refusals are the assembler's, not hardware runs: no raw word was run for any of them
(E474 ran raw words for the rotated immediate only), so each is a limit of tools/usse-asm at 8665d77
(unchanged since 1c90a19), not shown to be a limit of the hardware. Of the 61 one-line forms tried
for E469 to E476, 28 are refused: `ima32.u` with an immediate of 128 or 0xffffffff in source 2 or in
source 3, an immediate or a constant in source 1, `c64` in source 3, `.neg` on source 1,
`ima32 ... coe, i0`, and `ima32.u.testtaz`; `imae` with `coe` and `cie` on two different iN
(`coe, i1, cie, i0`) and with `.neg` on source 3; `iadd32` and `iaddu32` with no test; `xor.testtaz`
with `#128`; `and.testtanz` with `~#7` and with `~r2` and `xor.testtaz` with `~#7`; `or` with
`#0xffffffff`, `#0x00010001`, `#0x55555555` and `#0x12345678` and `and` with `~#0x00010001`;
`ba.savelink.nosched`; `mov pclink, #5` and `mov r10, #pclink`; `iaddu32 r5, #3, r5`; and `br` to
a label.

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged. Several of the forms
listed under 'What it does not show' ran in 11.25 with the sgxfive-test of 11.24 (E495, E496, E493):
the seven-bit immediates 4, 5, 6, 7, 8, 15, 16, 17, 31, 32, 33, 63, 64, 65, 100, 125 and 126 in
source 2 and in source 3 (68 of 68), so that 22 of the 128 values have run in source 2 and 21 in
source 3 (3 was not run there), and not 5; the operands pa0, pa1, pa4, sa0, sa1, sa4, o0, o1, o3,
i0, i1 and i2 in source 1 and pa0, pa1, pa4, sa0, sa1, sa4, o0, o1, g0, g1, g7, i0, i1 and i2 in
sources 2 and 3, accepted and read 0 where `mov` reads 0 (40 of 40, 31 of them reading 0 by both
routes, so only i0 to i2 show a nonzero value); the destinations r0, r9, r18, r28, r30, r31 (the six
r-bank destinations run), sa0, o0, i1 and i2 (written) and pa0 (not written); and the optional `i`
register after the destination, `ima32.u d, iK, a, b, c`, which writes the high 32 bits of a * b + c
to iK. So 'every 7-bit immediate reads as itself' is shown for 22 values and 'pa, sa, o, i and g
operands and other destinations were not run' no longer holds. Of the refusals listed, `ima32 ...
coe, i0` is still refused by the assembler, and the carry out that E470 looked for is the high word
through the extra operand (E493, E501). A raw word was run for that field and for the bits 46, 45,
44 and 35 of the ima32 word (E493), and for `~` in a test (E499, with E473's correction); no raw
word was run for the other refusals listed, which stay the assembler's.
