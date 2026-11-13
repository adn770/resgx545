+++
id = "E874"
claim = "Round 6 offline replay of the TA's page take for the tool's triangle with 1500 vertices (Q210; read from kept dumps and timelines that had been seen, so post hoc and SEMI, nothing held out in the strict sense): the global list holds 67-dword object blocks back to back (5 triangles each) and global page k begins inside object b_k = floor(1024 (k - 1) / 67), 149 of 149 global pages in kept dumps beginning where that puts them (2 fit pages; the first frozen version of the check was defective and its output seen before the fix, so SEMI); a region's stream block holds 31 dwords of entries and the entry of object b_k carries one more, the base of the new page, so every region covering the triangle opens a block at objects 0, 15, 30, ... (2089 to 2341 regions each at 2048x2048, read in the dumps); a block-level replay with only those constants and one fitted lag (the TA writes object b to the list 3 objects before it tiles it, fitted on 2048x2048) gives the dumps' block openings exactly, U = 0x213 at 2048x2048 and 0x3f7 at 4096x2048 (the kept needs), and 20 of 21 steps of the four other targets in their brackets (2048x4096 S3 is 0x129 against 0x12c); the steps are the page counts when b_k is written, the bursts the blocks opened at the next multiple of 15, the creep the regions that the moving copies reach later; the pages left by the first partial render are 2 iff the first threshold falls between a step and the model's burst end B_k, else 1 on the kept rows (H-PHASE: 26 of 26 fit rows at 2048x2048, 60 of 61 rows of the other targets, the miss a row reading 0; held out in R6-dpm, read ungated, it held at bands 3 and 4 of three new targets, 18 of 18, and failed 5 of 15 cells at bands 5 to 7 of 2048x2048, where one page is left only from B_k + 1 or B_k + 2, E881), so the first silent cell of the raise is B3 at all five targets (E774, E799, E801; post hoc), where the frozen timeline burst-end rule placed only 49 of 61; read after the fact, at the 21 kept grow cells the global count goes from 1 to 2 at the first sample after the render (H-PENDREQ), E802's --tri-full scene (71-dword blocks, 3-dword entries) has S2 0x201 and S3 0x302 by the same replay, so one global page at all its cells, and the replay with partial renders gives 43 of 43 partial-render counts of kept 2048x2048 jobs (exploratory) [corrected 2026-11-12, see Correction]"
unit = "dpm"
method = "Offline, no run (round 6, area dpm, decision R6-1 a; plan closing6/dpm/exp-dpm-r6.md section 3, steps F2 to F6, F8 and F9). The scripts in closing6/dpm/offline/ (standard library only; r6lib.py the planner's reader, tools/usse-asm dpm_words.py and pbdump.py of this tree for the dump words, render/closing-r5-dpm/gen/hu1.py for HU1's tile test) read the kept render dumps (param and TA data) and timelines of R1-pixgeo g-c1, R2-geo g-c2 and g-c3, R3-geo g-c4 to g-c7 and g-d36, R5-dpm d-a0 to d-a3 and d-t, S1 and S1b g-e1, read-only. Freeze order (FREEZE-LOG.txt, each script's sha256 in FREEZE-f<n>.sha256 before its first run): f2_objpage.py (H-OBJPAGE; its as-run version read PB page 1 as the list head in every dump and stopped on a job without 0x0658: kept as f2_objpage.as-run.py and .as-run.out, fixed version per FIX-f2.md, re-hashed, its held-out lines SEMI); f3_streams.py (no verdict; fixed after its first run to read every region header, FIX-f3.md); f5lib.py and f5_stepmodel.py (H-STEPMODEL: the lag fitted on 2048x2048 only, which had been replayed in a scratch try before the freeze, the four other targets replayed only after); f4_phase.py (H-PHASE: the burst-end rule's X fitted on 2048x2048 bands 2 to 4, then the other targets; F5's B_k scored on the same rows); f8_full.py, f6_pendreq.py and f9_loss.py. Written after their inputs were read, post hoc: f5_opens.py (the model's block openings against F3's), f4_flips.py (B3 against the flips of E774, E799, E801) and f6_table.py (f6_pendreq.py's own tally tests a criterion its lines do not fit; this counts the lines). Every value the held-out sides score had been printed by the planner's left_table.out, gap_rule.out or steps_iv.out (closing6/dpm/) or by E852/E861 before the scripts were written, so no line here is held out in the strict sense: fit side post hoc, the rest SEMI. Each script re-run from its published copy (resgx545-data cited/closing6/dpm/offline/) printed output byte-identical to the kept .out files, and every published script has the hash its FREEZE file names; the two as-run copies reproduce their kept outputs except the file paths of the traceback at their stop"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r1-pixgeo:out/g-c1/", "render-closing-r2-geo:out/g-c2/", "render-closing-r2-geo:out/g-c3/", "render-closing-r3-geo:out/g-c4/", "render-closing-r3-geo:out/g-c5/", "render-closing-r3-geo:out/g-c6/", "render-closing-r3-geo:out/g-c7/", "render-closing-r3-geo:out/g-d36/", "render-closing-r5-dpm:out/a2/", "render-closing-s1:out/g-e1/", "render-closing-s1b:out/g-e1/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "CR_DPM_PARTIAL_RENDER", "CSTREAM.PRIM_TILES"]
+++
**What was done.** E852 found the global page count stepping at fixed page counts S_k per target
and E862 a margin below each step in which the first partial render leaves one global page
instead of two; Q210 asks what sets both. The round 6 planner (O2 to O6) read the global list as
object blocks and the page take as bursts after each step, then creep. The offline stage turned
that into scripts with fit and held-out sides; every number below is printed by them
(the `.out` files in `closing6/dpm/offline/`).

**Results [HW, post hoc and SEMI].**

- *The object blocks (F2, `f2_objpage.out`).* In every dump whose PB page 1 is the list's head the
  first block's two head dwords recur every 67 dwords. Global page k of the first run is PB page
  S_k + 1, and the head pair recurs there exactly at the offsets o with (1024 (k - 1) + o) a
  multiple of 67: 2 of 2 pages in the fit dump (R5-dpm a0-cal-2048), 149 of 149 in the other
  dumps (pages 2 to 5 at five targets). After a partial render the list's head is no longer page
  1: the render frees the list's first pages (chains such as `0x241 0x35c ...` at 4096x4096).
- *The streams (F3, `f3_streams.out`, `f5_opens.out`).* In the dumps of jobs that completed in one
  run, a block holds entries up to 31 dwords and then the link (full blocks hold 31, 30 or 29
  dwords: 11463, 2646 and 47 of them at 2048x2048). Entries are 2 dwords (`0x90`, or one tile
  with at most two primitives) or 3 (a mask dword), and the entry of object b_k (15, 30, 45, 61,
  76, 91) has one more, the new page's base (`PRIM_TILES` bit 5; 2293 to 2329 regions each). So
  every region the whole triangle covers opens a block at objects 0, 15, 30, 45, 60, 75 and 90
  (2341, 2220, 2221, 2220, 2149, 2137 and 2089 regions at 2048x2048, 2450 regions with a
  stream), and the regions only some copies reach open blocks at other objects (10 to 98, 1 to 85
  regions each).
- *The replay (F5, `f5_stepmodel.out`).* `f5lib.py` builds the scene from the tool's source
  (triangle j moved j/16 pixel, five to an object), HU1's tile test, the entry sizes and block
  rule above and a page per macrotile every 32 blocks. With the TA writing object b to the list
  just before it tiles object b - 3 (the lag, the smallest of 0 to 4 that fits 2048x2048: lags 1
  and 2 put S7 at `0x1cb`, lag 0 misses S5 to S7) it gives the dumps' block openings object by
  object (2048x2048: identical, 16606 blocks; 4096x2048: identical up to object 76, where the
  dump's later objects could not be placed), U = `0x213` at 2048x2048 (E785) and `0x3f7` = 1015
  at 4096x2048 (a2b-cal-4x2's need, E861), and these steps against F1's brackets (E873):

| target | side | steps in bracket | steps |
|---|---|---|---|
| 2048x2048 | fit | 6 of 6 | `0x51 0x9d 0xe8 0x132 0x181 0x1ca` |
| 4096x2048 | SEMI | 6 of 6 | `0x97 0x126 0x1b9 0x24a 0x2db 0x36c` |
| 2048x4096 | SEMI | 5 of 6 | S3 `0x129` against `0x12c`; S2, S4 to S7 in |
| 3072x3072 | SEMI | 6 of 6 | `0xa9 0x14d 0x1ef 0x293 0x335 0x3d9` |
| 4096x4096 | SEMI | 3 of 3 | `0x125 0x240 0x35b` |

- *The phase (F4, `f4_phase.out`, `f4_flips.out`).* Scored on every distinct (thr0, pages left)
  row of the kept first partial renders, grow cells (thr0 = S_k) aside: left = 2 iff S_k < thr0 <
  E_k. With the model's burst end B_k (the page count after the first object with an index
  divisible by 15 tiled after the step) the rule placed 26 of 26 fit rows at 2048x2048 and 60 of
  61 others (2048x4096, 3072x3072, 4096x2048, 4096x4096); the miss is R3-geo c5b-cal, whose last
  in-stretch sample reads 0 global pages. B3 is the first silent cell of the raise at all five
  targets: `0xe3`, `0x352`, `0x1b3`, `0x1b7`, `0x1e9` against E799, E774 and E801. The frozen
  burst-end rule from timelines (the first T >= S_k + 2 after which no page comes for 75 us, X
  fitted on 2048x2048) placed 26 of 26 fit rows and 49 of 61 others: at 2048x4096 (bands 3, 4, 7)
  and 3072x3072 (band 7) its E_k fell at S_k + 2, where the wait after the step lies there.
- *The pending page (F6, `f6_pendreq.out`, `f6_table.out`, read after).* In the 21 kept jobs that
  grew the global list (thr0 = S_k) the first sample after the first partial render reads 2 global
  pages, after a minimum of 1 (0 in one) inside it; the 7 kept S_k - 1 cells read 1 there and the
  7 S_k + 1 cells 2.
- *E802 (F8, `f8_full.out`, post hoc).* `--tri-full`'s blocks are 71 dwords and 170517 of 171504
  of its stream entries carry a mask dword (`0x88`, `0x8c`); the same replay with those constants
  and lag 3 gives S2 = `0x201` (bracket [`0x200`, `0x201`]) and S3 = `0x302`: every region opens a
  block every 10 objects and the 14 objects before the 2nd global page take 2 bursts of 256 pages.
- *Partial renders (F9, `f9_loss.out`, exploratory).* The replay with a refused request starting a
  partial render that keeps the global pages holding the objects written and not yet tiled, and
  restarts the streams, with the job's own raise, gives the count of 43 of 43 kept 2048x2048 jobs
  with a partial render (R2-geo g-c3, R3-geo g-c4 and g-d36, R5-dpm d-a1, d-a2 and d-t) and
  every run's peak in 27.

**What it shows [infer].** The TA's page take for this scene is its stream blocks plus its global
pages, and the replay says when each comes: a global step is the write of the object that crosses
a page of the list; three objects later the TA tiles an object whose entry no longer fits in any
covering region's block, and those regions take blocks together (the burst, about a page per 32
regions); between bursts only the regions the moving copies reach open blocks (the creep). The
steps are evenly spaced because the list's pages hold 15.28 objects and the blocks 15 entries. The
margin of E852 and E862 is the burst: while the request refused falls between a step and its
burst's end, the objects under way span the last two list pages and the render keeps both; after
the burst it keeps one; at a step the refused request is the list's page itself, which the TA
takes as it restarts (H-PENDREQ). With R-5's guard (3d.md §6.4) that places every raise flip C.

**What it does not show.** No hardware held-out test: every compared value was printed before the
scripts. The lag of 3 objects is fitted, and why the TA writes ahead is not shown. The 2048x4096 S3
miss (3 pages) is not explained. The entry-size rule is read from the dumps of one scene and the
`--tri-full` constants from its own; other scenes, `--vtx-coords` (which parts H-BURST-PAGE from
H-BURST-CAP: here the blocks open at multiples of 15 entries, CAP's reading, with the base dword
at b_k) and the 1350-vertex scene are not modelled. F9 is exploratory and its keep rule was
chosen with the H-PHASE reading in mind.

**Correction 2026-11-12:** Round 6's laptop session R6-dpm held this record's rules out on the
hardware (E881 to E883); every frozen headline there is gated "cannot tell" by an r-a0 control
that has no reading by construction, so what follows is the ungated reading, post hoc. [HW, post
hoc] The step model held at three targets it was not read on: 2048x1024, 1024x2048 and 1536x1536
gave 18 of 18 steps in their brackets and the needs 277, 288 and 314 as replayed, and H-PHASE held
at their bands 3 and 4, 18 of 18 cells, with B3 the first silent cell of the raise at all three
(E881). At 2048x2048 bands 5 to 7 H-PHASE failed 5 of 15 cells: the first threshold that left one
global page was `0x178`, `0x1c3` and `0x20d`, the model's B_k + 2, + 2 and + 1 (E881), so "the pages
left are 2 iff the threshold falls between a step and B_k" is a reading of the kept rows and bands
3 and 4, not a rule of every band; the claim line is edited to say so. With larger objects
(`--vtx-coords` 4 and 8) neither the stream-block capacity reading this record leaned to
(H-BURST-CAP) nor one burst a step gave the steps (CAP 10 of 13 at N 4, 1 of 19 at N 8; E882).

Claim line edited 2026-11-12 (HACKING.md, Workflow: a correction that contradicts the claim):
where it now reads "else 1 on the kept rows (H-PHASE: ... the miss a row reading 0; held out in
R6-dpm, ... E881)" it read "else 1 (H-PHASE: 26 of 26 fit rows at 2048x2048, 60 of 61 rows of the
other targets, the miss a row reading 0)", and the mark "[corrected 2026-11-12, see Correction]"
was added at its end.

**Correction 2026-11-13:** r8-ldpm pinned the two steps this replay misses by the cell, from the
global page count at the first abort (E935) [HW, held out]: 2048x3072's S6 is `0x234` (the replay
`0x233`, E915's one-sample reading confirmed three times) and 2048x4096's S3 is `0x12c` (the
replay `0x129`, three pages low, as the kept creep cells read). Its steps held at four more
targets' calibrations (1536x1536, 1024x1024, 4096x2048, 3072x2048) and missed two new ones,
2560x3072's S6 by one page and 3072x2560's S3 and S6 by two (E936). F9's replay with partial
renders gave 13 of 15 held-out counts at 1536x1536, 1024x1024 and 3072x2048; the two misses are
band 4 cells where the threshold was not raised (E938).
