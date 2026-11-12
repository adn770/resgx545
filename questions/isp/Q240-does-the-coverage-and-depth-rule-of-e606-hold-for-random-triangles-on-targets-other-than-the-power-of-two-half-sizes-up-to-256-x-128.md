+++
id = "Q240"
question = "does the coverage rule of E606 (vertices on the 1/256 pixel grid, exact centre test, left and top edges owning ties) hold for random sub-pixel triangles on the targets no run has covered, odd widths, sizes past 4096 and the sizes between those run (E606's three, E680's ten, E913's ten), and what bounds the depth plane's error on every target but E606's three, where 1- and 2-pixel triangles exceed E606's 3 units (E913)?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E606", "E607", "E662", "E660", "E148", "E174", "E680", "E681", "E682", "E912", "E913"]
terms = []
+++

The pipeline simulator uses the E606 coverage and depth rule only inside what was run: the three
targets 64 x 64, 128 x 128 and 256 x 128 of E606, and refuses every other target. (A family of
power-of-two half-sizes up to 256 x 128 is how E606 words its envelope; three of its sizes ran and
the simulator admits those three. A sweep that runs more sizes widens the list by a record.) E662
shows that the rule gives the recorded image hash of the library's first triangle at all 16 sizes
of E148 and E174, among them 13 outside the three, so the first triangle does not separate the
rule from a rule of the same pixels for triangles with vertices on the 1/16 pixel grid. What is
open: random sub-pixel triangles (the sweeps, the ties and the edge cases of E606) on those targets,
where the TA lists regions by macrotile (four macrotiles a row from 640 x 480: E506) and where the
float conversion of a window coordinate has a resolution of 2^-13 pixel at 1024 pixels and 2^-11 at
4096 (E607's resolution argument), which may move the rounding of a vertex.

What would settle it: the E606 tool and tables (tri with --tri-v and --tri-z, the D jobs of random
small, medium and sweep cases) on 96 x 64, 64 x 192, 256 x 256, 1024 x 768 and 4096 x 4096, the
images and the depth dumps compared with the rule, with vertices of 1/4096 pixel near the tie at the
largest sizes.

Narrowed in 11.39 (E680, E681, E682: the sweep's records come before this question in the
sequence of phases). The coverage half of the question is measured: the rule holds
without tolerance on ten targets (96 x 64, 130 x 66, 200 x 120, 512 x 256, 512 x 512, 640 x 480,
1000 x 600, 1024 x 768, 2048 x 1024, 4096 x 4096) in 590 random triangles (0 of 1092224240 pixels
wrong, E680), the half-up rounding holds at the tie on seven of them (E681) and the edge function
is exact for edges up to 2052 pixels (E682). Not measured, and still this question's: the depth
plane and the iterated attributes on those targets (Q262), a target below 96 x 64, 4096 x small and
odd sizes, and the sizes between (the sweep's envelope document lists what the rule may take).
The simulator's list is not widened by this: it still admits the three targets of E606.

Status: open.

Narrowed 2026-11-12 (round 7, R7-geo stage zf, E913; decision 3 a of the ranking). Held out on
ten more targets, 64 x 128, 128 x 64, 256 x 64, 128 x 96, 128 x 144, 32 x 16 and 16 x 8 (below one
tile), 4096 x 16, 64 x 33 and 96 x 47 (odd heights): E606's coverage rule drew 240 of 240 images
and the depth store wrote each tile area whole and nothing past it (240 of 240). E606's 3-unit
depth tolerance held in 228 of 240 jobs; the 12 misses, as E912's 6, are 1- and 2-pixel triangles
(read after the run). The simulator admits the coverage on those ten targets (`isp::E913_TARGETS`,
`coverage_image`); a render or a depth there still refuses under this question, the depth bound
being open (Q200 for the arithmetic, Q262 on E680's targets). Still open: odd widths (the
userspace tool refuses them), sizes past 4096, the sizes between those run.
