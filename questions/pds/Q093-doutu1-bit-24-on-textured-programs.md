+++
id = "Q093"
question = "does DOUTU1 bit 24 (wait for iterations) change what a textured primary pixel program reads when the program iterates the vertex colour or several attribute registers, or reads pa0 to pa2, as the closed driver's programs that set it do?"
unit = "pds"
phase = 11
evidence = ["E345", "E364", "E436"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH"]
+++

The closed driver sets DOUTU1 bit 24 exactly when a douti of the primary iterates an attribute
into the primary attribute registers (E364, 21 of 21 captured primaries with a fetch).

In one program shape the bit adds nothing (E436, 96 jobs, three runs). That shape has a douti of
source 1, one iterated register and one doutt:

- with the fetch wait (bit 25), pa0 and pa1 are the same with bit 24 set or clear;
- with bit 24 alone or neither bit, the image changes every run;
- bit 24 without the douti's completion bit hangs, 24 of 24 jobs.

What is open: whether the bit matters in the shapes E436 did not try. 18 of E364's 21 programs
iterate the vertex colour (source 32), and 5 read pa0 to pa2. A program of that shape without
the bit might read an attribute register before its iteration lands. Why the closed driver adds
the bit is not shown either; that it is redundant under the fetch wait is an inference.

To settle it: on the laptop, run textured primaries that iterate the vertex colour, or two or
three attribute registers, with the fetch wait and bit 24 set or clear, three runs each, and
compare pa0 to pa2 and the image.
