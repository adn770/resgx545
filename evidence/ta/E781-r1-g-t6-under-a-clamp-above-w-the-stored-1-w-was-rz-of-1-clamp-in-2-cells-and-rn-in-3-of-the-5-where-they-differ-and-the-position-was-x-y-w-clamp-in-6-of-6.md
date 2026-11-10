+++
id = "E781"
claim = "R1-pixgeo stage g-t6 (7 jobs: a vertex program with x and y scaled by w = 1e-5 or 1e-4 and the state block's clamp (word 14) from 3e-5 to 1.2e-3): the control t6-ctl (clamp 3e-5, S1b's e3k-i-c3e5) held its stored 1/w 0x47023555, and in the six held-out cells the TA wrote an object each time with a 1/w that was always one of the two floats next to the exact 1/clamp, round-toward-zero in 2 cells (clamp 6e-5: 0x46823555; 7e-4: 0x44b29249) and round-to-nearest in 3 (1.5e-4: 0x45d05555; 6e-4: 0x44d05555; 1.2e-3: 0x44505555) of the 5 where the two differ, the sixth (clamp 2e-4: 0x459c4000) being a cell where they agree, so the stored 1/w under a clamp is within 1 ulp of 1/clamp and not a rounding rule; the stored x and y were the program's x and y divided by the clamp (the triangle shrunk by w over the clamp, HREP-xy') in 6 of 6 held-out cells within 1/64 pixel; the frozen verdict: control holds; mixed (RZ 2, RN 3 of 5): within 1 ulp, not a rounding rule; position HREP-xy' 6 of 6"
unit = "ta"
method = "R1-pixgeo stage g-t6 of the question-closing pass, round 2 (decision R2-17; 7 jobs: the control t6-ctl and the cells t6-c-6e5, t6-c-1p5e4, t6-c-2e4, t6-c-6e4, t6-c-7e4 and t6-c-1p2e3) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:54 laptop time (08:54 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 32 --pixels --tri vtxuse --width 64 --height 64 --blk 14=CLAMPWORD --dump-render with the vertex program t6-NAME__0.bin (vtx_wclip with x and y scaled by w, assembled on the Mac, frozen by sha256; clamp words 0x37fba882 = 3e-5, 0x387ba882 = 6e-5, 0x391d4952 = 1.5e-4, 0x3951b717 = 2e-4, 0x3a1d4952 = 6e-4, 0x3a378034 = 7e-4 and for the last cell the clamp 1.2e-3), a debugfs reset before each job, all 7 of class ok (rc 0); the object decoded through pbdump, its 1/w word compared with the frozen RZ word and RN word of the exact reciprocal of the clamp (the six cells chosen where they differ except 2e-4) and its vertices with the frozen shrunk position within 1/64 pixel; scored by the frozen score/score_r1.py g-t6 (out/score-g-t6.txt), re-run on the kept files with the same SUMMARY"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-t6/"]
terms = ["PB_OBJ.RHW", "WCLAMP"]
+++
**What ran.** E736 and E754 found that under a clamp the object stores 1/clamp as the 1/w and the
triangle shrunk by w over the clamp, and that no rounding model fitted the 1/w at every clamp (the
truncated reciprocal at a clamp of 3e-5, the rounded one at 3e-4). The stage chose clamps where the
float32 reciprocal rounded toward zero (RZ) and to nearest (RN) differ and one where they agree, and
froze both words and the position for each.

**Frozen verdict.** `control t6-ctl holds; mixed (RZ 2, RN 3 of 5): within 1 ulp, not a rounding
rule; position HREP-xy' (x, y / clamp) 6 of 6`.

**Results [HW].** Control (clamp 3e-5, w 1e-5): 0x47023555, an object at (24,24), (40,28), (28,40).
Cells, with the stored word and its class: clamp 6e-5 over w 1e-5: 0x46823555 (RZ; RN is ...56),
object (28,28), (36,30), (30,36); 1.5e-4: 0x45d05555 (RN; RZ ...54), (30.40,30.40), (33.60,31.20),
(31.20,33.60); 2e-4: 0x459c4000 (both), (30.80,30.80), (33.20,31.40), (31.40,33.20); clamp 6e-4 over
w 1e-4: 0x44d05555 (RN; RZ ...54), (28,28), (36,30), (30,36); 7e-4: 0x44b29249 (RZ; RN ...4a),
(28.57,28.57), (35.43,30.29), (30.29,35.43); 1.2e-3: 0x44505555 (RN; RZ ...54), (30,30), (34,31),
(31,34). All six wrote an object, which E754 had not found for a clamp of 1e-3 over w 1e-5 (the
objects here are at least 2.4 pixels wide). With the control (RZ, E754's 3e-5 again) and E754's
3e-4 (RN): the clamps that gave RZ are 3e-5, 6e-5 and 7e-4, those that gave RN 1.5e-4, 6e-4 and
1.2e-3 and (from E754) 3e-4.

**What it shows.** The 1/w stored under a clamp is one of the two floats around 1/clamp, never
further, and which one does not follow the clamp's size or the w (RZ at 6e-5 and 7e-4, RN at 1.5e-4
and 6e-4), so a simulator can store 1/clamp as either neighbour and report it as fitted, not exact
(the rule the proposal named). The position rule x_stored = x_in / clamp, in the band, held in
6 of 6 new cells (E754 found it in 4 of 5 jobs).

**Not shown.** A rule for the 1/w word, the clamp's effect when the triangle is smaller than
E780's threshold, a perspective w (only equal w at the three vertices was run), and the depth
under a clamp.
