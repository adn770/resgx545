+++
id = "Q147"
question = "does a write to a register past the task's allocation land in the register whose index is the register's modulo the allocation, or is it dropped, and do E486 and E519 disagree"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E486", "E519"]
terms = []
+++

Found when the 11.28 simulator was replayed on the vectors of 11.27: it refuses a register past the
task's allocation, as before, and 30 vectors that hardware ran stop on it. E486: with the
allocations 8 and 32, a marker written to r(n) past the allocation was not seen in r(n mod T) (4 of
4: the pixels read the value written to r(n mod T) by an earlier instruction), so the write is
dropped or lands elsewhere. E519 (usse-phas-high-b and usse-phas-high-c, 30 vectors): `phas`
requests of 260 to 376, which the modulo-256 rule that E519 fits would make the allocations 4 to 120
(E519 does not show what a request allocates: Q144), and a job that writes r123 and reads it back
gave o0 = the marker in all 30, which a landed write explains (but see the confound below).

The confound: every E519 job of `phas-high-b` and `-c` writes the same marker, 0x7E57007B, to r123,
so an earlier job legitimately wrote that very value, and E484 shows that temporaries persist from
one job to the next. The readback therefore fits a dropped write plus a stale read of the earlier
job's r123 as well as a write that landed. E519 says so itself (its read-back does not show that the
write landed), and E486 used a distinct marker per case, which is why the two records do not
disagree: the question of where a write past an allocation goes is Q132 (E486), the allocation of a
request above 256 is Q144 (E519), and this one is what the replay needs settled to run the 30
vectors.

What is open: whether the allocation is the request modulo 256 (E519 tags it [infer]); whether a
write past the allocation lands in r(n mod T) when it is the only write (E519) and not when an
earlier write to r(n mod T) exists (E486); and what the 88 to 99.6 percent of E486 and the other
pixels show. To settle it: run E519 with a different marker per job, the E486 probe with the marker
written to r(n) only, and the E519 probe with a marker first written to r(n mod T).
