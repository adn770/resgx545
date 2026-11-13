+++
id = "Q271"
question = "what does VDM_TASK1 bits 31:24 do when it is forced to differ from the natural (4 + N + 3) / 4 of the vertex's N outputs (E703: the render of 8 of 8 forced jobs differs from the natural jobs' at products R * V of 30 to 40, and the decoder reads 76 to 95 of 126 vertices as lost, a reading under a layout assumption; the two natural jobs at 32 and 33 are intact)"
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

Narrowed 2026-11-12 (round 6 housekeeping, decision R6-1 a; arithmetic, no run) to forced R. With N
at most 11 and V at most 16 no natural job has R * V of 34 or 35 (R = ceil((4 + N) / 4); the natural
products are 33 and less, then 36 and more), so for the streams our tools write a simulator needs
only "refuse R * V above 33", which it does; where a capacity limit lies between 33 and 36 is not
asked any more. What stays open is the forced field: what the rows do when they differ from the
vertex's own size, whether a forced R below the natural one loses vertices, and a forced = natural
control.

Note 2026-11-13 (round 8 offline, decision R8-1 a; ranking closing8/rank/rank-round8.md finding 3;
no claim of E703 changes). "A xor cannot write the natural value" no longer stands for the tool:
`sgxfive-test --vdm N=V` sets VDM word N to V (`sgxfive-test.c`, `src/poke.c`: a set where E703's
`7^=` is a xor) through the same path, so the forced = natural control exists without a tool
change: `--vdm 7=<natural word>` for N = 11 (V = 3) and N = 8 (V = 4), frozen as "the image of the
natural job", beside the forced-below and natural + 1 rows. They are R8-4's rows of session r8-geo.
