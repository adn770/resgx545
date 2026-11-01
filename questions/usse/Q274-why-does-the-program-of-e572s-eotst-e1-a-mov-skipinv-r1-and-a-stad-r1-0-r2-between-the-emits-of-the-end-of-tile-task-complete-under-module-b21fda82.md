+++
id = "Q274"
question = "why does a program equal to E572's eotst-e1 but for the address immediate (a `mov.skipinv r1` and a `stad [r1,+#0], r2` between the emits of the end-of-tile task) complete under module B21FDA82 and tool 1140 when E572's run of it faulted under module 5AD04F33 and tool 1126, and what faults the end-of-tile task of E707's two 8-temporary `mov.skipinv` programs at address 0x1"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E707", "E572"]
terms = []
+++
E572 (44 of 44 jobs with a store in the end-of-tile task faulted at 0x340042, 0x340043 or 0x740012
after the value landed) is the premise of Q183. E707 ran a program equal to it but for the
address immediate, with the same arguments, as a control that all three models predicted to fault:
it completed, with the store landed. Eight of 10 variants completed; the two that faulted had
`mov.skipinv` and 8 temporaries, with a fault 0xd0400 at address 0x1 (a position of 'before' and
'between' the emits alike). The 'before' cells also change the emit word (r1 is the PBE word 1 and
is overwritten): the design confounded position with that.

Open: which difference between the runs of E572 and E707 is the one (the address immediate, the
module, the tool, the scratch memory the stores landed in, the history of the script: E572's jobs
followed other faulting jobs), whether the 0x1 fault is the store's or an emit's, and whether Q183's
premise holds under the present kernel and tool at all.

To settle it: E572's program with its own address immediate on the present module and tool; E572's
second form with its 10 and 11 stores and its q053-eot2 programs (the stage and
tables are in the dataset) on the present kernel and tool, once each after a reset and in the
original order; a store before the first emit through a register that is not an emit word; the
8-temporary skipinv program repeated three times and with the `mov` plain and r1 not reused.
