+++
id = "Q205"
question = "what is the arithmetic by which the ISP decides the coverage and the depth of a pixel for an arbitrary triangle, and the iterators' arithmetic for the values they interpolate: the precision of the edge functions, the rounding of the plane equation, the rule for a pixel centre exactly on an edge outside the sample-position case, and the ulp behaviour of the plane evaluation?"
unit = "isp"
kind = "hw"
value = "high"
phase = 12
evidence = ["E023", "E148", "E174", "E307", "E048", "E072", "E214", "E215", "E542"]
terms = ["CR_ISP_MSAA", "CR_TE_AA"]
+++

No record or question gives the arithmetic of coverage and depth for an arbitrary triangle. What is
settled: the triangle is "exact" against a CPU reference in E023, E148 and E174 (the first
triangle, 13 and 16 target sizes, to 4096 x 4096), the 24 random triangles of E307 test which
regions the TA lists, not which pixels the ISP draws, and E542 settles which 16 x 16 tiles list a
primitive. Depth compares exactly to the ulp (E072) and the sample positions and the tie rule for
the sample-position case were measured (E214, E215, 11.8). The iterators' values agree with the
exact iteration to a maximum error of 1.2e-7 (E048, a tolerance, not a rule).

What is open, for a simulator that is pixel exact (the phase 12 bar: zero mismatch against the
recorded images):

- the precision and the rounding of the edge functions (fixed point or float, the width of the
  fraction in a sub-pixel coordinate), and the rule when a pixel centre lies exactly on an edge
  other than in the sample-position case;
- the rounding of the plane equations of depth and of the iterated values (how the three
  vertices' values become a plane, and how a pixel's value is read from it);
- whether the result for a very thin, very small or off-target-partly triangle follows the same
  arithmetic (the clipped scenes of E063 and E287 give pixel counts, which only such a rule
  reproduces).

To settle it: a sweep on the laptop of random sub-pixel triangles on 64 x 64 and 128 x 128
targets (and the ties: vertices on the sample grid, edges through pixel centres), through the
existing `tri` tool with `--vertices` and `--pixels`, the images and the depth read back (a depth
buffer dump, E465's layout), analysed offline against candidate fixed-point models; the 12.3
gate of the phase 12 plan. Until it is answered the pipeline simulator refuses an ISP result for a
triangle it cannot reproduce and reports the rate of those it can.
