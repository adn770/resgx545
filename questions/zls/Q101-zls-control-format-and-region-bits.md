+++
id = "Q101"
question = "what do bits 3, 4, 19, 24, 25 and 26 of CR_ISP_ZLSCTL do beyond what a store writes, given that they change the stored depth's format and the stored region?"
unit = "zls"
phase = 11
evidence = ["E057", "E284", "E411"]
terms = ["CR_ISP_ZLSCTL"]
+++

With the store setup of load-store.sh and control 0x17100c, flipping a bit changes what is stored
(E411, two runs, identical): bit 19 set stores the depth as -1.0, bit 24 as 0x00ffffff, bit 25 as
0xffffffff on two pages, bit 26 640 dwords of 0x0000f000 on two pages; bit 3 cleared stores a
shorter region, bit 4 set another. These read as a depth format and a region, but only the triangle
at one depth was stored.

What is open: what the stored values mean (which formats), and whether the bits are a field. To
settle it: store a depth ramp across the target with each of these bits and read the pages back, and
vary the load and store bases and the target size for the region bits.
