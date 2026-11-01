+++
id = "Q133"
question = "what limits a phas request to 192 temporaries (196 hangs the job whatever the task was started with) and is the limit the same for a firmware task"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E487"]
terms = []
+++

E487: requests of 8, 16, 32, 64, 96, 124, 128, 132, 136, 144, 160 and 192 ran (15 of 15 jobs,
started with 8; 192 also started with 32, 64 and 128) and 196, 200, 204, 208, 212, 216, 220, 224,
252, 256, 508 and 1020 hung the job (15 of 15; 196 also started with 32, 64 and 128): 12 values
each, not an interval (228 to 248 and 260 to 504 were not run); every request from 124 up wrote
r123 only, since r124 and up cannot be named, so a request above 124 exercised r123 and not the
registers past it; the field itself takes up to 1020 and counts in fours.

What is open: the quantity that bounds it ([infer] the register file divided by the instances in
flight), the request between 192 and 196 (the field counts in fours, so none is encodable), and
whether the microkernel's tasks request the same. To settle it: the limit against the number of
instances (a smaller target, a render with fewer pixels) and the EDM's own tasks (phase 12).
