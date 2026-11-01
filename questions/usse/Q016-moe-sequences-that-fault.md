+++
id = "Q016"
question = "which part of the smoa, smbo and smr sequences that fault the job makes it fault: the moest selectors, the changed state or the mirror mode?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 6
evidence = ["E087", "E369", "E370"]
terms = []
+++

Narrowed (E369, E370): the faults come from the probe template's own stores, not from `moest`. Run
ten times, interleaved, the three moest-state sequences completed in all 30 jobs. Split, `smoa
#-1, #-2, #511, #-512` alone, with each `moest` selector alone and with each operand's offset
alone completes. What faults is, [infer], the MOE state acting on the template's instructions
after the case: `smbo`'s first value moves the write of the stores' base register (the stores then
take their address from a stale register: one run of three faulted), and `smoa` mirror on source 0
moves the stores' address operand (six of six faulted). Every fault is a bus interface fault at an
address outside the scratch. The mixed pixels of the completed runs are the final `mov.end o0`
moved to o1, o0 keeping the job before's value.

What is left: that mechanism is read from which cases fault, not shown (no probe changed the
stores' base register itself, and `smbo` faulted one run of three), and which register a
mirrored source 0 reads.

To settle it: stores through a base register that is not r29 or r47, with `smbo` and mirror set
before it, and the base register read back after the case.
