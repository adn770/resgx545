+++
id = "Q210"
question = "what does the DPM compare with the limit C that decides whether the first abort's threshold is raised by 0x20 (E774: raised iff thr0 + 0x20 <= C = 0x371 at 4096x4096, 1350 and 1500 vertices; E786: the limit is on the threshold the TA runs, not on the knob P; E785: C is in [0xe0, 0x120) at 2048x2048; wd-glist-1500's missing raise at P of 0x422 and above is the clamp of thr0 at 0x400, E753), why is the raise 0x20, and what makes C differ between the targets (the target's size, the scene's page need or something of the scene)"
unit = "dpm"
kind = "hw"
value = "high"
phase = 11
evidence = ["E310", "E312", "E464", "E625", "E627", "E629", "E704", "E734", "E753", "E774", "E779", "E785", "E786"]
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
