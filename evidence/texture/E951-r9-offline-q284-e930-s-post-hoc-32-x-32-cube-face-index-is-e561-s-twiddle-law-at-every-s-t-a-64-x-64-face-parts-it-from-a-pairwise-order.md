+++
id = "E951"
claim = "Round 9 offline (Q284; no run): the face-local index E930 read post hoc on its three 32 x 32 cube jobs (4831 of 4831 predicted pixels: E923's Morton interleave of (s, t) with t in bit 0, and bit 8 = s4, bit 9 = t4) is, at every (s, t) of a 32 x 32 face, E561's twiddle law of a 32-bit texture, recorded in phase 11.32 before E930 ran: tiles of 16 x 16 interleaved with Y in bit 0, the tiles in raster order with x first (i8 = x4, i9 = y4), with s as x and t as y (1024 of 1024 by enumeration, and 256 of 256 at 16 x 16 against E923's rule) [HW, E930's pixels; the identity an algebra]; so a 32 x 32 face reads as an E561 texture [infer]; at 64 x 64 E561's law (i8, i9 = s4, s5; i10, i11 = t4, t5) and a pairwise order of the bits above 7 (s4, t4, s5, t5) agree at 2048 of 4096 (s, t) and the plain 6-bit Morton at 512, so a 64 x 64 face parts them"
unit = "texture"
method = "Offline, no run (round 9, decision S-2 a; seeds plan closing9/seeds/exp-seeds-r9.md finding 3). closing9/offline/q284/e561_vs_e930.py (standard library, no data read) writes the two index functions as E930 and E561 state them (E930's out/fold/post_read.py form: E923's 4-bit Morton of (s & 15, t & 15) with t in bit 0, bit 8 from bit 4 of s, the coordinate in the odd bits, bit 9 from bit 4 of t; E561's law: tiles of min(w, 16) x min(h, 16), the interleave inside a tile with Y in bit 0 and X in bit 1, the tiles in raster order with x first) and compares them at every (s, t) of faces of 16, 32 and 64, at 64 against the round 9 seeds' rivals H-PAIRSWAP and H-MORTON (output e561_vs_e930.out). sgx-pipe's cube::point_index (this commit, test first) takes 32 x 32 faces with E561's index; crates/sgx-pipe/tests/texture_cube.rs replays E930's three 32 x 32 jobs (render/closing-r8-geo out/20261113-015842/cube, cube-n32-b1 to b3) with the predicted pixels matched (1436, 1585 and 1810, the frozen predictions' counts) and the rest (face ties, exact texel boundaries at a |ma| that is no power of two) refused, no mismatch"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-geo:out/20261113-015842/cube/", "render-closing-r8-geo:out/fold/", "texture-p1132-tx-twiddle", "cited-scratch:closing9/offline/q284/"]
terms = ["TEXTYPE"]
+++
**What was done.** E930 ran three 32 x 32 cube programs: the faces sit 1024 dwords apart and the
(s, t) of E923's rule held, but its local index, the 5-bit Morton, failed (718, 783 and 921 of
1436, 1585 and 1810 predicted pixels). Post hoc it read every predicted pixel with bits 8 and 9 of
the local index taken from bit 4 of s and of t, the fifth bit pair in the other order, and called
that fitted. The round 9 seeds planner noticed that E561 (phase 11.32, before E930) states the
twiddle law of every 32-bit twiddled texture of a side above 16. This record writes both functions
down and compares them; nothing new was run or read from hardware.

**Results [algebra, on E930's HW pixels].** With s as E561's x and t as its y, E561's index equals
E930's post hoc index at 1024 of 1024 (s, t) of a 32 x 32 face, and E923's 16 x 16 rule at 256 of
256 (`e561_vs_e930.out`): inside a 16 x 16 tile both are the Morton interleave with t (y) in bit 0;
above it E561 numbers the tiles in raster order with x first, so bit 8 is s4 and bit 9 is t4,
which is E930's reading. So E930's 4831 pixels match a law recorded before the run, not only a
form fitted to them; the law was not frozen for r8-geo, though, so the match is not a held-out
test of the face. At 64 x 64 the readings part: E561 puts s4, s5 in bits 8, 9 and t4, t5 in bits
10, 11, a pairwise order (s4, t4, s5, t5) agrees with it at 2048 of 4096 (s, t), and the plain
6-bit Morton at 512.

**sgx-pipe.** `cube::point_index` now takes 32 x 32 faces with E561's index (refused before);
E930's three 32 x 32 jobs replay with every predicted pixel matched and the face ties and exact
texel boundaries refused as before (`texture_cube.rs`). A face of any other size is refused,
naming Q284.

**What it shows.** [HW + algebra] A 32 x 32 cube face's local index, as E930 read it, is E561's
twiddle law of a 32-bit texture. [infer] A cube face is addressed as an ordinary twiddled texture
of its size, the face base aside, as the 8 x 8 and 16 x 16 faces already were (a single tile).

**What it does not show.** A held-out row: the law was not frozen before E930, so the 32 x 32 index
stays to be held out on new directions, and 64 x 64 faces (which part E561 from a pairwise order)
are unrun; the round 9 seeds' stage cube2 does both. Ties, edges and other face sizes (Q284).
