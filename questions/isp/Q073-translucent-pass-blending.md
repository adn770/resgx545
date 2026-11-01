+++
id = "Q073"
question = "what does o0 hold at the start of an opaque pass's pixel shader?"
unit = "isp"
phase = 11
evidence = ["E077", "E283"]
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
