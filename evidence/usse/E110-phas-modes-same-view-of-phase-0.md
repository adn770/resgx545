+++
id = "E110"
claim = "In a triangle's two-phase pixel shader, parallel and perinstance give phase 1 the same view of what other instances did in phase 0: a counter incremented under lock #0 ends at 291 (0x123) in both and reads back with a similar spread (97 and 98 distinct values, smallest values 9 and 11 under parallel, 9 and 10 under perinstance), and quads that skip a long spin read the marker the spinning quads store, in both modes"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/phases.toml, probes usse-phases-phas-bar-parallel and -perinstance (phase 0 adds 1 to scratch dword 0 under lock #0, phase 1 reads it as the pixel) and usse-phases-phas-bar2-parallel and -perinstance (quads whose tile row has bit 1 set spin 4096 times and store a marker in phase 0, the others go straight on, phase 1 reads the marker), the first phas none, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-phases"]
terms = []
+++

**What runs.** The triangle's pixel shader is two phases and phase 0 is the part under test. In
the counter probes every quad adds 1 under lock #0 and phase 1 reads the total as the pixel; in
the marker probes the quads that skip the spin go to phase 1 while the others still spin, and
phase 1 reads the dword the spinners store. Both pairs differ only in the mode of the first
`phas`.

**Results.** All four jobs complete and draw the triangle's 1062 pixels. The counter dword ends
at `0x123` (291, one update a quad) in both modes. The values phase 1 read:

| first phas | distinct values | smallest values (pixels) | largest |
|------------|-----------------|--------------------------|---------|
| none, parallel | 97 | 9 (8 pixels), 11 (8), 24 (14) | 291 (13) |
| none, perinstance | 98 | 9 (4), 10 (4), 24 (10) | 291 (13) |

In both marker probes all 1062 pixels read `0x0badf00d`, the marker, and the scratch dword
holds it. The baseline triangles were exact; no visibility counter counted.

**What it shows.** Neither test separates the modes. The counter reflects other tasks as much
as a reader's own (tasks run alongside each other), and the markers are all read by every
pixel in both modes. E119 tests the boundary in a fill, where a task's instances can be told
apart in memory; E112 gives the one measured difference between the modes.

**Not shown.** One run per probe; the spread of values is a race and would differ in a repeat.
