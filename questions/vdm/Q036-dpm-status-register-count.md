+++
id = "Q036"
question = "what do the DPM status registers 0x0700, 0x070c, 0x0710 and 0x071c count, when they change on every render but not as a running page count?"
unit = "vdm"
phase = 10
evidence = ["E184"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl"]
+++

Across three triangle jobs (one 64x64 render, two 64x64 renders in one context, one 256x256
render) the four registers change at every step and agree in pairs: 0x0700 with 0x070c, 0x0710
with 0x071c (E184). The first pair reads 0x00020003, 0x00040005 and 0x00010006, the second 1, 3
and 5. The first two steps add 2 to each half of the first pair and to the second pair, but the
third breaks that count (the first pair's high half falls from 4 to 1, the low half goes on to
6). So they do not read as a number of pages allocated across these steps, and E184 states no
count. The registers were named for the free list; what they hold is not read. One run.

To settle it: sample the four registers with regtimeline before, during and after renders that
use a known number of parameter-buffer pages (the 64x64 and 1024x768 triangles, the same job
twice in one context, then in a new context, and a job that overflows a small buffer), and save
the parameter buffer after each to count the pages that hold objects and region lists. Compare
each half of each register with the page count, the render count and the context's page offsets.
