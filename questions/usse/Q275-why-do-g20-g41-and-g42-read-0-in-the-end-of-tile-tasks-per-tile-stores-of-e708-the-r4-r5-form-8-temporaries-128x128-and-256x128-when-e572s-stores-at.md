+++
id = "Q275"
question = "why do g20, g41 and g42 read 0 in the end-of-tile task's per-tile stores of E708 (the `[r4,+r5]` form, 8 temporaries, 128x128 and 256x128) when E572's stores at 64x64 read 1, 1 and 1.0 and the pixel task reads them so (E374), while g19 and g43 agree"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E708", "E572", "E374"]
terms = []
+++
E708's per-tile blocks: g16 0, g19 0x1a, g20 0, g25 3, g26 to g31 0 (ga) and g39 to g42 0, g43
0xff000000 (gb), in 32 of 32 tiles at 128x128 (and the 32 read of 64 at 256x128). E572's single
dword per job: g20 1, g41 1, g42 0x3f800000 at 64x64, g19 0x1a, g43 0xff000000.

Open: which of the differences moves the three (the register-offset store form, the pixel-event
program that ran before, the temporaries 8 against 32, the target 128 wide against 64, the module
and tool), and whether the constants depend on the tile (all 128 blocks read 0).

To settle it: E572's program form (a store through r1 with an immediate address) at 128x128 and with
8 temporaries, and E708's form at 64x64 and with 32 temporaries, g20, g41 and g42 alone, one factor
at a time.
