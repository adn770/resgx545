+++
id = "E371"
claim = "A register written by mov, or, fmad, frcp or fexp reads as the result in the next instruction and at every distance up to 8 instructions, with or without .nosched on the writer: 230 cases, every pixel the result"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/hazards.toml (hazard.s: r1-r5 = 1.5, 3, 5, 7, 9; the writer to r10, then 0 to 8 nops, then mov r11, r10, r11 as the pixel and r10, r11 stored), each writer with and without .nosched, two runs (180 cases); and the writer followed at once by or r11, r10, r10, five runs (50 cases); one run"
tiers = ["HW"]
date = "2026-11-03"
data = ["usse-hazards"]
terms = []
+++

**Results.** Every case reads the writer's result in all 2048 pixels and in both stored dwords:
`mov` 7, `or` 0xf, `fmad` 9.5 (1.5 x 3 + 5), `frcp` of 3 0x3eaaaaab, `fexp` of 1.5 0x403504f3.
No case shows the old value 0xa0a1a2a3, a mixed pixel or a failure.

**Not shown.** Whether the hardware stalls the reader or the result is ready in time (no timing
was taken); loads and other DRC results, which need their `wdf` (E367 for `idiv`); `.syncs`.
