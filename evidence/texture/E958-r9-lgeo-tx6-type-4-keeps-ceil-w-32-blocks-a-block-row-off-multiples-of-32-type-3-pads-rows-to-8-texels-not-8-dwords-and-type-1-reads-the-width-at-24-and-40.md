+++
id = "E958"
claim = "R9-lgeo stage tx6 (Q283; E725's 64 x 32 map-texture fill, dword i of the scratch 0xD0000000 | i; 14 jobs, 2 controls, no fault): type 4 at widths that are not multiples of 32 keeps ceil(w / 32) whole 32 x 32 blocks a block row (H-CEIL, E941's rule: 7 of 7 held-out windows of 48 x 64, 80 x 64 and 96 x 32 through the linear axis with offsets), where the width rounded up to a power of two (H-P2) held 5 and a partial block w mod 32 columns wide (H-PACK) 2; type 3 at format 5 (16-bit texels, two a dword, the low half first) reads rows max(8, w) texels apart (H-TX8: 2 of 2 at 4 x 8 and 8 x 8), not 8 dwords (H-DW8: 0 of 2) nor the width (1 of 2); type 1 at 24 x 8 and 40 x 8 reads a raster of the width, not a power of two above it (2 of 2, soft rows whose bridge, type 1 at 32 x 16 through the same axis, gave E725's image); controls pass; frozen verdicts 'Q283 type 4 past a multiple of 32: H-CEIL (ceil(w / 32) blocks a block row) held (7 of 7 rows decided)', 'Q283 type 3 padding rival: H-TX8 held (2 of 2 rows decided)' (the frozen favourite H-DW8 'is not supported: 0 held, 2 FAILED') and 'Q283 type 1 at 24 and 40 wide (soft, bridge held): RASTERW held (2 of 2 rows decided)'"
unit = "texture"
method = "R9-lgeo stage tx6 of the question-closing pass, round 9 (decision S-4 (a) of closing9/DECISIONS-R9.md; plan closing9/seeds/exp-seeds-r9.md section 5, session S9-lgeo), dataset render-closing-r9-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-080029 (lead log out/run-r9m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753 bound by source, TOOLSRC.sha256; every row replayed on the library mock before the run), built on the session kit (resgx545 f32dfac); jobs `probe --temps 32 --coords --pixels` of bins/r9l-*.bin (templates/tx_map.s with r8-lgeo's gen/texbuild.py and gen/texcatalog.py, byte copies, assembled by gen/lgen.py with usse-asm from git archive of resgx545 f32dfac); the two controls are E910's type 4 64 x 32 and E725's type 3 32 x 16 programs byte for byte; the type 4 and type 1 rows map u = (x + xo + 1/2) / w and v = (y + yo + 1/2) / h by fmad (gen/lgen.py lwin, texcatalog.swin at no offset, tests/test_gen.py), the repeat mode wrapping both; the type 3 rows use the map axis and T1 format 5; every row at t4's default 16 scratch pages (64 KiB; no rival reads past dword 7151); the health fill and triangle after every job (`after`); the three type 1 rows last and `soft`. Frozen before the first job (FROZEN.sha256 bc18b46e..., PREDICTIONS.sha256 3e70e55e..., FROZEN.commits pinning every input at resgx545 f32dfac and resgx545-data 2d666bfa): type 4 H-CEIL against H-P2 and H-PACK as the sha256 of the 2048 sampled dwords (gen/tx6model.py over gen/texmodel.py); type 3 at format 5 H-DW8 (rows max(16, w) texels), H-TX8 (max(8, w)) and RASTERW (w) as the sha256 of the 16-bit words read back from the pixels' top bits (tx6model.word_of), whether the pixels are also sgx-sim's widening and whether the words match a rule with the high half first printed as readings; type 1 RASTERW against RASTERP2; controls: the kept images. Scored by the frozen score/score.py tx6 in the run (score-tx6.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-lgeo:out/20261113-080029/tx6/", "render-closing-r9-lgeo:fold/", "vectors-closing-r9-lgeo-pixels"]
terms = ["TEXTYPE"]
+++
**What ran.** E941 held type 4's 32 x 32 blocks row by row at multiples of 32, E940 type 3's rows
max(8, w) dwords apart at format 12 and type 3's raster of the width at 24 and 40 wide; type 4 off
multiples of 32, type 3 at a 16-bit format and type 1 at widths that are not powers of two had not
run. Stage tx6 moved a 64 x 32 window over type 4 textures of 48 x 64 (y 0, 32), 96 x 32 (x 64)
and 80 x 64 (x 0, 64 by y 0, 32) through the linear axis with offsets (the map axis addresses
powers of two only), froze H-CEIL against H-P2 and H-PACK (H-PACK parts on 5 windows, H-P2 on the
2 at 80 x 64 y 32), ran type 3 at 4 x 8 and 8 x 8 of format 5 (H-DW8, the frozen favourite, against
H-TX8 and RASTERW; all three part at 4 x 8), and ended with type 1 at 24 x 8 and 40 x 8 and their
bridge.

**Frozen verdict (as printed).** `Q283 type 4 past a multiple of 32: H-CEIL (ceil(w / 32) blocks a
block row) held (7 of 7 rows decided)`; H-P2 `5 held, 2 FAILED`, H-PACK `2 held, 5 FAILED`; `Q283
type 3 padding at a 16-bit format: H-DW8 (rows max(8 dwords, w texels) apart) held is not
supported: 0 held, 2 FAILED`; `Q283 type 3 padding rival: H-TX8 held (2 of 2 rows decided)`;
RASTERW `1 held, 1 FAILED`; `BRIDGE tx6-lin-ty1-32x16 ...: held`; `Q283 type 1 at 24 and 40 wide
(soft, bridge held): RASTERW held (2 of 2 rows decided)`, RASTERP2 `0 held, 2 FAILED`. Both
controls passed.

**Results [HW].** Every pixel of every type 4 and type 1 row holds a texel tag. Type 4 reads dword
((y div 32) ceil(w / 32) + (x div 32)) 1024 + (y mod 32) 32 + (x mod 32) at 48, 80 and 96 wide: at
80 x 64 block row 1 starts at block 3, not 4, and the 16 columns past 64 sit 32 dwords apart inside
a whole block. Type 3 at format 5 reads 16-bit word (y mod 8) max(8, w) + (x mod w), the low half
of a dword first; its pixels are sgx-sim's B5G6R5 widening of those words (each field's bits
repeated, alpha 0xff), read so at the fold from the scorer's READING lines. Type 1 reads (y mod 8)
w + (x mod w) at 24 and 40 wide.

**What it shows.** [HW] Type 4 numbers whole 32 x 32 blocks row by row with ceil(w / 32) of them a
block row at every width run (4 to 256; with E910 and E941), a partial block taking a whole block's
room. Type 3 pads a row to 8 texels, not 8 dwords: max(8, w) texels at 16 and 32 bits a texel
(with E940, whose rows of max(8, w) dwords are texels at format 12). Type 1 reads a raster of the
width at widths that are not powers of two, as type 3 does (E940). E940 and E942 are not
contradicted: E940's dwords are format 12's texels, and E942's "H-DW8" is another hypothesis of
the same name (type 5's bit 0 of dword floor(t / 8)).

**What it does not show.** Why type 3 pads to 8 texels; other 16-bit and 8-bit formats on type 3,
type 1 and type 4 at a 16-bit format; type 4 heights that are not multiples of 32; type 1 above 40
at such widths; filters and address modes other than point and repeat.
