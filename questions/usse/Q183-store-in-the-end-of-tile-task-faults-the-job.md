+++
id = "Q183"
question = "which store forms in the end-of-tile task fault the job and why does E572's fault not reproduce in E707 (a program equal to E572's but for the address immediate completed; two 8-temporary `mov.skipinv` programs faulted at address 0x1)"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E572", "E707"]
terms = []
+++

In 44 of 44 jobs with a store between the end-of-tile task's two emits (the second form of the
program, 4 jobs, eotst, 3, and q053-eot2, 37) the scratch dword of the first store holds the value
and the job then faulted: 39 at 0x340042, 1 at 0x340043 and 4 at 0x740012 (no pattern with the
register or the target size); the 4 jobs of the first form (a store through r8) faulted at 0x42.
In the second form only the first of 10 or 11 stores landed. Programs of 7 to 10 instructions
without a store completed (5 of 5). The fault address is not the scratch. Not shown: whether the
store, the missing wait on its completion, the emit that follows or the task's end is what faults,
and what the address is.

Kind: hw. The question is about what the hardware does when a program of ours in the end-of-tile
slot stores; the closed firmware is not asked about. If the address proves to be one the firmware
reads or writes at the end of a tile, the open part becomes a question about the firmware's
behaviour and is parked as fw [infer].

To settle it: stores in other positions of the program, a store only (no emit), a store with the
end flag, and a second store, in the end-of-tile slot; the kernel log's fault status and address
per variant.

Reworded in 11.39 (E707, E708): the premise "a store in the end-of-tile task faults" is not
reproduced as it stood. The paragraphs above keep E572's measurements.

E572: 44 of 44 jobs with a store in the end-of-tile task faulted after the value landed (module
5AD04F33, tool 1126), at 0x340042, 0x340043 or 0x740012, and E130's form (stores before the
emits, a register offset from sa15) completed in 60 of 64 tile stores, no fault in five
probes, then and in E708 (5 of 5 completed, per-tile values read). The fault word is a page
number plus flags, not a code address. E707 ran eotst-e1 (bytes equal to E572's but for the
address immediate): it completed here. Open: which difference between the runs (the address
immediate, the module, the tool, the history of the script) is the one; none was tested.

Folded here 2026-11-12 (round 6 housekeeping, decision R6-1 a): Q274, split from this question in
11.39, asked the same unknown, and its open part and plan move here. E707's eotst-e1 (bytes equal
to E572's but for the address immediate, module B21FDA82, tool 1140) completed with the store
landed, where E572's run of it (module 5AD04F33, tool 1126) faulted; 8 of E707's 10 variants
completed and the two with `mov.skipinv` and 8 temporaries faulted at address 0x1 (0xd0400), at a
position of 'before' and 'between' the emits alike; the 'before' cells also change the emit word
(r1 is the PBE word 1), so position was confounded with it. Open from it: which difference between
the runs of E572 and E707 is the one (the address immediate, the module, the tool, the scratch
memory the stores landed in, the history of the script: E572's jobs followed other faulting jobs),
whether the 0x1 fault is the store's or an emit's, and whether this question's premise holds under
the present kernel and tool at all. To settle it: E572's program with its own address immediate on
the present module and tool; E572's second form with its 10 and 11 stores and its q053-eot2
programs (the stage and tables are in the dataset) on the present kernel and tool, once each after
a reset and in the original order; a store before the first emit through a register that is not
an emit word; the 8-temporary `mov.skipinv` program repeated three times and with the `mov` plain
and r1 not reused.
