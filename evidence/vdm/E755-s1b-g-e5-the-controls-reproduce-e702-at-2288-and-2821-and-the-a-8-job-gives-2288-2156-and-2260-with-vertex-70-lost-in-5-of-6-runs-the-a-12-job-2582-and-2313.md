+++
id = "E755"
claim = "Of E702's three events, in S1b's run of the same VDM words at R * V = 33 on a 64 x 64 target with 126 vertices, 8 coordinate outputs (the o0 histogram counts the pixels still reading 0xff203040, x), the two controls reproduce E702 (attribute rows 1 at N = 8: x2288, no vertex lost; attribute rows 9 at N = 2: x2821) but the a = 8 job (attribute rows 8) is not a function of its words: three runs with a reset before each gave x2156 with vertex 70 lost and objects split 15, 15, 15, 15, 9, 15, 9, 15, 15, 3; x2260 with vertex 70 lost and the regular split 15 x 8 and 6; and x2288 with no vertex lost, and three runs with no reset before gave x2260 with vertex 70 lost 3 of 3, the lost-vertex patterns of the two triples differing (HC, state carry, held out: the frozen scorer prints DIFFERENT; not ruled out by this table); the a = 12 job (attribute rows 12) gave x2582 and x2313, neither E702's x2028, nor the base x2288, and not S1's x2582 in 3 of 3: frozen HI, not a function of the words, in 2 of 2 (repeat only)"
unit = "vdm"
method = "S1b stage g-e5 of the question-closing pass (10 jobs, run in this order: the controls r-n8-a1 and r-n2-a9, a8 with a reset before each (r1 to r3, repeats of S1's a = 8 job), a8 without a reset before (nr-r1 to nr-r3, the held-out HC comparison: each starts from the state the previous job left), a12 twice (repeats of S1's a = 12 job)); probe --tri pixpds:12 --temps 32 --width 64 --height 64 --vertices 126 --vtx-coords 8 (2 for a9) with --vdm 6^=0x50000000 (a1) and --vdm 7^=0x00000400 (a9, N = 2), 0x00000480 (a8) or 0x00000680 (a12) added, the pixel program pix_pa0 and the vertex program vtx_c8 or vtx_c2, --dump-render; the runner's reset before every job but the three noreset ones; the tool echoed the VDM words of every job (the knob proof, a mismatch voids the job: none did); on the laptop (direct cable), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); tables, predictions, scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256); scored by the frozen score/score_s1.py g-e5 (out/score-g-e5.txt, re-run from the dataset with the same output), the lost vertices from the parameter-buffer dumps with q164_fate.py of vdm/verification-1141ta/recompute (read-only, frozen by hash)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/g-e5/"]
terms = ["VDM_TASK1.OUTPUT_SIZE"]
+++
**What ran.** E738 (S1) repeated E702's three events after controls and found the a = 7 event and
the 32-row hang repeating, the a = 12 job changing the render each time but to x2582 (not E702's
x2028), and the a = 8 job changing it in 2 of 3 runs (x2288, x2156, x2156, vertex 70 lost). S1b
took the a = 8 and a = 12 cases only, with frozen values: HO is the base histogram (2288, no
vertex lost), HL70 is S1's post-hoc reading of the a = 8 loss (x2156, vertex 70 lost), HS1 is S1's
a = 12 reading (x2582, no vertex lost), HD is E702's a = 12 value (x2028). The a = 8 repeats are
S1's post hoc fits run again (scored apart as "repeat only"), as are the a = 12 repeats. The one
new question is HC: whether the state left by the previous job carries (three a = 8 runs without a
reset before them against three with).

**Frozen verdict.** `controls reproduce E702; held out: r-n8-a8-nr: neither frozen model (HO (the
base), HL70 (S1 post hoc)): 2260 in 3 of 3; HC (state carry): reset ['', '70', '70'] vs no reset
['70', '70', '70']: DIFFERENT patterns; repeat only: r-n8-a8: HI (HO (the base) in 1 of 3: not a
function of the words) [(2156, '70'), (2260, '70'), (2288, '')]; r-n8-a12: HI (HS1 (S1 post hoc:
2582 x3) in 1 of 2: not a function of the words) [(2582, ''), (2313, '')]` (out/score-g-e5.txt).
The controls reproduced E702's histograms (2288, 2821) in both jobs, with no vertex lost in the a
= 1 one and all 126 vertices placed in nine objects (15 x 8 and 6) in both.

**Results [HW].** Every job rc 0, class ok, the kernel log clean, health fine after the stage.

| job | reset before | o0 count | vertex 70 | object sizes |
|---|---|---|---|---|
| a1 (control) | yes | 2288 | present | 15 x 8, 6 |
| a9 (control, N = 2) | yes | 2821 | present | 15 x 8, 6 |
| a8 r1 | yes | 2156 | lost | 15, 15, 15, 15, 9, 15, 9, 15, 15, 3 |
| a8 r2 | yes | 2260 | lost | 15 x 8, 6 |
| a8 r3 | yes | 2288 | present | 15 x 8, 6 |
| a8 nr-r1, r2, r3 | no | 2260 (3 of 3) | lost (3 of 3) | 15 x 8, 6 |
| a12 r1 | yes | 2582 | present | 15 x 8, 6 |
| a12 r2 | yes | 2313 | present | 15 x 8, 6 |

In the 2260 runs the objects hold 126 vertex slots, no vertex id is repeated, and id 70 is the
only one not found (the decoder's id of one slot is missing). The pixel count of the three
outcomes of the a = 8 words differs by 28 (2260) and 132 (2156) pixels from the base; the 2156 and
the 2260 runs lost the same vertex and differ in the object split and the histogram. The TA-data
dump is byte-identical in all ten jobs (one sha256); the parameter buffers of a8 r2, nr-r1 and
nr-r2 are byte-identical, nr-r3's (same count, same lost vertex) differs.

**Post hoc (read after the run; [infer], not held out).** The a = 8 words give three outcomes over
six runs with a reset before each or none, so the outcome is not a function of the words (S1's
three runs gave two outcomes). Without a reset the loss of vertex 70 and the count 2260 repeated 3
of 3 and with one it repeated 2 of 3 (one 2260, one 2156); with three runs a side that is a
difference of one run, which the frozen scorer reports as DIFFERENT patterns and which is not a
test of state carry: a carry that depends on the previous job (the clean 2288 run preceded the
first noreset job, which lost vertex 70) would have to be a property of more than the loss. The a
= 12 count moved to 2313 where S1 saw 2582 three times, so the a = 12 change of render is not a
constant either; vertex ids were all present in both runs, as in S1's. The loss of vertex 70 also
exists in the 2260 runs without the 2156 split, so the event E702 called a constant row (a = 7)
and this one (an id missing at 70) are of the same kind only by the missing id.

**Not shown.** A rate: six a = 8 runs and two a = 12 are too few to give a probability, and the
ordering of the jobs (controls first, a = 8 with a reset, then without, then a = 12) means a state
from the controls or from the a = 12 jobs is not separated from the reset; what the missing id at
70 holds (a default row, a vertex of the first row, E702's constant row); what E546's lost vertex
at R * V = 33 was; and whether a hardware or a firmware state selects the outcome, which a reset
before every job (the runner's) does not remove.