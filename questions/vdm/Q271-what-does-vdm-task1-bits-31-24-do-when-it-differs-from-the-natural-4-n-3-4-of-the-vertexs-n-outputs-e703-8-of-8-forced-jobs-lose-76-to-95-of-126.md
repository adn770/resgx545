+++
id = "Q271"
question = "what does VDM_TASK1 bits 31:24 do when it differs from the natural (4 + N + 3) / 4 of the vertex's N outputs (E703: the render of 8 of 8 forced jobs differs from the natural jobs' at products R * V of 30 to 40, and the decoder reads 76 to 95 of 126 vertices as lost, a reading under a layout assumption; the two natural jobs at 32 and 33 are intact), and where does the capacity limit of a task lie between R * V = 33 and 36"
unit = "vdm"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E703", "E702", "E546"]
terms = ["VDM_TASK0.MAX_VERTICES", "VDM_TASK1.OUTPUT_SIZE"]
+++
E546 found losses at 36 or more with natural rows and, at 33 or below, one lost vertex in one job (a
= 8, not seen again) (R = ceil((4 + N) / 4), N at most 11, so no natural job has R * V of 34 or 35).
E703 forced the rows with a xor on VDM word 7 (rows 4 to 7 with N = 2, 8 and 11) to reach 35, 36 and
40 and found that the forced field changes the render at every product: at 30 (N = 11, R = 5, V = 6)
and 32 (N = 8, R = 4, V = 8) too, where natural jobs lose nothing. The observation is the image (the
tool's o0 histogram: 418 to 1320 background pixels in 4 forced jobs and none among the listed values
in 4, against 2288 and 2821 in the natural jobs); the decoder's lost-vertex counts depend on a
layout assumption that may not hold when the rows differ (the repeated N = 2 job has the same
histogram and the readings 87 and 84). There is no forced = natural control: the two natural jobs (N
= 9 at 32, N = 8 at 33) carry no xor on word 7, and a xor cannot write the natural value, so nothing
separates 'the forcing breaks a job' from 'wrong rows break a job'. The forced route does not locate
the capacity; 34 and 35 are not reachable by it.

Open: what the rows do when they differ from the vertex's own size (a layout of the output rows, not
a count that multiplies V), whether a forced R below the natural one (not run: N = 11 with R = 3)
loses vertices as well, and whether the limit between 33 and 35 exists at all for a natural job:
with N <= 11 and V <= 16 the natural products are 33 (3 x 11) and, above it, 36 and more (3 x 12, 4
x 9), none at 34 or 35. If no natural job exists at 34 or 35, a simulator needs only the rule
'refuse R * V above 33', and the question narrows to whether any other way of writing the stream
(the output size field of OUTSEL, the index list) reaches 34 or 35.

To settle it: a forced = natural control (the natural value written through the same path, not by
a xor, if the tool can be changed), forced rows below the natural value (N = 11, R = 3, V = 8 and
11), forced = natural + 1 at a small product (N = 2, R = 3, V = 2) to see whether any forced job is
intact, and a stream with the vertex size field written beyond 11 (tri_probe.c checks it), if the
tool can be changed.
