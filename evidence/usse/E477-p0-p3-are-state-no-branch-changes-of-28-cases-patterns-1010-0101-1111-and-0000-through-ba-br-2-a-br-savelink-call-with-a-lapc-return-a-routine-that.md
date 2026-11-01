+++
id = "E477"
claim = "p0-p3 are state no branch changes: of 28 cases (patterns 1010, 0101, 1111 and 0000 through ba, br #2, a br.savelink call with a lapc return, a routine that rewrites the predicates, and a predicated ba, !p1 ba and p2 br taken and not) the predicates read back after the flow are those set before it, or the routine's own rewrite when it made one (28 of 28), and the same through ba.savelink calls, lapc returns, a p1 lapc that returns or falls through, and a p0 ba.savelink (16 of 16); across jobs the predicates are left over for most pixels but not all: a reader job that reads p0-p3 before setting them reads the previous setter's pattern in 98.4 to 99.2 percent of its 2048 pixels (2016 to 2032 pixels in each of the ten readers after a setter of the dataset: 1111 after a setter of 1 in five of five readers, 0000 after a setter of 0 in five of five) and another pattern in the other 16 to 32 pixels (0xd, 0x5, 0x1, 0xf or 0 of the packed bits p0..p3); the first reader, after the baseline triangle, has 1992 pixels at 0000 and 56 at others"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/pflow.toml (dump.s, 2 probes, flow 28 cases and leftover 21), probes/usse/risky.toml probe usse-risky-pflow-call (16 cases, risky table, run after link-ba-return and link-nested agreed: E476); two runs of each (probe.py outside the data, the campaign runner the dataset: the same readback in all 28 flow cases, all 16 call cases and the 10 setter jobs, and in the 11 reader jobs the scratch word and the majority pattern the same with different counts of minority pixels in 8 of them; over the nine fill tables (the datasets other than pclink and the placed ones) runs 1 and 2 agree in 1828 of the 1844 cases they share, and the 16 that differ are cross-job readers (pclink-initial 3, pclink-leftover 5, pflow-leftover 8), whose 2048-pixel mixtures vary; the author's tally: run 1 is not kept in the data, and the 1844 and the 16 are consistent with the datasets); the cross-job pair runs the jobs in the order of the table (the runner keeps the case order, E373 did the same) and each is a fill of its own on the same render node"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-pflow", "usse-risky"]
terms = ["Universal Scalable Shader Engine (USSE)", "Event Data Master (EDM)"]
+++

**What runs.** flow: `and.testtanz.chan0 !c0, pK, rK, rK` for K = 0..3 sets p0-p3 from r1..r4 (1
sets the predicate), then the flow under test, then `mov r10..r13, #0` and `pK mov rK, #1`, so
r10-r13 are the predicates after the flow; r14 = 1 when the instruction after the branch ran. The
flows are `ba #E` over an instruction, `br #2`, `br.savelink #3` with a routine that sets r14 = 1
and returns by `lapc`, a routine that also redoes the four tests from r5..r8 (the complement) before
`lapc`, `p0 ba #E`, `!p1 ba #E` and `p2 br #2`. pflow-call (risky) does the same with `ba.savelink`,
a `p1 lapc` in the routine (returns when p1, else r14 = 7 and a second `lapc` returns) and `p0
ba.savelink`. leftover: reader jobs (r10..r13 read from p0..p3 before any test, r14 = their bits
packed, as the pixel) alternate with setter jobs (four tests of 1, or of 0, then the same read):
reader, then five times (setter of 1, reader), then five times (setter of 0, reader).

**Results (campaign run).** flow 28 of 28 and pflow-call 16 of 16 for "the predicates are kept
across the flow" (a predicated `ba` or `br` is taken when its predicate is set, not when clear:
r14 = 1 only on the not-taken cases; the routine's rewrite stays: pattern 1010 read back 0101, 1111
read 0000). The setter jobs read what they set in 2048 pixels (10 of 10). The readers:

| reader job | pixels at the previous job's pattern | other pixels |
|---|---|---|
| first (the job before is the baseline triangle) | 0000: 1992 | 1111: 40, 0101: 16 |
| after a setter of 1 (five jobs) | 1111: 2028, 2026, 2028, 2032, 2028 | 1101: 16, 18, 16, 16, 16; 0000: 4, 4, 4, 0, 4 |
| after a setter of 0 (five jobs) | 0000: 2016, 2032, 2021, 2032, 2024 | 1111: 20, 8 ...; 0101: 12 to 16; 0001 (p0 only): 15 |

(0xf = all four set, 0xd = p0, p2, p3 set and p1 clear, 0x5 = p0 and p2, 0x1 = p0 only.) The
scratch word (one instance's) agreed with the majority in 21 of 21 jobs. The first run by probe.py
gave 2020, 2032, 2028, 2032, 2032 pixels of 1111 after the setters of 1 and 2012, 2016, 2024, 2024,
2022 of 0000 after the setters of 0 (outside the data), the same shape.

**What it shows.** [HW] The predicates survive `ba`, `br`, `ba.savelink`, `br.savelink` and `lapc`,
predicated or not, and a callee's changes to them stay after the return (there is no save and
restore of p0-p3 around a call); a predicated branch not taken leaves them as they were. Across jobs
on the same render node they are not reset: about 99 percent of the instances start with the pattern
the last job left, 1 percent with a pattern of some earlier job [infer] (the minority patterns,
1101, 0101, 0001, 1111, look like patterns of other programs run earlier on the instances that were
not reused by the last job; the data does not say which). A program must set p0-p3 by a test before
it relies on them.

**What it does not show.** Predicates across firmware (EDM) tasks and across the task boundary of
the microkernel: a fill's jobs are not tasks of the firmware in the sense of item 7 (Q124). Which
instance reads which pattern (the pixel positions were not kept for the predicates; for pclink they
are aligned 2 x 2 quads, E475: so the state is per quad of four instances, which the predicate
readers may share too, not shown). `p0-p3` after `bexception` or `emitpix`.
