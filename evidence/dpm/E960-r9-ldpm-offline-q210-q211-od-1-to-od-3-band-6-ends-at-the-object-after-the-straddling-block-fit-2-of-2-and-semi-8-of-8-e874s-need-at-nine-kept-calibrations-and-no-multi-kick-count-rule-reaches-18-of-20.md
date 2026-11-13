+++
id = "E960"
claim = "Round 9 offline steps of r9-ldpm (Q210, Q211; no run), each frozen by hash before its scoring: OD-1, E874's replay gives the need of the 1500-vertex scene at all nine kept calibrations (E915, E935, E936) and HU1 of its 500 triangles none (0x52 against 0x213 at 2048x2048), so HU1 is not that scene's need, and it picks four wide targets never run (4096x1024, 4096x1536, 3584x1024, 2048x512, U 0x20f, 0x302, 0x1d0, 0x9a); OD-2, the 'left 0x6' cells of E936 are the reader's last sample before the global list was trimmed (the next sample reads 2), and band 6 keeps the second global page until the object after the straddling block is tiled (H-NEXT1: 2 iff S_6 < thr0 < the page count once object b_6 + 1 is tiled), fitted on 3072x3072 and 2560x2560 (2 of 2) and SEMI on E936's eight other targets (8 of 8, where H-SPAN's A_6 gives 4 of 8), frozen only after one reader fix written after the first run's table was read (offline/OD2-FIX.md: the first run, its artefact test wrong, froze nothing); OD-3, of a closed family of six multi-kick count rules fitted on OL7 (b)'s 31 kept cells the best (H-FLUSH, 30 of 31) gave 7 of 20 of E938's cells (semi-held-out; H-KICKS 11), below the plan's 18, so stage k2 did not run"
unit = "dpm"
method = "Offline, no run (round 9, decision R9-5 (a); seeds plan closing9/seeds/exp-seeds-r9.md section 7, OD-1 to OD-3), by r9-ldpm's builder before the session was built, in render/closing-r9-ldpm offline/ (standard library): ol7lib.py and ol7_b_multikick.py are r8-ldpm's byte copies (render/closing-r8-ldpm gen/ol7/), loading E874's f5lib and f9_loss, E900's g3_span and HU1 from their published copies, hash-checked. od1_wide.py (FREEZE-od1.sha256, frozen before its run) scores E874's replay U and HU1 of the scene's 500 triangles on the nine kept calibration needs of r8-ldpm m6 and sp and R7-dpm, then U at twelve wide candidates (the plan's four first) and one F9 cell each. od2_band6.py reads r8-ldpm's kept m6, sp, a0 and f9 rows with r8-ldpm's frozen reader (score/read.py): (a) the last sample of the first partial render against the next sample, (b) per target A_6 and the replay's page count after objects b_6 + d, (c) ten candidates H-NEXTd (d = 0 to 4, d = 0 being H-SPAN) and H-HALFd, d fitted on 3072x3072 and 2560x2560, scored on the eight other targets; frozen (FREEZE-od2.sha256) before its first run, which used `next` only where `left` exceeded the abort's count and so read the two artefact cells as 6 and froze nothing (od2_band6.as-run.py and od2_band6.out kept); the fixed test (left = the abort's count, above 2, next below it; OD2-FIX.md, hash recorded before the second run) froze H-NEXT1 (H-HALF2 is the same end by algebra). od3_fit.py (FREEZE-od3.sha256) scores six rules written before its run (H-KICKS, H-KICKS-NORAISE, H-NR, H-LASTNR, H-FLUSH, H-FLUSH-LASTNR) on OL7 (b)'s 31 kept cells of closing-s1 g-e2a, g-e2b and closing-r1-pixgeo g-u1; the best was frozen by name and hash, then od3_score.py read r8-ldpm stage k's 20 explore cells (E938 had printed H-KICKS's aggregate). r9_tables.py (FREEZE-tables.sha256) wrote the session's tables; its run 1 found H-NEXT1's end equal to A_6 at three of the plan's four m6b targets, and run 2 took three targets where they part and one where they agree (model numbers only, no reading of them existed)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-ldpm:offline/", "render-closing-r8-ldpm:out/20261113-021431/m6/", "render-closing-r8-ldpm:out/20261113-021431/k/", "render-closing-s1", "render-closing-r1-pixgeo"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What was done.** The plan's three offline steps before the session was built, each frozen by hash
before it read what it scores. OD-1 asked which rule gives the need of wide scenes of the
1500-vertex triangle and picked four wide targets; OD-2 read band 6's extra cells (E936) for a rule;
OD-3 looked for a count rule of scenes of several kicks good enough (18 of 20 of E938's cells) to
run stage k2.

**Results.** OD-1 (`offline/od1_wide.out`) [HW, the needs read; the rule E874's]: E874's replay U
equals the read need at all nine kept calibrations (1024x1024 0x99 to 4096x2048 0x3f7); HU1 of the
500 triangles gives 0x1b to 0x9a, none. OD-2 (`offline/od2_band6.out`, `.fixed.out`) [HW, post hoc
on kept rows]: at `m6-map-c1212-0x3cf` and `m6-c0404-0x82` every sample of the partial render reads
the abort's 6 and the next sample 2; at 94 of 98 kept rows the last and the next sample agree, the
two others being step cells (a page pending after the grow). With those two cells read as 2, the
first one-page cell of band 6 is the replay's page count after object b_6 + 1 at all ten targets
(+3 at 3072x3072, +2 at 2560x2560 and 1536x1536, +1 at 4096x2048 and 2560x3072, +0 at the other
five, where object b_6 + 1 opens no page) [fit on two targets, SEMI on eight]. H-NEXT2 holds 6 of
8, H-SPAN 4 of 8. OD-3 (`offline/od3_fit.out`, `od3_score.out`): H-FLUSH (after the first partial
render each kick end but the last and the first one's is a partial render) fits 30 of 31 and gives
7 of 20 counts of E938's cells; H-KICKS and H-KICKS-NORAISE 11 (the same rule on scenes of one
object, one global page), H-LASTNR 11, H-NR 7.

**Disclosure.** OD-2's frozen first run froze no candidate because its test for the artefact was
wrong; the fix was written after its table was read, in which H-NEXT1's ends already matched every
target but the two artefact cells. H-NEXT1 was therefore a fit with SEMI support when stage m6b was
frozen on it; m6b held it out (E961).

**What it shows.** E874's replay, not HU1, gives the 1500-vertex scene's need [HW]. Band 6's second
page is kept to the object after the straddling block at the ten targets read [fit and SEMI]. No
rule of the family gives the multi-kick counts.

**What it does not show.** Why b_6 + 1 (and whether bands other than 6 end there); a multi-kick
count rule.
