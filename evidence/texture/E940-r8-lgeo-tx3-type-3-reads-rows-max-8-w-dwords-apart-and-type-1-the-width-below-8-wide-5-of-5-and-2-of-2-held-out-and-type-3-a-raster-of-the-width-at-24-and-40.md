+++
id = "E940"
claim = "R8-lgeo stages tx3 and tx4 (Q283; E725's 64 x 32 map-texture fill, dword i of the scratch 0xD0000000 | i; 12 jobs and 3 controls, no fault): below 8 texels wide type 3 reads rows max(8, w) dwords apart (H-MIN8, frozen from E910's one row: 5 of 5 held out, at 2 x 16, 4 x 8, 4 x 32, 2 x 8 and 1 x 16) and type 1 a raster of the width (2 of 2, at 2 x 16 and 1 x 16); through the linear axis type 3 at 24 x 8 and 40 x 8 reads a raster of the width, not the width rounded to a power of two (2 of 2, soft rows whose bridge, type 3 at 32 x 16 through the same axis, gave E725's map image); controls pass; frozen verdicts 'Q283 type 3 below 8 wide: H-MIN8 (rows max(8, w) dwords apart) held (5 of 5 rows decided)', 'Q283 type 1 below 4 wide: RASTERW held (2 of 2 rows decided)' and 'Q283 type 3 at 24 and 40 wide (soft, bridge held): RASTERW held (2 of 2 rows decided)'"
unit = "texture"
method = "R8-lgeo stages tx3 and tx4 (its three linear rows) of the question-closing pass, round 8 (decision R8-8; plan closing8/leftovers/exp-leftovers-r8.md section 3, session L2), dataset render-closing-r8-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-024441 (lead log out/run-r8m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, installed = loaded, knobs at their defaults at every stage start), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), built on the session kit (resgx545 91f21da); jobs `probe --temps 32 --coords --pixels` of bins/r8l-*.bin (templates/tx_map.s with r7-geo's generator, gen/texbuild.py and gen/texcatalog.py, assembled by gen/lgen.py with usse-asm from git archive of resgx545 91f21da; the three controls are E725's and E910's programs byte for byte, tests/test_gen.py), the health fill and triangle after every job (`after`), every job class ok; the linear rows map u = (x + 1/2) / w by fmad (texcatalog.swin) and ran `soft` after the bridge. Frozen before the first job (FROZEN.sha256 90ab0f4d..., PREDICTIONS.sha256 df01463d..., FROZEN.commits pinning every input at resgx545 91f21da and resgx545-data 1e83dc86): type 3 H-MIN8 against H-2W and RASTERW, type 1 RASTERW against H-MIN8 and H-2W, the linear rows RASTERW against RASTERP2, each as the sha256 of the 2048 sampled dwords (gen/texmodel.py); controls: the kept images of E725's type 3 32 x 16 and E910's type 3 and type 1 4 x 16. Scored by the frozen score/score.py tx3 and tx4 in the run (score-tx3.txt, score-tx4.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (out/fold/reproduce.sh)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r8-lgeo:out/20261113-024441/tx3/", "render-closing-r8-lgeo:out/20261113-024441/tx4/"]
terms = ["TEXTYPE"]
+++
**What ran.** E910 held types 1 and 3 out as a raster of the width at 64 and 128 wide and type 1 at
4 x 16, but type 3 at 4 x 16 read rows 8 dwords apart (post hoc, one row); widths that are not
powers of two had not run (the map window maps powers of two only). Stage tx3 ran E725's
map-texture fill for type 3 at 2 x 16, 4 x 8, 4 x 32, 2 x 8 and 1 x 16 and type 1 at 2 x 16 and
1 x 16, with H-MIN8 (rows max(8, w) dwords apart) frozen for type 3 against H-2W (2 w, the other
reading of E910's row, parting at 2 and 1 wide) and RASTERW. Stage tx4 ended with three soft rows
through the linear axis: type 3 at 24 x 8 and 40 x 8 (RASTERW against RASTERP2, the stride rounded
up to a power of two) and their bridge, type 3 at 32 x 16 through the same axis.

**Frozen verdict (as printed).** `Q283 type 3 below 8 wide: H-MIN8 (rows max(8, w) dwords apart)
held (5 of 5 rows decided)`; H-2W `2 held, 3 FAILED`, RASTERW `0 held, 5 FAILED`; `Q283 type 1
below 4 wide: RASTERW held (2 of 2 rows decided)` (H-MIN8 and H-2W `0 held, 2 FAILED`); `BRIDGE
tx4-lin-ty3-32x16 (the linear axis gives E725's map image): held`; `Q283 type 3 at 24 and 40 wide
(soft, bridge held): RASTERW held (2 of 2 rows decided)`, RASTERP2 `0 held, 2 FAILED`. The three
controls passed.

**Results [HW].** Every pixel of every row holds a texel tag. Type 3 reads dword (y mod h) max(8,
w) + (x mod w) at 1, 2 and 4 wide and heights 8 to 32; type 1 reads (y mod h) w + (x mod w) at 1
and 2 wide; type 3 at 24 x 8 and 40 x 8 reads (y mod 8) w + (x mod w), the 64 pixels of a row
wrapping at the width by repeat.

**What it shows.** [HW] Type 3's row pitch is max(8, w) dwords from 1 to 128 texels wide (with
E725 and E910), held out at five sizes, and type 1's is the width from 1 to 128; type 3's pitch is
the width at 24 and 40, not a power of two above it, and repeat wraps such a texture at its own
width.

**What it does not show.** Why type 3 pads a row to 8 dwords; type 1 at widths that are not powers
of two (not run); type 3 above 40 at such widths, other formats than 32-bit texels, other filters
and address modes than point and repeat; columns past 63 of a type 1 or 3 texture (the window).
