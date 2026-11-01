+++
id = "Q120"
question = "what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and how are they laid out, given that they store depth and stencil packed or nothing?"
unit = "zls"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E466", "E490"]
terms = ["CR_ISP_ZLSCTL"]
+++

E466: of the eight values of bits 26:24 only 0 (float32), 1 (24-bit) and 2 (16-bit) store plain
depth. At 1024 x 768 with G = 33 and no stencil buffer, 3 stores 965120 scrambled dwords in 1885
slots of 512, 5 stores 96580 and 6 stores 86084, and 4 and 7 store nothing. With a stencil buffer,
3 stores 965120 depth dwords and 17920 stencil dwords, 4 stores 245760 depth dwords and no stencil,
5 96580 and 1792, 6 86084 and none, 7 18432 and none. E490 repeated the counts without a stencil
buffer from stored dumps, in the x ramp (965120, 96580 and 86084 dwords for 3, 5 and 6, none for 4
and 7; the y ramp stores 965120, 84480 and 73760, so for 5 and 6 the count depends on the stored
data, and format 3 reaches the last dword of the 1000-page buffer, so 965120 is a lower bound) and
decoded none of the layouts.

What is open: the layout of each (bytes a pixel, the in-tile order, whether the stencil is inside
the depth words, whether 5 and 6 are compressed and by what), and what the hardware does with 4 and
7 when no stencil is present. To settle it: a depth ramp and a stencil pattern (a stencil buffer
with a known value per pixel, through the loads of E467 or a stencil operation) stored in each
format, the dwords decoded against the pixels, at several sizes.
