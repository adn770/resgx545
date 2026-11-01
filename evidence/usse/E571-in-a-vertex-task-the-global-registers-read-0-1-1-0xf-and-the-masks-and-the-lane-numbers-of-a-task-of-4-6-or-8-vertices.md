+++
id = "E571"
claim = "In the vertex task of the triangle job (126 vertices at 4, 6 and 8 vertices a task, 12 jobs), 125 of the 126 vertices of each job read in full (vertex 67 is cut by the 4 KiB boundary at 0x2000: its first nine dwords read 0 in all 12 jobs): g16, g19, g26-g31 and g40 read 0 and g20 1 on 125 of 125, g42 reads 0x3f800000, and g41 0xf and g43 0xdf000000 (where the pixel task has 1 and 0xff000000) on every vertex of a task of 4 or more, a last task of 2 vertices reading 0x3 and 0x20000000; g17, g22, g24, g25 and g39 follow the vertex's task and lane (g25 = lane mod 4, g22 = lane div 4 mod 2, g39 = 4 * g22, g24 = 8 * (task mod 2), g17 = task mod 4) in 125 of 125 vertices in each of the 12 jobs (24 of 24 job-register scores, 12 of them held out at 4 and 6 vertices a task), and g23 = 0x10 * (task div 2 mod 2) in 125 of 125 in each of the 4 jobs that read it, a rule read from the data after all 12 jobs were in"
unit = "usse"
method = "script tables q053-vtx (6 jobs: groups A g16-g23, B g24-g31, C g39-g43 with g17-g19, twice, VDM_TASK0 MAX_VERTICES 7 = 8 a task) and q053-vtx2 (6 jobs, declared after the first, at fields 3 and 5 = 4 and 6 a task), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed equal to loaded at the start of every script, never reloaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written: the vertex program (own assembly) moves 8 global registers into the vertex outputs o6 to o13 and a job marker constant into o14, 126 vertices (--vertices 126, --vtx-coords 11), the vertex words read from the parameter buffer dump; read again in a fold of the review with its own decoder, a scan of the dump for the job's marker constant (a vertex is the 12 dwords that end at one, the vertices in ascending address order are the draw's sequence)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["usse-globals-vertex-eot", "vectors-usse-globals-vertex"]
terms = []
+++

**What ran.** 12 jobs, all completed, each with its own marker constant in o14. The marker is in the
parameter buffer 126 times in every job (12 dwords apart within an object, 64 between 8 pairs of
objects, 1036 once). 125 vertices read in full. Vertex 67, at 0x2008, is cut by the 4 KiB boundary
at 0x2000: its first nine dwords, below it, read 0 in all 12 jobs, and its last two before the
marker, in the page that starts there, hold what the rules below give where they are not 0 anyway
(g18 0x16 or 0x12 in the group C jobs, g23 0x10 in one group A job); it is skipped here and in the
vectors. An earlier reading of the same dumps found 119 readable vertices and counted 118 to 119 of
119 in each score, with vertices 60 to 66 as "unreadable": that was a fault of its object decoder
(those seven sit at 0xeb8 to 0xfd8 with full records), not hardware, and the 118 of 119 scores were
vertex 67 alone.

**Declared and hashed.** q053-vtx ran at 03:27:07; its table and the base declared files have a
modification time of 03:29:58, after the run, and the hashes were written at 03:36:48. The
held-out jobs (q053-vtx2, at 4 and 6 a task) were declared at 03:36:48, with their hash recorded
then, and ran at 03:38:00; that declaration does precede its run.

**Constants.** [HW] On 125 of 125 vertices of every job: g16, g19 (by the mov), g26 to g31, g40
read 0; g20 reads 1; g42 reads 0x3f800000. g41 reads 0xf and g43 0xdf000000 (the pixel task's g41
is 1 and g43 0xff000000, E374) on 125 of 125 at 8 and at 6 a task, and on 123 of 125 at 4 a task:
the last task of the draw holds 2 vertices there (126 = 31 * 4 + 2), and both (vertices 124 and
125) read g41 0x3 and g43 0x20000000. At 8 a task the last task holds 6 (vertices 120 to 125) and
reads 0xf and 0xdf000000. So g41 and g43 are measured with 2 vertices held and with 4, 6 and 8, and
not with 1, 3, 5 or 7 [infer: that the first quad's mask and a g43 that is 0xdf000000 less the
lanes missing is the rule; two measured values fit it]. g19 here is a mov source as in E372, which
read 0x11 through the bitwise group and 0x1a as a store's source: only the mov was run in a vertex
task.

**Per vertex.** [HW] With v the vertex's number over the objects in address order, V the vertices
a task holds, task = v div V and lane = v mod V: g25 = lane mod 4, g22 = (lane div 4) mod 2,
g39 = 4 * g22, g24 = 8 * (task mod 2), g17 = task mod 4. The rules were fitted to the 6 jobs of 8
a task (q053-vtx) and declared for the 6 jobs of 4 and 6 a task (H53-Q, against H53-F: the same
registers by a fixed grouping of 4 and 8 whatever V: g25 = v mod 4, g22 = (v div 4) mod 2,
g24 = 8 * ((v div 8) mod 2), g17 = (v div 8) mod 4). Each job reads two of the five registers
(24 job-register scores): H53-Q is right on 125 of 125 vertices in all 24, including all 12 of the
held-out jobs. H53-F is right in 12 of the 12 scores at 8 a task (they are the fit) and in 1 of the
12 held-out scores, g25 at 4 a task, and gives 29 to 66 of 125 in the other 11. That one score
does not discriminate: for a V that is a multiple of 4, lane mod 4 equals v mod 4, so g25 is the
same under both rules at 4 and 8 a task; at 6 a task it is not (H53-F gives 36 to 66 of 125 there).

g23 = 0x10 * ((task div 2) mod 2) (the task sequence 0, 0, 0x10, 0x10, repeating) is right on 125
of 125 in each of the 4 jobs of group A (8, 8, 4 and 6 a task). It was read from the q053-vtx jobs
after all the data were in hand and was not declared: the 4 and 6 a task jobs fit it, and they are
not a prediction. g18 and g21 follow the task too and have no rule here: g18 per task at 8 a task
reads 0x14, 0x16, 0x16, 0x16, 0x12, 0x14, 0x14, 0x14, 0x16, 0x12, 0x12, 0x12, 0x10, 0x10, 0x10,
0x10 and g21 0x1d, 0x1f, 0x1f, 0x1f, 0x1c, 0x1e, 0x1e, 0x1e, 0x1f, 0x1d, 0x1d, 0x1d, 0x1e, 0x1c,
0x1c, 0x1c. Their ranges depend on V: g18 0x10 to 0x16 and g21 0x1c to 0x1f at 8 a task, g18 0xe to
0x16 and g21 0x1a to 0x1f at 4, g18 0xe to 0x16 and g21 0x1b to 0x1f at 6; at 6 a task g18 reads
differently in the group A job and the group C job in 2 of the 21 tasks (16 and 20).

**Not shown.** What sets g18 and g21; whether g41 and g43 depend on the vertices a task holds as
the two partial tasks suggest or on their quads [infer]; whether g23 keeps its rule at other V; the
global registers of a vertex task of another program or a task that reads more than the first set
of inputs.

**In the simulator.** The vertex task's registers above are modelled (sgx-sim `Machine::vertex`) and
checked against the 12 jobs as vectors (vectors-usse-globals-vertex: every vertex but 67, the
outputs and the marker). The model refuses what was not measured: g0 to g15, g18, g19, g21, g32 to
g38 and g44 to g63, a draw of other than 126 vertices, a task of other than 4, 6 or 8 vertices, and
g41 and g43 with 1, 3, 5 or 7 vertices held.
