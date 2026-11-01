+++
id = "Q037"
question = "does a hung job's saved render memory show how far the TA got, when the control hung in its pixel task leaves its object in one run and none in the next?"
unit = "vdm"
phase = 10
evidence = ["E186"]
terms = ["VDM_STATE1.BITS15_13", "Parameter Buffer (PB)"]
+++

After the jobs with VDM state word 1 bits 15:13 at 0, 5 or 6 hang, and after the three-index lines
job, the saved parameter buffer holds no object and no control-stream page, in both runs (E186).
That would read as the TA stopping before it writes the object, if the control showed that a
job hung later keeps its object. In the first run it does: the job hung in its pixel task leaves
the object and the stream page. In the follow-up run it leaves neither, like the other hangs. The
lines job also differs between runs: its TA data is all zero in the first and equal to the drawn
triangle's in the second.

So what a hung job leaves in the saved memory is not reproducible, and a missing object cannot be
read as never written. The save happens after the kernel reports the hang; what the recovery does
to the memory in between is not read.

To settle it: run the pixel-hang control ten times, alternating with the bits 15:13 cases and on
fresh boots, saving the parameter buffer and TA data each time, to see how often the object is
there and what decides it. Then save the render memory before the kernel recovers (a debug switch
that holds recovery until the dump is done), so that the dump is the hung job's and not the state
after recovery.
