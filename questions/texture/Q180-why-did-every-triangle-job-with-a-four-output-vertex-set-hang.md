+++
id = "Q180"
question = "why did all 28 triangle jobs of the Q021 probes hang (E569), the two controls with the old source word 0x40800801 included: is it the four outputs o4 to o7, the two extra temporaries, or something else in the vertex program"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E569", "E420", "E541"]
terms = ["DOUTI0.COMPONENTS"]
+++

E569: 28 of 28 hung, each recovered by a reset. To settle it: E420's own probe re-run unchanged in
the same session (is the module the cause), then the vertex program changed one step at a time (the
temporaries, the output count, the o6 constant) with a reset and the health triangle after each
job. Q021 waits on it. E541 (the TA's object tables of 11.31: jobs that hung or faulted where a
set was described past what the vertex program writes) is a lead: here the set has four outputs and
the program writes o4 to o7.
