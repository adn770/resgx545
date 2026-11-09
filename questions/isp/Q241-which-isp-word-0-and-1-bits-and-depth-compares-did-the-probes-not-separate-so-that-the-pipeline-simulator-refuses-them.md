+++
id = "Q241"
question = "what do ISP word 0 bits 15, 16, 17 and 18, the depth compares 2, 3, 5 and 6 against equal depths, the visibility test (ISP word 1 bit 3), the polygon offset (bit 23), a pass type other than 0 over several triangles of one object, a vertex depth outside [0, 1] and the pairs of ISP word 1 bits 31:26 and CR_ISP_CTL bits 5:0 that E232 and E235 did not run do to the image, the stored depth and the counters?"
unit = "isp"
kind = "hw"
value = "low"
phase = 12
evidence = ["E065", "E070", "E071", "E072", "E232", "E235", "E282", "E287", "E291", "E660", "E739"]
terms = ["ISP0.PASS_TYPE", "ISP0.DCMP_MODE", "ISP1.VISTEST", "ISP1.POLY_OFFSET"]
+++

The pipeline simulator decodes an object's ISP words (E660) for the compares 0, 1, 4 and 7, the
depth and colour write bits and the pass types of a single triangle, and refuses the rest, naming
this question where no other question owns it. The decode of the compares, the write bits and the
gate is checked by unit tests of the model against itself: no replayed vector exercises it (the
depth-test and punch-through vectors of the census all stop at Q094). Open here:

- ISP word 0 bits 15 to 17 changed the image when flipped on the 64 x 64 triangle (bit 15 left 48
  pixels, bits 16 and 17 none: E065) and bit 18 faulted the job; no table separates what each does.
- The compares 2, 3, 5 and 6 draw as 0, 1, 7 and 4 against unequal depths (E072); that they are
  equal, less or equal, not equal and greater or equal is read from the stencil compare's order. A
  probe with equal depths settles it, and the simulator needs the depth to be decided exactly, which
  E606 says it is not (a plane's error is up to 3 units where the gradient is below 0.03: Q200).
- The visibility test counts "in some boots only" (E070): non-repeatable, to be recorded as an
  `either`; the polygon offset's units and clamp are shown for flat and one sloped triangle (E071,
  E291) and not as a rule.
- A pass type of 1, 2, 4, 5 or 6 draws a single triangle as type 0 (E065) for the library's colour
  write, the shader E065 ran; another shader (a translucent or punch-through object whose shader
  writes alpha), two or more triangles of one object, the translucent blend (Q073) and the
  punch-through feedback (Q032) are open, and the simulator refuses them.
- The gate: E232 measured CR_ISP_CTL bits 5:0 of 1 to 8, 16, 32 and 63 (and 0) with the library's
  ISP word 1 (bits 31:26 = 0); E235 measured bits 31:26 of 0 and 63 at the values 1 and 63. The
  comparison "removed when the bits are below the value" is read from those pairs; the equality
  away from 63 and the pairs between are not measured, and the simulator refuses them. Pass types
  3 and 7 were run with the library's words only.
- A vertex depth outside [0, 1]: E287 saw a negative depth compare as 0 and one above 1 as itself,
  in one run and by inference. The simulator refuses such a triangle under a compare or a depth
  write; an always without a depth write does not use the depth.

What would settle it: the flips of bits 15 to 17 with a counted image and a stored depth; a depth
compare table with equal depths on a loaded depth buffer; the visibility counter repeated n times
per setting; two-triangle objects of each pass type.

Status: open.

Post hoc 2026-11-09 (S1, E739; not an answer): ISP pass type 1 (bits 27:25 of word 0) on either of
two overlapping objects gave images identical to the opaque pair at both depth orders (6 of 6 jobs,
controls passing); the frozen table could not tell depth order from pass order.
