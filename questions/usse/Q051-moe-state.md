+++
id = "Q051"
question = "what state do smoa, smbo, smr, imo and setfc set in the MOE, and what does moest return, beyond the smlsi increments the probes pinned?"
unit = "usse"
phase = 11
evidence = ["E087", "E097", "E105", "E109"]
terms = []
+++

The probes pinned smlsi's swizzle mode (iteration k of a repeat takes the swizzle's k-th component
as its register offset, E097), smoa's address modes, which map an operand's first register once and
step on from it (E105), and smbo's first value, which offsets the destination register of the
instructions after it (E087). moest does not load the state word its selector names from its
register, and setfc changes nothing a fill shows (E109).

What is open (usse_isa.md §8, item 2): the MOE state as a whole: what each of these instructions
sets, what moest returns for each selector and whether the state survives from one task to the next.
Q016 asks the narrower question of which part of a faulting sequence faults.

To settle it: on the laptop, a fill per instruction that sets a known state, reads it back with
moest into a register and stores it, then runs a mov.repeat4 whose writes show the offsets in force;
every selector of moest, two runs each, and a second task in the same job that reads the state
without setting it.
