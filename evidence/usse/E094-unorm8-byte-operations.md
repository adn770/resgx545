+++
id = "E094"
claim = "The test group's unorm8 operations clamp per byte: fpadd8 is x + y up to 255, fpsub8 x - y down to 0, and fpmul8 round(x * y / 255) exactly rounded, in all 24 cases (96 byte pairs); the zero test sees each byte's unclamped result: an fpsub8 whose byte 0 clamps to 0 without being 0 does not test as zero"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/unorm8.toml, probes mul and add-sub-mul, a fill whose pixel program runs `OP.testtaz.chan0 r10, p0, r1, r2` on four byte pairs and marks the zero test in r16 and r17; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-unorm8"]
terms = []
+++

**What runs.** 24 cases of four bytes each: 16 of fpmul8 (including pairs that the usual
approximate unorm8 multiplies round differently, such as 250 * 2, 254 * 254 and 1 * 128, and
asymmetric pairs), 4 of fpsub8 and 4 of fpadd8. Each runs
`OP.testtaz.chan0 r10, p0, r1, r2` and sets r16 = 1 if the test is true, r17 = 1 if not.

**Results.**

- fpmul8: all 64 byte pairs of the 16 cases equal round(x * y / 255) (a half rounds up).
- fpsub8: every byte is x - y clamped at 0; fpadd8: every byte is x + y clamped at 255.
- Zero test: the chan0 test of all 24 cases agrees with the unclamped byte 0 of x - y or x + y
  (or the product) being zero. In one fpsub8 case byte 0 clamps to 0 but x - y is not 0, and p0
  is clear: the test saw the unclamped result.

**Not shown.** The random pairs, only 24 cases, one run; the other approximations of the
multiply are not tried.
