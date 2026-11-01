+++
id = "Q122"
question = "what does the ZLS store write for the pixels of an edge tile that lie outside the target, and for the 16 x 16 blocks outside it?"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E465"]
terms = ["CR_ISP_ZLSCTL"]
+++

E465: a 34 x 18 target has four tiles; the store writes all 2048 dwords of them, 612 for the
target's pixels, 312 more for pixels outside it that the full-screen triangle covers (they hold the
ramp), and 1124 dwords of the background depth 1.0 for the rest. So the store writes whole tiles
whatever the target's size, and which outside pixels hold the triangle's depth and which the
background follows some rule of the rasteriser (a 16 x 16 block, a 2 x 2 quad) that one size does
not show.

What is open: that rule, and whether it matters to a depth buffer that a later render loads (it
does if the buffer is read back outside the target). To settle it: the ramp stores of E465 at sizes
that end inside a block (a width of 34, 50, 66, 18) and their outside dwords counted.
