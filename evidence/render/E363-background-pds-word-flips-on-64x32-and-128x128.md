+++
id = "E363"
claim = "The background object's first PDS word with bit 27 or 28 flipped faults at page 0x0001f000 and with bit 30 or 31 at page 0x2e001000 (the pixel PDS heap's second page), on 64x32 and 128x128 alike; on 64x32 bits 27 and 28 leave 11 to 14 whole rows and the rest of the first 16 rows at half width, bits 30 and 31 rows 0 to 15 whole and rows 16 to 31 at half width (32 of 64 pixels, 16 half rows), and on 128x128 no row; the second word's bits 27 and 31 and the third's bit 27 change nothing, its bit 31 faults at the same pixel-heap page with no row rendered; three runs and one"
unit = "render"
method = "probes/render/bg-pds-words.toml on the laptop, linux fork b5a86838ae59 with the debug option on: sgxfive-test tri --pixels --poke cmd:N^=BIT for render command words 23 (bits 27, 28, 30, 31; 64x32 and 128x128, three runs each), 24 and 25 (bits 27 and 31; 64x64, once); per case the count of non-sentinel pixels in each row and the driver's fault line since the case's kernel log mark"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["render-bg-pds-words"]
terms = ["cmd_ta.pds_bgnd", "CR_BIF_FAULT", "CR_BIF_INT_STAT"]
+++

**Results.**

| flip | target | fault (status at address) | rows rendered (of 64 pixels / of 32) |
|---|---|---|---|
| word 23 bit 27 | 64x32 | 0xd0400 at 0x0001f06x | 12, 11, 12 whole, then half to row 15 (12+4, 11+5, 12+4) |
| word 23 bit 28 | 64x32 | 0xd0400 at 0x0001f061 | 11, 11, 14 whole, then half to row 15 (11+5, 11+5, 14+2) |
| word 23 bits 30, 31 | 64x32 | 0x92000 at 0x2e001011 | rows 0-15 whole, rows 16-31 half (diff: 512 of 2048), every run |
| word 23 bits 27, 28 | 128x128 | 0xd0400 at 0x0001f02x | none |
| word 23 bits 30, 31 | 128x128 | 0x92000 at 0x2e001011 | none |
| word 24 bits 27, 31; word 25 bit 27 | 64x64 | none | the control's |
| word 25 bit 31 | 64x64 | 0x92000 at 0x2e001014 | none |

- Faulting cases also hold 8 non-sentinel pixels in one row near the bottom (row 28 of 64x32 under
  bits 27 and 28, row 127 of 128x128, row 62 of 64x64); under bits 30 and 31 on 64x32 row 28 holds
  36 where its neighbours hold 32. A control does not show this pattern.
- The fault's low bits name the context's directory list (E360); the status's request bits differ
  between the two pages (0xd0400 for the low page, 0x92000 for the heap page).

**What it shows.**

- A high-bit flip of the first word makes the background program fetch from a wrong address, low
  memory for bits 27 and 28 and the PDS pixel heap for bits 30 and 31, and the tiles rendered
  before the fault stops the 3D are a target's first tiles in order: on 64x32 more than the first
  tile, on 128x128 none [HW] [infer: the order]. The number of rows still varies from run to run
  under bits 27 and 28.
- Of the other two words only the third word's bit 31 matters among the bits tried [HW: one run].
