+++
id = "E494"
claim = "The carry in of ima32 and imae adds bit 0 of iN for every iN and value that ran: ima32.u d, a, b, c, cie, iK adds bit 0 of iK for K = 0, 1 and 2 and the eight values 0x10000, 0x80000000, 0xfffffffe, 0x10001, 0x80000001, 2, 0x55555554 and 0xaaaaaaab (24 of 24 cases, 3 * 7 + 100 with the other two i registers holding 1; adding all of iK fits 0 of 24 and its low 16 bits 12 of 24), imae.u cie, iK for K = 0 and 1 and the values 0x10000, 0x80000000, 0x10001 and 1 does the same (8 of 8), and imae coe, iK writes the carry of the sum to the iK named and leaves the other i registers at their presets 0x55, 0x66 and 0x77 (8 of 8: for K = 0 and 1 and the four triples (2, 3, 0xfffffffe), (2, 3, 0xfffffff0), (0xffff, 0xffff, 2) and (1, 1, 1), of which only the first carries, so 1 carry and 3 sums without for each K)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/ima32-forms.toml probes cie-in (24 cases), imae-cie-in (8) and imae-coe-in (8) (dump.s); the campaign runner once for the table, no probe.py first run. The draft of this record counted two carries and two sums without per K in the coe probe; recounted from the readbacks, one of the four triples carries"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-ima32-forms"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

**What runs.** `mov i0, r5; mov i1, r6; mov i2, r7` presets the i registers, then `ima32.u r10, r1,
r2, r3, cie, iK` with 3 * 7 + 100 and the K-th register set to each value while the other two hold 1
(a wrong register read adds 1 where the right one adds 0 or 1); `imae.u r10, r1.low, r2.low, r3,
u32, cie, iK` for K = 0 and 1 over the four values; and `imae.u ..., coe, iK` over the four triples
(i0-i2 preset 0x55, 0x66, 0x77, then read back). The assembler refuses `imae ... cie, i2` and `coe,
i2` (and `coe, cie` with i2).

**Results.** ima32: r10 = 121 + bit 0 of iK in 24 of 24 (0x79 for the values with bit 0 clear, 0x7a
for 0x10001, 0x80000001 and 0xaaaaaaab). imae cie: 0x79 for 0x10000 and 0x80000000 and 0x7a for
0x10001 and 1, for both K, 8 of 8. imae coe: iK = 1 for (2, 3, 0xfffffffe) (r10 = 4) and 0 for the
other three triples (r10 = 0xfffffff6, 0xfffe0003 and 2), the other i registers as preset, for both
K (8 of 8); the carry of E471 is therefore written to the iN named, and only to it.

**What it shows.** [HW] The bit-0 reading of E470 and E471 holds for iN with bit 0 clear and a high
bit set (0x10000, 0x80000000, 0xfffffffe, 0x55555554), for iN other than i0 (i1 and i2 for `ima32`,
i1 for `imae`), and for `imae`; `coe, iN` addresses the iN named for K = 0 and 1. The values are the
eight listed (the table did not run others), so 'bit 0 only' is shown for them. [infer] That `imae`
has no i2 form is the assembler's refusal (no raw word run), and `ima32 cie` together with the extra
operand of E493 was not run.

**What it does not show.** Values of iN other than those listed, a carry in on `ima32.s`, `imae`
with a repeat, `u16` or `z16` sources or `.rsN`, `imae coe` with a sum that carries more than the
one triple (one carrying case per K). Narrows Q127: `cie` with iN of a clear bit 0 and a high bit
set and iN other than i0 are answered for `ima32` and `imae`; the rest stays open.
