+++
id = "Q074"
question = "why does a second end-of-tile emit in a tile leave the next job's image wrong, and does SIDEBAND bit 9 mark an emit that counts against a PBE tile?"
unit = "pbe"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E030", "E130", "E239", "E240", "E386"]
terms = ["SIDEBAND.BIT9", "PIXEL_EVENT.END_OF_TILE"]
+++

An end-of-tile program that emits a tile twice stores the first emit's tile and leaves the next
job's image wrong at about 2000 of 4096 places (E239); sideband bit 9 (`TILERELATIVE` in the
specs) clear hangs the job, on a one-tile target too (E239), so we read it as marking an emit
that counts against a PBE tile (E240). The pixel-event program runs per tile (E130).

Narrowed in 11.14 (E386): on a 64x64 target (eight tiles) every double emit hangs the job, bit 9 on
both, the first or the second (two runs each, 6 hangs); on one tile a double emit with bit 9 on both
or the first only completes, and the jobs after it store a tile or none by turns, a job that stores
nothing included, until a hang's recovery reset (the two runs differ: the tile comes a job later in
run 2 for some cases); with bit 9 on the second only, a job one or two later hangs. So the second
emit may be carried out during a later job, and so on, until a reset [infer]. The second emit aimed
at another buffer was not run.

What is open (3d.md §12.1): that the second emit is carried out during the next job, and the
reading of bit 9 [infer].

To settle it: on the laptop, the double emit followed by jobs that write a different colour each,
both targets read back, so that each stored tile names the job it came from; the second emit aimed
at a separate buffer.

Scope, corrected 2026-11-09. This question is the double emit and sideband bit 9 only, as above.
It is not "which tile an end-of-tile task names": the 1813 refusals that E620 and the transfer
model (`sgx-pipe` `xfer`) filed under this id are 1534 sweeps of the end-of-tile task's U1 x
field (511) and y field (1023) on the fill, plus 279 pokes of the pixel-event program's data
words (the figure follows from E620's 1813; the 511 and 1023 are the scenes of
`scene-vectors/transfer/pds/end-of-tile`). None emits twice or varies bit 9. Those belong to
Q289. The model's refusal sites and the scenes' `expect.refuse` lists still carry Q074 until
they are relabelled; the double emit and bit 9 are untouched by them and still need their laptop
run.
