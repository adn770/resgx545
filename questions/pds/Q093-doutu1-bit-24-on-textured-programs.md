+++
id = "Q093"
question = "does DOUTU1 bit 24 (wait for iterations) hang a job under the fetch wait, as it did in 4 of 126 jobs with both bits in colour and coordinate shapes, and why does the closed driver set it with bit 25?"
unit = "pds"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E345", "E364", "E436", "E454", "E459", "E460"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH"]
+++

The closed driver sets DOUTU1 bit 24 exactly when a douti of the primary iterates an attribute into
the primary attribute registers (E364, 21 of 21 captured primaries with a fetch).

Answered for what the programs read (E436, E454, E460): under the fetch wait (bit 25) a textured
primary reads the same registers and image with bit 24 set and clear, in one source-1 shape (E436,
96 jobs), the vertex colour (E454, 29 of 29 completed jobs with both bits) and the coordinate sets
(E460: a 2-component set alone, the colour then a 2-component set, the colour then a 3-component
set, once the vertices carry the set's dwords, E459): 33 of 33 completed jobs with both bits equal
the 36 of 36 with bit 25 alone. Without bit 25 the registers change from run to run, with bit 24
alone or neither; bit 24 without the douti's completion bit hangs (E436, 24 of 24).

What is left is the hang with both bits. E454 had 1 job of 30 hang (reading the colour, pa0, of the
colour then 2-component shape); E460 had 3 of 36 jobs in the 12 probes, each in the probe that
reads the last register the program iterates (3 of 9 such jobs, 0 of the other 27 with both bits),
and 0 of 60 more jobs (30 on E454's vertices, 30 on the sized ones, reading the colour) with both
bits: 4 of 126 jobs with both bits in all (E454's 30, E460's 36 and 60). No job with bit 25 alone
hung (0 of 96: E454's 60, with the completion bit set or clear, and E460's 36). The count leaves
out the 3 jobs with each setting of the probe that reads a register nothing writes (none hung). The
hang's cause is not shown.

Open: what makes a job with both bits hang (whether reading the last iterated register right after
the iteration's completion is the condition, which E460's 3 of 9 fits, 3 hangs in 3 probes of one
run each, and E454's hang does not), whether it needs the fetch wait, shapes E454 and E460 did not
try (18 of E364's 21 programs were not run themselves), and why the closed driver adds bit 24 under
bit 25 (that it is redundant for the values read is an inference).

To settle it: run the last-register read of each shape with both bits at least thirty times and the
other registers as many, and one of E364's captured primaries with its own PDS data.
