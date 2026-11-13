+++
id = "E1021"
claim = "Round 12 offline (Q163; no run): on the 11.31 VDM state sweeps (vdm/state-units: 133 jobs of three scripts in run order, E545's two-block stream; c taken as 0 at each script's start, every script ending in a GPU reset), with E700's counter frozen by hash before the outcomes were scored (c is 0 after a hang or a reset, a job adds v - 2 a block, hangs iff c + add > 8; c teacher-forced from the outcomes), the 54 jobs with v 3 to 7 in a block (13 hangs) follow it 54 of 54 under E700's g(1) = -1 (M1) and E701's post hoc variant (M3): 12 of 12, 28 of 28 and 14 of 14 in the three scripts, every hang needing the history (a stateless threshold gets 41 of 54, 'v 1 or 6 hangs' 37); the 31 jobs at v = 2 in both blocks complete and are predicted, 31 of 31; 28 jobs whose state word E545 had found to hang by its other bits were excluded before scoring and all hung. Below 2 (20 jobs) the counter's clauses do not hold out: M0 and M1 14 of 20, M3 17 of 20 (its block-2 v = 1 hang at c = 0 misses three block-2 v = 1 hangs at c = 5), and E701's M2 20 of 20 only through its v = 0 reset, which misses a v 3 to 7 job (st-b1-b119-4-r2 hung at c = 7 where the reset gives c = 4), the third refutation of that reset; block-2 v = 1 hung in all 6 jobs of the risky script and completed in the grid's rows 4 to 7 [HW, held out offline with named leaks; infer: the grid's bits 7:0 explain the v = 1 rows as well as c]"
unit = "vdm"
method = "Offline, no run (round 12, decision R12-5 a of closing12/DECISIONS-R12.md and closing12/plan/rank-round12.md, finding 3). Data: vdm-state-units (scripts vdm-state-units, vdm-state-risky and vdm-state-grid, E545's sweeps; cases.tsv in run order, output.txt for each job's rc, kernel.log for the job markers and the 'hung, recovering' and 'SGX reset:' lines: 47 hangs, 2, 40 and 5 by script; two resets without a hang are the last jobs of two scripts). Check closing12/plan/c2-q163/: c2_rule.py (sha256 1e6a9e12a97e55562cfc7b8b41d43ef1d3c16900d6ab34401231735b81156868, FREEZE.log 2026-11-13T12:21:12Z) freezes the counter (g(v) = v - 2 from 2 up; M0 g(1) = 0, M1 g(1) = -1, M2 E701's v = 0 reset, M3 E701's post hoc variant with a block-2 v = 1 hang at c = 0, all formed before these data), the rivals NULL (a stateless threshold at 9), NEVER and V16 (v in {1, 6} hangs), the exclusions by E545's word causes (bits 15:13 = 0, 5, 6 or 7, bit 17, the closed forms: 28 jobs of the risky script), the sets S37 (a block at 3 to 7), TRIV (2 and 2) and SLO (a block below 2), and the verdict (HOLDS: no miss on S37 and TRIV and more right than NEVER and V16; PARTLY 1 or 2 misses; REFUTED 3 or more; SLO judged apart). Leaks before the freeze (FREEZE.log): the round 12 survey's hang totals per script, E545's own per-word outcome statements, two control rc lines, and the first 28 outcome lines of vdm/state2-fields' report (a dataset then not scored: neither state2-fields nor state2-consts keeps a run order or per-case markers). Scorer c2_score.py (c2_score.out), the threshold sensitivity c2_sens_posthoc.py (c2_sens_posthoc.out, post hoc: T = 8 the only threshold with no miss, T 7 and 9 miss 5 and 2), notes NOTE.md. This fold re-ran c2_score.py and c2_sens_posthoc.py with python -I on resgx545-data ffd076572 and got byte-identical outputs; sgx-pipe's vdm.rs refuses bits 11:9 of 1 and 3 to 7 under Q163 as a function of the word and the counter (the_state_words_bits_11_to_9_and_12_say_no_object_and_other_values_are_refused)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["vdm-state-units", "cited-scratch:closing12/plan/c2-q163/", "cited-scratch:closing12/plan/rank-round12.md"]
terms = ["VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13"]
+++
**What was done.** E700 predicted 52 jobs of its own series by a counter fitted on E413, and E701
fitted its clauses below 2 post hoc. E545's 11.31 sweeps, run before either, put the same words in
the same two-block stream in three scripts, and no record had scored them against the counter. The
round 12 planner froze the counter, its three variants and three rivals by hash and scored all 133
jobs in run order; this fold re-ran the scorers byte for byte. The leaks are named in the method;
none is an outcome of the scored scripts beyond E545's statements per word.

**Results [HW, held out offline]** (c2_score.out), jobs right of each set (105 scored, 28 excluded):

| set | jobs | hangs | M0 | M1 | M2 | M3 | NULL, NEVER | V16 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S37 (a block at 3 to 7) | 54 | 13 | 53 | 54 | 53 | 54 | 41 | 37 |
| TRIV (2 and 2) | 31 | 0 | 31 | 31 | 31 | 31 | 31 | 31 |
| SLO (a block below 2) | 20 | 6 | 14 | 14 | 20 | 17 | 14 | 14 |

Verdicts as frozen: M1 and M3 HOLDS, M0 and M2 PARTLY (one miss each). M0's miss is grid `sg-v7-r4`
(c = 4, a v = 1 counted 0: predicted hang, completed); M2's is units `st-b1-b119-4-r2` (its v = 0
reset gives c = 4, the job hung at c = 7). Block-2 hangs by v: 3 and 4 0 of 6 each, 5 1 of 6, 6 7 of
16, 7 3 of 10. Every S37 hang needs the history: its own add is at most 5.

Below 2: block-2 v = 1 hung in the risky script's 6 jobs (`st-b2-b119-1-r1`, `-r2` and
`st-grid-r1-v1` at c = 0; `st-grid-r2`, `-r3` and `-r8-v1` at c = 5 by M1 and M3) and completed in
the grid's `sg-v1-r4` to `-r7` (c 4 down to 1); M3 misses the three c = 5 hangs, M0 and M1 all six,
M2 none only because a block-2 v = 0 job precedes each. Block-1 v = 1 completed 2 of 2 and v = 0 4
of 4.

**What it shows.** [HW, held out offline] E700's counter, with its threshold 8 and its step v - 2,
holds on a second set of the same stream run before it was fitted: 54 jobs with v 3 to 7, 13 hangs,
none of them reachable without the history (an appended note on E700). Its clauses below 2 do not:
E701's v = 0 reset fails a third time and M3's block-2 v = 1 hang at c = 0 fails at c = 5 (an
appended note on E701). [infer] The grid's bits 7:0 (rows 1, 2, 3 and 8 hang, 4 to 7 complete) fit
the block-2 v = 1 rows as well as c does; the two are not parted here. sgx-pipe's vdm.rs refuses
the field's values 1 and 3 to 7 as a function of the word and the counter.

**What it does not show.** What the counter is, the v below 2 clauses (a block-2 v = 1 at a
controlled c with the grid's bits 7:0 held), other shapes, time and other jobs between (Q163). It
assumes c = 0 at each script's start (every script ends in a GPU reset; the scripts run between
them are not kept). Refuted by: a v 3 to 7 job that hangs with c + add at most 8 after completed
jobs
and no reset.
