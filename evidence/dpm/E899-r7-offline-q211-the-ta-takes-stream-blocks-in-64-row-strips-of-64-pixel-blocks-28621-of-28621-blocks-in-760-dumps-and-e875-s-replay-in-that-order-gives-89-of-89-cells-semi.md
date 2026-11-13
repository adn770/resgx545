+++
id = "E899"
claim = "Round 7 offline stage G1, G2 and G4 (Q211; no run): the TA takes a region's 128-byte stream block walking the target in strips of 64 pixel rows, each strip in 64 x 64-pixel blocks left to right and a block's 32 x 16 regions row by row, a macrotile filling its current page (32 blocks) before it takes another (H-WALK64, named by the planner after printing u-2048's pages): frozen verdict HELD, every block of 760 kept dumps of one-object, one-kick jobs without a partial render at its page and slot, 28621 of 28621 (fit u-2048 2341; SEMI ten dumps, 13683; held out 749 dumps, 12597, of which only 18, at 1024x768 and 128x128 with 8009 blocks, separate the walk from row order, which places 2114 of those; none held out above 1024x768); E875's replay, unchanged, in that order gives the partial-render count and every TA run's peak of the 89 kept one-triangle cells at 4096x4096 (eight scenes, U 119 to 287) and the 37 record counts of E625 and E779 (frozen verdict HELD, SEMI: the planner had tallied every cell), where row order gives 83 counts and 47 peak sets and column order 73 and 23; read after, in scenes of several kicks each kick is one more walk of a macrotile's blocks, and the first block of a later walk went to the page the earlier one had left open 157 of 163 times (21 dumps)"
unit = "dpm"
method = "Offline, no run (round 7, area dpm, decision R7-1 a; plan closing7/b/exp-dpm-r7.md section 3, steps G1, G2 and G4; no lead stop). The scripts in closing7/b/offline/ (standard library only; olib.py the shared reader, the round 6 library from its published twin cited/closing6/dpm/offline/, dpm_words.py of this tree) read the kept render dumps (PB and TA data) and timelines of resgx545-data render/closing-*/out read-only. g1_walk64.py: the dumps of every cases.tsv row that draws one object of the tool's triangle in one kick (tri or --tri, no --vertices other than 3, no --geometry, no -n above 1, no --obj2, --aa4, --poke, --kpoke, --kpoke-render, --vdm, --fault, --cmd or --tadata-fill-render; the last render's dump only) and completed it (no 0x0658 stretch in the timeline or, without one, a target whose every region taking a block stays below P - 0x22); every region header with a stream is replayed in the walk's order (a macrotile's blocks fill its current page, 32 a page; pages ranked by address) and its (page rank, slot) compared with the header's address; the fit and SEMI dumps named in the script. Freeze order (FREEZE-LOG.txt, sha256 in FREEZE-g<n>.sha256 before the first run that opened held-out data): g1_walk64.py and olib.py after a dry run on the fit and SEMI dumps only (g1_walk64.dryrun.out); g2_replay64.py (the planner's q211_replay64.py and q211_records64.py cell rules, unchanged); g4_multikick.py (exploratory, no verdict). No script was fixed. Each re-run from the published copy (resgx545-data cited/closing7/b/offline/, Python 3.15.2, data and tree from this fold's worktrees) gave output byte-identical to the kept one. The planner's tallies (closing7/b/q211_walk64.out, closing7/b/q211_replay64.out, closing7/b/q211_records64.out) are the reason the G2 cells and the ten dumps are SEMI"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r1-pixgeo:out/", "render-closing-r2-geo:out/", "render-closing-r3-geo:out/", "render-closing-r3-pixel:out/", "render-closing-r3k-pixel:out/", "render-closing-r3k-regress:out/", "render-closing-r4-pixel:out/", "render-closing-r4-q285:out/", "render-closing-r4-render4x:out/", "render-closing-r5-pixel:out/", "render-closing-r5-render4x:out/", "render-closing-r6-pixel:out/", "render-closing-r6-render4x:out/", "render-closing-s1:out/", "render-closing-s1b:out/", "render-closing-r3-geo-c:out/g-qf/", "render-closing-r3-geo-c:out/g-qh/", "render-closing-r5-dpm:out/a2/d-b/", "render-closing-r6-dpm:out/a2/r-b/", "cited-scratch:cited/closing7/b/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "CR_DPM_PAGE_STATUS", "CR_DPM_PARTIAL_RENDER", "REGION_HDR.STREAM"]
+++
**What was done.** E875 replayed the partial-render count of one-triangle scenes page by page with
no fitted number; the walk order was the open detail, and row order, named after the counts were
read, failed on four new scenes (E883). The round 7 planner read the order instead of guessing it:
a region header holds the address of its stream block (`REGION_HDR.STREAM`), so a completed
one-object dump shows in which order the TA took the blocks of each page. From u-2048's pages
(q211_walk.py) the planner named H-WALK64 and scored it once on eleven dumps, then replayed E875's
cells in that order once. The offline stage redid both under a freeze: G1 scores the order on
every kept dump of a completed one-object, one-kick scene, by a rule fixed before any held-out
dump was opened; G2 the replay on the planner's cells; G4 reads scenes of several kicks.

**Results [HW; fit, SEMI and held out as labelled].** G1, `g1_walk64.out` (blocks placed exactly
at their page and slot):

| label | dumps | blocks | walk | row order | column order |
|---|---|---|---|---|---|
| fit (u-2048) | 1 | 2341 | 2341 | 140 | 3 |
| SEMI (planner's ten) | 10 | 13683 | 13683 | 939 | 42 |
| held out | 749 | 12597 | 12597 | 6702 | 1038 |

Frozen verdict: `VERDICT H-WALK64: HELD (0 dumps off)`; the replayed page count equals the dump's
in every dump. One dump met the args rule and was not scored (o8-1x-4096x4096-p422 of R4-render4x:
no 0x0658 in its timeline and a target that could reach the threshold). Of the held-out dumps 731
are 64x64 targets, one 64 x 64 block, where row order gives the same order; the 18 that separate
the walk from row order are 14 at 1024x768 (the default triangle in ten, the triangle moved in
one, `--tri-full` in three) and 4 at 128x128, 8009 blocks, row order placing 2114. Two of the 14
ended in -ENOSPC with no partial render (E866: the default triangle at P `0x34`, 27 blocks, and
`--tri-full` at `0x52`, 32 blocks); their dumps hold the blocks taken before the refusal.
The held-out dumps had been read by earlier records for other words (tiles, pixels), not for
their block addresses.

G2, `g2_replay64.out`: frozen verdict `VERDICT H-REPLAY64: HELD (0 of 89 cells off, 0 record cells
off; SEMI)`. By scene (U, cells; count and every run's peak exact): 287, 31 (g-qf 22, R5-dpm's
five repeats, R6-dpm's four controls); 275, 6; 262, 8; 243, 8; 220, 8; 198, 10; 179, 8; 119, 10.
Rivals on the same cells: row order 83 counts and 47 peak sets exact (s262 4 of 8 counts),
column order 73 and 23, E854's spacing d = 7/4 71 counts and d = 1 75. E625's ten and E779's nine
counts at 4096x4096 and E625's 18 at 1024x768: 37 of 37 for the walk and for both rivals.

G4, `g4_multikick.out` (exploratory, no verdict): 54 dumps of jobs with `--geometry` or `-n` above
1. In each region the scene's kicks share one stream block (blocks equal regions in every dump);
per macrotile the blocks in address order fall into as many walks as the scene had kicks with a
region in it (2 to 4 in the 21 dumps of scenes that ran in one TA run), and at each new walk the
next block went to the page the previous walk left open 157 times and to a new page 6 times.
u-4096-2 (two kicks) places 4697 of its 13804 first blocks by one walk, as the planner found.

**What it shows.** The walk order is not a guess any more: one order places every block of every
kept dump of a one-object, one-kick job without a partial render, 28621 blocks, from 64x64 to
4096x4096, and the 749 dumps opened only after the freeze place theirs too [HW]. With that order
E875's replay, unchanged, gives every kept count and every run's peak of one-triangle scenes at
4096x4096, where row order missed 6 counts and 42 peak sets [HW, SEMI]: the count clause of Q211 for
such scenes is the replay's. [infer] A later kick walks the target again, and its blocks fill the
pages each macrotile already has open before new ones.

**What it does not show.** The held-out part of G1 is mostly 64x64 dumps, which test the page take
and the slot order inside one block only; no held-out dump is larger than 1024x768, and the new
scenes among them are the three `--tri-full` dumps and the four at 128x128 (the other eleven repeat
scenes of the SEMI dumps), so the order across strips at large targets rests on the fit and SEMI
dumps (eleven, 512x384 to 4096x4096). G2 is SEMI: every cell's count and peaks had been
tallied by the planner before the freeze, and no new scene was run; the replay still needs the
frozen held-out cells the plan puts on the laptop (stage s-b). Scenes of many objects (the
1500-vertex scene uses E874's replay, in row order inside an object), the six new walks of G4 that
opened a page, and Q211's U clause for wide scenes are outside it. Contexts larger than the target
(`--max-width`), 4x arrays and hand-poked runs were not scored.

**Correction 2026-11-12:** The replay was held out on the hardware. Round 7's R7-dpm stage s-b
froze H-REPLAY64 for five new one-triangle scenes at 4096x4096 (twice), 4096x2048, 2048x2048 and
1024x768 (E916) [HW, held out]: 24 of 24 counts and every run's peak at 23 of 24 cells (the
frozen verdict held on four scenes and read "not supported" on the 1024x768 one, whose missing
peak is a first TA run that fell between two timeline samples, read post hoc), and H-WALK64 placed
every block of the scene's 2048x2048 calibration dump, a dump never opened, where row order placed
113 of 2306.

**Correction 2026-11-13:** The reading "a later kick walks again and fills the pages its
macrotiles have open", made into a replay (H-KICKS, round 8's OL7 (b): each kick's regions walked
in turn, a region counted once, the open pages filled), did not reproduce 4 of 31 kept multi-kick
cells offline and gave 11 of 20 counts (8 of 8 at 4096x4096, 3 of 12 at 2048x2048) and no run's
peaks at r8-ldpm's five multi-kick scenes (E938, explore rows) [HW]; the replay of the union in
H-WALK64's order gave none. It is not the count rule of several kicks. The one-kick replay this
record froze is untouched (E916).
