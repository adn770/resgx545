+++
id = "E287"
claim = "The MTE clips the triangle at clip z = -w and z = w: at w 1 a flat triangle at clip z from -1 to 1 draws whole and one at -1.01, 1.01 or beyond is removed, and a sloped one is cut where its z passes -1 or 1; the depth the viewport makes is not clipped: a z offset of -0.5 to 1.5 draws the whole triangle under depth always; against a clear depth a depth above 1 compares as itself (1.01 and 1.5 pass greater than 1.0) while a negative one compares as 0 (-0.01 and -0.5 fail less than 0.0 and pass less than 1.0); each probe ran once"
unit = "mte"
method = "probes/mte/depth-range.toml and depth-range2.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with its clip z set by vtx_zab.s (z = A x + B; the first table's program named the wrong second phase and hung every case, depth-range2 runs it fixed), and with the viewport's z offset (state-block word 10) from -0.5 to 1.5 under depth always, less against the clear depth 1.0, greater against 1.0 and less against 0.0 (render command word 14), with depth writes off; every pixel read back; one run each"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["mte-depth-range", "mte-depth-range2"]
terms = ["VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE", "ISP0.DCMP_MODE", "CR_ISP_BGOBJDEPTH"]
+++

**What runs.** `mte-depth-range2-clip`: a flat triangle at clip z -2, -1.5, -1.01, -1, -0.5, 0,
0.5, 1, 1.01, 1.5 and 2 (w 1), and sloped ones, z = 2x, 4x, 2x + 1 and 2x - 1 over the triangle's
clip x from -0.75 to 0.75. `mte-depth-range-viewport` and `-viewport-less`: the job's flat
triangle (clip z 0) with the viewport's z offset at -0.5, -0.01, 0, 1, 1.01 and 1.5 and the z
scale at 0.5, depth always and less against 1.0. `mte-depth-range2-clamp`: the offset at 1.5 and
1.01 under greater than the clear depth 1.0, -0.5 and -0.01 under less than 0.0, with controls
(0.9 greater than 0.8, 0.1 less than 0.2). `mte-depth-range-clip`, in the first table, hung all
15 of its jobs: its vertex program's first instruction named instruction 10 as the second phase,
which sits at 11 (isp_words.py's tests now check every table's vertex programs for this).

**Results.**

- Flat: 1062 pixels at clip z -1 to 1, none at -2, -1.5, -1.01, 1.01, 1.5 and 2.
- Sloped: z = 2x keeps 906 pixels, the columns from 16 on (clip x from -0.5); 4x keeps 472
  (columns 24 to 39); 2x + 1 keeps 714 (columns up to 31, where z reaches 1); 2x - 1 keeps 348
  (columns from 32).
- Viewport offset, depth always: 1062 pixels at every offset from -0.5 to 1.5. Less against 1.0:
  1062 at -0.5, -0.01 and 0; none at 1, 1.01 and 1.5.
- Clamp probe: greater than 1.0 draws at 1.5 and 1.01; less than 0.0 draws at neither -0.5 nor
  -0.01; both controls draw.

**What it shows.** The clip volume's z bounds are -w and w: a triangle wholly past one is removed
and one crossing it is cut along it. The viewport's z offset and scale come after the clip, and
their result is not clipped to [0, 1]. A depth above 1 reaches the depth test as it is, and a
negative depth as 0 [infer: from two values each side, consistent with a clamp of the negative
side only]. That answers the first part of Q069.
