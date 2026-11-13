+++
id = "Q141"
question = "do the background pixels of a multisampled render under the full triangle hold out as the seam holes of the region model (E922: every one of E502 and E504, in sample; a stored half takes only its half-region's primitive list) at sizes, modes and slopes never run (round 8's R8-1 row)"
unit = "isp"
kind = "hw"
value = "low"
phase = 11
evidence = ["E502", "E503", "E504", "E618", "E727", "E762", "E922"]
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

Narrowed 2026-11-13 (round 8 offline, decisions R8-1 a and R8-3 a; E922). The landed region model
of E727 (unchanged) gives every background pixel of E502's 48 identity jobs as a set (48 of 48)
and of E504's 15 tri-full jobs that store a triangle (the 136 at (32, 32) among them), with its
two-halves rule; without the halves it misses all 8 jobs with holes. The holes are staircases at a
tile's top-left along the diagonal of the quad the TA clips the tool's triangle to (E762's decode),
so of the three readings above the region left without a primitive and the clip are out, and the
edge seen in the window is the model's halves [infer]. In sample only (the seam was set on E502);
out of sample E727 (17 of 17) and E762 (28 holes at 320 x 400, post hoc). E618 refuses these 13
tiles in sgx-pipe. What stays: the held-out row, R8-1 of session r8-geo (24 jobs, the hole set of
each frozen under the model and its halves-off rival in
`closing8/offline/r8-1/q141_r8pred.tsv`); the question retires on it if every held-out set is
exact.
