+++
id = "Q051"
question = "what state do smoa, smbo, smr, imo and setfc set in the MOE, and what does moest return, beyond the smlsi increments the probes pinned?"
unit = "usse"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E087", "E097", "E105", "E109", "E294", "E296", "E369", "E370"]
terms = []
+++

The probes pinned smlsi's swizzle mode (iteration k of a repeat takes the swizzle's k-th component
as its register offset, E097), smoa's address modes, which map an operand's first register once and
step on from it (E105), and smbo's first value, which offsets the destination register of the
instructions after it (E087). moest does not load the state word its selector names from its
register, and setfc changes nothing a fill shows (E109).

In 11.7 the simulator takes setfc and moest (selectors 0 to 8) as changing nothing a fill
shows (E294). Of their unmapped bits and imo's, flipped one at a time, only enc[51] does
anything: on setfc and on imo it hangs the job, where in the MOE group it selects the
register forms of smoa, smr, smlsi and smbo (E296).

Narrowed in 11.13: the state does not outlive its job: after a job that runs `smbo #1, #0, #0, #0`
or `smlsi` with increments 2, the next job's moves land as with no MOE instruction, three runs
(E370). `moest` with any selector after `smoa #-1, #-2, #511, #-512` writes nothing a fill reads
and faults nothing (E369).

What is open (usse_isa.md §8, item 2): what each of these instructions sets beyond the offsets,
modes and increments pinned, what `moest` returns and where, and whether the state survives from
one task to the next within a job.

To settle it: a fill whose quads run different `smbo` values chosen by a predicate on the quad's
position, then a plain move, to see whether one task's state reaches the next; `moest` with a
register destination in each bank and a store after it.
