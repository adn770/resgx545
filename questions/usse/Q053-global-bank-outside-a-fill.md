+++
id = "Q053"
question = "what sets the global registers g18 and g21 in a vertex task, and what do g17, g18, g21 to g25 and g39 hold in the end-of-tile task of each tile (only the last tile's store survives)?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E085", "E086", "E372", "E374", "E571", "E572", "E708"]
terms = []
+++

In a 64x32 fill g23 is the pixel's x in its 32x16 tile, g24 its y, g25 its place in the 2x2 quad,
g17 the tile quarter and g18 a per-tile number (E086); c0 to c63 read one fixed table (E085).

Narrowed in 11.13: in the triangle's pixel program at 64x64 and 128x128, g16, g19, g26-g31 and g40
read 0, g20 and g41 1, g42 1.0 and g43 0xff000000 on every pixel, as in the fill; g17, g18,
g21-g25 and g39 vary per pixel (E374). g19 reads by the instruction that reads it (E372).

Narrowed in 11.33 (E571, E572; the question asked for g18 to g20 and g39 to g43 in all three tasks).
Answered for the vertex task: g16, g19 (through a mov), g26-g31 and g40 read 0, g20 1, g42 1.0, g41
0xf and g43 0xdf000000 (0x3 and 0x20000000 in a last task of 2 vertices), and g17, g22, g23, g24,
g25 and g39 follow the vertex's task and lane by rules fitted at 8 vertices a task and held at 4 and
6 (g23 read from the data after the fact), 125 of 125 vertices in each of 12 jobs. Answered for the
end-of-tile task of the last tile: g16, g20, g26-g31 and g40-g43 read as in a pixel task and g19
reads 0x1a through a store (E572). What remains open is the part of the question that has no rule:
g18 and g21 in a vertex task, which change with the task (0xe to 0x16 and 0x1a to 0x1f, by vertices
a task) and differ for g18 between the group A and group C jobs in 2 of 21 tasks at 6 a task; and
every register that varies in the end-of-tile task (g17, g18, g21 to g25 and g39), read only as the
last tile's value because each tile's store lands in the same dword and a store faults the job
(Q183).

To settle it: a vertex program that writes g18 and g21 with a counter that fixes the task number
and one that stores a second register per vertex; an end-of-tile program that stores to an address
built from g17 or g18 once a store that does not fault is found (Q183).

Narrowed in 11.39 (E708, 5 jobs). The per-tile values of the end-of-tile task are readable
without a fault with E130's form (a register-offset store to r4 + a slot from sa15): 32 tiles
at 128x128 (and 32 of 64 at 256x128): g16 0, g19 0x1a, g25 3, g26 to g31 0, g43 0xff000000,
g17 in 0 to 3, g18 in 0xa to 0x16, g21 in 0x3 to 0x1f, g22 in {0, 1}, g23 in {1, 0x11}, g24 in
{1, 9}, g39 0; the frozen prediction that the form completes held (5 of 5). g20, g41 and g42
read 0 where E572 read 1, 1 and 1.0 (Q275). Open: the rule for g18 and g21 in a vertex task and
per tile, and the vertex-task program that counts tasks (not run).
