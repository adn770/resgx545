+++
id = "Q117"
question = "where does a point's size come from, what footprint does the 3D cover for a point object (E181 shows the TA writes one), and does the closed driver's extra output row carry the size?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E181", "E340", "E346", "E414"]
terms = ["VDM_INDEX0.PRIMITIVE_TOPOLOGY", "CSTREAM.PRIM_POINTS", "ISP0.OBJ_TYPE"]
+++

Topology 2 in the index list header names points; the TA's primitive word has bits 30:29 = 3 for a
point (CSTREAM.PRIM_POINTS) and ISP word 0 adds 0x18000 to mark one (ISP0.OBJ_TYPE,
doc/specs/3d.md). The TA does write a point object (E181, the points probe, three points with index
list type 2): ISP word 0 is 0x01d18200, the primitive list is (16, 16, 16), (17, 17, 17),
(18, 18, 18), the primitive word is 0x64800101 and the object word's bits 31:26 are 5. The job of
E414 (the five-copy triangle job with the topology set to 2) completes and writes no object, every
pixel the background, so that job does not make a point object; E181's points are the TA's. The
closed driver's point-size shader has one more output row than the plain points draws (E346), which
fits a size written per vertex [infer]. No run of ours has drawn a point to pixels.

Open: where the size comes from and in what unit (the extra output row, or a state word), what
footprint the 3D covers for a point object (a square of the size, in pixels or fractions) and
whether that rule reads the object's vertex or the primitive word. The region test for lines and
points is Q070's.

To settle it: the closed driver's point corpus captured against ours (the capture tables of 11.11),
then `probe --tri` with `--vdm` setting the topology to 2 and `--blk N=V` writing the object and
primitive words E181 shows, a size vertex output stepped from 1 to 64, and the pixels counted
(`--pixels`).
