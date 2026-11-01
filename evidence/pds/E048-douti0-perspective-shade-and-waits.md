+++
id = "E048"
claim = "In the textured-triangle host with w = x + 2 at the vertices, DOUTI0 bit 24 makes every one of the 1062 pixels hold the perspective-correct iteration of the vertices' x (largest error 1.2e-7, against 0.29 for the affine one), DOUTI word 1 bit 6 iterates flat, bits 26:25 pick vertex 0, 1, 2 or the smooth iteration only with bit 21 set, and DOUTI0 bits 29 and 30 signal the last iteration and the last fetch that DOUTU1 bits 24 and 25 wait for: a wait with no matching signal hangs the job, and a signal with no wait leaves the attribute holding leftovers of earlier tasks (or hangs the job, with a fetch)"
unit = "pds"
method = "probes of probes/pds/iteration-waits.toml (persp-bits, persp-w1, iter-shade, iter-done29, iter-done29-fetch, iter-bit30, iter-nofetch, iter-wait24 and its variants) on the laptop, linux fork with the debug option on: the 64x64 triangle with a vertex shader giving w = x + 2 (1.25, 2.75, 1.625) and its x as coordinate set 1, the pixel PDS program issuing the iteration (and the fetch, in the cases that have one) with DOUTI0, DOUTI word 1 and DOUTU1 from the case, every pixel read back and fitted; every table ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-iteration-waits", "pds-iteration-sources", "pds-iteration-waits-followup"]
terms = [
    "DOUTI0.PERSPECTIVE", "DOUTI0.SHADEMODEL", "DOUTI0.FLAT", "DOUTI0.LAST_ITER",
    "DOUTI0.LAST_FETCH", "DOUTI.PERSPECTIVE", "DOUTI.SHADEMODEL", "DOUTI1.FLAT",
    "DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH", "DOUTI0.FIXED_OUT", "DOUTI0.F16",
]
+++

**What runs.** The vertex shader gives each vertex its x (-0.75, 0.75, -0.375 at the three
vertices) as coordinate set 1 and w = x + 2, so an affine iteration returns each pixel's own x
and a perspective-correct one does not. The pixel shader writes the first primary attribute
out. A case supplies DOUTI0, DOUTI word 1 and the task's DOUTU1; 1062 pixels are in the
triangle and each is read back.

**Results.**

- Perspective (persp-bits). The base case (source 1 with a fetch, nothing else) is affine: every
  pixel holds its own x, error 1e-16 against the affine fit and 0.29 against the
  perspective-correct one. With bit 24 set every pixel fits the perspective-correct iteration
  of the vertices' x, error 1.2e-7, and no longer the affine one (0.29). Bits 17, 19, 20, 25, 26,
  29 and 31 change nothing; bit 21 gives -0.75 at every pixel and bit 18 the wrapped values of
  E047.
- DOUTI word 1 (persp-w1), every bit alone: bit 6 gives every pixel -0.75 (vertex 0's x, a flat
  iteration); the other 31 bits change nothing.
- Shade model (iter-shade, with U1 bit 24 and the completion bit 29). With bit 21 clear,
  bits 26:25 = 0, 1, 2 and 3 all give the smooth x (47 distinct values, affine fit exact). With
  bit 21 set, 0, 1 and 2 give every pixel the value of vertex 0, 1 or 2 (-0.75, 0.75, -0.375)
  and 3 gives the smooth x.
- Completion bits, U1 bits 24 and 25 against DOUTI0 bits 29 and 30.

  | case | outcome |
  |---|---|
  | no fetch, bit 29, U1 bit 24 | the iterated value (x, or the window position for source 0) |
  | no fetch, bit 29, U1 bit 25 | hang |
  | no fetch, bit 29, neither bit | leftovers (window-position-like floats, 19.5 to 25.5) |
  | no fetch, no bit 29 or 30, U1 bit 24 | hang (every form tried) |
  | no fetch, no bit 29 or 30, no wait | leftovers |
  | fetch, bit 30, U1 bit 25 | the iterated value |
  | fetch, bits 29 and 30, U1 bits 24 and 25, or U1 bit 25 | the iterated value |
  | fetch, bit 30, U1 bits 24 and 25 | hang |
  | fetch, bit 30, U1 bit 24 alone | hang |
  | fetch, bit 29, U1 bit 24 | leftovers |
  | fetch, bit 30 clear, U1 bit 25 | hang |
  | fetch, bit 30 clear, no wait | leftovers |
  | fetch, bit 30 set, no wait | hang |

  With U1 bit 24 and no fetch, the word 0x37c00800 gives half floats (the pixel pairs
  0xb9e0b9e0, 0xb9e0b9a0, 0xb9a0b9e0 on a few pixels, as in E047's bit 28), and the two-component
  word 0x20400800 gives the same x as source 1.

Both runs agree on every hang, every iterated value and every flat value. They differ only in
the leftover cases (four of them: bit 30 clear with the fetch and no wait, bit 29 with the
fetch and U1 bit 24, bit 29 with no wait, and the cases of iter-nofetch), where the attribute
holds whatever earlier tasks left, so the counts of each leftover value vary from run to run.

**Not shown.** The table gives what the pixels look like, not which unit raises a hang. Whether
other programs set these bits as these cases do is not tested here. The visibility counters
stayed at 0.
