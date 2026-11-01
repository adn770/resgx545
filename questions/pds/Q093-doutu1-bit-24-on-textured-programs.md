+++
id = "Q093"
question = "does DOUTU1 bit 24 (wait for iterations) change what a textured primary pixel program reads when it iterates a coordinate set (two or three components) before the fetch, or hang the job, as the closed driver's programs that set it do?"
unit = "pds"
phase = 11
evidence = ["E345", "E364", "E436", "E454"]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH"]
+++

The closed driver sets DOUTU1 bit 24 exactly when a douti of the primary iterates an attribute
into the primary attribute registers (E364, 21 of 21 captured primaries with a fetch).

In one program shape the bit adds nothing (E436, 96 jobs, three runs). That shape has a douti of
source 1, one iterated register and one doutt:

- with the fetch wait (bit 25), pa0 and pa1 are the same with bit 24 set or clear;
- with bit 24 alone or neither bit, the image changes every run;
- bit 24 without the douti's completion bit hangs, 24 of 24 jobs.

Narrowed by E454 (the fetch wait set, bit 24 set or clear, 10 probes of three program shapes, 180
jobs):

- The colour-only shape (the vertex colour iterated, then the fetch) is settled: bit 24 set or
  clear gives the same image under the fetch wait, whichever pa the shader writes out (E454).
  Over the three shapes, the 29 jobs that completed with bits 24 and 25 equal the 30 of 30 with
  bit 25 alone; one job with both bits hung (0 of 30 with bit 25 alone);
- in the coordinate shapes the coordinate registers read 0x00000000 in all 1062 triangle pixels of
  every stable image (pa1 and pa2 of the two-component shape, pa0 to pa2 of the three-component
  one), with bit 24 set or clear. The comparison there is against a constant zero, so these
  shapes are open: it is not shown that the iteration delivers a coordinate set under either bit
  setting.

What is open: the coordinate shapes (what a coordinate register holds under the fetch wait, with
the bit set, when it does not read 0); whether the one hang with bits 24 and 25 (the first run of
the colour then two-component shape, pa0; the same program completed in its other two runs)
recurs; and shapes E454 did not try (18 of E364's 21 programs iterate the vertex colour and 5
read pa0 to pa2, and 18 of the 21 were not run themselves). Why the closed driver adds the bit is
not shown either; that it is redundant under the fetch wait is an inference, for the colour.

To settle it: on the laptop, run the coordinate shapes with a source that delivers a non-zero
value (a program shape where the registers do not read 0), bit 24 set or clear, three runs each,
and repeat the colour then two-component shape with bits 24 and 25 at least thirty times to see
whether the hang recurs.
