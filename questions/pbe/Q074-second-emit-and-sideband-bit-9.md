+++
id = "Q074"
question = "why does a second end-of-tile emit in a tile leave the next job's image wrong, and does SIDEBAND bit 9 mark an emit that counts against a PBE tile?"
unit = "pbe"
phase = 11
evidence = ["E030", "E130", "E239", "E240"]
terms = ["SIDEBAND.BIT9", "PIXEL_EVENT.END_OF_TILE"]
+++

An end-of-tile program that emits a tile twice stores the first emit's tile and leaves the next
job's image wrong at about 2000 of 4096 places (E239); sideband bit 9 (`TILERELATIVE` in the
specs) clear hangs the job, on a one-tile target too (E239), so we read it as marking an emit
that counts against a PBE tile (E240). The pixel-event program runs per tile (E130).

What is open (3d.md §12.1): that the second emit is carried out during the next job, and the
reading of bit 9 [infer].

To settle it: on the laptop, the double emit followed by a job that writes nothing, both targets
read back; the second emit aimed at a separate buffer; two emits with bit 9 set on the first only
and on the second only.
