+++
id = "E418"
claim = "Plane 0's held clip result survives a job that hangs and the reset after it: with fdpc having put every vertex outside (a job drew nothing) the next jobs without fdpc were removed before the hang and after it (2 of 2 runs), and with fdpc having put them inside the next jobs drew before and after the hang, with the distance dwords at -1 and +1 changing nothing (2 of 2 runs each); fdpc with the vertices inside cleared the held outside result (2 of 2)"
unit = "mte"
method = "probes/mte/plane-reset.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the plane 0 probes of probes/mte/clip-plane-state.toml and clip-plane-dist.toml as three sequences of jobs, each job a fresh process, one of them hanging (VDM state word 1 bits 15:13 = 0), each sequence twice: A) hang, then the distance dword o4 at -1 and +1 without fdpc; B) fdpc outside, no fdpc, hang, no fdpc, fdpc inside, o4 -1, o4 +1; C) fdpc inside, hang, o4 -1, +1, -1 (34 jobs, 6 hangs)"
tiers = ["HW"]
date = "2026-11-07"
data = ["mte-plane-reset"]
terms = ["OUTSEL.PLANES"]
+++

**What was seen.** Sequence B, both runs: fdpc with the vertices outside plane 0 drew nothing (4096
background pixels); the next job without fdpc drew nothing; the hang followed (job hung, context
lost, GPU reset); the next job without fdpc again drew nothing; fdpc with the vertices inside drew
the triangle (1062 pixels) and so did the two jobs after it, o4 at -1 and at +1. Sequence C, both
runs: fdpc inside, the hang, then three jobs without fdpc, o4 at -1, +1 and -1, all drew the
triangle. Sequence A, run 1: after the hang the four jobs without fdpc (o4 -1, +1, -1, +1) all drew
nothing; in run 2, which followed sequence C of run 1 (held result inside), all four drew the
triangle. The first run of A followed a long series of hangs and resets (the day's earlier jobs).

**What it shows.** A GPU reset after a hang does not clear plane 0's held result: it stays outside
or inside across the reset, as E280 found across jobs. A held result outside after a boot and many
resets (sequence A, run 1) shows the same. With the held result inside the distance dword at -1
removes nothing, as E280. What clears the outside result is a job whose fdpc puts the vertices
inside.

**What it does not show.** Where the result is held (the MTE, the USE, per vertex or plane); whether
a firmware reload or a full power cycle clears it; planes 1 and 2.
