+++
id = "Q291"
question = "does the 1.25 band of the ZLS store (x + 0.5 < 1.25 W, y + 0.5 < 1.25 H, E730) apply to the iterated attributes, that is, do the pixel tasks of the tile area past the target run with an iterated pa0 (clip x) over the same band, read through per-instance scratch stores since the colour store ends at the target"
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

Reworded 2026-11-12 (round 6 housekeeping, decision R6-1 a). The band lies past the target, where
the colour store writes nothing, so an iterated attribute there cannot be read through the image:
it is read through a per-instance store of each instance's iterated value to scratch, at the
pixels of the tile area past the target (the `--pixels` form of E606). The plan the round 6
ranking froze for it (R6-2): the clip x probe at 34 x 18, 34 x 19 and 34 x 23, reading rows 19 to
31 of the tile area, predicted to show the depth band's rows [infer: a guard-band clip, E730];
not run.
