+++
id = "Q016"
question = "which part of the smoa, smbo and smr sequences that fault the job makes it fault: the moest selectors, the changed state or the mirror mode?"
unit = "usse"
phase = 6
evidence = ["E087"]
terms = []
+++

Five cases fault the job in the moe tables (E087): `smoa #1, #2, #3, #4, none,
repeat, clamp, mirror` and `smoa #-1, #-2, #511, #-512, mirror, clamp, repeat, none`, each
followed by the sixteen `moest` selectors; `smbo #1, #2, #3, #4` followed by them; and `smr` with
`smoa mirror` on all four operands before a repeated `mov` (smr 4 with repeat8 and smr 2 with
repeat4).

Three fault in both runs: smoa #-1, #-2,
#511, #-512 followed by moest (`moest-state` case 2), and the two mirror cases (`smr-smoa` case
4 and `window` case 4). The other two, smoa #1-#4 and smbo #1-#4 followed by moest (cases 1 and
5), fault the job in the first run and complete in the follow-up run, with mixed pixels (0xacadaeaf
at 1340 pixels and 0xa0a1a2a3 at 708 for case 1; 1130 and 918 for case 5). So the data shows
these two as sometimes faulting, not always.

The other cases of the same table complete: moest after task start, after smlsi #1-#4 and
#5-#8, after smr #5-#8 and #4095..., and after smbo #4095, #2048, #1024, #7 (whose dump the
offsets move). smoa with non-zero offsets and mode none, repeat or clamp does not fault by
itself.

Open: which part is the cause. The candidates are the moest selectors after a changed
state (but moest after other changed state completes), the mirror mode (smr + smoa mirror
faults without moest), the offsets reaching an addressing path (E087: smbo changes register
numbers), or a race (two of the five faults are intermittent).

To settle it: run each faulting sequence ten times; then split it: smoa #-1... alone with a
plain dump, with moest #0 to moest #15 one selector at a time, with mirror on one operand at
a time (the four operands, in each of the four modes), and the same with smbo's four values.
