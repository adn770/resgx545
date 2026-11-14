+++
id = "Q241"
question = "what does ISP word 0 bit 15 keep (E065: 48 pixels of the library's triangle; E1045 and E1056: bits 15 to 17 select no winding, and bits 16 and 17 alone leave no pixel of it) and bit 18, the depth compares 2, 3, 5 and 6 against equal depths, the visibility test (ISP word 1 bit 3), the polygon offset (bit 23), a pass type other than 0 over several triangles of one object, the stored depth of the polygon a vertex depth outside [0, 1] cuts (E1056: its coverage is the clip at the plane with the made vertices rounded half away from zero; the plane stored differs from the original vertices' by up to 7.8e-5) and the pairs of ISP word 1 bits 31:26 and CR_ISP_CTL bits 5:0 that E232 and E235 did not run do to the image, the stored depth and the counters?"
unit = "isp"
kind = "hw"
value = "low"
phase = 12
evidence = ["E065", "E070", "E071", "E072", "E232", "E235", "E282", "E287", "E291", "E660", "E739",
            "E757", "E995", "E998", "E1045", "E1056"]
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

Narrowed 2026-11-10 (S1b, E757; the pass-type bullet only). With the compare always on a farther
second object, pass type 1 drew it over the first (red 1098 pixels, green 0, 2 of 2), as an opaque
always did; with it on the first object under a nearer opaque second, the second's colour stayed (2
of 2). Depth order and pass order, E739's two surviving hypotheses, are refuted in 2 of 4 each; list
order and 'pass type 1 changes nothing' are consistent and not separated. Two or more triangles of
one object, the translucent blend with a shader that writes alpha and the other pass types stay
open.

Narrowed 2026-11-13 (r10-x, E995 and E998). The compares 2, 3, 5 and 6 are equal, less or equal,
not equal and greater or equal, decided exactly on equal depths at 0.5 and one ulp either side
(E995, 14 of 14 held out with the GL order). ISP word 0 bits 15, 16 and 17, each set alone under a
depth compare with writes, remove E977's ramp triangle whole (no pixel, the background depth
stored: E998, 3 of 3), and ISP word 1 bits 3 (the visibility test) and 23 (the polygon offset)
change neither the image nor the stored depth of that ramp (2 of 2). Open: what bits 15 to 17
select (the other vertex order, E065's 48 pixels), bit 18 (faults), the visibility counter and the
polygon offset's units, the pass types over several triangles, a vertex depth outside [0, 1] and
the gate pairs.

Narrowed 2026-11-14 (r14-isp stage wind, E1045, held out; the question line is reworded, the
question is not retired). It read "what do ISP word 0 bits 15, 16, 17 and 18, the depth compares
2, 3, 5 and 6 against equal depths, the visibility test (ISP word 1 bit 3), the polygon offset (bit
23), a pass type other than 0 over several triangles of one object, a vertex depth outside [0, 1]
and the pairs of ISP word 1 bits 31:26 and CR_ISP_CTL bits 5:0 that E232 and E235 did not run do to
the image, the stored depth and the counters?". Each of bits 15, 16 and 17 removes E977's ramp
triangle with its vertex order reversed as well (no pixel, the background depth: 3 of 3, the
frozen one-winding cull refuted), so on that triangle the bits select no winding. Under the
compare always with the depth written, a vertex depth above 1 or below 0 removes the pixels whose
depth lies past [0, 1] and stores the background there (2 of 2; clamping, storing the plane as it
is and clearing its sign refuted), as a clip at the near and far planes would (sgx-pipe mte.rs,
E287) [infer]. Open: what bits 15 to 17 select (E065's 48 pixels), bit 18, the visibility counter
and the polygon offset's units, the pass types over several triangles, the cut's made depths and
edge pixels, and the gate pairs.

Narrowed 2026-11-14 (r15-isp stage zcut, E1056, held out; the question line is reworded, the
question is not retired). It read "what do ISP word 0 bits 15 to 17 select (E1045: each removes
E977's ramp in both vertex orders, so no winding; E065: bit 15 left 48 pixels of the library's
triangle) and bit 18 ... the depth and the edge pixels of the cut that a vertex depth outside [0,
1] makes (E1045: the pixels past [0, 1] are removed) ...". A vertex depth at 1.25 or -0.25 cuts the
triangle as a polygon clipped at the plane, each made vertex rounded half away from zero to 1/256
pixel, then E606's coverage: 6 of 6 target images pixel for pixel on rows whose cut line passes
within 1/512 pixel of 8 to 10 centres and every background dword of the band, the per-pixel cut
and the unrounded polygon 0 of 6 (8 to 11 pixels a row apart). The stored depth of the drawn
pixels is the original plane within 7.8e-5 and no plane through three vertices of the polygon fits
(a scratch fit): open. ISP word 0 bits 16 and 17 alone on the library triangle left no pixel (2 of
2, E065's jobs again, with the pixels printed), so they are as E1045's rows: removal, not a
winding. Not retired: bit 18 (faults) was not run this round, nor were the visibility counter, the
offset's units, the pass types over several triangles, the gate pairs and what bit 15 keeps.
