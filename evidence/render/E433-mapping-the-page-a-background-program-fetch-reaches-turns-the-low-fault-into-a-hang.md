+++
id = "E433"
claim = "With the TA command's word 23 (the background object's first PDS word) bit 27 or 28 flipped, mapping the page 0x1f000 it fetches from (filled with 0xd1d1d1d1, 0 or 0xffffffff) turns the fault into a hang with 512 pixels changed where the unmapped job faults with 1024 to 1184 (3 of 3 runs, each fill); with bit 30 or 31 flipped, mapping the pixel PDS heap's second page changes nothing (fault, 512 pixels at 64x32, 3 of 3 runs, each fill)"
unit = "render"
method = "probes/render/bg-pds-map.toml (bg-pds-map.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on, vm_low on: sgxfive-test tri --pixels at 64x32 and 128x128 with --poke cmd:23^=0x08000000, 0x10000000, 0x40000000 and 0x80000000, each unmapped and with one page mapped to the render's VM by --scratch 1 --scratch-at 0x1f000 (bits 27, 28) or 0x2e001000 (bits 30, 31) holding 0xd1d1d1d1, 0 or 0xffffffff, three runs: 102 jobs"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["render-bg-pds-map"]
terms = ["cmd_ta.pds_bgnd"]
+++

**Results** (3 of 3 runs for every case; at 128x128 every case differs at all 16384 pixels):

- Unmapped, as E363: bits 27 and 28 fault (64x32: 1152 and 1184 or 1024 pixels differ), bits 30
  and 31 fault (512 pixels).
- Bits 27 and 28 with 0x1f000 mapped, any of the three fills: the job hangs and is recovered; at
  64x32 512 pixels differ (the first 16 rows whole, then mostly half rows), the bits 30 and 31
  pattern, instead of 12 to 14 whole rows.
- Bits 30 and 31 with 0x2e001000 mapped, any fill: the job faults as unmapped, 512 pixels differ;
  the page the fetch faults on is not that one.

**What it shows.** The rows rendered before a faulting background fetch depend on whether the
fetch resolves: a mapped page (whatever it holds) lets the 3D go on to a hang with the first 16
rows done. The address the bits 30 and 31 fetch reaches is not the pixel PDS heap's second page
[infer]; it is not found. Q014 is narrowed.
