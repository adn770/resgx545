+++
id = "Q262"
question = "do the depth and iteration tolerances of E606 (3 U for depth at a gradient below 0.03, 4 U for the iterated clip z, in units of 2^-23) hold on the targets of E680 (up to 4096 x 4096, half-sizes not powers of two) and for a depth plane through vertices outside the target"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E606", "E607", "E680", "E684"]
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
