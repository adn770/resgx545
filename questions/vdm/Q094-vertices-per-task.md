+++
id = "Q094"
question = "what hardware capacity bounds VDM_TASK0.MAX_VERTICES as a function of the task's output rows and attribute rows (the captures have 15, 13, 9, 7 or 2), and what does a vertex task do when the field is above it?"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E346", "E546", "E702", "E703"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE"]
+++

Over 1888 captured index lists the field is 15 for most GLES2 draws (one to four output rows,
one attribute), 13 with eight vertex attributes and two output rows, 2 with nine output rows,
9 for every GLES1 draw (three output rows) and for GLES2's point-size shader (three), and 7 for
the clears and screen-space pieces (two output rows) (E346). A budget over the attribute and
output rows fits the eight-attribute and nine-output draws.

To settle it: capture shaders that step the outputs from one to nine rows and the attributes
from one to eight, one at a time, and on the laptop run our triangle with the field at the values
the closed driver picks and above them, with as many output rows, to see where a task overruns.

Narrowed in 11.21 to the hardware part. Why the closed driver picks 15, 13, 9, 7 or 2 for a draw is
the driver's own choice and not the target. Open: the limit the hardware puts on the vertices of
one task (the USSE output or attribute space, as a function of the output rows in VDM_TASK1 bits
31:24 and the attribute rows in 14:7), and the behaviour of a task that overruns it (a fault, a
hang, vertices dropped or overwritten). A budget over the attribute and output rows fits the
eight-attribute and nine-output draws. The capture alone does not give the limit. Related to Q092,
the
index list's trailing word. The laptop run named above settles it.

Narrowed in 11.31 (E546, 73 jobs): with 126 vertices and R output rows (R = ceil((4 + N) / 4) of N
coordinate outputs, VDM_TASK1 bits 31:24 [infer]) a vertex task of V = MAX_VERTICES + 1 vertices
keeps all vertices in regular objects when R * V <= 32 (31 of 31 jobs) and drops or splits some when
R * V >= 36 (21 of 21 jobs); at 33 it depends on the program (N = 5 and 8 regular, N = 6 irregular,
9 jobs). An overrun does not fault or hang: the objects take 3, 6, 9, 10, 12 or 16 vertices and the
sum is 93 to 130 (vertices dropped, or counted twice); the same job gives the same splitting (13 of
13). A dword budget is wrong (three decisive jobs). The attribute rows (VDM_TASK1 bits 14:7) enter:
at R * V = 33 rows 8 splits objects that rows 2 and 4 keep regular, at 36 rows 4 and above change
the split (vdm-vtask5, 12 jobs: 4 differ from the default rows), and at 32 rows up to 8 change
nothing (5 of 5). Open: the weight of an attribute row against an output row, the exact limit
between 33 and 35 and its dependence on N, which vertices are lost, and whether the image follows
the objects. Status: narrowed, not answered.

Reworded in 11.39: the comparison with GLES1's 10 vertices at three output rows against 16 at
four in the shader corpus is dropped from the first and the 11.21 paragraphs above (the closed
driver's choice is not the target, so the comparison tests nothing).

Narrowed in 11.39 (E702, E703, 26 jobs). At R * V = 33 (N = 8, 3 rows, 11 vertices) and 32
(N = 11, 4 rows, 8; N = 2, 2 rows, 16) the attribute rows 1 to 24 left the render unchanged in
13 of 15 completed jobs (the tool's o0 histogram). Two N = 8 jobs changed it: a = 7 (three
vertices read one constant row, 3 pixels differ) and a = 12 (every vertex identity present, 260
pixels differ), and E546's one lost vertex at 33 with 8 rows was not seen in the two a = 8 jobs
here (another module and tool). The three are alike, each one an event not yet repeated, pending a
repeat (Q272); no conclusion about a limit at 33 is drawn from them. By the vertex count the
budget in which attribute rows add (33 plus the rows over 8) was wrong in 10 of 15 jobs, and the
model in which they do not count in 1 (14 of 15 scored, 14 of 16 counting the job that hung at
32 rows). The rows field forced to a value other than the natural (4 + N + 3) / 4 changed the
render in 8 of 8 jobs at products from 30 to 40 (the decoder reads 76 to 95 of 126 vertices as
lost, a reading under a layout assumption); no job with the forced field equal to the natural
one exists, so the forcing is not separated from wrong rows and the forced-rows route cannot
place the limit between 33 and 36 (Q271); natural jobs reach 33 and then 36 or more only.
Status: narrowed, not answered; for a simulator: keep refusing natural-row jobs above 33, refuse
forced rows, and mark attribute rows 7, 12 and 32 as unmodelled.
