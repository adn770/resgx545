+++
id = "Q107"
question = "what is the window of the depth buffer that a ZLS store writes (64512 dwords at 1024x768, 326656 at 4096x4096), and what are the 15104 (80640) leading zero dwords and the sign bit set on the rest in a job that overflows?"
unit = "zls"
kind = "hw"
value = "high"
phase = 11
evidence = ["E461", "E058", "E411"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_ZSTORE_BASE"]
+++

E461: with a depth buffer of the target's width x height dwords at the store base and the clearing
store control 0x0017100c, a job writes the first 64512 dwords of it at 1024x768 (62122 x 1.0 and
2390 x 0.5 for the triangle at z 0.5 whose image has 207456 pixels) and the first 326656 at
4096x4096, with the whole scene in the parameter buffer. E058 stored 4096 dwords for the 64x64
triangle, one for each pixel. So the window is not one dword per pixel of a larger target, and its
size does not follow the target's area (64512 / 786432 = 0.082, 326656 / 16777216 = 0.019).

In a job that overflows the buffer the first 15104 dwords of the window (80640 at 4096x4096) read
0.0 and, from 0x28 pages down (1024x768), the rest hold the depth with its sign bit set (-1.0,
-0.5).

Open: what the window is (a region of the target in stored order, a limit of the library's render
details, the ZLS control's region bits 3, 4 and 26 of Q101), what the leading zero dwords are
(15104 = 118 x 128, 80640 = 630 x 128) and whether the sign flip is the depth format bit of the ZLS
control that the partial-render path sets.

To settle it: store a depth ramp across a 1024x768 target with the stride and region bits varied
and read the buffer back dword by dword, with and without a partial render (the sign bit and the
zero dwords against the pixels they belong to).
