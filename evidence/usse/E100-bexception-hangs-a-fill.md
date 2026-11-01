+++
id = "E100"
claim = "bexception between two marker writes, with or without .nosched, hangs a fill's pixel task (the job times out and the context is lost), and the baseline triangle run before and after each case is exact, so the kernel recovers the GPU; the same fill without bexception completes with both markers"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/branch.toml, probes usse-branch-bexc-none, usse-branch-bexc and usse-branch-bexc-nosched (client fill, one case a probe, each preceded and followed by the baseline 64x64 triangle), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-branch"]
terms = []
+++

**What runs.** The fill's pixel task writes `0x0A0A0A0A` to r20, runs the case, writes
`0x0B0B0B0B` to r21, and stores both registers to scratch (r20 is also the pixel). The cases are
nothing in between (control), `bexception #0` and `bexception.nosched #0`, which the assembler
writes with its target and predicate fields at 0 (E108 gives what those fields do).

**Results.** The control completes: every pixel reads 0x0a0a0a0a and the scratch holds both
markers. `bexception` and `bexception.nosched` each end as `job hung, context lost (Connection
timed out)`, and the scratch is unchanged, so nothing tells whether the first marker was
written. The baseline triangle before and after every probe of the table, those two included,
differs from the reference in 0 of 4096 pixels, so the next job after each hang ran clean. The
visibility counters read 0 throughout.

**Not shown.** A hung job reads back nothing, so the hang gives no information on the path the
task took; E108 shows where `bexception` goes. One run: whether the hang repeats was not
tested.
