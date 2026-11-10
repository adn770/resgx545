+++
id = "E503"
claim = "A multisampled render stores in each 32 x 16 tile of the target the pixels of a half window of the tile's own area, every sample slot written: tile (tx, ty) holds the source pixels from x = 32 tx + 16 b31 and y = 16 ty + 8 b30 (b30 acts in mode 2 only; stated for modes 1 and 2, the modes run with the bits: mode 0 ran only with CR_TE_AA 0x20000000, where b31 = b30 = 0), 16 columns by 16 rows in mode 1 and by 8 in mode 2, each stored twice in x (modes 1, 2) and in y (mode 2), where b31 and b30 are CR_TE_AA bits 31 and 30; the rule was read post hoc from the 64 x 64 runs (88 tiles of 11 configurations, 88 of 88) after the declared test decoded nothing (E502), and agrees with all 634 tiles of the 29 configurations at the four sizes declared held out (634 of 634: an agreement found after the rule was written, not a prediction) and with the 64 tiles of the 8 repeat runs, 786 of 786 tiles of the 48 runs of E502, of which 773 are written in all 512 pixels; the declared H30a (a tile of its own pixels, only its 16 x 16 corner written) failed as a test (0 of 48 runs decodable) and post hoc holds in its origin only, not in its corner"
unit = "isp"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), the 96 outputs of E502, read by analysis/an_ident.py (post hoc, after the declared recompute decoded nothing): per tile the source pixel of every stored pixel, tested against the window above; the rule was written from the 64 x 64 jobs (the 11 fit configurations) and then compared with every run, so its agreement at the held-out sizes is post hoc and was not declared before the run; one run of each of 40 configurations, four of them twice more"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["isp-msaa-ident"]
terms = ["CR_ISP_MSAA", "CR_TE_AA", "CR_ISP_MULTISAMPLECTL"]
+++

**The rule** [HW]. Stored tile (tx, ty) is 32 x 16 pixels at (32 tx, 16 ty) of the target, local
position (a, b). The pixel it holds at (a, b) has x = 32 tx + 16 b31 + a div sx and y = 16 ty + 8
b30 + b div sy, with (sx, sy) = (1, 1) in mode 0, (2, 1) in mode 1 and (2, 2) in mode 2, b31 and b30
CR_TE_AA bits 31 and 30 (b30 counts in mode 2 only: with mode 1 and 0x60000000 all 8 tiles at 64 x
64 and all 32 at 128 x 128 equal the rule with no y shift, 7 and 29 of them written in every pixel).
The bits were run in modes 1 and 2 only: mode 0 ran with 0x20000000 alone (2 runs, b31 = b30 = 0),
and its runs with 0x60000000 and 0xa0000000 (E504) draw a full green image, which shows no window,
and with 0xe0000000 fail the image check (Q141); so the b31 and b30 terms are the rule for modes 1
and 2 and not tested in mode 0. So a mode 2 tile holds 16 x 8 pixels of its 32 x 16, four samples
each in a 2 x 2 block; a mode 1 tile 16 x 16 pixels, two samples each side by side. CR_TE_AA 0x20,
0x60, 0xa0 and 0xe0 in mode 2 select the four windows (0, 0), (0, 8), (16, 0) and (16, 8) of the
tile, which tile the 32 x 16 tile exactly (the windows are disjoint and their union is its 512
pixels); in mode 1 the two windows (0, 0) and (16, 0) do the same with 16 rows.

**Counts.** 786 tiles in the 48 runs: 88 in the 11 fit configurations (64 x 64), 634 in the 29
configurations of the sizes declared held out (128 x 128: 352, 128 x 64: 96, 64 x 128: 96, 96 x 80:
90) and 64 in the 8 repeat runs; every one equals the rule on every decodable pixel (786 of 786;
722 of 722 outside the repeats, 634 of them post hoc as above). 773 tiles decode in all 512 pixels;
the other 13 hold the 455 background pixels of E502 (in 8 configurations: the mode 1 CR_TE_AA
0x60000000 runs at 64 x 64 (1 tile, 64 pixels) and 128 x 128 (3), the mode 1 0xe0000000 run at 128
x 64 (3) and at 96 x 80 (2), and the 96 x 80 runs with CR_TE_AA 0 or 0x20000000 (1 each), with 9 or
17 pixels a tile). Their positions are in the dataset (analysis/an_ident.py lists them); they are
left open (Q141).

**Against the declared hypotheses.** H30a, "a stored tile holds the samples of its own pixels,
doubled in x (and in y in mode 2), only its 16 x 16 corner written, the rest background": the
origin (32 tx, 16 ty) holds with CR_TE_AA 0 and 0x20000000 in every tile of those runs except one
tile in each of the four 96 x 80 runs (the tile with background pixels, Q141), the doubling holds,
but no part of a tile is left unwritten and a mode 2 tile holds 16 x 8 pixels, not 16 x 16: [HW]
the corner is not written alone; the stored tile is filled. The declared test could not be
evaluated as written (E502), so these are post hoc readings with the offsets of the control. H30b,
"a tile holds another tile's pixels, a shift by whole tiles": no tile is shifted by whole tiles (0
of 786); CR_TE_AA bits 31 and 30 shift the window by half a tile (16 columns, 8 rows). The declared
prediction "H30a for modes 1 and 2 with CR_TE_AA 0 and 0x20000000 at every size, none for the other
values" holds in its first half only as far as the origin and the doubling, and in its second half
with one exception: every other value moves the origin except mode 1 with 0x60000000, where b30
does not act and the origin holds in 7 of 8 tiles at 64 x 64 and in 29 of 32 at 128 x 128 (the
others the background tiles).

**E415 explained [infer].** E415's small triangle at in-tile offset 4 is stored in the first and
third tile columns with the bits clear and one at offset 20 in none: with b31 clear the window
holds source columns 0 to 15 of each tile, so offset 4 is stored (at 2 x 4 = 8 in mode 1 or 2) and
offset 20 is outside; with b31 set the window holds columns 16 to 31 and the triangle at offset 20
appears. The "constant of 4 pixels" is the doubling of the in-tile offset, not a displacement.

**What it does not show.** The window for CR_TE_AA values without bit 29 (the triangle is gone,
E281); mode 3; the sample positions inside a pixel (E502); whether the four windows of a tile are
written by four renders of one frame (Q089).
