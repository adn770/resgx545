+++
id = "Q291"
question = "does the 1.25 band of the ZLS store (x + 0.5 < 1.25 W, y + 0.5 < 1.25 H, E730) apply to the iterated attributes, that is, does a pa0 iterated clip x run at the same sizes store the same band"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E730", "E465"]
terms = ["CR_ISP_ZLSCTL"]
+++
Split on 2026-11-10 from Q287, whose last clause it was. E730 ran the band on the depth store only
(12 of 12 jobs at widths 18, 34, 50, 66, 98 and heights 18, 26, 34, 50), so what an iterated
attribute does at the band is not shown: the same band, a different one or none.

To settle it: a pa0 iterated clip x run at the sizes of Q287's run (widths 17, 19, 33, 35, 32 and
64, heights 17, 19, 21), reading the stored attribute at and beyond x + 0.5 = 1.25 W. Predicted
before the run: the band of the depth store, the floor of x + 0.5 < 1.25 W, i.e. x < ceil(1.25 W
- 0.5).

Status: open. Touches Q122 (the edge) and Q287 (the depth rule, which closes first).
