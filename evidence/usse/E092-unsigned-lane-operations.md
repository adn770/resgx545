+++
id = "E092"
claim = "The test group's umul8, uadd8, usub8, uadd16 and umul16 work on each byte or 16-bit lane on its own, unsigned and wrapping; .sat clamps the unsigned byte results to 255 (the Rogue instruction set reference's UADD8, UMUL8, UADD16 and UMUL16 lane by lane); iadd8.sat writes the wrapped bytes, not a signed clamp; imul8, iadd16 and imul16 give the unsigned results"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/lane-integer.toml, probe rogue-int, a fill whose pixel program runs one test-group operation as `OP.testtaz.chan0 r10, p0, r1, r2` and stores r10 and the marks of the zero test; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-lane-integer"]
terms = []
+++

**What runs.** Eleven cases, each `OP.testtaz.chan0 r10, p0, r1, r2` followed by
`p0 mov r16, #1` and `!p0 mov r17, #1` (r16 and r17 start at 0). For the byte operations
r1 = 0x80ff7f02 and r2 = 0x80020203, for the 16-bit ones r1 = 0xffff8000 and r2 = 0x00028000,
so that every lane gives a carry, a product past the lane or a value with its top bit set.

**Results.** r10 (byte 3 down to byte 0, or high and low halves):

| operation | r10 | per lane |
|---|---|---|
| umul8 | 0x00fefe06 | 80*80 -> 00, ff*02 -> fe, 7f*02 -> fe, 02*03 -> 06 |
| umul8.sat | 0xfffffe06 | the same, 0x4000 and 0x1fe clamped to ff |
| uadd8 | 0x00018105 | 80+80 -> 00, ff+02 -> 01, 7f+02 -> 81, 02+03 -> 05 |
| uadd8.sat | 0xffff8105 | the same, 0x100 and 0x101 clamped to ff |
| usub8 | 0x00fd7dff | 80-80 -> 00, ff-02 -> fd, 7f-02 -> 7d, 02-03 -> ff |
| imul8 | 0x00fefe06 | the low byte of each product, as umul8 |
| iadd8.sat | 0x00018105 | as uadd8: 7f+02 -> 81, 80+80 -> 00, no signed clamp |
| uadd16, iadd16 | 0x00010000 | ffff+0002 -> 0001, 8000+8000 -> 0000 |
| umul16, imul16 | 0xfffe0000 | ffff*0002 -> fffe, 8000*8000 -> 0000 |

In all eleven cases r16 = 0 and r17 = 1: the chan0 zero test was false, as byte 0's result
(5, 6, 0xff or 0x06) predicts. Lanes never carry into each other.

**Reading [infer].** The unsigned operations are lane-wise unsigned arithmetic that wraps, and
`.sat` clamps an unsigned byte at 255, which is what the public Rogue instruction set reference
states for UADD8 and UMUL8 (saturate 0..255) and for UADD16 and UMUL16. The signed-named
operations give the unsigned results here.

**Not shown.** One input pair per operation; the signed ranges of imul8 and iadd8 are probed
only at these values, and 16-bit .sat is not run. One run.
