+++
id = "E809"
claim = "R3x-c3 stage c3 (13 jobs of start.s, a task of ours; S0 a reader alone, then 12 jobs in which a writer set sa63, r20, r21, i0 and i1 to random markers and p0 to p3 to the job's flags 0011, 0100 or 1010, armed a reader for the next event and called the closed task, then a perturbation: N 1200 ms, F a client fill, L a firmware reload, R a debugfs reset and a reload, three jobs each): the tick was kept in 13 of 13 jobs; the reader at the next entry read all five markers in 12 of 12 writer jobs, pclink 0x98, p0 1 and p1 as the writer left it in 12 of 12, and p2 and p3 as the writer left them in 12 of 12 (1 1, 0 0 and 1 0), so in the 8 jobs where a flag was 0 H-KEEP (p2, p3 as left) held 8 of 8 and H-SET (p2 = p3 = 1 at the next entry) is REFUTED, 8 of 8; after 1200 ms (N) the five markers and p2 p3 were still as written in 3 of 3 jobs, with p0 p1 1 1 and pclink 0x98"
unit = "edm"
method = "R3x-c3 stage c3 of the question-closing pass, round 3 (session L3b, decisions R3-R1 and R3-R9; one stage of 13 jobs, started 16:36:50 Mac time, out-l3b.log), dataset edm-closing-r3x-c3, on the laptop (host cedar, direct cable), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded, checked at preflight), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), health tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); one firmware task of ours, asm/start.s (112 instructions, blob sha256 f728519f8196c06c..., accepted by the landed tools/fwtask verifier at 927bea4 and at 7aaa017 to the same bytes, the lead's refreeze before the first job), armed with own_arm slots=0x1 entry=0 once at the start, again in each reload and reset job; per job the host's reader (rd0), the writer (cmd 1: sa63, r20, r21, i0, i1 = markers, p0 to p3 = the job's flags, the reader armed for the next event, the closed task called), the reader at the next event (rdA), the perturbation and the host's reader again (rdB), each reader storing the entry values of pclink, p0 to p3, r20, r21, i0, i1, sa63, sa64, sa65, sa100, sa127, sa20, sa24 and pa0 to pa2 to the results page; the tick checked after each step (HostCtl dword 12 and USE0_SERV_EVENT advancing); scored by the frozen score/score_c3.py c3 (out/score-c3.txt; the disclosed post-run fix of POSTRUN-FIX.md prints out/score-c3.fixed.txt); the register values quoted were read from the kept job records out/c3/NAME.json; health ok after the stage"
tiers = ["HW"]
date = "2026-11-10"
data = ["edm-closing-r3x-c3:out/c3/"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E536 read p2 and p3 as 1 1 after its writer set them 1 1, but also 1 1 after 1200
ms, 0 0 in the controls and 0 1 after a fill, so it could not tell whether a task finds them as the
last task left them; E792 read 1 1 after every writer of round 2. C3's writer leaves three
different flag sets, two with a 0 in p2 or p3 (the discriminating jobs), and the reader at the next
event reads them after the closed task's pass.

**Frozen verdict (as printed).** `Q124 p2/p3 at the next entry, 8 discriminating jobs (a flag 0):
H-KEEP supported (the writer's p2 p3 read back 8 of 8), H-SET refuted` and `Q158 N (1200 ms):
sa63, r20, r21, i0, i1 kept in 3 of 3 jobs`; the `SUMMARY` line: `c3: kept 13 of 13 read jobs,
stops 0 []; controls failed none`, with H-SET among the refuted replicate rows.

**Results [HW].** At the next entry (rdA), by the writer's flags p0 p1 p2 p3:

| flags | jobs | p0 p1 p2 p3 read | pclink | markers |
|---|---|---|---|---|
| 0 0 1 1 | n1, f1, l1, r1 | 1 0 1 1 | 0x98 | 5 of 5 in 4 jobs |
| 0 1 0 0 | n2, f2, l2, r2 | 1 1 0 0 | 0x98 | 5 of 5 in 4 jobs |
| 1 0 1 0 | n3, f3, l3, r3 | 1 0 1 0 | 0x98 | 5 of 5 in 4 jobs |

After 1200 ms (rdB of n1, n2, n3): p 1 1 1 1, 1 1 0 0 and 1 1 1 0, pclink 0x98, the five markers
in 3 of 3. Every job's rd0 read the previous job's last reading (the carry control, 12 of 12).

**What it shows and does not.** A task of ours finds p1, p2 and p3 at its next entry as it left them
after the closed task's pass (p1 also E792's 19 of 19), and p0 at 1 whatever it left, with pclink
0x98 (sa64 not written). After a fill, a reload or a reset the picture differs (E810). The tick bit
of sa64, which E792 showed changes pclink, was not written here.
