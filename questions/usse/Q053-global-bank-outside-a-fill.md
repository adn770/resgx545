+++
id = "Q053"
question = "what do the global registers g18 to g20 and g39 to g43 hold in a triangle's pixel task, a vertex task and the end-of-tile task?"
unit = "usse"
kind = "hw"
value = "high"
phase = 11
evidence = ["E085", "E086", "E372", "E374"]
terms = []
+++

In a 64x32 fill g23 is the pixel's x in its 32x16 tile, g24 its y, g25 its place in the 2x2 quad,
g17 the tile quarter and g18 a per-tile number (E086); c0 to c63 read one fixed table (E085).

Narrowed in 11.13: in the triangle's pixel program at 64x64 and 128x128, g16, g19, g26-g31 and g40
read 0, g20 and g41 1, g42 1.0 and g43 0xff000000 on every pixel, as in the fill; g17, g18,
g21-g25 and g39 vary per pixel (E374). g19 reads by the instruction that reads it (E372).

What is open (usse_isa.md §8, item 4): the global registers in a vertex task and in the
end-of-tile task.

To settle it: the triangle job's vertex program writing each global register to an output read
back through the parameter buffer, and the end-of-tile program emitting one as its colour.
