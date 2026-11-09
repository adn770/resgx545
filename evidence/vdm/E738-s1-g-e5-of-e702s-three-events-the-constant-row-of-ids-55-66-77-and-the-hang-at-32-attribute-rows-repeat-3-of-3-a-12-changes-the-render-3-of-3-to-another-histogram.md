+++
id = "E738"
claim = "Repeated three times each after controls that reproduced E702's histograms (N = 8 base 0xff203040 x2288, N = 2 base x2821), E702's events at R*V = 33 and 32 behave as follows: 7 attribute rows at N = 8 give x2285 in 3 of 3 (the frozen verdict HD) and 32 rows at N = 2 hang 3 of 3 (HD); 12 rows at N = 8 give x2582 in 3 of 3, which the frozen scorer labels HO but which is neither E702's x2028 (HD) nor the base x2288 (the proposal's HO); 8 rows at N = 8 give x2288 once and x2156 twice (HI, 2 of 3); read after the run with q164_fate.py's decoder, the a = 7 jobs lose ids 55, 66 and 77 in 3 of 3, the a = 12 jobs keep every vertex in the regular split, and the two changed a = 8 jobs lose vertex 70 with objects of 9, 9 and 3 vertices"
unit = "vdm"
method = "S1 stage g-e5 (14 jobs, 6 conditions; paths relative to render/closing-s1/ of the dataset: E702's commands, probe --tri pixpds:12 --temps 32 --width 64 --height 64 --vertices 126 --vtx-coords N with --vdm 6^= and --vdm 7^= for the field and the attribute rows, --dump-render, pix_pa0 and vtx_cN programs rebuilt from the landed templates), the expected hangs declared (expecthang), a debugfs reset before each job, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage; scored by the frozen score/score_s1.py g-e5 (out/score-g-e5.txt, the tool's o0 mixed line and the echoed VDM words as knob proof); vertex fates by analysis/scripts/geo_e5_fate.py, written after the run, which applies the functions of resgx545-data vdm/verification-1141ta/recompute/q164_fate.py to the S1 dumps"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/g-e5/"]
terms = ["VDM_TASK1.OUTPUT_SIZE"]
+++
**What ran.** Q272 asks whether E702's three events (a = 7: a constant row; a = 12: 260 pixels
changed with an irregular split; N = 2 with 32 rows: a hang) and E546's lost vertex (a = 8) repeat.
Frozen: HD (each repeats 3 of 3 as E702 saw it), HO (none repeats: the base histogram 0 of 3), HI
(1 or 2 of 3: not a function of the words).

**Frozen verdict.** controls reproduce E702; r-n8-a7: HD (3 of 3); r-n8-a12: HO (0 of 3); r-n8-a8:
HI (2 of 3); r-n2-a32: HD (3 of 3) (out/score-g-e5.txt).

**Results [HW].** a = 7: x2285 three times. a = 12: x2582 three times (the three 0xbea80000,
0xbe980000 and 0xbe880000 colours x46 each as in the base, "other" x1376 against the base's x1670).
a = 8: x2288, x2156, x2156 (the first run after the a = 12 runs is the unchanged one). 32 rows at N
= 2: hung 3 of 3 and recovered. The echoed VDM words matched the table in every job.

**The a = 12 label.** The scorer compares a = 12 with E702's x2028 only and calls 0 of 3 "HO";
the proposal's HO is the base x2288 in 0 of 3. By the frozen definitions the result is neither: the
render changes in 3 of 3, to a histogram that is not E702's.

**Post hoc vertex fate [infer from the dumps].** a = 7: ids 55, 66 and 77 unreadable in 3 of 3 (the
three of E702), 9 objects (15 x 8 + 6). a = 12: every vertex present, the regular 15 x 8 + 6 split
in 3 of 3 (E702's job split 15 x 7, 9, 12). a = 8: the first run clean; the second and third lose
vertex 70, 10 objects of 15, 15, 15, 15, 9, 15, 9, 15, 15 and 3. Base jobs clean. So a lost vertex
appeared again in the a = 8 jobs, twice in three and vertex 70 both times (E546's record does not
give its vertex id, so that it is E546's vertex is not shown); and a = 12's change here is not the
split E702 decoded. A frozen run that confirms needs the fate in the scorer and a reset-or-not pair
for a = 8.

**Not shown.** What the constant row is, what makes a = 8 split in some runs, and what a = 12
changes in the image when every vertex is present.
