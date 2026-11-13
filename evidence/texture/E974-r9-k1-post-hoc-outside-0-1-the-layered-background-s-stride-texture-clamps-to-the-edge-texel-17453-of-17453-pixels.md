+++
id = "E974"
claim = "R9-k1 stages s1 and s2, read post hoc at the fold (not frozen): at every background pixel whose layer coordinate lies outside [0, 1) under the plane that held (E971, E972), 1/64 texel off a texel edge, the pixel is the clamped texel (min(max(floor(64 u), 0), 63), the same for v) at 17453 of 17453 pixels (16367 in s1, 1086 in s2) and the repeated texel (mod 64) at none, as sgx-sim's rule for a stride texture (it clamps to the edge)"
unit = "texture"
method = "R9-k1 (render/closing-r9-k1) of the question-closing pass, round 9 (decisions K-1 to K-6 (a) of closing9/DECISIONS-R9.md; plan closing9/k1/exp-k1-r9.md), dataset render-closing-r9-k1, on the laptop, 2026-11-13, one attempt out/20261113-083450 (lead log out/run-r9k.log; no stop, no lead decision; s1n's gate shut as frozen, H-NONE failed at c-rawu and c-rawv), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74: debugfs render_bg_layer and render_bg_src, bg kernel pokes to word 22 with the layer; fafea977 builds the 23-dword one-layer object from the tag), stock firmware, tool ~/sgxfive-test-t9 (t9, sha256 7a28be39..., built from resgx545 97447b04 by lead/build_tool9.sh, FROZEN.commits' built line; it reads both knobs and refuses a row whose option and knobs disagree; every row replayed on its library mock with its knob words before the run), health fill and triangle with ~/sgxfive-test-rgn4 (t4) after every job, the knobs written as row words (render_bg_layer Y, render_bg_src 0x3e800000) and restored after every job by the kit (session kit, resgx545 d95a264); the 64 x 64 one-triangle render of E590 (triangle 0xff00ff00, 1062 pixels; the 3034 background pixels scored are those of E590's kept control b66f1-control-1, gen/bgmask.txt), the layer's source a 64 x 64 RGBA8888 buffer at 0x3e800000 whose texel (x, y) is ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x, sampled by the copy's primary (asm/transfer/pds_prim_1src.s, DOUTI0 0x40012001) and use_copy, one attribute row (bgobj_words[1] 0x30001); frozen before the first job (FROZEN.sha256 49b19929..., PREDICTIONS.sha256 28927935..., FROZEN.commits pinning the kit and every input at resgx545 d95a264 and resgx545-data 2d666bfa): the model gen/bgl_model.py (the plane through three vertex values at the pixel centre (x + 0.5, y + 0.5), texel (floor(64 u), floor(64 v)) nearest; a pixel within 1/64 texel of a texel edge or outside [0, 1) not predicted) and every texel map as a sha256 in predictions/; scored by the frozen score/score.py (a texel map right at <= 1 % of its predicted pixels wrong, wrong above 10 %); at the fold the scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh); read by fold/posthoc.py (part 1) on the kept --pixels outputs with gen/bgl_model.py's plane; the copy's texture words are sgxfive_tex_words' (T0 strides and point filter, T1 0xcc000000 | (w - 1) << 12 | (h - 1): NP2_STRIDE_EXT, B8G8R8A8), not varied"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-k1:fold/", "render-closing-r9-k1:out/20261113-083450/s1/", "render-closing-r9-k1:out/20261113-083450/s2/"]
terms = []
+++
**What ran.** E971 and E972 left out of their predictions every pixel whose coordinate the
plane puts outside [0, 1): the plan did not model the address mode. At the fold those pixels were
compared with the two rules.

**Frozen verdict (as printed).** None: a post hoc reading. The frozen predictions did not cover
these pixels.

**Results [HW].** s1: 16367 pixels out of range off the texel edges, clamp 16367, repeat 0 (543 at
an edge not read); s2: 1086, clamp 1086, repeat 0 (2 at an edge).

**What it shows.** [HW, post hoc] The layered background's copy texture, a stride texture,
clamps to its edge texels outside [0, 1), as sgx-sim's tex.rs has stride textures do; the layer adds
no wrap of its own. A frozen held-out check would make it a prediction (the pixels were not chosen
for it).

**What it does not show.** Twiddled or tiled textures under a layer, their address modes, filters
other than point.
