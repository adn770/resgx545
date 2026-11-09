+++
id = "Q138"
question = "how does the closed driver's 4x render of a 64 x 64 texture fill a 64 x 64 image when one render with CR_TE_AA 0xe0000000 stores only a 16 x 8 window of each 32 x 16 tile (E503): are the four windows (0x20000000, 0x60000000, 0xa0000000, 0xe0000000) four renders of one frame, and what combines them"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E503", "E508", "E510", "E339", "E439", "E727"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++

E503 (a rule read post hoc from the 64 x 64 runs, then found to agree with all 634 tiles of the
sizes declared held out): a mode 2 render stores in each 32 x 16 tile the pixels of one quarter
window chosen by CR_TE_AA bits 31 and 30 (bit 29 set), and the four values 0x20000000, 0x60000000,
0xa0000000, 0xe0000000 choose four disjoint windows that tile the 32 x 16; mode 1 has two. E508: the
closed driver's setting (0xe0000000) stores 1024 distinct pixels of the 4096. E510 (11.26 resume, 66
jobs): no single bit of the end-of-tile sideband resolves or blends: the bits change channel order,
a 16-bit pack and a partial write, 14 of 64 flips, and the other 50 draw the controls' image. So no
single bit of the sideband of our own emit resolves (64 one-bit flips from two bases); the closed
driver's own sideband and combinations of bits are not excluded.

What is open: whether the closed driver renders each frame four times (once per window) and what
reads the four stored images, or whether one render at 0xe0000000 is all the hardware does and the
other three quarters are produced by a later pass; and, if there are four renders, whether the
windows of one render can be combined with the targets' addresses. To settle it: a capture walk of
the closed driver's frame that counts the renders of a 4x frame and the CR_TE_AA word of each (E339
compared one render only), and on the laptop a mode 2 frame rendered four times with the four
values into the same target, checking that the stored windows do not overwrite one another.

Note from 11.39 (E727): the stored image equals the region model's in 17 of 17 jobs. A 12 x 6
triangle in a region other than the last visited reads a non-zero visibility counter 0x0498 (144
in 0xe0 jobs) with an empty image in 7 of 7 jobs (6 distinct jobs and a repeat), but the same
empty image reads counter 0 at TE 0x20 (4 controls), so the counter does not show that every
region is walked [infer]; it may count stored samples (144 = 4 x 36). This does not resolve a 4x
render and does not remove "the region is skipped"; the question stays open.

Noted 2026-11-09: near duplicate of Q089, not merged (both ask how the closed driver's 4x render
becomes a 64 x 64 image). A merge or a fold decides which text survives.
