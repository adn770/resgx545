+++
id = "E052"
claim = "A scene accumulates the geometry of several TA kicks that carry no end-of-scene: the first job that ends the scene renders all of them (2 kicks: 1730 triangle pixels, 625 of them from the first kick; 3 kicks: 1794, 695 more from the earlier two), and the next render is a scene of its own triangle only whatever BIT2, NO_DEALLOCATE or BIT10 the closing render carried; both rounds agree"
unit = "render"
method = "hand-run script probes/render/templates/scenes.sh (geometry-kicks and kicks-parameter-buffers) on the laptop, linux fork with the debug option on: sgxfive-test tri with --geometry N jobs, triangles 12 pixels apart, kernel pokes of the render flags, two rounds of the first group"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-scenes"]
terms = ["GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK", "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "FRAG_FLAGS.BIT10"]
+++

**What runs.** A job submitted with the geometry flag (`--geometry N`) is a TA kick that does
not end the scene: it completes when its TA does, and the tool reports "geometry only, the
scene left open". The next job adds to the same scene, and the first job without the flag
renders the scene and closes it. Pixels of an earlier triangle in a later image count as "wrong
outside" its reference. The script runs ten cases, twice, and a second group (one, two and
three kicks, with the parameter buffer dumped) once.

**Results.**

- The control, two jobs of one triangle each: 1062 and 1046 triangle pixels, 0 outside.
- Kick 1 geometry, job 2 closing: job 2 stores both triangles, 1730 triangle pixels, 625 outside
  (the first kick's). Kicks 1 and 2 geometry, job 3 closing: 1794 triangle pixels, 695 outside.
  The group with the triangles at other offsets gives 1730 / 625 for two kicks and 2026 / 1074
  outside for three, so each kick adds its triangle.
- With the triangles of render 2 moved 12 pixels right (render 3 12 down), job 2 closing gives
  1548 triangle pixels, 459 outside, and job 3 gives 1054 triangle pixels, 0 outside: render 3
  is a scene of its own triangle only. It does so whether job 2 carried BIT2, NO_DEALLOCATE,
  both, or BIT10 cleared, and whether job 3 had FIRST_KICK set or cleared (seven cases).

**Not shown.** The runs do not show what BIT2 and NO_DEALLOCATE keep: without a render of the
same scene again, neither changes an image. The kernel rewrites the render target data's size
words and counters before each job, and whether a firmware path that keeps a scene across
renders depends on them is not looked at. E053 asks the same question with no new geometry.
