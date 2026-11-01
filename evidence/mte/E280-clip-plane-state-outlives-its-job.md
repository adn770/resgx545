+++
id = "E280"
claim = "A user clip plane's state, set by fdpc on cpN, outlives the job that set it: after a job whose fdpc put every vertex outside plane N (-w), later jobs with that plane enabled and no fdpc are removed until an fdpc puts the vertices inside (+w) again, in planes 0, 1 and 2 and both runs; while the state is inside, the vertex's distance dwords o4 and o5 at -1 or +1 remove nothing with plane 0, plane 1 alone or planes 0 and 1 enabled (and o6 nothing under plane 1 alone with a 7-dword vertex); no run varies a distance dword under plane 2 with its state inside, and plane 2 alone was removed until its state was first set inside"
unit = "mte"
method = "probes/mte/clip-plane1.toml, clip-plane-state.toml and clip-plane-dist.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with OUTSEL (state-block word 13) at 0x53001, 0x63002, 0x63003, 0x73002 and 0x73004 and 5- to 7-dword vertices (vtx_fdpc.s and vtx_fdpc10.s write o4-o6 and run fdpc on cp0, cp1 or cp2 with the plane -w or +w), each probe's cases one job after another in order; the shader writes 0xff00ff00; every pixel read back; the state and distance probes twice"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["mte-clip-plane1", "mte-clip-plane-state", "mte-clip-plane-dist"]
terms = ["OUTSEL.PLANES"]
+++

**What runs.** `mte-clip-plane1-six` (0x63002, plane 1 alone, 6-dword vertex) sets o4 and o5 to
each pair of signs; `-seven-p2` (0x73002) and `-seven-p4` (0x73004, plane 2 alone) set o4, o5
and o6 with one or all at -1; `-fdpc` runs fdpc on cp1 or cp0 under 0x63002. The state probes
run seven jobs in order per plane: no fdpc, fdpc -w, no fdpc, fdpc +w, no fdpc, fdpc -w, no fdpc,
with every distance dword at +1. The distance probes first set each enabled plane's state inside
(fdpc +w), then run jobs without fdpc with o4 and o5 at each pair of signs, then fdpc -w, a job
without fdpc, and fdpc +w.

**Results.** "Drawn" is the triangle's 1062 pixels, "removed" an image of background only.

- Plane 1 alone, 6-dword vertex: drawn for (o4, o5) = (+1, +1), (-1, -1), (+1, -1), (-1, +1),
  both runs. 7-dword vertex, 0x73002: drawn in all five cases; 0x73004: removed in all five, both
  runs. fdpc under 0x63002 (one run): cp1 -w removed, cp1 +w drawn, cp0 -w drawn.
- State, planes 0, 1 and 2 alike from job 1 on, in both runs:

  | job | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
  |---|---|---|---|---|---|---|---|
  | fdpc | none | -w | none | +w | none | -w | none |
  | image | as left | removed | removed | drawn | drawn | removed | removed |

  Job 0, which inherits what the jobs before it left, was removed for planes 0 and 2 in both
  runs, and for plane 1 drawn in the first run (`mte-clip-plane-state-p1`) and removed in the
  second (`-p1-r2`): the state the jobs before it left on cp1 differed between the runs.
- Distance, both runs: with the state set inside, every job without fdpc draws, whatever the sign
  of o4 (plane 0), of o4 and o5 (plane 1 alone, planes 0 and 1); fdpc -w on cp0 or cp1 removes
  the triangle, the next job without fdpc is removed too, and fdpc +w draws again. These probes
  enable plane 0, plane 1 or both and write o4 and o5 only: plane 2 is not enabled in any of
  them, and in `-seven-p4`, the only probe that varies a dword with plane 2 alone, its state was
  outside throughout.

**What it shows.** fdpc's clip result is held per plane past the end of the job, so a job that
runs no fdpc inherits whatever the last fdpc on that plane left, through the jobs of other
tables and the baseline renders between them (none of which enables a plane). In these runs the
distance dwords after the position decide nothing for planes 0 and 1; for plane 2 that is not
measured. That explains why the earlier user-clip-plane
records saw plane 1 alone removed in one session [infer]: the plane's held state, not o4 or o5.
Where the state is held, what resets it, and under which conditions the distance dwords count
(E198 saw o4 at -1 remove plane 0's triangle between two jobs without fdpc) are open (Q039).
