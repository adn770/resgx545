+++
id = "Q059"
question = "why do PDS stores totalling 2, 3 or 4 dwords fault the job, and why does an rwfence after a store, or after a faulted job, touch page 0?"
unit = "pds"
kind = "hw"
value = "low"
phase = 11
evidence = ["E143", "E144", "E145", "E395"]
terms = ["CR_BIF_FAULT"]
+++

A PDS load's dwords reach its registers only at the next fence, a store reaches memory (E143), and a
program with stores and no rwfence faults when they total 2, 3 or 4 dwords, after every dword has
landed (E144). The kernel logs one BIF fault per faulting case (E145). Q025 asks what the fault's SB
field encodes and why the runs differ.

Narrowed in 11.14 (E395): totals of 11, 13, 14, 15 and 17 dwords complete (one total-11 job of three
faulted), so the faulting totals stay 2 to 4; a total of 2 faults with an rfence between the stores
too. The rwfence cases with page 0 mapped were not run.

What is open (pds_isa.md §7, item 3): the rule behind the totals that fault, and why an rwfence
after a store, or after a faulted job, touches page 0.

To settle it: on the laptop, the store totals E144 did not run (11, 13, 14, 15 and 17 dwords) in
every split, and totals 1 and 10, which fault in one run only, ten runs each; then an rwfence after
a store and an rwfence right after a faulted job, the two cases whose fault lands on page 0 (E145),
with page 0 mapped to a scratch page that is read back after each case and the fault registers
sampled.
