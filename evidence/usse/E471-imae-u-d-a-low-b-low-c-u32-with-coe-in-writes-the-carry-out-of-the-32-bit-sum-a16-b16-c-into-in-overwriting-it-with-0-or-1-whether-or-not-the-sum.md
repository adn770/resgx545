+++
id = "E471"
claim = "imae.u d, a.low, b.low, c, u32 with coe, iN writes the carry out of the 32-bit sum a16 * b16 + c into iN, overwriting it with 0 or 1 whether or not the sum carried (14 of 14 cases with iN preset 0x55; writing only on a carry fits 7, ORing it in 0); cie, iN adds bit 0 of iN only to that sum (10 of 10; iN = 2 adds nothing, iN = 0xffff and 0xffffffff add 1); coe and cie together on one iN assemble and write the carry of the whole sum including the added bit (14 of 14, the sum a16 * b16 + c + bit 0 of iN); two imae chained through i0, a coe then a cie, are an exact 64-bit accumulate of a16 * b16 products (10 of 10); and imae.s multiplies the 16-bit halves as signed values and adds c as an unsigned 32-bit number, the carry being that add's (6 of 6 cases, no model beforehand)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/imae-neg.toml (dump.s; i0 set by mov i0, r4, read back by mov r11, i0), 5 probes and 54 cases; two runs of each probe, the first by probe.py over ima32-neg.toml (outside the data), the second by the campaign runner (the dataset): the same readback in all 54 cases. The signed carry cases and the coe-cie sums were checked by a script against the formulas above after the run (the table's own model for coe-cie added all of iN and was wrong for the cases where iN = 2)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-imae-neg"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

**What runs.** `imae.u r10, r1.low, r2.low, r3, u32, coe, i0` then `mov r11, i0` over 14 triples
(0 + 0 + c, 0xffff * 0xffff with c below and above the carry point, c = 0xffffffff with and
without a product, sums of exactly 2^32); `cie, i0` over 10 cases with i0 from 0 to
0xffffffff; both flags on i0 over 14; two chained `imae` (`imae.u r10, r1.low, r2.low, r3, coe,
i0` then `imae.u r11, r6.low, r6.low, r4, cie, i0`, lo and hi as the accumulator) over 10; `imae.s`
with `coe` over 6.

**Results (campaign run).**

- coe: r10 = the low 32 bits and iN = 0 or 1 in 14 of 14, including the cases with no carry (iN
  preset 0x55 reads 0, not 0x55).
- cie: the sum gains iN & 1: i0 = 2 adds 0, i0 = 0xffff adds 1, i0 = 0xffffffff adds 1 (imae 10 of
  10, and `ima32.u ... cie, i0` the same, E470).
- coe and cie on one iN: (r10, iN) = the low 32 bits and the carry of `a16 * b16 + c + (iN & 1)` in
  14 of 14. Case: a = b = 1, c = 0xfffffffe, iN = 1: r10 = 0, iN = 1 (the carry-in made it carry);
  iN = 2: r10 = 0xffffffff, iN = 0.
- chain: lo' = lo + a16 * b16 (r10) and hi' = hi + carry (r11) equal the 64-bit sum in 10 of 10,
  among them lo = 0xffffffff, hi = 0xffffffff giving a carry that wraps hi to 0, and hi = 0x7fffffff
  becoming 0x80000000.
- imae.s with coe: (a16 = 0xffff = -1, b16 = 0xffff, c = 0xfffffff0) gives r10 = 0xfffffff1 and iN =
  0, so the product -1 * -1 is read as +1; (0x8000, 0x8000, 0xffffffff) gives 0x3fffffff with a
  carry (the product is +2^30); (0xffff, 1, 0) gives r10 = 0xffffffff and iN = 0, the product -1
  extended to 32 bits. All six cases are `sext16(a) * sext16(b) + c` as an unsigned 32-bit add, with
  its carry.

**What it shows.** [HW] `imae` has a one-bit carry in and a one-bit carry out, written to and read
from an `iN` register, and the pair chains: a 64-bit accumulate of 16 x 16 products is two
instructions. That is not a 32-bit add of two arbitrary registers, because the only 32-bit input
of `imae` is `c` and the other sources are 16 bits: the 32-bit add and subtract are `ima32`
(E469, E470) and the borrow of a 32-bit compare is the software formula of E472.

**What it does not show.** The `coe` of `imae` with other `u16`/`z16` source types, with a repeat,
or with a `.rsN` shift; `imae.s` with a negative `c` other than the three cases; the `iN` registers
other than i0 (every case used i0). `cie` ran iN = 0, 1, 2, 0xffff and 0xffffffff (and 0, 1, 2 in
the coe-cie probe): among the readings "adds iN & mask" only the mask 1 fits, but an iN with bit 0
clear and a high bit set (0x10000, 0x80000000) was not run. The `.s` formula was fitted after the
six cases, so it is a fit to six cases and not a prediction that held. [infer] `imae` has no
negated source: the assembler refuses it (tools/usse-asm at 8665d77), no raw word was run.

**Correction, 2026-11-08 (11.25).** The measurements above are unchanged; two statements under 'What
it does not show' are answered by E494: `imae cie, iN` ran with i0 and i1 and the values 0x10000,
0x80000000, 0x10001 and 1 (8 of 8: bit 0 only, so an iN with bit 0 clear and a high bit set adds
nothing), and `imae coe, iN` ran with i0 and i1 over four triples, one of which carries (8 of 8: the
iN named gets the carry and the others keep their presets). `ima32 cie, iN` with iN other than i0
and with the high-bit values also ran (24 of 24). The `i2` forms of `imae` are still refused by the
assembler (no raw word run), and the `.s` formula is still a fit to six cases.
