+++
id = "Q023"
question = "what do PDS_SIZE bits 17:16 do, given that they move where the output registers o1 to o3 land?"
unit = "pds"
phase = 7
evidence = ["E139", "E081"]
terms = ["PDS_SIZE.BITS17_16"]
+++

With the field at 3 (the plain value of our jobs) the output register o1 of a triangle shader
changes 508 pixels (a pixel is changed when it holds a value the shader wrote to that register), o2
604 and o3 400, mostly displaced by 16 or 32 rows and 0 or 32 columns (E081). At 0, 1 and 2 the
counts become 545, 705 and 747 for o1, 210, 383 and 495 for o2, and 83, 211 and 392 for o3, while o0
lands on the pixel's own position for all 1062 covered pixels in every table (E081, E139). One run
of each table.

E139 reads this as a size or count of output register banks a pixel task is given. That is our
inference. Not shown: whether the field is a size or a count, whether 3 means all, why no value
removes the displaced writes, and whether other banks (inputs, attributes) depend on it.

To settle it: a shader that writes a distinct value to each of o0 to o7, with the field at 0, 1,
2 and 3, read back every pixel and map which destination each oN reaches; run each table twice to
see whether the destinations are fixed. A second shader that reads its own inputs back would show
whether the field affects the other banks.
