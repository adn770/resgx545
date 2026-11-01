+++
id = "E189"
claim = "VDM_TASK0 bits 31:28 set how many vertices one vertex task takes: with 126 vertices, values 1, 2, 5 and 6 give tasks of 2, 3, 6 and 7 vertices in index order, each ending early when its last quad is short of vertices, values 3, 7 and 15 fill every quad of four, and 0 gives single-vertex tasks for 18 vertices and then hangs the job"
unit = "vdm"
method = "the probes vdm-vertex-tasks-vtxtask-NN of probes/vdm/vertex-tasks.toml (vtx_task.s, 126 vertices, field set through vdm:6), on the laptop with the linux fork and the debug option on, one run each, the quads read back with tools/sweep/vtx_tasks.py"
tiers = ["HW"]
date = "2026-11-01"
data = ["vdm-vertex-tasks"]
terms = ["VDM_TASK0.MAX_VERTICES"]
+++

**What runs.** The triangle job is given 126 vertices (42 copies of the triangle, `vertices = 126`)
and the vertex program `vtx_task.s`. Every valid instance stores its own x and the x of the
instances one to three places on in its quad of four (a sentinel where an instance is empty) to a
scratch slot that its x and y pick. Every vertex has its own x, so the stored words say which
vertices shared a quad. A vertex task fills quads of four in vertex order, so the quads show where
tasks end: a quad short of vertices ends a task. The field is `vdm:6` bits 31:28 (15 in the job),
set to 0, 1, 2, 3, 5, 6, 7 and 15 by XOR, one probe each.

**Results.** The quads, as vertex indices:

| field | quads | vertices per task |
|---|---|---|
| 15, 7, 3 | 0-3, 4-7, ... 120-123, 124 125 | 4 or more |
| 6 | 0-3, 4 5 6, 7-10, 11 12 13, ... 123 124 125 | 7 |
| 5 | 0-3, 4 5, 6-9, 10 11, ... 124 125 | 6 |
| 2 | 0 1 2, 3 4 5, ... 123 124 125 | 3 |
| 1 | 0 1, 2 3, ... 124 125 | 2 |
| 0 | 0, 1, 2, ... 17 | 1 |

For 6, 5, 2 and 1 every task takes the field plus one vertices. Every probe that completed drew the
same image, 1275 pixels of the probe's colour and 2821 background. The field 0 probe did not
complete: it reported "job hung, context lost" and the scratch slots hold the single-vertex quads of
vertices 0 to 17 and none after. The same field values leave the three-vertex triangle's TA output
unchanged (E060), and three probes that replace the pixel program by a copy of o0 (fields 7, 1 and 0
on the 64x64 triangle) wrote byte for byte the same parameter buffer and TA data. Their images
differ in 24 pixels between field 1 and fields 0 and 7 (3792 and 3768 pixels of one colour); the
pixel program shows registers it never wrote, as in E060, so those counts are not fixed numbers.

**Not shown.** With fields 3, 7 and 15 every quad is full, so tasks of 4 and of 8 or 16 vertices
look the same: the size of a task above 7 vertices is not measured, and a task of 8 or 16 for fields
7 and 15 is a reading, not a count. A task boundary is seen only where a quad is short, so a task
that ends on a quad boundary is not told from two. The hang at field 0 is seen at 126 vertices; a
triangle whose three vertices are in three tasks may be what fails, which this table does not
separate from the task count. One run per field.
