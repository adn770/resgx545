+++
id = "E139"
claim = "PDS_SIZE bits 17:16 are not unused: at 0, 1 and 2 against 3 they change where the output registers o1 to o3 land, and o0 and the pixels it covers stay the same; we read the field as a size or count of the output register banks a pixel task is given, 3 being the plain value; this reading is an inference"
unit = "pds"
method = "inference from our measurements, E081's output-register probes (usse-output-registers: a 64x64 triangle whose shader writes a pixel's x or y to one register oN, with the plain PDS_SIZE and with bits 17:16 at 0, 1 and 2, one run); the reading is ours"
tiers = ["infer"]
date = "2026-11-01"
data = ["usse-output-registers"]
terms = ["PDS_SIZE.BITS17_16"]
+++

**What supports it.** In E081, o0 lands on the instance's own pixel for all 1062 covered pixels in
the plain table and in each of the three tables with the field at 0, 1 and 2. For o1 to o3 the
number of pixels changed moves with the field, as E081 lists them: o1 545, 705 and 747 at 0, 1 and
2 against 508 at 3; o2 210, 383 and 495 against 604; o3 83, 211 and 392 against 400. "Pixels
changed" is E081's count of target pixels that hold a value written by the shader that writes
oN: in the plain table 508 for o1, of which 252 are the instance's own pixel and the rest are
displaced by 16 or 32 rows or 0 or 32 columns, so displaced writes exist at the plain value 3 as
well (E081 reads them as writes past the banks the task was given). A field that
sizes the banks of output registers a task is given would leave o0 alone and move the writes to
the later registers, as seen. The field is 3 in the plain table of our jobs.

**What does not support it.** One run of each table, and no value of the field removes the displaced
writes. The reading of the field as a size or count of attribute banks or layers that the
triangle does not use (the glossary term PDS_SIZE.BITS17_16, which cites E046, where clearing the
field changed nothing on the triangle) is not what the output registers show: the field does
change what the triangle writes, but only through o1 and later.

**Not shown.** Which of size or count the field is, whether 3 means all, and whether any other
output, input or attribute bank depends on it. A program that fills the later registers with the
field at each value, and a run of the same tables twice, would settle more.
