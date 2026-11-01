+++
id = "E216"
claim = "The triangle's stencil test (ISP word 2 compare, reference in ISP word 0 bits 7:0) tests against a stencil value held in register 0x04bc bits 7:0: with the job's value equal-0 draws the triangle and equal-1 does not, with 0x301 it is the other way round, and bit 8 clear (0x201) stops the value being used; bit 9 clear (0x101, 0x1) leaves the target with old pixels; register 0x04e8 at 0, 1 and 0x101 changes none of 9 runs' outcomes"
unit = "isp"
method = "the 18 stencil probes of probes/isp/stencil.toml that set ISP word 2 (always, never, eq0, eq1 and their 0x04bc and 0x04e8 variants) on the laptop, linux fork with the debug option on: the 64x64 triangle with ISP word 0 = 0x01d00300 (0x01d00301 for reference 1), compare mask 0xff and every operation keep in ISP word 2, 0x04bc poked through rd:17 and 0x04e8 through rd:51, every pixel read back, each probe fenced by a baseline render before and after; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-stencil"]
terms = ["CR_ISP_REG_04E8", "ISP0"]
+++

**What runs.** The 64x64 triangle with the ISP word 2 added to its state block: word 0 as
0x01d00300 (the word-2-present bit set) with the stencil reference in bits 7:0 (0 or 1), and word
2 giving a compare in bits 27:25 (never = 0x0000ff00, equal = 0x0400ff00, always = 0x0e00ff00).
The probes leave 0x04bc and 0x04e8 at the job's values, or poke 0x04bc to 0x301, 0x201, 0x101 or
0x1, or poke 0x04e8 to 0, 1 or 0x101. The pixel shader writes one colour.

**Results.** "Drawn" is the triangle's 1062 pixels of 0x00ff8040 on 3034 background pixels.

| compare, reference | 0x04bc | 0x04e8 | triangle |
|---|---|---|---|
| always, 0 | job's | job's | drawn |
| never, 0 | job's | job's | not drawn |
| equal, 0 | job's | job's, 0, 1, 0x101 | drawn (4 runs) |
| equal, 1 | job's | job's, 0, 1, 0x101 | not drawn (4 runs) |
| equal, 0 | 0x301 | job's, 1 | not drawn (2 runs) |
| equal, 1 | 0x301 | job's, 0, 1 | drawn (3 runs) |
| equal, 1 | 0x201 | job's | not drawn |
| equal, 1 | 0x101 | job's | no background written: 2186 background pixels, the rest colours of earlier renders |
| equal, 1 | 0x1 | job's | the same kind of image: 3040 background, the rest old colours |

**What it shows.** The stencil test works in this block and its reference is compared with a
stencil value that register 0x04bc bits 7:0 set: the job's value acts as 0 (equal-0 passes), 0x301
as 1. With bit 8 clear and the value at 1 the test fails as if the value were not applied, so bit 8
enables the value's use. With bit 9 clear the background object is not drawn: the pixels the
triangle does not cover keep earlier contents, so no triangle result can be read there. Register
0x04e8 at 0, 1 and 0x101 changed no outcome in the 9 runs that vary it, so it holds neither this
stencil value nor its enable.

**Not shown.** What 0x04e8 does. The mask and the operations (all keep, mask 0xff) were not
varied. The job's value of 0x04bc is read from its behaviour, not printed in the data. The two
probes with 0x04bc at 0x101 and 0x1 show old pixels, so whether the triangle was drawn on them is
not read. One run.
