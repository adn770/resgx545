+++
id = "E095"
claim = "fdpc's clip-plane result has no visible effect with the TA state our kernel sets by default: a vertex shader that runs fdpc against a plane every vertex is outside of (cp0 and cp5, the plane (0, 0, 0, -1)), inside of, or that splits the triangle by x still draws the control's image, 1062 triangle pixels and 3034 background"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/mte/user-clip-planes.toml, probe fdpc-clip, the triangle's vertex shader with six instructions after the position load (four load a plane into r4-r7, then fdpc.skipinv.repeat4 r8, cpN, pa0, r4 or a nop in the control), a 64x64 render; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["mte-user-clip-planes"]
terms = []
+++

**What runs.** Five cases with the default render state (no change to the output-select
word): the control with `nop`s, `fdpc cp0` against the plane (0, 0, 0, -1) (every vertex
outside, -w), `fdpc cp0` against (0, 0, 0, 1) (every vertex inside), `fdpc cp5` against
(0, 0, 0, -1), and `fdpc cp0` against (1, 0, 0, 0), which splits the triangle by x.

**Results.** All five cases draw the control's image: 1062 pixels of the triangle colour
(0xff00ff00) and 3034 background pixels (0xff203040).

**Not shown.** With the default state fdpc's result goes nowhere this scene shows: the
related probes of the same table (E096) turn a plane on by the output-select word and then
the result does remove the triangle. One run.
