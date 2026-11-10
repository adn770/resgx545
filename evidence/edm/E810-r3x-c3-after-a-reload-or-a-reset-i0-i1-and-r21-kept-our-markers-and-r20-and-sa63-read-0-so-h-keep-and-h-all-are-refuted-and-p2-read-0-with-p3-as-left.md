+++
id = "E810"
claim = "In R3x-c3 stage c3 (E809's jobs), after a client fill (F, 3 jobs) i0, i1 and sa63 kept the writer's markers in 3 of 3, r20 read 0 and r21 0x1000, 0x2000 and 0x3000; after a firmware reload (L, 3 jobs) and after a debugfs reset and a reload (R, 3 jobs) i0, i1 and r21 kept the markers and r20 and sa63 read 0 in 6 of 6; sa65 read 0x02000000 after every reload and reset and stepped by 0x02000000 with each fill (0x04000000 to 0x08000000); sa100 0x3cc00010, sa127 0x3f800000, sa20 0 and sa24 0 in every reading of the stage; after F, L and R alike p0 p1 read 1 1 and pclink 0x98, and p2 p3 read 0 1 where the writer had left 1 1 and 0 0 where it had left 0 0 or 1 0 (9 of 9); so the frozen H-KEEP (i and sa63 survive a reload or a reset, r20 and r21 do not) and H-ALL (r20 and r21 survive too) are both REFUTED, H-KEEP by sa63 (0 in 6 of 6) and H-ALL by sa63 and r20, E536's frozen p2 p3 readings held in 1 of 3 fills (0 1) and 4 of 6 reloads and resets (0 0); the start state S0, read after the stage's own arm and before any writer, was pclink 0x98, p0 to p3 1 1 0 0, r20 0, r21 0x2000, i0 0xcd7aa809, i1 0xff326b8c, sa63 0, sa64 2, sa65 0x02000000; the frozen scorer printed 'r20/r21 survived 3/3' for L and for R, a scorer bug (it counted a pair of values, always true, not the row), and two hypothesis lines that score the r20/r21 row alone, both corrected by a disclosed post-run fix"
unit = "edm"
method = "R3x-c3 stage c3 of the question-closing pass, round 3 (session L3b, decisions R3-R1 and R3-R9; one stage of 13 jobs, started 16:36:50 Mac time, out-l3b.log), dataset edm-closing-r3x-c3, on the laptop (host cedar, direct cable), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded, checked at preflight), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), health tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); one firmware task of ours, asm/start.s (112 instructions, blob sha256 f728519f8196c06c..., accepted by the landed tools/fwtask verifier at 927bea4 and at 7aaa017 to the same bytes, the lead's refreeze before the first job), armed with own_arm slots=0x1 entry=0 once at the start, again in each reload and reset job; per job the host's reader (rd0), the writer (cmd 1: sa63, r20, r21, i0, i1 = markers, p0 to p3 = the job's flags, the reader armed for the next event, the closed task called), the reader at the next event (rdA), the perturbation and the host's reader again (rdB), each reader storing the entry values of pclink, p0 to p3, r20, r21, i0, i1, sa63, sa64, sa65, sa100, sa127, sa20, sa24 and pa0 to pa2 to the results page; the tick checked after each step (HostCtl dword 12 and USE0_SERV_EVENT advancing); scored by the frozen score/score_c3.py c3 (out/score-c3.txt; the disclosed post-run fix of POSTRUN-FIX.md prints out/score-c3.fixed.txt); the register values quoted were read from the kept job records out/c3/NAME.json; health ok after the stage"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3x-c3:out/c3/"]
terms = ["Event Data Master (EDM)", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** Q158 asks which of a task's sa, i and r registers keep their values across a fill, a
firmware reload and a debugfs reset. E536's controls read i0, i1, sa100 and sa127 as E533's writer
had left them after a reset and a reload, and r20 0, r21 0x1000; E537's control read r21 0x3000
after a reload. C3 splits E536's confound: L reloads the firmware with no reset, R resets and
reloads (after a reset only the stock firmware runs, so every R job re-arms). Our task may write
sa63 only of the sa (R2-1 b), so sa100, sa127, sa20 and sa24 are read, not written.

**Frozen verdict (as printed, out/score-c3.txt).** The `SUMMARY` line: held out 39 held, 10
FAILED, refuted `E536 (fill: p2 p3 = 0 1)`, `E536 controls (after reset and reload: 0 0)`, H-ALL
and H-KEEP; replicate 116 held, 20 FAILED, refuted H-ALL, H-KEEP and H-SET; control 24 held. The
verdict lines `Q158 L (reload (no reset)): kept i0/i1 3/3, sa63 0/3, r20/r21 survived 3/3; p2 p3
after: 01 00 00` (R the same), `Q158 F (client fill): kept i0/i1 3/3, sa63 3/3, r20/r21 replaced
3/3`, `H-KEEP (r20/r21 after a reload or a reset): held in all 6` and `H-ALL (r20/r21 after a
reload or a reset): refuted in 6 of 6 jobs`.

**The scorer's inconsistency, resolved from the kept records [HW, post-run fix].** The kept job
records read, after L and R, r20 = 0 and r21 = the writer's marker in 6 of 6 jobs (l1: r20 marker
0xa6565cef read 0, r21 0x99bebc5c read 0x99bebc5c; the others alike), so r20 and r21 together
survived in 0 of 6. The Q158 lines counted a pair of values (r20, r21), always true, instead of the
row; the two hypothesis lines score the frozen row "r20 and r21 both kept" alone (no in 6 of 6:
H-KEEP's value, not H-ALL's) and not the hypotheses, which also predicted sa63 kept (0 in 6 of 6);
the `SUMMARY`, which lists both refuted, is right. The published copy fixes the scorer after the
run (POSTRUN-FIX.md; predictions untouched, both outputs kept): `out/score-c3.fixed.txt` prints
`r20/r21 both survived 0/3 (r20 0/3, r21 3/3)` for L and for R and `H-KEEP as a whole ...: 12
held, 6 FAILED of 18`, `H-ALL as a whole ...: 6 held, 12 FAILED of 18`.

**Results [HW].** After the perturbation (rdB), the writer's markers read back (yes) or the value:

| row | i0 i1 | r20 | r21 | sa63 | sa65 | p0 p1 p2 p3 (flags 0011, 0100, 1010) |
|---|---|---|---|---|---|---|
| F (fill) | yes 3/3 | 0, 0, 0 | 0x1000, 0x2000, 0x3000 | yes 3/3 | 0x04000000, 0x06000000, 0x08000000 | 1101, 1100, 1100 |
| L (reload) | yes 3/3 | 0, 0, 0 | yes 3/3 | 0, 0, 0 | 0x02000000 x3 | 1101, 1100, 1100 |
| R (reset, reload) | yes 3/3 | 0, 0, 0 | yes 3/3 | 0, 0, 0 | 0x02000000 x3 | 1101, 1100, 1100 |

pclink 0x98 and sa64 2 in every reading; sa100 0x3cc00010 and sa127 0x3f800000 in all 37
readings (neither is E533's marker: they were set before this run, by what the data does not say).
The page's pass count restarted after each reload and reset (0x3dc to 0x3f4 at rdB, against 0x576 to
0x2762 at the reader before it).

**Read after the run [infer, no frozen row].** In all 9 F, L and R jobs p2 read 0 and p3 read the
value the writer left (1 in f1, l1, r1; 0 in the six others): p2 cleared, p3 kept, by a fill, a
reload and a reset alike. E536's 0 1 after a fill and 0 0 after its controls are that reading
with its writer's 1 1 and its controls' 0 0 [infer].

**What it shows and does not.** Across a reload, with or without a reset, i0, i1 and r21 keep our
values and r20 and sa63 do not, with sa65 back at 0x02000000; a fill keeps sa63 and i and replaces r20 and r21
(E536). What clears r20 and sa63 and keeps r21 (the reload's boot or the closed task's first pass)
is not separated; sa100 and sa127 were not written here, so their survival says only that they
were not changed. The start state is read after the stage's arm, not after a cold boot.
