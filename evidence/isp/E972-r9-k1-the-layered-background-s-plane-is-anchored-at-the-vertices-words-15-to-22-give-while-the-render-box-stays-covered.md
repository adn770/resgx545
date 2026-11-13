+++
id = "E972"
claim = "R9-k1 stage s2 (Q066, and the anchor E971 left open; 20 held-out jobs, the layered 64 x 64 render with kernel pokes of the vertex words 15 to 22: a move of 16 pixels and a bit flip each, four two-word moves; no fault): the layer's plane is anchored at the vertices those words give in E590's encoding (TL, TR, BL as 24-bit Y then X, 8 fraction bits, offset 4096; H-VPLANE: right on 20 of 20 rows, every predicted pixel the predicted texel), not at the fixed render box (H-VBOX: wrong on the 16 rows that move a vertex, right on the 4 that poke words 19 and 22, which hold no vertex); every background pixel stays covered and a texel in all 20 (1062 triangle pixels each), as E590's coverage; every poked word reads back; frozen verdict 'H-VBOX: the plane is anchored at the render box, whatever words 15-22 say is not supported: 4 held, 16 FAILED, 0 cannot tell of 20'"
unit = "isp"
method = "R9-k1 (render/closing-r9-k1) of the question-closing pass, round 9 (decisions K-1 to K-6 (a) of closing9/DECISIONS-R9.md; plan closing9/k1/exp-k1-r9.md), dataset render-closing-r9-k1, on the laptop, 2026-11-13, one attempt out/20261113-083450 (lead log out/run-r9k.log; no stop, no lead decision; s1n's gate shut as frozen, H-NONE failed at c-rawu and c-rawv), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74: debugfs render_bg_layer and render_bg_src, bg kernel pokes to word 22 with the layer; fafea977 builds the 23-dword one-layer object from the tag), stock firmware, tool ~/sgxfive-test-t9 (t9, sha256 7a28be39..., built from resgx545 97447b04 by lead/build_tool9.sh, FROZEN.commits' built line; it reads both knobs and refuses a row whose option and knobs disagree; every row replayed on its library mock with its knob words before the run), health fill and triangle with ~/sgxfive-test-rgn4 (t4) after every job, the knobs written as row words (render_bg_layer Y, render_bg_src 0x3e800000) and restored after every job by the kit (session kit, resgx545 d95a264); the 64 x 64 one-triangle render of E590 (triangle 0xff00ff00, 1062 pixels; the 3034 background pixels scored are those of E590's kept control b66f1-control-1, gen/bgmask.txt), the layer's source a 64 x 64 RGBA8888 buffer at 0x3e800000 whose texel (x, y) is ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x, sampled by the copy's primary (asm/transfer/pds_prim_1src.s, DOUTI0 0x40012001) and use_copy, one attribute row (bgobj_words[1] 0x30001); frozen before the first job (FROZEN.sha256 49b19929..., PREDICTIONS.sha256 28927935..., FROZEN.commits pinning the kit and every input at resgx545 d95a264 and resgx545-data 2d666bfa): the model gen/bgl_model.py (the plane through three vertex values at the pixel centre (x + 0.5, y + 0.5), texel (floor(64 u), floor(64 v)) nearest; a pixel within 1/64 texel of a texel edge or outside [0, 1) not predicted) and every texel map as a sha256 in predictions/; scored by the frozen score/score.py (a texel map right at <= 1 % of its predicted pixels wrong, wrong above 10 %); at the fold the scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh); jobs as E971's with --kpoke-render 1:bg:15 to 22 (bg:17 to 22 only with the knob on at the poke's write); the moves: TL y and x to -16, TR y to +16, TR x to 80, BL y to 80, BL x to -16, words 19 and 22 to 0x1000; the flips: TL y and x bit 20 (to -4096), TR y bit 8 (+1), TR x and BL y bit 15 (192), BL x bit 8 (+1), words 19 and 22 bit 31; two-word: TL (-16, -16), TR x 80 with BL y 80, TL x -16 with TR x 80, TL y -16 with BL y 80; H-VPLANE and H-VBOX frozen as texel maps"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-k1:out/20261113-083450/s2/", "render-closing-r9-k1:fold/", "vectors-closing-r9-k1-pixels"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++
**What ran.** E590 found that no vertex word of the layerless object changes a 64 x 64 render:
the whole box gets the background. With a layer the plane needs anchor points; the plan froze two
rivals, the vertices words 15 to 22 give (E590's decoding) and the fixed render box. Stage s2 poked
each vertex word with an outward move of 16 pixels where one word can make it and with one bit flip,
then four two-word moves.

**Frozen verdict (as printed).** `s2: H-VBOX: the plane is anchored at the render box, whatever
words 15-22 say is not supported: 4 held, 16 FAILED, 0 cannot tell of 20`; `heldout H-VPLANE: 20
held, 0 FAILED, 0 cannot tell of 20`.

**Results [HW].** In the 16 rows that move a vertex H-VBOX's identity texels hold at 9 to 1366 of
3034 pixels; H-VPLANE's texels hold at every pixel it predicts (1917 to 3034 a row). The four rows
on words 19 and 22 give the identity image, as both rivals say. In all 20 rows every background
pixel is a texel and the triangle keeps its 1062 pixels.

**What it shows.** [HW] The layer's coordinates are interpolated over the triangle the vertex words
give, decoded as E590 decoded them [HW now for the decoding's three vertices]: TL in words 15 and
16, TR in 17 and 18, BL in 20 and 21, words 19 and 22 unread in these rows; the coverage of the
render box does not follow them (E590's reading, with a layer too). So a render's layered background
evaluates the transfer copy's plane (xfer.rs) off the target's rectangle as well.

**What it does not show.** Degenerate or flipped triangles, vertices far outside the box beyond the
two -4096 flips, words 19 and 22 at other values, coverage in another ISP_BGOBJVALS.
