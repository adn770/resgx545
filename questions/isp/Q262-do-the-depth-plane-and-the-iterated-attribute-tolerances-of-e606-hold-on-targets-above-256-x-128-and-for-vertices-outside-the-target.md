+++
id = "Q262"
question = "what bounds the error of the stored depth and of the iterated clip z on E680's targets, where E606's tolerances fail for some triangles of gradient below 0.03 (1- and 2-pixel triangles up to 9 units of 2^-23 above the plane against 3, the iterated clip z of 3 medium triangles offset by 3.6 to 5.8 units against 4; E912), and do E606's rule and tolerances hold for a depth plane through vertices outside the target"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E606", "E607", "E680", "E684", "E912", "E913"]
terms = []
+++
E680 to E684 measured coverage only (colour images). The depth part is open: E606's depth runs were
at 64 x 64 to 256 x 128 with the depth pitch fixed by the E465 window rule, and the tiling of the
depth buffer on a target of 4 macrotiles a row or with a width that is not a multiple of the tile
has not been run with random triangles. The simulator refuses the depth plane, the iterated
attributes and any depth compare on those targets.

To settle it: E606's D jobs (tri --depth with the pitch rule) on 512 x 256, 640 x 480, 1024 x 768
and 2048 x 1024, small and medium triangles with vertices at 1/256, the depth error in units of
2^-23 against the exact plane through the rounded vertices; at 4096 x 4096 only a few jobs and a
depth dump of a window, since the buffer is 64 MB.

Status: open.

Narrowed 2026-11-12 (round 7, R7-geo stages zd and zi, E912; ranking decision R7-7 a asked for
retirement if every size held, and the depth tolerance did not). Answered, held out: on 512 x
256, 640 x 480, 1024 x 768, 2048 x 1024 and 4096 x 4096 E606's coverage held for every depth job
and iteration probe (100 of 100, 24 of 24) and the depth store wrote the whole tile area and
nothing outside (100 of 100). Not as asked: E606's 3 units held in 94 of 100 jobs and the 4 units
of the iterated clip z in 21 of 24, so E606's tolerances are not a bound on these targets. Read
after the run, the 6 depth misses are 1- and 2-pixel triangles (up to 9 units; every job covering
5 pixels or more within 2.64), as are E913's 12 on ten other targets, and the 3 iteration misses
are offsets nearly constant over the triangle. Open: a bound or rule for those errors (the depth
plane's arithmetic is Q200), whether E606's own targets show the same misses on 1- and 2-pixel
triangles, and vertices outside the target, which no stage here ran. The simulator still refuses
the depth and the iterated attributes on E680's targets under this question.
