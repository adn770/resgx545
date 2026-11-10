+++
id = "E759"
claim = "Rerun with the order control c-u three times and the frozen criterion that the tag-2 fraction is at least 0.98 (S1 required exactly 1.0 and saw 0.990), the control passed in 3 of 3 runs (tag 2 at 486, 482 and 488 source pixels, the first-write tag 2' at 5, 4 and 2: fractions 0.990, 0.992 and 0.996; the first write survives at (16,27) and (17,27) in all three runs, at 5 sources including (16,25) and (18,27) and (19,27) in the first, as in S1); with the control E709's o4g-3 at 26 tag-5 pairs (17 to 29), S1's post-hoc readings of the predicate guard repeated in the same numbers: g25 == 7 gives no tag 2 (0 of 486 o1 landings), g25 == 0 gives 0.253 of the landings, all at (even, even) sources, g25 == 3 0.248, all at (odd, odd) sources, and the g23 test 0.237 (frozen 0.25 within 0.07); the frozen verdict is held out: none (no row of the table was held out), repeat only: HQ (g25 = the lane in the 2 x 2 quad) consistent 3, HP-g23 1, HA (all or nothing) refuted 3 of 3 and HN (both writes land, the second wins) 4 of 4, and the replicate c-k7-x-rep read the same tag-2 fraction (0.000) as c-k7-x with 61 dwords different"
unit = "pds"
method = "S1b stage p-c of the question-closing pass (17 jobs, x and y pairs of 64 x 64 pixel-task probes with the PDS setup of E709 and S1's p-c: c-e709 (the control of E709's o4g-3), c-u, c-u-r2 and c-u-r3 (both o1 writes unpredicated), c-k7, c-k0 and c-k3 (predicate g25 against k = 7, 0, 3), c-g23 (and.testtanz g23 & 0x10) and the replicate c-k7-x-rep; programs bins/ of the dataset, frozen; paths relative to render/closing-s1b/), a debugfs reset before each job, run 1794266362-25757 on 2026-11-10 00:19 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); tables, predictions, scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256; verified before the stage and before scoring); the o1 tag per source pixel from each x and y pair as S1 (gen/s1pix.py, score/score_pix.py), the S1 scorer's defects fixed in advance (the replicate compared, not dropped; the order criterion frozen as a minimum fraction); verdict by the frozen score/score_s1.py p-c (out/score-p-c.txt, reproduced on the kept files)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/p-c/"]
terms = ["PDS_SIZE.BITS17_16"]
+++
**What ran.** E742 (S1) could not read Q276 because its order control c-u failed an exact
criterion (tag 2 everywhere required; 0.990 seen), and its post-hoc reading was that the predicate
gates o1 per lane with g25 the pixel's place in its 2 x 2 quad (HQ). S1b ran the same programs
again, the order control three times with the criterion frozen at 0.98 (a value set from the one
S1 run, PREFLIGHT inconsistency 8), and froze S1's post-hoc fits as repeats: HQ (tag-2 fractions 0,
0.25 and 0.25 for k = 7, 0, 3 with the tag-2 sources at no pixel, (even, even) and (odd, odd)),
HP-g23 (0.25, refrozen from S1's 0.253), HA (all or nothing per job) and HN (every write lands,
the second wins: tag 2 everywhere). No guard row of this table is held out: each is S1's
post hoc fit run again, and the scorer prints "held out: consistent none, refuted none" for that
reason.

**Frozen verdict.** controls pass; held out: consistent none, refuted none; repeat only:
consistent ["HP-g23 (refrozen from S1's 0.253: S1 post hoc) (1)", 'HQ (S1 post hoc: g25 = the lane
in the 2x2 quad) (3)'], refuted ['HA (3 of 3)', 'HN (4 of 4)']; replicates c-k7-x-rep same
(out/score-p-c.txt).

**Results [HW].** All 17 jobs rc 0, class ok. Tag counts per configuration (tag 2 = the p1 write,
tag 2' = the write the predicate does not gate, 5 = o4 pairs):

| config | tag 2 | tag 2' | tag-2 fraction | tag-5 pairs | tag-2 sources by (x & 1, y & 1) |
|---|---|---|---|---|---|
| c-e709 | 499 | 0 | 1.000 | 26 | all four classes |
| c-u | 486 | 5 | 0.990 | 8 | all four classes |
| c-u-r2 | 482 | 4 | 0.992 | 33 | all four classes |
| c-u-r3 | 488 | 2 | 0.996 | 18 | all four classes |
| c-k7 | 0 | 486 | 0.000 | 27 | none |
| c-k0 | 124 | 366 | 0.253 | 24 | (0, 0) only |
| c-k3 | 116 | 352 | 0.248 | 25 | (1, 1) only |
| c-g23 | 115 | 370 | 0.237 | 19 | all four classes (27 to 30 each) |

The order control's sources keeping the first write: c-u (16,25), (16,27), (17,27), (18,27),
(19,27), exactly S1's five; c-u-r2 (16,27), (17,27), (18,27), (19,27); c-u-r3 (16,27), (17,27). The
scorer prints the first as the frozen cluster (HCL, S1 post hoc, predicted in the table but not
entered in the verdict) and the other two as not the cluster; the common part, (16,27) and (17,27),
is in all three runs. c-k7-x-rep: 61 dwords differ from c-k7-x (S1 saw 36), tag-2 fraction 0.000
and 0.000.

**Read after the run [infer].** The criterion of 0.98 is met in 3 of 3 control runs, so the rule
"the unpredicated second write lands at (almost) every pixel" holds at 0.990 to 0.996, not at 1.0,
and at a handful of sources the first write survives, near the same place (x 16 to 19, y 27). S1's
oddity was therefore not a single run's: two sources reproduced in the three runs. The guard rows
reproduce S1's numbers to within 0.016 (0.253 and 0.248 against S1's 0.252 and 0.248; g23 0.237
against S1's 0.253), HA and HN fail on them as they did, and HQ's parity clause holds in all three.
This confirms that S1's reading describes the hardware in the same jobs, not that it describes it
in another job.

**Caveats.** HQ and HP-g23 were fitted to S1's data and S1b's jobs have the same programs, targets
and k, so the agreement is a repeat. The 0.98 threshold was set from the one S1 run it admits.
Tag 2' at the five sources is read from the x and y pairs agreeing; whether the surviving first
write belongs to a lane or to a place was not separated. The quad reading says which lane writes,
not what g25 or g23 hold.

**Not shown.** Any held-out guard (a k other than 0, 3, 7, a predicate on another global); what
g23 and g25 hold beyond the position in the quad; why the first write survives at those sources;
Q023's o4 to o7 in a plain job.
