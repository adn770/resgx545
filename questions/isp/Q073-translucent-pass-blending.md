+++
id = "Q073"
question = "what does o0 hold at the start of an opaque pass's pixel shader?"
unit = "isp"
phase = 11
evidence = ["E077", "E283", "E417"]
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
