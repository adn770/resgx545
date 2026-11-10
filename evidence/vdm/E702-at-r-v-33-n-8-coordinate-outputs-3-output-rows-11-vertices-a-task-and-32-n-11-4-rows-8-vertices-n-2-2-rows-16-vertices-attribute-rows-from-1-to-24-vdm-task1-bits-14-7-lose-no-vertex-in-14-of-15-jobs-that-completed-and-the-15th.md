+++
id = "E702"
claim = "At R*V = 33 (N = 8 coordinate outputs, 3 output rows, 11 vertices a task) and 32 (N = 11, 4 rows, 8 vertices; N = 2, 2 rows, 16 vertices), attribute rows from 1 to 24 (VDM_TASK1 bits 14:7) left the render unchanged in 13 of the 15 jobs that completed (the tool's o0 histogram equal to that of the other jobs of the same N); two jobs at N = 8 changed it, a = 7 (3 pixels differ; ids 55, 66 and 77 hold one constant row) and a = 12 (260 pixels differ, though the decoder finds every vertex identity, in an irregular split of the objects), and the one job of E546 that lost a vertex at 33 with 8 rows was not seen again in the two a = 8 jobs here (another module and tool): the three are treated alike, each one an event not yet repeated, pending a repeat, and no limit at 33 is concluded; by the vertex count the model in which attribute rows add to the budget (33 plus the rows over 8) was wrong in 10 of 15 jobs and the model in which they do not count wrong in 1 (14 of 15 scored, 14 of 16 counting the job that hung); 32 attribute rows at N = 2 hung the job"
unit = "vdm"
method = "table capacity (16 jobs, safe: probe --tri pixpds:12 --temps 32 --width 64 --height 64 --vertices 126 with --vtx-coords N, the field VDM_TASK0.MAX_VERTICES set by --vdm 6^= and the attribute rows by --vdm 7^=, a reset before every job), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the tool's o0 mixed lines (the colour histogram of the render) were read after the run for the claims about images; the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE"]
+++
**What ran.** 16 jobs of the E546 vertex-task probe (126 vertices, 42 triangles, decoded with the
landed p1131 decoder, the vertex fate of q164_fate.py): N = 8 coordinates, rows R = 3, V = 11 (the
field at 10): R*V = 33, attribute rows a = 1 (the plain job), 5, 7, 8, 9, 10, 12, 16 and a repeat of
8; N = 11, R = 4, V = 8 (R*V = 32), a = 9, 12, 16, 24; N = 2, R = 2, V = 16 (32), a = 9, 16, 32.
Frozen: MA (the attribute rows do not count: a job at 33 or below loses no vertex) and MB (a
budget of R*V plus the integer part of a / 8, capacity 33: loss where that exceeds 33), the second
formed on E546's one job (a = 8 at 33).

**Results.** [HW] 15 jobs completed, one hung (N = 2, a = 32: `job hung, recovering`, rc 3, no
dump). The tool's own `o0 mixed` line, the colour histogram of the 64x64 render, which the first
reading of this table did not use, is the same in the 7 jobs at N = 8 with a = 1, 5, 8, its repeat,
9, 10 and 16 (0xff203040 x2288, three of 0xbea8, 0xbe98 and 0xbe88 0000 at x46, other x1670) and in
the 6 jobs at N = 11 and N = 2 (0xff203040 x2821, other x1137, the histogram of the natural N = 9
job of E703). Two jobs at N = 8 differ: a = 7 reads 0xff203040 x2285, other x1673 (3 background
pixels fewer, the number of its three constant-row vertices, not shown to be their effect) and
a = 12 reads 0xff203040 x2028, 0xbf040000 x55, 0xbe980000 x53, 0xbe880000 x52, other x1908 (260
background pixels fewer: another image). By the decoder (a layout assumption of its own), 14 of the
15 jobs that completed keep all 126 vertices in 9 objects with no duplicate: the sizes are 15 eight
times and 6 once, except a = 12 at N = 8 (15 seven times, 9 and 12: an irregular split with every
identity present and a render that differs). The 15th (N = 8, a = 7) has the same 9 objects and
sizes, but three vertices, number 55 in the 4th object, 66 in the 5th and 77 in the 6th (the last
one in the object that carries bit 21), read as one constant row (words 0x3f3a2e8b 0x3f800000
0x3f900000 0x3f400000 0x3f600000 0x3f800000 0x3f900000 0x3fa00000 0x3fb00000) in place of their own
coordinates: three vertices are lost without a slot missing.

**One event kind, three events.** [HW] At R*V = 33, 2 of the 9 N = 8 jobs here changed the render
(a = 7, a = 12), and E546's a = 8 job lost a vertex; at 32 (N = 11 and N = 2) none of the 6 changed.
None of the three N = 8 events has been repeated under its own conditions: the a = 8 jobs here
(2 of 2 unchanged) ran under another module, tool and date than E546's, so they do not repeat it.
The three are treated alike, as not repeated and pending a repeat; the data fit 33 being marginal for
N = 8 as well as they fit a limit at 33, and nothing is concluded about attribute rows and the
limit.

**Scores of the frozen models.** MA 14 of 15 scored jobs by the frozen criterion (a vertex missing:
the miss is a = 7; the hung job has no vertex data and is not scored: 14 of 16 if it counts as a
miss; a = 12 counts as a hit because no identity is missing, though its render differs: by an
unchanged-render criterion MA is right in 13 of 15). MB 5 of 15 (ten misses: a = 7, where it
predicted no loss, and nine jobs where it predicted one and none occurred: a = 9, 10, 12, 16, 8 and
the repeat of 8 at N = 8, 16 and 24 at N = 11, 16 at N = 2). MB was formed on one job and is
refuted by these 10 by the vertex count.

**Page claim, post hoc.** The 13 jobs with an extra dword (bit 21 of the primitive word, E546, Q164)
carry one such object each (extra 0x400, 0x800 for a = 12). With Q164's claim (the head of the
object is on the page (extra >> 10) - 1 of the parameter buffer) 12 of 13 objects are fully
identified, the 13th being the a = 7 object with the constant-row vertex; the alternative (the page
before the tail) identifies 0 of 13. The claim was fitted on E546's jobs; these 13 are not in that
fit, but the analysis was not frozen before the run.

**What it shows.** [HW] Attribute rows between 1 and 24 left the render unchanged in 13 of 15 jobs
at R*V of 32 and 33. The reading of E546 that the rows enter the budget is not supported by these
jobs (the one job it rested on was not seen again, under other conditions). The two N = 8 jobs
that changed the render (a = 7, a = 12) and the hang (a = 32 at N = 2) are one job each,
unexplained and not repeated (Q272); whether they are noise, intermittent attribute-row effects at a
marginal product or a limit is not shown, and no rule about a limit at 33 follows from this table.

**Not shown.** Whether a = 7, a = 12 and E546's a = 8 repeat (under their own conditions); whether
the hang at 32 rows depends on N or on R*V; R*V of 34 and 35 (no natural job reaches them, E703).

**Correction 2026-11-10:** The statement above that the a = 8 jobs ran under another module and tool
and 'do not repeat' E546's lost vertex is answered by later runs of these very words: a = 8 lost
vertex 70 in 2 of 3 runs of S1 (E738) and in 5 of 6 of S1b (E755), with three outcomes (x2288,
x2156, x2260), and the a = 12 event is x2582 and x2313 on the later runs, not x2028 (E755). The
three N = 8 events are therefore intermittent and not functions of the words; E702's own a = 8 jobs
(2 of 2 unchanged) were the unchanged outcome.
