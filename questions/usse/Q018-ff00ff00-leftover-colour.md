+++
id = "Q018"
question = "where does the 0xff00ff00 colour left in the opaque pass and the punch-through phase scene come from, and why does its pixel count vary from run to run?"
unit = "usse"
phase = 6
evidence = ["E077", "E082"]
terms = ["ISP0.PASS_TYPE"]
+++

The colour 0xff00ff00 turns up where a pixel shader's output is not written by the shader
itself (E077, E082). Counts:

- E077, opaque pass, `mov o0, o0` over a 64x64 triangle (1062 covered pixels): 3748 pixels of
  the background 0xff203040 and 348 of 0xff00ff00 (the xor case: 800 covered pixels read the
  background and 262 read 0xff00ff00). One run. In the translucent pass the triangle's pixels
  read the background and none read 0xff00ff00.
- E082, the colour phase after a punch-through phase with U1 bit 24, depth-always scene: 118 to 407
  pixels of 0xff00ff00 per case (run 1 and run 2: 324 and 383, 288 and 288, 203 and 288, 118 and
  288, and for the cases that write into pa0, a primary attribute register, 407 and 383, 288 and
  288, 288 and 288). The punch-through scene writes none. 288 is the count in 8 of the 14.
- The VDM state probe of Q015, which only copies o0: 269 and 185 pixels of 0xff00ff00 beside
  3827 and 3911 background pixels in two runs.

So 0xff00ff00 is a colour that appears in the opaque pass and the colour phase, not in the
translucent pass, and its count differs from run to run. In E082 it is written by the colour
phase itself; in the o0-copying jobs it is what o0 holds.

Open: where the colour comes from (an earlier task's output, a tile initial value or a default
of the pass), why 288 recurs, and what picks the pixels that hold it.

To settle it: with the output buffer filled with a known colour per job, run the opaque pass
ten times and print the positions of the 0xff00ff00 pixels, to see whether they are whole quads,
rows or tiles and whether their positions repeat; run after a job that leaves another colour in
the tile buffer, and with the tile's initial value changed, to see whether 0xff00ff00 follows
either.
