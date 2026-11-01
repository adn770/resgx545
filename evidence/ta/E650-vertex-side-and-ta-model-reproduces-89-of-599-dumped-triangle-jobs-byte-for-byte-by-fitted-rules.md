+++
id = "E650"
claim = "A model of the vertex side and the TA written for the pipeline simulator (sgx-pipe vdm, vtx, mte, ta, render: the VDM stream parsed, each state block and each vertex of a vertex task run through its PDS program and USSE task on sgx-sim unchanged, the clip position through the viewport, then the object, the region headers and the control streams written) reproduces the parameter buffer pages 0x1000 to 0x6000 and the TA data headers of 89 of 89 dumped one- to five-triangle jobs on 64 x 64 to 256 x 256 targets with no differing dword (21229 non-zero dwords compared, 79 distinct expected buffer sets), every one by a fitted rule so none is reported matched; of 266 more built scenes the model refuses all, each naming what blocks it (lines Q159 and Q160 81, points Q161 26, a state word nobody flipped in a two-object stream Q047 and Q112 104, Q163 with Q047 and Q112 12, Q163 with Q112 5, Q112 alone 9, Q162 20, Q094 4, Q042 3, Q069 1, Q230 1) and none mismatches; the 89 are 25 percent of the 355 built scenes and 15 percent of the 599 dumped jobs, every one a job that keeps the library's pass-through vertex program, and the 130 two-object jobs of vdm-state-units contribute none; the jobs no earlier record described are 3 (ta-object-words 1, vdm-vtask-capacity 2), and the stream forms 0x88, 0x8a and 0x8c, the page order and the four non-square targets were read from no record before the replay"
unit = "ta"
method = "offline, no new run: tools/usse-asm/ta_scenes.py rebuilds each case's words (the render command, the five program and stream pages) with sgxfive-test --mock probe --tri --emit-scene and pairs them with the case's saved parameter buffer and TA data; the check against the dump is that the rebuilt state block's three pixel PDS words equal the dump's first three object dwords (E306: 332 of 332 where the dump has an object; the 23 culled dumps have none to check): a three-word consistency check of the state block, the same three words in every job, that cannot see a wrong vertex, viewport or index; what guards the rebuilt inputs is that the library under userspace/libsgxfive (last changed 2026-11-01 before the emit option) and the probe tables ta and vdm (last changed 2026-11-01) are unchanged since before the runs of 2026-11-02 and 2026-11-08 whose dumps are the expected words, and that the tsv tables carry the recorded command; cargo test --release -p sgx-pipe --test render_scenes replays them through the Rust model; the gate is zero mismatches and a dword the model writes inside a window that the hardware left 0 counts as one; rules written before the replay from E176 (the 23-dword object with its 8 packed dwords, checked as a unit test), E177, E180 and 3d.md 10; the stream forms, the allocation order and the header flags were then read from the ta-tri-region dumps (35 jobs: in sample); the tile test is E180's fit and E542's refit and the primitive word forms of E177 and E180, so ta-regions is also in sample for them"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["ta-tri-region", "ta-regions", "ta-objects", "ta-object-words", "ta-line-point", "ta-points", "ta-zero-words", "vdm-state-units", "vdm-vtask-capacity", "scene-vectors-12-2"]
terms = ["PB_OBJ.PDS_WORDS", "PB_OBJ.RHW", "PB_OBJ.ISP_WORDS", "PB_OBJ.PRIM_LIST", "PB_OBJ.FORMAT", "PB_OBJ.SET_MASKS", "CSTREAM.PRIM_TILES", "CSTREAM.OBJ_ISP_ADDR", "REGION_HDR.POS", "REGION_HDR.FLAGS", "REGION_HDR.STREAM"]
+++

**What ran.** 355 scenes built from nine tables (tri-region 35, regions 37, objects 14, object-words
1, vtask-capacity 9, line-point 107, points 20, state-units 130, zero-words 2); 244 cases were not
built because they replaced the vertex program or a PDS program (the pixel program is a placeholder:
the TA does not read it) or, for 3, because the rebuilt block differs from the dump's object. The
ta-object-format jobs (59) all replace the vertex program and are not built.

**Results.** [HW] 89 scenes reproduce: ta-tri-region 35, ta-regions 37 (the 26 shifted triangles of
E180, one to five copies, the targets 64 x 32, 32 x 64, 192 x 64, 64 x 192 and 256 x 256), ta-
objects 14, ta-object-words 1, vdm-vtask-capacity 2. 21229 non-zero dwords of the dumps are
compared, 238 a job, of which 21 a job (8.8 percent: the PDS words, the ISP words, the line widths,
the format word and the like) are the same in every job; 79 expected buffer sets are distinct (ten
jobs repeat another's exactly). The comparison is of the parameter buffer pages 0x1000 to 0x6000
(the object and the first five pages of streams) and the TA data headers only: the DPM words of the
dumps are outside it. No dword the model writes inside the windows is one the hardware left 0, and
one outside every window would count as a mismatch too. All 89
rest on fitted rules (E541, E542, E651, E652), so the replay reports them fitted. 266 scenes are
refused, by question, the whole stream walked so that every blocking question is named: lines (the
index list header's topology 1) Q159 and Q160 81, points Q161 26, an output select other than the
library's Q162 20, a vertex task word Q094 4 (and E546's limit of 32 output words a task),
VDM_INDEX2 Q042 3, a cull mode Q069 1, a triangle no target region lists Q230 1, and the 130 jobs of
vdm-state-units, every one a stream of two objects (six blocks, Q112) whose state words are also
open: a word nobody flipped Q047 with Q112 104, bits 11:9 of VDM_STATE1 at 1 or 6 (the job completes
or hangs by history: E545) Q163 with Q047 and Q112 12, at 7 Q163 with Q112 5, a clean
state word and only the shape Q112 9. The vdm-state-units tables therefore contribute no modelled
job and no dump here checks the state word 1 rules (E185, E191, E413, E545). None is predicted as a
hang.

**Denominators and bias.** 89 of 89 is 89 of the 355 scenes built (25 percent) and of the 599 jobs
dumped in the nine tables (15 percent). The 244 not built are builder limits, not model refusals:
73 vtask-capacity, 11 and 1 object and vdm slot jobs, 14 ta-objects (every vertex-output variant),
24 zero-words (kpoke), 66 points and 59 ta-object-format replace the vertex program or a PDS
program, and are the hard ones. So the vertex program run on sgx-sim is the library's pass-through
copy program with w = 1, the object layout is called with position only (E541's stored-dword rule
is exercised in its position-only form), no job uses the 1/w replacement, and every fitted job has
one to five visible triangles with the clip removing none and a clip z whose viewport product the
replay does not tell the sign of (a unit test does). All render command words 10 to 25 are the
same in every scene.

**What went wrong on the way, and the cause.** One scene mismatched: ta-zero-words
cull-offscreen, a triangle 1000 pixels off a 64 x 64 target. The hardware wrote no object and empty
headers; the model wrote an object with no stream. Not fitted away: the model refuses a triangle no
region lists (Q230), because the data does not separate "no object when no region lists a
primitive" from "no object beyond a guard band". A second error was the model's own: its check of
CR_MTE_SCREEN had the halves swapped (the library writes (w - 1) | (h - 1) << 16; the squares could
not show it) and refused the four non-square targets as Q231 until a unit test with a 64 x 32 job
fixed it; no TA rule changed.

**Refused for lack of a measurement.** A triangle with a vertex beyond z = -w or z = w refuses
(Q230): E287 measured pixels only, and no dump says whether the TA writes an object for a triangle
the clip removes. The render command words 10 to 25, the state block's WCLAMP (word 14, the
library's and the 1e-3 of ta-objects-wclamp, whose object was unchanged at w = 1) and VDM_STATE1
bits 7:0 (5 for a draw, 1 for the end of scene) are read by nothing in the model; any other value
refuses (Q231, Q047), so a scene that varies them is not fitted by ignoring them. A 1/w equal to
the minimum refuses too (E197's values all lay clear of the boundary).

**What it shows [infer].** The vertex side runs on sgx-sim unchanged: 18 state dwords reach the
MTE through the PDS `doutd` copy and the state task, and each vertex's four dwords by index times
stride. The task is run only to its first hand-off to the vertex cache (the second phase, after
the cull wait, is not run); the MTE takes the outputs there. The rules fitted to one table (E651,
E652) are reproduced on the others only where the data was not their source (below).

**In sample, held out.** The rules were written before the replay from E176 (the 23-dword object, a
unit test taken from the record), E177, E180 and 3d.md 10; ta-regions is the data of E177 and E180,
and E542's tile test is the refit of E180's 472 regions, so for the tile test and the forms 0x80,
0x98 and 0x90 the 37 ta-regions jobs and the 14 ta-objects jobs (E176, E651) are in sample. The
stream forms 0x88, 0x8a and 0x8c, the walk order of the streams, the page of each macrotile and the
header flags were read from the 35 ta-tri-region dumps (E652): in sample. Held out are the 3 jobs
no earlier record described (ta-object-words 1, vdm-vtask-capacity 2: the same triangle with 12 and
15 vertices of the plain probe, three- and four-triangle scenes among them) and what the earlier
records did not give in the ta-regions jobs (the forms 0x88, 0x8a and 0x8c, the page order, the four
targets with a non-square tiling), a held-out set of dumps and not of runs on the hardware, so the
rules stay fitted (D6). That the rules were fixed before the first replay is not shown by a kept
log, and is not claimed.

**Not shown.** What the DPM-written words of the dumps hold (1066 non-zero dwords of a dump past
the windows are the state page and the like: 12.7); lines and points; an object of more than five
triangles; a second object; the other macrotile counts (four in a row from 640 x 480: no dump);
perspective vertices and a triangle the clip removes or cuts (Q230); the state word 1 rules of
two-object streams.
