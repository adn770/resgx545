+++
id = "E365"
claim = "With CR_CLKGATECTL2 as the boot leaves it, CR_CLKGATESTATUS reads 0x20 idle and 0x000ccfa0 at every EDM tick, 0x000fffa7 and 0x000fffa4 while a fill runs a pixel loop of six fmads or of six integer multiply-adds alike, 0x00000078, 0x000ccff8, 0x000fffa7, 0x000fffff and, in one 256x256 render of three, 0x000fffa4 through renders; bits 20 and above never read 1; one run of each loop twice"
unit = "platform"
method = "probes/platform/event-timelines.toml and probes/platform/event-trigger.toml on the laptop (regtimeline over CR_CLKGATESTATUS among others, as E357): the distinct values each job's timeline shows; debugfs kreg cannot write CR_CLKGATECTL2 (not among the registers it allows)"
tiers = ["HW"]
date = "2026-11-03"
data = ["platform-event-timelines", "platform-event-trigger"]
terms = ["CR_CLKGATESTATUS", "CR_CLKGATECTL2", "MADD"]
+++

**Results.**

| job | values read (samples where it changed) |
|---|---|
| idle, fill, copy | 0x20, 0x000ccfa0 (about once a millisecond) |
| loop fills, integer or fmad, 128 to 12500 iterations | also 0x000fffa7, 0x000fffa4 |
| renders 64x64 to 256x256 | also 0x00000078, 0x000ccff8, 0x000fffa7, 0x000fffff; 0x000fffa4 once (tri-256-n3-1) |
| held TA hang, fault | 0x00000078, 0x000ccff8 |

**What it shows.**

- The status does not tell a floating-point loop from an integer one with the gates as the boot
  leaves them [HW]; mapping its bits to units needs writes of `CR_CLKGATECTL2`, which our debug
  interface does not offer (Q048).
