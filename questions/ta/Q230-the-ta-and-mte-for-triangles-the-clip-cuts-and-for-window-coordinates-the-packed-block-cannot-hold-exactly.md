+++
id = "Q230"
question = "what does the TA write when the MTE removes a triangle wholly beyond z = -w or z = w or cuts one at it, when a triangle is not listed by any target region (the hardware wrote no object for one 1000 pixels off a 64 x 64 target: where is the limit between that and a triangle partly on the target), and how are window coordinates with more than 8 fraction bits, and the depth and 1/w of a vertex with w other than 1, rounded and stored in the object?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 12
evidence = ["E063", "E182", "E194", "E287", "E307", "E651", "E650", "E736"]
terms = ["PB_OBJ.RHW", "PB_OBJ.ISP_WORDS", "VIEWPORT.X_OFFSET", "WCLAMP"]
+++

The pipeline simulator's vertex side and TA (E650) compute an object only for whole triangles whose
three vertices have w = 1, window coordinates that are multiples of 1/256 pixel, and that at least
one region of the target lists. Everything else refuses here:

- a triangle with a vertex beyond z = -w or z = w, whether all three are (the clip removes it from
  the image: E287 measured flat triangles at -1.01 and 1.01 removed, by pixels) or one is and
  another inside (E287 measured sloped ones cut along the line where z reaches the plane); nothing
  dumped says whether the TA writes an object for the removed triangle, as for the one no region
  lists below, or what it writes for the cut one;
- a 1/w equal to the minimum of the command (E197's three values were all clear of it: whether the
  replacement applies on the boundary is open);
- a triangle no target region lists: the zero-words baseline (viewport x offset 1000) gives no
  object and empty headers, and the object of every dumped triangle that reaches the target is
  written, so the limit is open: a rule "an object is written when some region lists a primitive"
  and a rule "an object is not written beyond a guard band" both fit the data;
- window coordinates with more than 8 fraction bits: the packed block holds 24 bits of
  (v + 4096) * 256, and every coordinate dumped so far is a multiple of 1/16 pixel, so truncation,
  rounding and the viewport's own arithmetic (a multiply then an add, or a fused one) are not told
  apart;
- the depth and 1/w of a vertex with w other than 1 (E063, E194 measured the pixels), and a w
  below 1e-3.

What would settle it: a triangle wholly beyond z = w and one beyond z = -w, dumped; a table of
triangles with window coordinates on a 1/1024 grid and with w of 0.5, 2 and 4, their objects
dumped; triangles moved across the target's edge by 8, 64, 128, 512 and 1000 pixels; a triangle
with one vertex beyond z = w, dumped.

Status: open.

Post hoc 2026-11-09 (S1, E736; the frozen verdict was cannot tell, because the control of the
WCLAMP group failed; nothing here is held out or an answer). The WCLAMP control, w = 1e-5 under a
clamp of 1e-3, wrote an object (4 vertices, a 0.96 pixel square at the target's centre covering no
pixel centre, 1/w 0x4479ffff), not "no object" as E194's image had been read: the 35 dumped objects
are in E736. Read per group after the run: triangles wholly beyond z = w or z = -w leave no object;
cut and w-clipped triangles are stored as clipped polygons of 3 to 5 vertices; a viewport offset of
8 and 64 pixels keeps the object and 128, 512 and 1000 leave none; 1/1024 coordinates are packed
rounded to 1/256; x and y are divided by w exactly at w = 2 and 0.5; a clamp one ulp above w = 1e-3
stores the clamp's reciprocal as 1/w. Each needs a frozen run with the group's control gating that
group alone.
