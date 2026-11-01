+++
id = "E121"
claim = "phas's vcull wait makes the next phase of a vertex shader wait for the MTE's cull decision and skips it for a culled triangle: with MTE control's cull mode 1 culling the triangle, phase 1 runs under none (one increment of its counter) but not under vcull, and the triangle is not drawn either way; with cull modes 0 and 2 the triangle (1062 pixels) is drawn and both phases run under both waits"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/phases.toml, the six usse-phases-vcull-c{0,1,2}-{none,vcull} probes (the triangle's vertex shader, vtx_wait.s, the first phas waiting vcull or none, MTE control word 15 of the block set to 0x1555620, 0x1555621 and 0x1555622) and the six usse-phases-vcull-count probes (vtx_wait_count.s: each phase adds 1 to its own scratch dword under lock #0), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-phases"]
terms = ["MTECTL.CULL_MODE"]
+++

**What runs.** The triangle's vertex shader has two phases: phase 0 ends in the VCB emit and
phase 1 in the MTE emit. The first `phas` waits `vcull` or `none`. The cull mode, the low bits of
MTE control, is 0, 1 or 2; mode 1 culls this triangle. The count probes add 1 to scratch dword 1
in phase 0 and to dword 0 in phase 1, both under lock #0.

**Results.** Drawing: cull mode 0 and 2 draw the triangle (1062 pixels of `0xff00ff00`) under
both waits; cull mode 1 draws nothing (all 4096 pixels are background) under both waits.
Counters (the dword starts at `0xd0000000` plus its slot number):

| cull mode | wait | phase 0 (dword 1) | phase 1 (dword 0) |
|-----------|------|-------------------|-------------------|
| 0 | vcull | `0xd0000002` | `0xd0000001` |
| 0 | none | `0xd0000002` | `0xd0000001` |
| 1 | vcull | `0xd0000002` | not written |
| 1 | none | `0xd0000002` | `0xd0000001` |
| 2 | vcull | `0xd0000002` | `0xd0000001` |
| 2 | none | `0xd0000002` | `0xd0000001` |

Baselines before and after every probe were exact.

**What it shows.** Under vcull the vertex shader's second phase is held until the MTE has
decided whether the triangle is culled, and it does not run for a culled one; under none it runs
regardless, and the MTE discards the culled triangle. The image never shows the difference, only
the work done. The counters count 2 in phase 0 and 1 in phase 1 where the job has one triangle
of three vertices; what a unit of count is (a task, a vertex, a group) is not told by this
table.

**Not shown.** One run per probe; only one triangle and one vertex layout.
