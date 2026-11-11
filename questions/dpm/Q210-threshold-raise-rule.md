+++
id = "Q210"
question = "what does the DPM compare with the limit C that decides whether the first abort's threshold is raised by 0x20 (E774: raised iff thr0 + 0x20 <= C = 0x371 at 4096x4096, 1350 and 1500 vertices; E786: the limit is on the threshold the TA runs, not on the knob P; E785 and E799: C = 0x102 at 2048x2048; E801: 0x1d2 at 4096x2048, 0x1d6 at 2048x4096 and 0x208 at 3072x3072; E800: the target sets it, not the context; E802: another scene raises above 0x102 at 2048x2048; wd-glist-1500's missing raise at P of 0x422 and above is the clamp of thr0 at 0x400, E753), why is the raise 0x20, and what makes C differ between the targets and the scenes (no law in the target's size fits, E801)"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E312", "E464", "E625", "E627", "E629", "E704", "E734", "E753", "E774", "E779", "E785", "E786", "E799", "E800", "E801", "E802"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_STATE_BASE0", "ta3d_ctl"]
+++

E625: of 70 overflowed jobs of the default triangle (the jobs `analysis/an_raise.py` selects:
1024x768 in 0x23 to 0x34 pages, 4096x4096 in 0x23 to 0x100, 5 pokes of the descriptor's threshold)
the dwords 37 and 38 read as a raise by 0x20 after the first abort in the 41 for which 2 * thr0 <
U + k (thr0 the first abort's status, U the whole-buffer need, 19 and 287 pages) and not in the
other 29; the boundary pairs are P = 0x2c and 0x2d at 1024x768 (k 2 or 3) and the thresholds 142
and 150 at 4096x4096 (k up to 13). The rule was read from those pairs after the follow-up ran: no
job is held out against it, and at 1024x768, where every count of partial renders is 1, the raise
is seen in the dwords and the second set of lists only, the physical raise being shown at
4096x4096 by the counts. E627: with the raise the state page holds the lists the TA built after
the last partial render, without it the abort's lists (sum thr0 - 1 in 28 of 28); E629: the sign
bit of the stored depth follows the raise in 44 of 44 jobs.

Open: what the DPM compares (pages still to come, a count of the TA's remaining work, a firmware
variable), why the raise is by 0x20, and the value of k, which the boundary pairs bound and do not
fix (the pages the count formula adds are Q211's). When the raised job's second set of lists is
stored is Q045's.

To settle it: a scene of a second shape (two triangles, a wider one) whose need U is known from
its whole-buffer page count, run over P across the predicted boundary, the cells declared before
the runs; a regtimeline of the state page's base and of 0x0658 through a raised job and an
unraised one, sampled while the TA runs.

Narrowed in 11.39 (E704). wd-glist-1500 (1500 vertices at 4096x4096, dword 36 = 3, no raise
although the rule R2 predicts one: the run after the first partial render reaches the status of
the first, R2 formed after reading tg-1024-n-0x28, so fitted, 109 of 110 timeline jobs of the
partial-model batch and 64 of 64 in E625's own scenes) repeated at P = 0x422, 0x424, 0x430,
0x440, 0x442, 0x460 and 0x500 and again at 0x422: the same timeline (status 0x400 at the first
partial render, peaks 0x400, 0x400, 0x11c) and the same control block words in 8 of 8 jobs, no
raise (dwords 37 and 38 zero). P above 0x422 changed nothing the TA does: its threshold register
read 0x400 at the first sample of every job and dword 35 was 0x3fe for every P from 0x422 to
0x500, the parameter-buffer dumps are byte-identical, so the 8 jobs are one condition and 7
repeats if the knob or the page buffer clamps P at 0x422. Two readings are open [infer]: a
ceiling of the threshold at status 0x400, or a P clamped at 0x422. The page-supply model (the
raise needs the pages) is untested above 0x422, not refuted: its 3 misses at P = 0x442 to 0x500
may not have had those pages. The threshold is held at 0x3fe only for P in 0x422 to 0x500; nothing
was run below. The controls below the step of dword 36 (1400 and 1300 vertices) did not run: the
tool refuses vertex counts that are not multiples of 3. Open: whether the knob takes effect, the
ceiling reading (P below 0x420, Q273), the part of dword 36, the exact step between 1350 and
1500.

Narrowed 2026-11-09 by source (see Q273). "At every P tried from 0x422 to 0x500" was one P: the
fork's `sgx_render_pb_pages()` returns 0x422 above 0x422, so the eight jobs of E704 are one
condition and seven repeats, and the exception of wd-glist-1500 has been tested at one buffer size
only. The ceiling reading and the page-supply reading are both still untested for the scene at a
smaller P; Q273 holds the run. The question is not answered or reclassified here.

Post hoc 2026-11-09 (S1, E734; a reading of the stage's data after the run, not a result and not
held out; the stage's frozen verdict was METHOD BROKEN, nothing concluded). R2 and E625's rule
(raise iff 2 * thr0 < U + k) also predict a raise for 1350 vertices at P = 0x3e0 (thr0 0x3be) when
U is read as the summed run peaks, and none was seen; of the 22 jobs the raise (dwords 37 and 38)
appeared at thr0 0x1de and 0x2de and in none of the 19 jobs with thr0 from 0x3be whose second run
reached thr0. A limit on the raised threshold, 0x2fe <= C < 0x3de, fits all of them. A frozen run
that tests it needs P between 0x300 and 0x3e0 for two scene sizes.

Narrowed 2026-11-10 (S1b, E753). The exception is explained and the rule bounded: the threshold of
wd-glist-1500 is clamped at 0x400 for P of 0x422 and above, so thr0 + 0x20 is 0x41e, above a limit C
on the raised threshold that a frozen ladder found in [0x35e, 0x37e) (raises at P = 0x320 to 0x360,
none at 0x380 to 0x3e0, for 1350 and 1500 vertices alike, controls passing, HP1 held out). R2's rule
(raise iff 2 * thr0 < U + k) alone does not give the step: every non-raising ladder job had its
second run reach thr0. Open: what the DPM compares with C, why the increment is 0x20, and whether C
depends on the target size and the scene (one target, 4096x4096, one pixel program).

Narrowed 2026-11-10 (R1-pixgeo, E774; the limit is exact, the question stays open). A fine ladder
at 4096x4096 (15 cells of 1500 vertices in steps of 2, 5 of 1350, a step-1 cell after the flip, both
E753 controls reproduced, each job's own 0x0624 read P - 0x22) raised the threshold by 0x20 at every
P from 0x360 to 0x373 and at none from 0x374 to 0x380, one flip: the raise happens iff thr0 + 0x20
<= C with C = 0x371 (thr0 at most 0x351, 849 pages), so the last raised threshold is 0x371 and the
first refused 0x372. HP1 held out: each of the 5 cells of 1350 vertices gave the outcome of the 1500
cell at that P. E753's ladder, E734's raises, E704's clamp case and E625's default-triangle raises
are all on the side of C that their thr0 puts them (a check after the run, not frozen). The clause
"wd-glist-1500 as an exception" is answered by the clamp (E753) and the limit. What the ladder does
not separate: it moves P and thr0 together, so a constant C of the core or the firmware and a limit
tied to P give the same flip; the descriptor poke of the proposal (a threshold set without P, E625's
`pb:11`) and a second target (2048x2048) did not run. E779's nine jobs at the default triangle
(thr0 0x7e to 0x8e) all raised, as C says. Open: what C is compared with and why the increment is
0x20, whether C follows P (a poke ladder), and whether it moves with the target and the scene
(2048x2048, another triangle count).

Narrowed 2026-11-10 (R2-geo, E785 and E786; the question line is reworded, the question stays
open). Both open halves of the note above ran, with their controls passing.
- The poke ladder (E786, held out). With P held at 0x422 and the first threshold set by `pb:11`
  at 1500 vertices and 4096x4096, the threshold was raised at V = 0x300, 0x33e and 0x351 and not at
  0x352, 0x35e, 0x3a0 and 0x3de, 7 of 7 as H-abs says (raise iff V + 0x20 <= 0x371), the flip at the
  place E774's knob ladder had it. H-P (a limit on P's value) failed 3 of 7 and H-rel (the limit
  follows P) 4 of 7. So the limit is on the threshold the TA runs and not on P.
- The second target (E785, held out). At 2048x2048 the scene needs 0x213 pages, so the cells that
  E774's C would put at the flip (P = 0x354 to 0x394) never overflowed and were void; the low cells
  gave a raise at thr0 0x80 and 0xc0 and none at 0x100, so C is in [0xe0, 0x120) there. H-same (the
  same C at both targets) is refuted, 2 of 3 cells.
- Combined reading [the lead's reading of E774, E785 and E786, [infer] where it goes past the
  data]. C is not a function of P; it is a limit on the raised threshold that differs between the
  two targets, 0x371 at 4096x4096 and between 0xe0 and 0x120 at 2048x2048, so it follows the target
  or something that moves with it (the page need of the scene is 0x213 at 2048x2048 and about 1300
  at 4096x4096; the triangles' size in pixels is not separated from the target either). The two C
  are not in the ratio of the areas (a quarter of 0x371 is 0xdc, below the bracket). One target
  pair, one triangle, 1500 vertices only: the data do not say which.
Open: what C is compared with and why the increment is 0x20; whether C follows the target's size,
the page need or the scene (a third target, another vertex count at 2048x2048, a scene whose need
at 2048x2048 reaches thr0 up to 0x140 and beyond); and the exact C at 2048x2048 (thr0 0xc1 to 0xff
not run).

Narrowed 2026-11-10 (R3-geo, E799 to E802; the question line is reworded, the question stays
open). The four DPM stages on C ran after g-c4's four controls passed.
- Exact C at 2048x2048 (E799, held out). The runner's bisection gave one exact flip: last raise at
  thr0 0xe2, first silent 0xe3, so C = 0x102, inside E785's bracket. LT (C proportional to the
  region count from 0x351 at 4096x4096, last raise 0xd4) is refuted.
- Context (E800, held out). A 2048x2048 target in a context made for 4096x4096 flipped at g-c4's
  place (3 of 3 cells): H-target holds, H-context is refuted.
- Three more targets (E801, held out). Exact flips at 4096x2048 (last raise 0x1b2, C 0x1d2),
  2048x4096 (0x1b6, C 0x1d6) and 3072x3072 (0x1e8, C 0x208). The two transposed targets have the
  same region count and different limits, so LT and the affine laws in the region count, the
  macrotile area and the tail-pointer side squared are all refuted at all three targets.
- Another scene (E802, held out). `--tri-full` at 2048x2048 raised the threshold at every valid
  cell from thr0 0xd2 to 0xf3, 0xe3 included, which g-c4's scene did not raise: C depends on the
  scene (at least 0x113 for it; no silent cell was reached).
Open (the reworded line): what C is compared with and why the increment is 0x20; which property of
the scene and of the target sets C (no law in the target's size fits five targets; one other scene
gives a different limit at one target, its value not reached).

Note 2026-11-11 (round 4, a reading of the landed firmware dataflow, `doc/specs/edm_dataflow.md`,
generated from E013; [source], a static reading, no run). The raise is the firmware's own write in
its out-of-memory routine at 0xb50-0xc22: `CR_DPM_ZLS_PAGE_THRESHOLD` (0x0624, the register that
reads P - 0x22) is written as itself + 0x20, `ta3d_ctl.zls_threshold_step` (dword 38) is written
from 0x20, `CR_DPM_TA_GLOBAL_LIST` is written as (itself & 0xffff) + 0x10 | 0x10000 with its old
value saved in dword 37, `abort_page_count0` and `abort_page_count1` (dwords 35 and 36) are written
there and tested against the high halves of `CR_DPM_PAGE_STATUS` and `CR_DPM_GLOBAL_PAGE_STATUS`,
and `CR_DPM_REQUESTING` bit 0 branches. So 0x20 is a constant of that routine (with E625's dwords 37
and 38 as the saved threshold and the step), the clause "why is the raise 0x20" is answered at the
tier of a static reading plus E625, and the limit C is a branch of that routine, not a hardware
compare. The spec leaves the routine with "a branch on a predicate of unknown origin" and dwords 35
and 36 "written from ?", so the guard of the + 0x20 write is not read yet. Dword 36 is written in
that routine at every abort, which is what H-last (the count before the last abort, 58 of 58 with an
abort, E803) needs; the value it is written from is the remaining open part of the former Q273
(retired as answered by E803) and is read with this question. Next, offline: the conditions of the
routine on the path to the + 0x20 write and the source of the two abort counts (reading R-5, facts
only, reviewed), then a test held out by construction: the condition must place the five exact flips
(0x351/0x352 at 4096x4096, 0xe2/0xe3 at 2048x2048, 0x1b2, 0x1b6, 0x1e8; E774, E799, E801) and
E802's scene from the registers g-c4's and g-c5's kept timelines hold (0x0624, 0x0628, 0x0724,
0x0728, 0x072c). Refuted by one flip on the wrong side. No hardware unless a register it needs was
not sampled.

Note 2026-11-11 (round 4, reading R-5 of the guard of the + 0x20 write, `closing4/p7/reading-r5.md`
with `flips.py`, `flips.out`, `guard.py` and `sweep_last.out` beside it; our disassembly of the
cut firmware, a static reading, then an offline test on kept timelines; no run).
[source] Facts, by instruction index. The write at 0xbe1 (`str #393`, 0x0624 += 0x20) is reached
only through the decision at 0xbbf-0xbd2: sa8 bit 7 set (0xbbf, 0xbc0), bit 9 clear (0xbc1, 0xbc2),
and then, with bit 8 clear, `isub16.testpat` of dword 35 against the high half of 0x0724 (0xbca), or
with bit 8 set of dword 36 against the high half of 0x072c (0xbd1); 0xbd2 `p0 ba` goes to the abort
when the low lane is not negative and falls into the raise otherwise. Dwords 35 and 36 are written
only at the abort (0xc11, 0xc19) as those high halves less 2, dword 36 floored at 0. Bits 7 and 8
are set only by the resume (0xdcc-0xddc), by the same compare with the counts read there, and
cleared by the abort (0xbf6) and the TA finish. So the guard is: with PS_hi and GPS_hi the page
counts, the raise happens at an entry iff the resume saw GPS_hi above dword 36 (or PS_hi above
dword 35, bit 8 clear) and the entry again sees it above. [infer] The operand order of `isub16`
(source 1 minus source 2) is read from the form line, not stated in a record; the reversed order
fits 35 of 101 jobs and this one 100 of 101.
Offline test (SEMI: the guard was written from the instructions before any timeline was read; the
variants ran after the result). On the kept register timelines the guard places all 12 cells of the
five exact flips (E774 and E786's two pairs, E799, E801; last raise: 3 global pages at the abort, 2
at the resume, 4 at the entry; first silent: 3, 1, 3), E802's six raised cells (1, 1, 1; the floor
makes the saved count 0), 288 of 289 decisions over 107 jobs, and the dword rule 107 of 107
(E803 extended). Variants: reversed subtraction 35 of 101, no "less 2" 35 of 101, no resume stage
66 of 101. One miss is open: c4-b3 (E799's grid, 2048x2048, thr0 0xe8, silent) has the inputs of the
raised c4-b5 and is the only job whose timeline shows the global list grown before the first abort;
a gate before 0xbbf at its second entry, or a condition the grow leaves, is not excluded and
0x0734, sa8 and the exit paths were not sampled [open]. The sa8-bit-7-only path (dword 35) never
fired: unexercised.
[infer] What it answers: the firmware compares the global page count after the partial render with
the one at the abort less 2, not a threshold, an area or a limit C. C is where the hardware's
partial render frees one global page instead of two (the first silent cells go 3 to 1 pages, the
last raised 3 to 2), and 0x20 is the routine's constant (above). What stays open is that
accounting, by target and scene (why one page below C and two above, why E802's scene holds one
global page), and c4-b3.
Would refute it: one cell with a raise and GPS_hi at the resume at or below dword 36, or a
raise-less cell above it with no grow before it, reproduced (c4-b3 is the one such cell in the kept
data; repeating it at the same P with 0x0734, sa8 and the exit paths observed turns it into noise or
into the missing condition); a repeat of the flips on other hardware that moves the page drop moves
the flips, not the guard. A prediction needs only 0x072c and 0x0724 at the abort and at the resume,
which every kept timeline holds; a hardware row is justified for the grow case only. Not read: the
callees 0xb0b, 0x1765, 0x1676, 0x1773, 0x159e, 0xb46, and what CR_DPM_OUTOFMEM 1 and 4 do.
