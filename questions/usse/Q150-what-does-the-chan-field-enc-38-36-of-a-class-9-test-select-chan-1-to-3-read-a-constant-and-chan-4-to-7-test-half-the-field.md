+++
id = "Q150"
question = "do the raw test words with the chan field enc[38:36] = 1 to 7 on 8-bit and 16-bit lane operations, on the fields other than the six run and with the o join read as the rule of the Test channels page says"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E530", "E499"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E530: seven raw and-test words with enc[38:36] = 1 to 7 and the a join, six field values and six
pairs each (36 jobs a table) on a 32-bit result: the prediction that the field is ignored failed in
all seven. The 252 readings are what the channel table of the assembler (chan0 to or02 for
enc[38:36] = 0 to 7) and the rule of the landed Test channels page (a channel with no lane reads 1:
taz 0, tanz 1, nat 0, pat 1) give, read after the data; a 32-bit test names chan0, and that advice
stands.

What the landed Test channels page already has [HW] is the lane operations through the assembler's
chan names (360 cases). What is open is smaller: the raw words with the chan field on 8-bit and
16-bit lane operations (where the other channels have lanes), on the fields other than the six run,
on result classes the six pairs did not give, and with the o join (E529). To settle it: the same
table on lane operations with distinct bytes in the operands, the byte under test known, with the
rule as the hypothesis.
