+++
id = "E322"
claim = "11.6's scenes of one, two and three TA kicks run again on the kernel that counts each kick: every context cleanup completes and the table's kernel log holds no reset, where the 11.6 run had reset the GPU for the scenes of several kicks; the parameter buffers and TA data dumped after the closing renders are byte for byte those of the 11.6 runs, and the images the same (1062, 1730 and 2026 triangle pixels); one run"
unit = "ta"
method = "probes/render/kick-objects-again.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script kick-objects-again.sh runs the scenes of probes/render/kick-objects.toml (sgxfive-test tri, the later kicks geometry jobs with their triangles moved) once, each scene's render memory dumped after the closing render and the context's cleanup trace after each; the dumps compared by hash with render-kick-objects"
tiers = ["HW"]
date = "2026-11-03"
data = ["render-kick-objects-again", "render-kick-objects"]
terms = ["hw_rt_data_set.executed_count", "control stream"]
+++

**Results.** One kick: 1062 triangle pixels; two kicks: 1730 (625 outside the closing render's
own triangle); three kicks: 2026 (1074 outside). Each cleanup trace ends with the PB step and
`ret 0`. The six dumps (parameter slot and TA data per scene) hash the same as the 11.6 runs'
(both of them).

**What it shows.** Counting each kick changes no image and no byte the TA writes, and removes
the cleanup failures and resets the scenes of several kicks caused [HW]. E288's reading of the
objects stands as recorded.
