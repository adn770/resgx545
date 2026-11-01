+++
id = "Q053"
question = "what do the global registers g18 to g20 and g39 to g43 hold in a triangle's pixel task, a vertex task and the end-of-tile task?"
unit = "usse"
phase = 11
evidence = ["E085", "E086"]
terms = []
+++

In a 64x32 fill g23 is the pixel's x in its 32x16 tile, g24 its y, g25 its place in the 2x2 quad,
g17 the tile quarter and g18 a per-tile number (E086); c0 to c63 read one fixed table (E085). Q017
asks why g19 reads differently as a store's source and through a mov.

What is open (usse_isa.md §8, item 4): g18 to g20 and g39 to g43 outside a fill.

To settle it: on the laptop, store every global register from the triangle job's pixel shader, from
its vertex shader (as outputs read back through the parameter buffer) and from the end-of-tile
program, on two target sizes, three runs each.
