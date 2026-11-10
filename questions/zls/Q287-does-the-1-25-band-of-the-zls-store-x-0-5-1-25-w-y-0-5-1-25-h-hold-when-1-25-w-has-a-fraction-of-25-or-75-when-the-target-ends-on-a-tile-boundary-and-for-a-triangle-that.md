+++
id = "Q287"
question = "does the 1.25 band of the ZLS store (x + 0.5 < 1.25 W, y + 0.5 < 1.25 H) hold when 1.25 W has a fraction of .25 or .75, when the target ends on a tile boundary and for a triangle that does not cover the band (the iterated attributes are Q291)"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E730", "E465"]
terms = ["CR_ISP_ZLSCTL"]
+++
E730: 12 of 12 jobs at widths 18, 34, 50, 66, 98 (2 mod 4, so 1.25 W is x.5) and heights 18, 26,
34, 50 (all 2 mod 8). To settle it: widths 17, 19, 33, 35 and heights 17, 19, 21 (1.25 W with a
.25 or .75 fraction), widths 32 and 64 (band outside the tile area), a triangle with vertices
inside the band (so the hypotenuse, not the band, bounds it); the pa0 iterated clip x run is Q291's. Predicted before the run: the floor of x + 0.5 < 1.25 W, i.e. x < ceil(1.25 W - 0.5).

Status: open. Narrows Q122 (the rule at the tested alignments); touches Q199 (the MTE clip).

**Correction 2026-11-10:** narrowed to depth. The clause "does it apply to the iterated
attributes", the pa0 iterated clip x run, is split off as Q291 (E730, E465); Q287 closes on the depth rule once that run has held.
