+++
id = "E970"
claim = "R9-k1 stages s0t and s0p (Q190; the 64 x 64 one-triangle render with debugfs render_bg_layer on and render_bg_src at a mapped 64 x 64 source, 7 controls, no fault): the render details' background tag says one layer (rd:18 bits 30:25 = 1) and the object after the job holds the kernel's one-layer words 3 to 10 (0, 0, 1.0, 0, 0, 1.0, 0, 0x202; H-BUILT); with the copy's primary every one of the 3034 background pixels is its own source texel (H-TEX, twice, and with word 5 poked to its own 1.0: c-noop); with a primary whose douti reads coordinate set 1 with two components (DOUTI0 0x40400801), pa0 holds (x + 0.5) / 64 and pa1 (y + 0.5) / 64 at 3034 of 3034 within 2^-12 (H-ITER; H-SWAP, H-NONE and H-17 fail, H-LM fails on u); E442's background primary still writes x + 0.5 at 3034 of 3034 with and without the layer (H-POS); the layerless controls keep E590's hash 0x99385a04ee01c585; frozen verdicts 'H-BUILT and H-TEX ... (3 of 3 rows decided)' and 'H-POS and H-ITER ... (4 of 4 rows decided)'"
unit = "isp"
method = "R9-k1 (render/closing-r9-k1) of the question-closing pass, round 9 (decisions K-1 to K-6 (a) of closing9/DECISIONS-R9.md; plan closing9/k1/exp-k1-r9.md), dataset render-closing-r9-k1, on the laptop, 2026-11-13, one attempt out/20261113-083450 (lead log out/run-r9k.log; no stop, no lead decision; s1n's gate shut as frozen, H-NONE failed at c-rawu and c-rawv), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74: debugfs render_bg_layer and render_bg_src, bg kernel pokes to word 22 with the layer; fafea977 builds the 23-dword one-layer object from the tag), stock firmware, tool ~/sgxfive-test-t9 (t9, sha256 7a28be39..., built from resgx545 97447b04 by lead/build_tool9.sh, FROZEN.commits' built line; it reads both knobs and refuses a row whose option and knobs disagree; every row replayed on its library mock with its knob words before the run), health fill and triangle with ~/sgxfive-test-rgn4 (t4) after every job, the knobs written as row words (render_bg_layer Y, render_bg_src 0x3e800000) and restored after every job by the kit (session kit, resgx545 d95a264); the 64 x 64 one-triangle render of E590 (triangle 0xff00ff00, 1062 pixels; the 3034 background pixels scored are those of E590's kept control b66f1-control-1, gen/bgmask.txt), the layer's source a 64 x 64 RGBA8888 buffer at 0x3e800000 whose texel (x, y) is ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x, sampled by the copy's primary (asm/transfer/pds_prim_1src.s, DOUTI0 0x40012001) and use_copy, one attribute row (bgobj_words[1] 0x30001); frozen before the first job (FROZEN.sha256 49b19929..., PREDICTIONS.sha256 28927935..., FROZEN.commits pinning the kit and every input at resgx545 d95a264 and resgx545-data 2d666bfa): the model gen/bgl_model.py (the plane through three vertex values at the pixel centre (x + 0.5, y + 0.5), texel (floor(64 u), floor(64 v)) nearest; a pixel within 1/64 texel of a texel edge or outside [0, 1) not predicted) and every texel map as a sha256 in predictions/; scored by the frozen score/score.py (a texel map right at <= 1 % of its predicted pixels wrong, wrong above 10 %); at the fold the scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh); jobs: s0t `tri --bg-layer --pixels --keep-going --dump-render $W --words $W` (c-tex, c-noop with --kpoke-render 1:bg:5=0x3f800000) and the layerless `tri` c-off; s0p `probe --tri bgpds:12 --slot bgpixel=pix_pa0|pix_pa1 [--bg-layer] --pixels` of pds_bg_pos.s (POS, E442) and probes/isp/templates/pds_bgl_raw.s (L-RAW: E709's pds_iter_xy with DOUTI0 0x40400801, its control row the premise check of the second component, run/hooks.sh); s4 repeated c-tex and c-off at the end (E971's method)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-k1:out/20261113-083450/s0t/", "render-closing-r9-k1:out/20261113-083450/s0p/", "render-closing-r9-k1:out/20261113-083450/s4/", "render-closing-r9-k1:fold/", "vectors-closing-r9-k1-pixels"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++
**What ran.** Q190 asked whether a render's background object with a texture layer (the
23-dword form of a transfer copy) reads its coordinate words as a copy does (E209); E590 had shown
no word 3 to 16 of the layerless object read. Module B60AB0B4 builds the one-layer object when its
debugfs `render_bg_layer` is on and checks `render_bg_src`; t9 maps a 64 x 64 source of
position-coded texels there and gives the background the copy's primary with one attribute row.
Stage s0t ran the layerless control, the layered image with its words and dump, and the layered
image with word 5 poked to its own value; stage s0p ran E442's position primary without and with
the layer and the raw-coordinate primary with pa0 and pa1 written out. s4 repeated the layered and
the layerless controls at the end of the session.

**Frozen verdict (as printed).** `s0t: H-BUILT and H-TEX: the render's object is the 23-word
one-layer form and its background samples the source's identity texels (3 of 3 rows decided)`;
`s0p: H-POS and H-ITER: the background primary works with the layer, and the layer's coordinate set
iterates u = (x + 0.5) / 64, v = (y + 0.5) / 64 (4 of 4 rows decided)`; `s4: the end controls: the
layer and the layerless render as at the start (2 of 2 rows decided)`.

**Results [HW].** rd:18 of the render details reads the layer count 1 in bits 30:25 after the job
(c-tex, c-tex2), and the object at 0x463000 of the render_param dump holds words 3 to 10 as the
kernel built them. Every background pixel of c-tex, c-noop and c-tex2 is its own texel (3034 of
3034 each; diff 0). With DOUTI0 0x40400801, pa0 is f32((x + 0.5) / 64) and pa1 f32((y + 0.5) / 64)
at 3034 of 3034 pixels within 2^-12 (the rivals: pa0 = (y + 0.5) / 64 34 of 3034, one value 64 of
3034, 0 at 0). E442's primary writes f32(x + 0.5) exactly at 3034 of 3034 with and without the
layer. The layerless c-off and c-off2 give E590's hash, diff 0.

**What it shows.** [HW] In a render the tag's one layer makes the object the copy's 23 words, the
background primary's coordinate set 1 delivers the layer's iterated (u, v), the u in the first
component and the v in the second (DOUTI0 0x40400801, measured until now only on a triangle's
vertex coordinates, E709), and the texture unit samples the copy's source with them: the identity
plane over the render box gives one texel a pixel, as a 1:1 copy does (E048, E209). The position
path of the background primary (E442) is unchanged by the layer. Which words carry the plane is
E971 and E972.

**What it does not show.** Another target size, more than one layer, another ISP_BGOBJVALS than
0x300, a source that is not 64 x 64 RGBA8888, and filters other than point; what the three PDS
words mean (E590, E410).
