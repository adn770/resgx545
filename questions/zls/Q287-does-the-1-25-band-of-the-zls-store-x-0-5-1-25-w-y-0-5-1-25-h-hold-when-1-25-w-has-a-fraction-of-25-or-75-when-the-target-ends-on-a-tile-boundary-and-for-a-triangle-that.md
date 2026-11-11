+++
id = "Q287"
question = "does the band of the ZLS store follow rule A (x + 0.5 < 1.25 W, y + 0.5 < 1.25 H) or FLOOR (x < floor(1.25 W)) when 1.25 W or 1.25 H has the fraction .75 (W or H = 3 mod 4, the only sizes that separate them; .25 is a confirmation), sizes the tool refuses as odd (the iterated attributes are Q291)"
unit = "zls"
kind = "hw"
value = "low"
phase = 11
evidence = ["E730", "E465", "E831"]
terms = ["CR_ISP_ZLSCTL"]
+++
E730: 12 of 12 jobs at widths 18, 34, 50, 66, 98 (2 mod 4, so 1.25 W is x.5) and heights 18, 26,
34, 50 (all 2 mod 8). To settle it: widths 17, 19, 33, 35 and heights 17, 19, 21 (1.25 W with a
.25 or .75 fraction), widths 32 and 64 (band outside the tile area), a triangle with vertices
inside the band (so the hypotenuse, not the band, bounds it); the pa0 iterated clip x run is Q291's. Predicted before the run: the floor of x + 0.5 < 1.25 W, i.e. x < ceil(1.25 W - 0.5).

Status: open. Narrows Q122 (the rule at the tested alignments); touches Q199 (the MTE clip).

**Correction 2026-11-10:** narrowed to depth. The clause "does it apply to the iterated
attributes", the pa0 iterated clip x run, is split off as Q291 (E730, E465); Q287 closes on the depth rule once that run has held.

**Narrowed 2026-11-11 (R3-geo-c g-z, E831).** The question line was "does the 1.25 band of the ZLS
store (x + 0.5 < 1.25 W, y + 0.5 < 1.25 H) hold when 1.25 W has a fraction of .25 or .75, when
the target ends on a tile boundary and for a triangle that does not cover the band". Two of its
three clauses are answered held out at even sizes (E831): rule A gave the stored set in 10 of 10
full-screen cells (W 20, 36, 44, 76, 32, 64 at H 18; H 20, 28, 36, 32 at W 34), ROUND and CEIL
refuted 10 of 10, RSTRICT 6 of 10; where the band passes the tile area (W 32 and 64, H 28 and 32)
the store stops at the last tile and writes nothing past the target's tiles (post hoc, 15 of 15
dumps); two single triangles inside and across the band stored exactly their own raster cut by
the band. At every even size rule A and FLOOR give the same set, so what is left is the
fraction (each rule's extent, x below it):

| 1.25 W | W mod 4 | A | FLOOR | ROUND | CEIL |
|---|---|---|---|---|---|
| n | 0 | n | n | n | n |
| n + .25 | 1 | n | n | n | n + 1 |
| n + .5 | 2 | n | n | n + 1 | n + 1 |
| n + .75 | 3 | n + 1 | n | n + 1 | n + 1 |

To settle it: widths 19 and 35 at H 18 and height 19 at W 34 (the .75 cells), widths 17 and 33
and heights 17 and 21 as confirmations (.25), the 34 x 18 control; the tool refuses odd sizes
(`userspace/libsgxfive/src/render.c`, `width % 2 || height % 2`), so a tool change comes first.
Q122's rule (an edge tile past the target) is answered at even sizes by E730 and E831.
