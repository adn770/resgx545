+++
id = "E971"
claim = "R9-k1 stage s1 (Q190; 44 jobs, the layered 64 x 64 render with kernel pokes of the object's words 3 to 8, 1 to 3 words a job at k/8 values, 14 fit and 30 held out drawn with the seed r9-k1 after the model was frozen, each read through the texel of every background pixel; no fault): the words are (u, v) of the vertices TL, TR and BL in that order and the pixel samples the plane through them at its centre (H-VM + H-AFF: right on 30 of 30 held-out rows and 14 of 14 fit rows, every predicted pixel the predicted texel), where the coordinates read component by component (H-LM), u and v exchanged (H-SWAP), the poke not read (H-NOREAD), one texel (H-NONE) and the 17-word layout (H-17) are wrong on 29, 30, 30, 30 and 30 held-out rows; every poked word reads back in the object after the job; frozen verdict 'H-VM + H-AFF: words 3-8 are (u, v) of TL, TR, BL, the plane at the pixel centre (30 of 30 rows decided)'"
unit = "isp"
method = "R9-k1 (render/closing-r9-k1) of the question-closing pass, round 9 (decisions K-1 to K-6 (a) of closing9/DECISIONS-R9.md; plan closing9/k1/exp-k1-r9.md), dataset render-closing-r9-k1, on the laptop, 2026-11-13, one attempt out/20261113-083450 (lead log out/run-r9k.log; no stop, no lead decision; s1n's gate shut as frozen, H-NONE failed at c-rawu and c-rawv), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74: debugfs render_bg_layer and render_bg_src, bg kernel pokes to word 22 with the layer; fafea977 builds the 23-dword one-layer object from the tag), stock firmware, tool ~/sgxfive-test-t9 (t9, sha256 7a28be39..., built from resgx545 97447b04 by lead/build_tool9.sh, FROZEN.commits' built line; it reads both knobs and refuses a row whose option and knobs disagree; every row replayed on its library mock with its knob words before the run), health fill and triangle with ~/sgxfive-test-rgn4 (t4) after every job, the knobs written as row words (render_bg_layer Y, render_bg_src 0x3e800000) and restored after every job by the kit (session kit, resgx545 d95a264); the 64 x 64 one-triangle render of E590 (triangle 0xff00ff00, 1062 pixels; the 3034 background pixels scored are those of E590's kept control b66f1-control-1, gen/bgmask.txt), the layer's source a 64 x 64 RGBA8888 buffer at 0x3e800000 whose texel (x, y) is ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x, sampled by the copy's primary (asm/transfer/pds_prim_1src.s, DOUTI0 0x40012001) and use_copy, one attribute row (bgobj_words[1] 0x30001); frozen before the first job (FROZEN.sha256 49b19929..., PREDICTIONS.sha256 28927935..., FROZEN.commits pinning the kit and every input at resgx545 d95a264 and resgx545-data 2d666bfa): the model gen/bgl_model.py (the plane through three vertex values at the pixel centre (x + 0.5, y + 0.5), texel (floor(64 u), floor(64 v)) nearest; a pixel within 1/64 texel of a texel edge or outside [0, 1) not predicted) and every texel map as a sha256 in predictions/; scored by the frozen score/score.py (a texel map right at <= 1 % of its predicted pixels wrong, wrong above 10 %); at the fold the scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh); jobs `tri --bg-layer --pixels --keep-going --dump-render $W --kpoke-render 1:bg:N=V` (`expectdiff`: rc 1 with `job: ok` and a diff line is a reading); fit: words 3 to 8 at 0.5 and at 0.25 one at a time, (3, 4) at 0.25, (5, 8) at 0.75; held out: 30 pokes kept when H-VM predicts at least 40 % of the scored pixels and differs from H-NOREAD on at least 20 %; gate of s2 and s3: H-VM right on >= 28 of 30 held out and every rival wrong on >= 3 (opened). L-RAW rows with pokes (plan section 3) were not run: the kit forbids probe's --kpoke, so every poked row reads texels"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-k1:out/20261113-083450/s1/", "render-closing-r9-k1:fold/", "vectors-closing-r9-k1-pixels"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++
**What ran.** E970 showed the layered object built and its identity plane sampled. Stage s1 poked
the coordinate words one, two or three at a time to multiples of 1/8 and read every background
pixel's texel, which names the (floor(64 u), floor(64 v)) the pixel sampled. The 14 fit rows moved
one word at a time; the 30 held-out rows were drawn after the model and its rivals were frozen.

**Frozen verdict (as printed).** `s1: H-VM + H-AFF: words 3-8 are (u, v) of TL, TR, BL, the plane at
the pixel centre (30 of 30 rows decided)`; tallies `heldout H-VM: 30 held, 0 FAILED`, `H-LM: 0 held,
29 FAILED, 1 cannot tell`, `H-SWAP`, `H-NOREAD`, `H-NONE` and `H-17: 0 held, 30 FAILED`; `fit H-VM:
14
held, 0 FAILED`. Every control of s0t and s0p passed.

**Results [HW].** In all 44 jobs every pixel H-VM predicts (1398 to 3034 of 3034 a job, the rest at
a texel edge or outside [0, 1)) is the predicted texel, and every poked word reads back after the
job (0x463000 + 4 N of the dump). The pixels outside [0, 1) are E974.

**What it shows.** [HW] In a render's one-layer background object words 3 to 8 are u0, v0, u1, v1,
u2, v2 of the vertices top-left, top-right and bottom-left, vertex by vertex as in a copy's object
(E209), and the attribute is the plane through them evaluated at the pixel centre, exact to the
texel at every pixel predicted: the render reads all six words (Q190's clause), which E590 could
not show for the layerless object. With E970 the layer's coordinates reach the shader as a copy's
do.

**What it does not show.** Values outside [0, 1] at the vertices, coordinates that are not finite,
the iteration's arithmetic below a texel (no L-RAW row was poked), perspective, more than one layer,
other target sizes.
