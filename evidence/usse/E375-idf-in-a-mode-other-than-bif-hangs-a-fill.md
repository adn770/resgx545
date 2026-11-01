+++
id = "E375"
claim = "In a fill's pixel program, idf drc0 with mode pixelbe or the reserved modes 2 and 3 followed by wdf drc0 hangs the job, with a plain or a .bypassl1 load after it, two runs of each (12 of 12); with bif every pixel loads back the dword it stored"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/idf-modes.toml (idf_mode.s: each instance stores 0x5EED5EED to its own scratch dword, idf drc0 in the mode, wdf drc0, ldad of the same dword, the pixel the load), modes bif, pixelbe, 2 and 3, each with ldad and ldad.bypassl1; two runs; the kernel recovered every hang"
tiers = ["HW"]
date = "2026-11-03"
data = ["usse-idf-modes"]
terms = []
+++

**Results.** With `bif` both loads give 0x5eed5eed on all 2048 pixels. Every case with
`pixelbe`, `reserved(=2)` or `reserved(=3)` fails as a hang (the job does not end; the kernel's
recovery resets the GPU and the next baseline is exact).

**Not shown.** What the other modes wait for (the pixel back end's writes, plausibly, which a
fill's pixel task has none of before its end) and whether a program that has emitted waits
correctly; `lock`, `release` and `setm`.
