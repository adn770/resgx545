+++
id = "Q025"
question = "what does the SB field of CR_BIF_FAULT encode in the PDS faults, and why did a store of one dword fault in the follow-up run only, and a store of two dwords then eight in the first run only, and (folded from Q059) why do PDS stores totalling 2, 3 or 4 dwords fault the job, and why does an rwfence after a store, or after a faulted job, touch page 0?"
unit = "pds"
kind = "hw"
value = "medium"
phase = 7
evidence = ["E143", "E144", "E145", "E395"]
terms = ["CR_BIF_FAULT", "CR_BIF_FAULT.CID", "CR_BIF_FAULT.SB"]
+++

SB. The kernel logs of the two runs hold 37 (first run) and 38 (follow-up run) fault lines, one
for each PDS case that faulted (E145). SB (bits 8:4) is 2 or 3 in all 75. For the stores totalling
2 dwords (12 faults in each run) it is 2, and for stores totalling 3 or 4 dwords (8 in each run) it
is 3; for `rwfence` after a store in the same program (10 in each run) it is 2, and for `rwfence` in
programs with no store before it (6 in each run, all right after faulted jobs) it is 3. The status
is 0xd2000 for the store faults (21 and 22) and 0x92000 for the 16 `rwfence` faults of each run.
The 36 cases that faulted in both runs have the same SB in both. The three one-run faults do not
follow the total: the store of one dword (two programs, follow-up run) has SB 3 and the store of 2
then 8 (first run) has SB 2. Whether SB is the kind of access, its size, or a count of requests is
not shown: the stores of 3 and 4 dwords share a value, and the `rwfence` faults take either value
depending on the program. CID varies between page directories (0 in all 16 faults of the one
directory that repeats, in each run) and is not the question.

The one-run faults (E144). `store` of one dword from ds1 and `store` of one dword followed by nine
`nop`s faulted in the follow-up run and completed in the first; `store` of 2 dwords and then of 8
faulted in the first run and completed in the follow-up. In each case every dword landed and the
registers were stored at the end, as for the faults of totals 2 to 4. Everything else (the other
86 cases of the table) agrees between the runs. The state a faulted job leaves does not explain
the three, since the two runs ran the same jobs in the same order.

Narrowed in 11.14 (E395): the one-run faults of E144 did not recur: a store of one dword (alone, and
with nine nops after it) and 2 then 8 completed in five runs each; the total-2 faults logged BIF
status 0xd2000 at 0x10020, and a one-run total-11 fault after a faulted job 0x1002e.

Open: what SB encodes; whether a fault leaves state (a pending request, a stale translation) that
makes the next job fault; whether the one-run faults depend on timing, or on the contents of the
memory the store reaches.

To settle it: log the faults of at least five runs of pds-memory-mem, -mem2, -mem5 and -mem6 with
the status and value of each, and tabulate SB against the store's size, the fence and the previous
job's outcome. Run the store of one dword, the store of one dword and nine `nop`s, and 2 + 8, each
alone in a fresh context ten times, and again after a deliberate fault. Add stores totalling 2 to 4
dwords with an `rfence` between them, to see whether SB follows the total.

**Correction 2026-11-16 (round 31, with the user):** Q059 is folded into this question (retired as
folded into Q025 after E1125; a fold is not an answer): both ask about the same PDS store faults,
from the same records (E143, E144, E145, E395), Q059 for the totals that fault and the `rwfence`
that touches page 0, this question for the fault's SB field and the one-run faults. Its clauses
are appended to the line above; its evidence and its term (`CR_BIF_FAULT`) were already this
question's. Its text, kept here: a PDS load's dwords reach its registers only at the next fence, a
store reaches memory (E143), and a program with stores and no `rwfence` faults when they total 2,
3 or 4 dwords, after every dword has landed (E144). The kernel logs one BIF fault per faulting case
(E145). Narrowed in 11.14 (E395): totals of 11, 13, 14, 15 and 17 dwords complete (one total-11
job of three faulted), so the faulting totals stay 2 to 4; a total of 2 faults with an `rfence`
between the stores too. The `rwfence` cases with page 0 mapped were not run.

Open from Q059 (pds_isa.md §7, item 3): the rule behind the totals that fault, and why an
`rwfence` after a store, or after a faulted job, touches page 0. To settle it (Q059's plan): on the
laptop, the store totals E144 did not run (11, 13, 14, 15 and 17 dwords) in every split, and
totals 1 and 10, which fault in one run only, ten runs each; then an `rwfence` after a store and an
`rwfence` right after a faulted job, the two cases whose fault lands on page 0 (E145), with page 0
mapped to a scratch page that is read back after each case and the fault registers sampled.
