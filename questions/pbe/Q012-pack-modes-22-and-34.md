+++
id = "Q012"
question = "what do pack modes 22 and 34 encode, given a single value in 727 of the triangle's 1062 pixels and backgrounds that vary from run to run?"
unit = "pbe"
phase = 6
evidence = ["E032"]
terms = ["SIDEBAND.PACKMODE", "PACKMODE"]
+++

With the 64x64 triangle (o0 0x80ff8040 over the background 0xff203040), pack mode 22 writes
0x00000088 and mode 34 writes 0x60800000 in 727 dwords, in both runs (E032). All 727 pixels lie
inside the triangle (1062 pixels in the plain ARGB8888 image). One value per pixel; no dword
holds an interleaved pair.

The rest of the target is not stable. Mode 22 first run: 0x08800088 in 1323 dwords, 0x08800000 in
1269, 0x088ffc00 in 341 and 436 other; follow-up run: 0x08800000 in 1560, 0x08800088 in 1322,
0x00000000 in 307 and 180 other; 531 of 4096 dwords differ between runs. Mode 34: 0x60800304 and
0x00000304 and 0x00000000 and 546 other values in the first run, a different mix in the follow-up
run, 602 of 4096 dwords differ. The stable part of modes 22 and 34 is the 727 pixels.

Neither value matches the luma or chroma of the triangle colour or of the background in studio
or full range (BT.601 luma 152 or 159 for the triangle, 55 or 45 for the background), or any
channel's top bits (mode 26 stores R >> 3 and G >> 3, and 22 and 34 do not follow it).

Open: what the two modes encode; why 727 and not 1062 pixels hold the value (the other 335
triangle pixels may hold a value that is not in the stable set); whether the backgrounds'
variation is state left by an earlier job. Only one triangle colour and one background colour
ran, so a rule that depends on colour is not excluded.

To settle it: run both modes with five or more distinct triangle colours (single channels at 0,
0x80, 0xff, and a grey ramp), read every pixel of the target in both runs, and look for the
fields that move with a channel; run the target buffer filled with a known pattern first,
to tell a partial write from leftover state; locate the 727 pixels (and the 335) by position
against the triangle's coverage.
