+++
id = "Q039"
question = "which vertex dword does user clip plane 1 read as its distance when it is enabled without plane 0?"
unit = "mte"
phase = 10
evidence = ["E198"]
terms = ["OUTSEL.PLANES"]
+++

OUTSEL bits 7:0 enable user clip planes: plane 0 alone reads its distance from o4, and planes 0
and 1 together read o4 and o5 (E198). With bit 1 alone the triangle is removed in all four cases
run: a 5-dword vertex (0x53002) with o4 at -1.0 and at +1.0, and a 6-dword vertex (0x63002) with
o4 = -1, o5 = +1 and with o4 = +1, o5 = -1. Each case has one of o4 and o5 positive, so neither
dword on its own decides it, and the case with both positive was not run. Plane 1 alone may read
o5, read o4, need both, or reject every triangle for another reason, such as a distance it reads
past the vertex. With a 4-dword vertex every plane bit removes the triangle or faults the job.

To settle it: run 0x63002 with o4 and o5 both +1 and both -1, and 0x73002 (a 7-dword vertex) with
o4, o5 and o6 set one at a time to -1 and the rest +1; also `fdpc cp1` inside and outside with
0x63002. One run each, the follow-up run repeating any case that draws.
