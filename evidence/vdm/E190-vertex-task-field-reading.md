+++
id = "E190"
claim = "VDM_TASK0 bits 31:28 are the number of vertices per vertex task less one, a reading that fits the values 0, 1, 2, 5 and 6 and is not told apart from a cap on a task's quads at 3, 7 and 15"
unit = "vdm"
method = "reading of the vertex-task quads of E189 (the reading is ours, no public source is cited: the tree holds no citation record for one); one run of each field value on the laptop, linux fork with the debug option on"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["vdm-vertex-tasks"]
terms = ["VDM_TASK0.MAX_VERTICES"]
+++

**Reading.** Bits 31:28 of `vdm:6` change how the vertices of a job are split into vertex tasks
(E189), which makes a limit on a task's size a candidate reading. What the data of E189 show is the
following.

**Results.** With the field at 1, 2, 5 and 6 the 126 vertices form tasks of 2, 3, 6 and 7 vertices,
that is the field plus one; at 0 the vertices form tasks of one vertex and the job hangs after 18
(E189). At 3, 7 and 15 every quad is full. So the reading "vertices per task less one" holds for the
five values that can be told, and for 3, 7 and 15 it is a prediction the data do not contradict:
tasks of 4, 8 and 16 vertices give the same quads as any larger limit would.

**Not shown.** That the field counts vertices and not instances in some other sense is not
separated: every measured task size is a count of vertices. One run per value.
