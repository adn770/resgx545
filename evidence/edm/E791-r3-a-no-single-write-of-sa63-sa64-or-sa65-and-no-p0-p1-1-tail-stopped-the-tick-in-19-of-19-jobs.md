+++
id = "E791"
claim = "R3-events stage a (Q152 rows A0 to A6, 19 jobs: a writer of ours, one entry of alias.s, 208 instructions, wrote sa63, sa64 or sa65 (or none of them) and then called the closed general task, and our reader ran at the next event): the tick was kept in 19 of 19 jobs and no job stopped it (HostCtl dword 12 and USE0_SERV_EVENT advancing in every check after the reader, 912 to 1035 Hz); the controls held (A0 x2: the reader's pclink 0x98, p1 1, sa64 2, sa65 0x02000000, sa63 0); H-63 (sa63 stops the tick) is refuted by A1, a marker written to sa63 and left there, kept in 3 of 3 jobs and still read back 1200 ms later in 3 of 3, and H-P11 (p0 = p1 = 1 at the tail call with r20, r21, i0 and i1 written) is refuted by A6, kept in 2 of 2; A2 (sa65 written with its own entry value), A3 (sa65 written with a marker and restored before the tail call, 3 of 3 restored) and A4 and A5 (sa64 written, E792) kept the tick 3 of 3 each; the frozen scorer printed fit 12 held and 0 FAILED, held out 21 held, 4 FAILED and 1 cannot tell, replicate 40 held, 7 FAILED and 2 cannot tell, the FAILED rows being the kept-or-not rows of the two refuted hypotheses (H-63 in A1 x3, H-P11 in A6 x2) and the p1 rows of A2 and A5 (E792); the sa65 value E537's writer left (0xb009c5dc, with bits no event raised) was not written by any row, so the cause of E537's stop is not among these single writes, and no row reproduced that stop"
unit = "edm"
method = "R3-events stage a of the question-closing pass, round 2 (19 jobs: a0, a0-r2, a1, a1-r2, a1-r3, a2 to a5 each with two replicates, a6 and a6-r2; blob asm/alias.s, 208 instructions, sha256 22495dfc13301a7a9f5b0041a163bb0c89e8171a90f54141e59b7083ea98ee9b, accepted by the landed tools/fwtask verifier, armed with own_arm slots=0x1 entry=0; no str, no register write, ldr of none), run 1794307123-28500 of the dataset edm-closing-r3-events, on the laptop (host cedar), 2026-11-10 from 11:38:43 laptop time (10:38 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71, the health tool); each job: a writer command (command 1: sa63 = a marker; 2: sa65 = its own entry value; 3: sa65 = a marker, then restored; 4: sa64 = pa0 with bit 1 cleared; 5: sa64 = pa0; 6: r20, r21, i0 and i1 written and no sa; 0 and 9: no write, the reader), each setting p0 to p3 to 0, 0, 1, 1 before its tail call except command 6, which called the closed task from the dispatch with p0 = p1 = 1, and arming the reader (command 9, which stores the entry registers, sa63 to sa65 and pa0 to pa2 at the next event); the runner brackets the tick (HostCtl dword 12 read three times, 20 ms apart, rate 900 to 1100 Hz kept) before and after the reader, reads the stop signature twice 30 ms apart before any reset if the tick stopped, and a debugfs reset and re-arm follow a stop (none occurred); A1 also reads the sa63 marker again 1200 ms later and restores sa63; the tables, predictions and scorer were frozen before the first job (FROZEN.sha256, PREDICTIONS.sha256, LAPTOP.sha256, TOOL.sha256: the tool is S1b's build), the freeze resting on file times, hashes and the author's word; scored by score/score_r3.py a (out/score-a.txt); stages a, b and k7 ran in that order, the gate of each being the previous stage's kept stage.json. Disclosures: README.md and PREFLIGHT.md are the pre-run documents (README.md says prepared, not run); the scorer's wording, comments and the runner's name for the stop class of a tool that gives no answer were reworded after the run for the clean-room guard (REWORDED.md): the predictions, the laptop's data and the assembled tasks are byte-identical and the reworded scorer prints the same SUMMARY line; the end-of-stage debugfs reset logs the line 'error state captured in /sys/class/devcoredump', as the reset of E533 did; the offline readings behind the rows are the notes of 2026-11-10 on E536, E537, Q124 and Q152 (01391e5), made before this run"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3-events:out/a/"]
terms = ["Event Data Master (EDM)"]
+++
**What ran.** E537's writer stopped the tick and E536's did not, and they differed in several writes
at once (sa63, sa65, the tail's p0 = p1 = 1). Stage a gives each its own job with a reader at the
next event as the instrument (E536's design): a writer that changes one thing, calls the closed
task, and a reader armed for the next event, whose own run is the proof that an event was
delivered. The tick bracket and the reader's run are both kept-output gates.

**Frozen verdict** (`out/score-a.txt`). `A0 held; kept 19 of 19 read jobs, stops 0`. Tally as the
scorer printed it: fit 12 held, 0 FAILED, 0 cannot tell or void; held out 21 held, 4 FAILED, 1
cannot tell or void; replicate 40 held, 7 FAILED, 2 cannot tell or void. The scorer listed H-63,
H-ALIAS and H-P11 as refuted; its per-hypothesis lines said H-63 refuted (A1 kept 3 of 3), H-P11
refuted (A6 kept 2 of 2) and, for A4's next entry (pclink 6, p1 0, every rep), H-ALIAS supported.
The refutation of H-ALIAS in the summary comes from the p1 rows of A2 and A5, which E792 reads;
the FAILED rows are exactly these: the kept-or-not rows of H-63 (A1 x3) and of H-P11 (A6 x2), and
the p1 rows of A2 and A5 (3 each).

**Results [HW].**

- A0 (no writer; the reader only): pclink 0x98, p0 1, p1 1, p2 0, p3 0, sa64 2, sa65 0x02000000
  and sa63 0, in both jobs; the tick bracket 997 Hz.
- A1 (sa63 = 0xf55ff16f, 0xec6207ce, 0xee92efcc): kept 3 of 3 (946 to 1035 Hz); the reader at the
  next event and the reader 1200 ms later read the same marker in each job, so sa63 survives the
  closed task's passes and the wait, as E536's sa100 and sa127 did.
- A2 (sa65 = its own entry value, 0x02000000), A3 (sa65 = a marker, read back, then written back
  with the entry value before the tail call; the read-back of the restored value held), A5 (sa64 =
  pa0): kept 3 of 3 each. A4 (sa64 = pa0 & ~2): kept 3 of 3 (E792).
- A6 (r20, r21, i0 and i1 written, no sa write, p0 = p1 = 1 at the tail call): kept 2 of 2, and
  the reader at the next event read the r20, r21, i0 and i1 the writer had written (2 of 2, a
  different set in each job; the other jobs read the same r20 = 0, r21 = 8192 and i0, i1 of the
  earlier writers).
- No job logged a stop, no fatal, no log line outside the allowed ones; the health check after the
  stage was exact.

**What the stage does not cover [infer].** Every sa65 row writes the value it found or restores it
before the tail call, so the closed task never ran with another sa65 than the event's own: A3's
marker is a control for the write path, not a test of the closed task's reading of it. E537's
writer left sa65 = 0xb009c5dc and sa64 = 0xb0150d9d in place when it called the closed task; the
proposed rows that would leave such a word (A7, sa65 with bit 23 set, and A8, E537's markers
again) were not run. So the leading candidate of the note on E537 (a word asking for handlers no
event raised) is neither confirmed nor refuted: what is refuted is a stop from the register
writes themselves (sa63 alone, sa64 with or without the tick bit, the p0 = p1 = 1 tail with r and
i written).

**Not shown.** What E537's stop depends on (the value left in sa65, the combination of writes, or
a first stop that does not repeat: E537 was one run); whether the closed task reads sa63 at all.

**Correction 2026-11-10:** (R3x-events, E814) "No row reproduced that stop" stands for this stage.
In round 3 a single sa65 word with the count byte and bit 8 (0x02000100) reproduced E537's stop with
both of its marks, and E537's word without bit 8 stopped the tick without them, so the cause of
E537's stop is among single sa65 writes, not among the sa63, sa64 and sa65 writes of this stage.
