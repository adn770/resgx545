+++
id = "Q141"
question = "why does a handful of pixels in one tile stay background when the full triangle covers the target, with CR_TE_AA bits 30 or 31 set in mode 1 (64 pixels at 64 x 64, tile (1, 2)) or at 96 x 80 in modes 1 and 2 (9 to 39 pixels), and 136 pixels at (32, 32) in mode 0 with 0xe0000000"
unit = "isp"
kind = "hw"
value = "low"
phase = 11
evidence = ["E502", "E503", "E504"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++

E502 and E503: 455 pixels in 13 tiles of 8 of the 48 runs hold the background colour with the full
triangle (1 tile at 64 x 64 and 3 at 128 x 128 in mode 1 with 0x60000000, 3 at 128 x 64 in mode 1
with 0xe0000000, and 6 at 96 x 80); E504: the tool's check finds 136 pixels at (32, 32) wrong in
mode 0 with 0xe0000000.

What is open: whether they are the triangle's edge seen in the window (the window of a tile sees a
different part of the target than the triangle's own tile does), a tile the TA leaves without a
primitive, or a clip. To settle it: the same configurations with a triangle that has a different
slope and a second identity map of the edge pixels.
