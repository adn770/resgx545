+++
id = "Q073"
question = "what does o0 hold at the start of an opaque pass's pixel shader?"
unit = "isp"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E077", "E283", "E417", "E739", "E757", "E1143"]
terms = ["ISP0.PASS_TYPE"]
+++

This record first asked how a translucent pass blends; that is answered (E283), and the question is
now the opaque pass's o0. In a translucent pass the stored pixel is exactly the shader's o0, so in
the one ISP and PBE state run no unit after the shader blends [infer]; o0 starts as the pixel's
colour (E077).

What is open: in the opaque pass o0 starts as a leftover. In E283 some pixels held the colour an
earlier case's shader wrote and the counts differ between runs (517 and 426), so what it is left
from (an earlier task's output buffer, another tile's pixel) is not shown.

To settle it: an opaque pass passing o0 on, after a job whose shader wrote a known colour, and
after one of a different size; ten runs, every pixel read.

Narrowed in 11.15 (E417, 33 jobs): o0 at the start of the opaque pass holds the previous job's o0 on
part of the triangle's pixels (390 to 450 of 1062 at 64x64, 0 to 336 of 2403 at 96x96, 0 to 183 of
4284 at 128x128) and the background on the rest, repeating counts (426 four times of seven at 64x64)
and surviving pass-through jobs. A job of another size before the pass-through was not run (each
probe ran at one size). Status: narrowed, not answered.

Post hoc 2026-11-09 (S1, E739; the frozen verdict: depth order and pass order both fit all six
jobs, list order is refuted, and the table could not separate the two). The images of the
translucent jobs (pass type 1 on the second, the first or neither object) are pixel-identical to
the opaque pair at both depth orders, so "pass type 1 changes nothing here" fits as well; not a
frozen hypothesis.

Narrowed 2026-11-10 (S1b, E757; this does not answer the question of o0). A table where depth order
and pass order differ, the pass-type-1 object's compare being always (ISP word 0 bits 24:22 = 7,
word 0x03c00200) and the object farther: the second object drew over the first at any depth (red
1098 pixels, green 0, 2 of 2), and as the first object under a nearer opaque second it left the
second's colour (2 of 2); an opaque always second object gave the same image. Frozen verdict:
controls pass; list order and 'pass type changes nothing' are consistent in 4 of 4 (they predict the
same), depth order and pass order are refuted in 2 of 4 each. E739's reading that depth order and
pass order both fit is therefore corrected for the compare always. The translucent pass's images are
still the shader's colour, with no blend seen, which says nothing about what o0 holds at the start
of an opaque pass.

Narrowed 2026-11-18 (r35-o0, E1143; the frozen rule decided nothing). A pass-through after a shader
that stores a value unique per pixel: the three 128 x 128 controls of that shader failed (1 to 30
of 4284 pixels, in 4 x 4 blocks, held another pixel's value), and the frozen gate put them in front
of every row, so every hypothesis was cannot tell: NARROW. The pass-through after a constant colour
kept it on 426 of 1062 pixels (2 of 2, E417's count). Post hoc, not decided: at 64 x 64 the kept
pixels read the previous job's o0 at the same pixel (148 of 188 in three rows) or at fixed offsets
of 32 rows, of 32 columns and 16 rows, or of 16 rows; a debugfs reset between keeps them, the t10
fill between replaces them with its colour, and after a 128 x 128 job a 64 x 64 pass-through kept
no pixel (2 of 2). The corrected rerun r35-o0b freezes those readings as its fit. Status: narrowed,
not answered.
