+++
id = "Q013"
question = "what does bit 18 of the copy's pixel-event data word 2 do, when it leaves the copy unchanged and changes a few pixels of the fill and the triangle?"
unit = "pds"
phase = 6
evidence = ["E043", "E046"]
terms = ["PIXEL_EVENT.END_OF_TILE"]
+++

The sweep `pds-data-words` flips every bit of every data dword of the pixel-event program of a
fill, a copy and a triangle (the end-of-tile word `pixev:12` is E043; E046 covers other words
of the program), and ran twice (the second is the follow-up run). Word 2 of the program
(`pds:pixev:2`) has no record. The case `pds:pixev:2^=0x40000` (bit 18):

- copy, plain source (`pds-copy`): `job: ok`, 0 of 2048 pixels differ (hash
  0x9b1c0be484ac0d25), in both runs. Over the every-value source (`copy-every-pds`) also
  unchanged in both.
- fill (`pds-fill`): changes 5 pixels (first at (0, 0), value 0x00000002) in both runs.
- triangle (`pds-tri`): changes 7 pixels in the first run and 6 in the follow-up run (first at
  (32, 0), value 0x00000002).

Other bits of the same word on the copy: bit 16 faults the job (2048 of 2048 pixels at the
sentinel) in both runs; bit 17 changes 2 pixels (first at (16, 0), value 0x00000002) in both;
bit 19 changes none in the first run and 1 pixel (at (16, 12), value 0x00000002) in the
follow-up run. Over the every-value source bit 17 changes 1 pixel in the first run and 3 in
the follow-up run, bit 19 none and 1.

So the bits of this word can add a stray write of 0x00000002 to the copy, and the outcome of a
flip varies from run to run for bits 17 and 19. Bit 18 is stable on the copy (unchanged in
both runs), and the fill and triangle changes are a few pixels at fixed first positions.

Open: what the word is (an event mask, a count, an address part); why bit 18 leaves the copy
alone and writes a few pixels of the fill and the triangle; whether the stray 0x00000002 writes
have the same cause as the pixels of bit 18; what makes the number of stray pixels differ
between runs.

To settle it: run bits 16 to 19 of `pixev:2` ten times each on the copy with `--pixels`,
recording the positions and values of the changed pixels; record the visibility counters
(they count in some boots only); vary the copy's size (64x32 against 128x128) to see whether
the stray pixels follow the tile.
