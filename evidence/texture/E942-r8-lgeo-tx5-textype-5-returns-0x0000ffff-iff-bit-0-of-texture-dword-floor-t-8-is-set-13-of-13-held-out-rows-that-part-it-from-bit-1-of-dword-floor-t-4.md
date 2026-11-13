+++
id = "E942"
claim = "R8-lgeo stage tx5 (Q178; type 5 on E725's map-texture fill and on stored dwords, 28 jobs, no fault): TEXTYPE 5 with format 12 returns 0x0000ffff for a texel t = (y mod h) w + (x mod w) iff bit 0 of texture dword floor(t / 8) is set, else 0 (H-DW8, the round 8 planning's post hoc fit on E911's six rows: 13 of 13 held-out rows where it parts from H-DW4B1, bit 1 of dword floor(t / 4), which held 0; 8 of 8 rows where the two agree, the high bits and the raster index at 32 x 8, 8 x 32, 16 x 8 and a 64 x 64 window at y 32); controls pass (E911's 8 x 8, 16 x 16 and zeroed 16 x 16 images); read after the run, the format 9 row is bit 0 of 16-bit word floor(t / 8) and format 18 and the bilinear filter gave the format 12 point images; frozen verdicts 'Q178 type 5 (rows where the two part): H-DW8 (bit 0 of dword floor(t / 8)) held (13 of 13 rows decided)' and 'H-DW8 = H-DW4B1 held (8 of 8 rows decided)'"
unit = "texture"
method = "R8-lgeo stage tx5 of the question-closing pass, round 8 (decision R8-8; plan closing8/leftovers/exp-leftovers-r8.md sections 0 (P2) and 3, session L2), dataset render-closing-r8-lgeo, on the laptop, 2026-11-13, one attempt out/20261113-024441 (lead log out/run-r8m.log; no stop, no lead decision), kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0), stock firmware, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558..., resgx545 4623753), built on the session kit (resgx545 91f21da); jobs `probe --temps 32 --coords --pixels` of bins/r8l-ty5-*.bin (templates/tx_map.s; the stored rows write their dwords before the sample with the generator's inject, 64 of them at 8 x 8 and 112 at 16 x 16; the three controls are E911's programs byte for byte), the health fill and triangle after every job, every job class ok; four explore rows last, `soft`: format 9, format 18, and the bilinear filter at 16 x 16 and 8 x 8. Frozen before the first job (FROZEN.sha256 90ab0f4d..., PREDICTIONS.sha256 df01463d..., FROZEN.commits at resgx545 91f21da and resgx545-data 1e83dc86): H-DW8 against H-DW4B1 as the sha256 of the 2048 sampled dwords (gen/texmodel.py); the explore rows had no prediction. Scored by the frozen score/score.py tx5 in the run (score-tx5.txt); at the fold the same scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (out/fold/reproduce.sh). Post hoc at the fold, not frozen: out/fold/tx5_read.py compares the explore images with the format 12 point images and scans 'bit B of word floor(t / K)' over 16-bit words and dwords for format 9"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-lgeo:out/20261113-024441/tx5/", "render-closing-r8-lgeo:out/fold/"]
terms = ["TEXTYPE"]
+++
**What ran.** E911 showed that type 5 follows the texture memory and returns 0 or 0x0000ffff, and
the round 8 planning found offline that "bit 0 of dword floor(t / 8)" (H-DW8) and "bit 1 of
dword floor(t / 4)" (H-DW4B1) are both exact on E911's six rows (one function of the map fill).
Stage tx5 froze H-DW8 against H-DW4B1 on rows that part them: 8 x 8 with all 64 dwords stored
0x1, 0x2, 0xfffffffe, 0xfffffffd; one dword j = 0xffffffff among zeros (j 0, 1, 3, 7 at 8 x 8;
0, 5, 31 at 16 x 16); 16 x 16 with 112 dwords stored 0x1 or 0x2; and on rows where they agree
(stored 0x4, 0x8, 0x10000, 0x80000000; plain fills at 32 x 8, 8 x 32, 16 x 8 and a 64 x 64
window at y 32).

**Frozen verdict (as printed).** `Q178 type 5 (rows where the two part): H-DW8 (bit 0 of dword
floor(t / 8)) held (13 of 13 rows decided)`; `Q178 type 5 rival: H-DW4B1 (bit 1 of dword floor(t /
4)) held is not supported: 0 held, 13 FAILED`; `Q178 type 5 (rows where the two agree: the raster
index, the high bits): H-DW8 = H-DW4B1 held (8 of 8 rows decided)`. The three controls passed.

**Results [HW].** Every row's 2048 pixels are 0 or 0x0000ffff as H-DW8 gives them: one stored
dword lights the 8 texels 8 j to 8 j + 7, a stored 0x1 or 0xfffffffd lights every texel and 0x2,
0xfffffffe, 0x4, 0x8, 0x10000 and 0x80000000 none.

**Read after the run (post hoc, not frozen; out/fold/tx5_read.py).** Format 9 (16 x 16) lit 512
of 2048 pixels, exactly 'bit 0 of 16-bit word floor(t / 8)' (words little endian; no dword rule
fits); format 18 and the bilinear filter (16 x 16 and 8 x 8) gave the format 12 point images.

**What it shows.** [HW] With format 12 TEXTYPE 5 reads one bit per 8 texels: texel t returns
0x0000ffff iff bit 0 of dword floor(t / 8) of the texture is set, else 0, t the raster index of
the texel, held out at 8 x 8 and 16 x 16 and on the plain fill from 8 x 8 to 64 x 64. [infer] It
is a 1-bit texture of 8 texels per element, the element the format's size (a 16-bit word for
format 9, one row), and the filter does not blend it.

**What it does not show.** Why bit 0 only (the other 7 bits of the element's low byte are ignored
on every row run); formats other than 12 held out (format 9 and 18 are one explore row each);
other address modes; widths that are not powers of two; what the type is for.
