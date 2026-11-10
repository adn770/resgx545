+++
id = "Q132"
question = "where does a write to a temporary or a register past the task's allocation go (does it land in the register whose index is the register's modulo the allocation, or is it dropped: E486, E519 and E535 do not disagree), and which instances' registers do the pixels that do not read the wrapped register read"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E486", "E519", "E535"]
terms = []
+++
E486: r(n) for n above the allocation T reads the marker of r(n mod T) in 88 to 99.6 percent of the
pixels of client pixel tasks (T = 8, 16, 32 and 64) and a write to r(n) did not change r(n mod T)
(4 of 4, T = 8 and 32 only).

What is open: whether the write lands in a neighbouring instance's register file (the rest of the
pixels read other values, leftovers or other markers), and what an allocation other than 8, 16, 32
and 64 does. To settle it: the same probe with every instance writing a different marker (pa0 or a
number from the instance) past its allocation and each instance reading its own and its
neighbours'.

**Correction 2026-11-10:** Q147 is merged into this question (retired as folded into Q132; a fold is not an answer), and its question is now a clause of the one above. Its question was: does a write to a register past the task's allocation land in the register whose index is the register's modulo the allocation, or is it dropped (E486 and E519 do not disagree: E535).

Found when the 11.28 simulator was replayed on the vectors of 11.27: it refuses a register past the
task's allocation, as before, and 30 vectors that hardware ran stop on it. E486: with the
allocations 8 and 32, a marker written to r(n) past the allocation was not seen in r(n mod T) (4 of
4: the pixels read the value written to r(n mod T) by an earlier instruction), so the write is
dropped or lands elsewhere. E519 (usse-phas-high-b and usse-phas-high-c, 30 vectors): `phas`
requests of 260 to 376, which the modulo-256 rule that E519 fits would make the allocations 4 to 120
(E519 does not show what a request allocates: Q133), and a job that writes r123 and reads it back
gave o0 = the marker in all 30, which a landed write explains (but see the confound below).

The confound: every E519 job of `phas-high-b` and `-c` writes the same marker, 0x7E57007B, to r123,
so an earlier job legitimately wrote that very value, and E484 shows that temporaries persist from
one job to the next. The readback therefore fits a dropped write plus a stale read of the earlier
job's r123 as well as a write that landed. E519 says so itself (its read-back does not show that the
write landed), and E486 used a distinct marker per case, which is why the two records do not
disagree: the question of where a write past an allocation goes is the first part of this question (E486), the allocation of a
request above 256 is Q133 (E519), and the merged one is what the replay needs settled to run the 30
vectors.

Narrowed in 11.30 (not retired). The first of the three runs named below ran, as two runs: E519's
job with a different marker per job, in two orders (E535, 36 jobs). A write to r123 under a request
of 100 or less is not seen by the read of r123 (0 of 12 jobs; all pixels of run a's six, the pixels
listed in run b's report), under 124 or more it lands (24 of 24 with the controls), and the six
requests of 260 to 448 landed it too (12 of 12), so the read-back of `phas-high-b` and `-c` was a
landed write and E486 and E519 do not disagree: E486's drop is the request-of-100-or-less row of
E535. The request of 260 to 376 allocates at least 124 registers and not its value modulo 256
(Q133). The 30 vectors of E519 stay stops in the simulator because it takes the allocation to be the
request modulo 256 (Q133); the 36 vectors of E535 are in the data, and 14 replay exactly (the
controls and the request of 448), 12 are left out (their pixels are a mixture) and 10 stop on r123
past the allocation.

What is open: T = 101 to 123 (no case ran), the read side (E486's "n mod T" reads, 88 to 99.6
percent of 2048, beside E535's read of r123 under T <= 100, which returned physical r123 contents of
earlier jobs: different probes, not a contradiction in the data, unreconciled), whether a write past
the allocation lands in r(n mod T) when it is the only write and not when an earlier write to r(n
mod T) exists (E519's design against E486's, neither of which the E535 runs repeat: they read r123
only), where a dropped write goes, and what the 88 to 99.6 percent of E486 and the other
pixels show. To settle it: the E486 probe with the marker written to r(n) only, and the E519 probe
with a marker first written to r(n mod T), with a distinct marker per job.
