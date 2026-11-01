+++
id = "E075"
claim = "Our own pixel programs measured on the hardware what USSE instructions do beyond their text, in 16 tables (169 probes, 2199 cases): of the 169 probes, the table's own model fits every case of 119, 2 do not fit (internal-register bank 7 and efo.gpiext on its own instance) and 48 are recorded explorations; the settled ones cover tests, 16-bit lanes, shifts, index registers, repeats, float rounding, dot products, internal registers, pack and unpack, colour operations, dual issue and efo"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/branch.toml, colour-ops, dot-products, dual-issue, efo, flags, fmad, fmad16, gradients, indexing, integer, internal-registers, moe, pack, predicates and test-channels, client fills whose pixel program runs the instruction under test on preset inputs and writes the result to the pixel and the scratch buffer; one run of each table"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-branch", "usse-colour-ops", "usse-dot-products", "usse-dual-issue", "usse-efo", "usse-flags", "usse-fmad", "usse-fmad16", "usse-gradients", "usse-indexing", "usse-integer", "usse-internal-registers", "usse-moe", "usse-pack", "usse-predicates", "usse-test-channels"]
terms = ["REGTYPE.INDEX", "REGTYPE.FPINTERNAL", "FDUAL.FDDP_IREG_DEST_NUM"]
+++

**What runs.** Each case is a fill (64x32, 2048 instances) whose pixel program, assembled from
our source, runs one instruction on preset registers and stores the result registers to
scratch and the pixel. A probe is a group of cases with one question; "settled" below means
the table's own model of the instruction matched every case of the probe, "recorded" means the
probe only recorded values.

**Results.** Probes, settled, recorded and cases per table:

| table | probes | settled | recorded | cases |
|---|---|---|---|---|
| colour-ops | 12 | 12 | 0 | 458 |
| dot-products | 8 | 8 | 0 | 100 |
| dual-issue | 5 | 4 | 1 | 95 |
| efo | 3 | 3 | 0 | 69 |
| flags | 1 | 1 | 0 | 7 |
| fmad | 5 | 5 | 0 | 27 |
| fmad16 | 4 | 4 | 0 | 67 |
| gradients | 2 | 2 | 0 | 18 |
| indexing | 10 | 7 | 3 | 56 |
| integer | 30 | 29 | 1 | 169 |
| pack | 34 | 33 | 1 | 291 |
| predicates | 1 | 1 | 0 | 6 |
| test-channels | 5 | 5 | 0 | 459 |
| internal-registers | 11 | 3 (2 do not fit) | 6 | 77 |
| branch | 13 | 1 | 12 | 28 |
| moe | 25 | 1 | 24 | 272 |

What the settled probes found:

- Tests and lanes: sign test n is the sign bit, p is >= 0; iadd32 and iaddu32 add src1's low
  16 bits (sign- or zero-extended) to the 32-bit src2; chan1 to chan3 clear the predicate on
  32-bit and 16-bit operations alike (test-channels, 459 cases: one result per channel, bytes
  for 8-bit operations, halves as channels 0 and 2 for 16-bit ones, the value as channel 0 for
  32-bit and float).
- 16-bit operations: isub16, usub16 and ima16 work on both lanes, wrapping, with an immediate
  in both lanes; ima8 is per byte, wrapping, saturating with .sat.
- Shifts by a register or immediate amount of 32 and over: shl and shr give 0, asr the sign,
  rol takes the amount mod 32.
- Index registers: r[il + #n] and sa[il + #n] address the register i.l + n with bits 10 and up
  of i.l ignored (sa: bits 16 and over); i.lh takes the low half for i.l and the high for i.h;
  ldr's index is masked to 14 bits.
- Floats: fmad rounds the product before adding (not fused), to nearest even, and flushes
  denormals to a zero of their sign; invalid results are NaN 0x7fffffff (0x7fc00000 for fdp);
  fmad16 is lane-wise with one rounding; fdp.repeatN writes the N-term dot product to
  d + N - 1 only, each product and sum rounded in order; fddp writes s0.s1 to d and s0.s2 to
  iN; fds gradients are coarse (one difference per quad).
- Internal registers: i0 to i2 are per instance and kept from task to task; i3 reads the next
  instance's i0 in the quad and drops writes; efo's multipliers read i2 for i0 and i0 for i1
  across a quad.
- Pack and unpack (34 probes): x * 255 to nearest even for u8, x * 127 and 32767 for s8 and
  s16, x * 65535 for u16, c10 lanes at bits 0, 10, 20 clamped to +-2.0, f16 toward zero with
  denormals kept; unpack divides by the same scales correctly rounded; c10 to 16-bit puts lane 0
  bits 4, 6, 8 into bits 15, 1-14, 0.
- Colour operations (458 cases): channels read as x / 255, products summed exactly, divided
  once, rounded and saturated; min and max of the sources; c10 operands are signed 10-bit lanes
  clamped to +-510; sop2wm mask bit N writes byte N.
- Dual issue: both operations read before either writes, the secondary wins a shared
  destination, a repeat runs both twice; ima32 as a secondary computes two 16-bit lanes.
- efo: every product and sum rounded to nearest even, denormals flushed, d = i0 or i1 (old
  values), a0 or a1, i0 and i1 written after.
- branch: br #1 is the next instruction (from the br itself); predicated br with disagreeing
  instances is E089, bexception is E100 and E108.

Two probes do not fit the table's model: internal-registers bank7 (reading i3 to i15 as a
register bank gives values that name other instances, with one pixel that varies between
runs) and efo-gpiext (efo.gpiext on its own instance); the quad-wide efo-gpiext case is settled.

**Not shown.** The moe (E087 and E097 give what its probes show), branch bexception and
indexing width probes are recorded explorations. The video filters are not in this record
(E078 to E080). One run of each table.
