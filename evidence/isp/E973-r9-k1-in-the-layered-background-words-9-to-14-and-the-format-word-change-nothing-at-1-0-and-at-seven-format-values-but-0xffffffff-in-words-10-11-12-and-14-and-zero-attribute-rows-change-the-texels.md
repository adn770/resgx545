+++
id = "E973"
claim = "R9-k1 stage s3 (Q066 explore; 21 jobs, the layered 64 x 64 render, no fault): words 9 and 11 to 14 at 1.0, word 9 and word 13 at 0xffffffff, the format word 10 at 0, 0x202, 0x404, 0x101, 0xffff, 0x10000 and 0x80000000, and bgobj_words[1] (render command dword 24) at one and four attribute rows leave every background pixel its own texel (16 of 21 rows, H-FMT0); word 10 at 0xffffffff makes every pixel texel (0, 0) (3034 of 3034, E209's copy picture); word 12 at 0xffffffff makes every v-texel 0 with u unchanged, word 14 at 0xffffffff every u-texel 0 with v unchanged, word 11 at 0xffffffff every u-texel 0 and v at 35 values (1629 pixels at 63); zero attribute rows (0x30000) gives every pixel a texel of the source but its own at 74 of 3034 (143 distinct texels, mostly within 8 columns and 4 rows of its own; H-NOTEX, no texel, wrong); explore rows, frozen verdict 'H-FMT0 (explore): words 9-14 and bgobj_words[1] at 0, 1 or 4 rows change nothing is not supported: 16 held, 5 FAILED, 0 cannot tell of 21'"
unit = "isp"
method = "R9-k1 (render/closing-r9-k1) of the question-closing pass, round 9 (decisions K-1 to K-6 (a) of closing9/DECISIONS-R9.md; plan closing9/k1/exp-k1-r9.md), dataset render-closing-r9-k1, on the laptop, 2026-11-13, one attempt out/20261113-083450 (lead log out/run-r9k.log; no stop, no lead decision; s1n's gate shut as frozen, H-NONE failed at c-rawu and c-rawv), kernel 7.3.0-resgx545, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74: debugfs render_bg_layer and render_bg_src, bg kernel pokes to word 22 with the layer; fafea977 builds the 23-dword one-layer object from the tag), stock firmware, tool ~/sgxfive-test-t9 (t9, sha256 7a28be39..., built from resgx545 97447b04 by lead/build_tool9.sh, FROZEN.commits' built line; it reads both knobs and refuses a row whose option and knobs disagree; every row replayed on its library mock with its knob words before the run), health fill and triangle with ~/sgxfive-test-rgn4 (t4) after every job, the knobs written as row words (render_bg_layer Y, render_bg_src 0x3e800000) and restored after every job by the kit (session kit, resgx545 d95a264); the 64 x 64 one-triangle render of E590 (triangle 0xff00ff00, 1062 pixels; the 3034 background pixels scored are those of E590's kept control b66f1-control-1, gen/bgmask.txt), the layer's source a 64 x 64 RGBA8888 buffer at 0x3e800000 whose texel (x, y) is ((x ^ y ^ 0xa5) & 0xff) << 24 | y << 12 | x, sampled by the copy's primary (asm/transfer/pds_prim_1src.s, DOUTI0 0x40012001) and use_copy, one attribute row (bgobj_words[1] 0x30001); frozen before the first job (FROZEN.sha256 49b19929..., PREDICTIONS.sha256 28927935..., FROZEN.commits pinning the kit and every input at resgx545 d95a264 and resgx545-data 2d666bfa): the model gen/bgl_model.py (the plane through three vertex values at the pixel centre (x + 0.5, y + 0.5), texel (floor(64 u), floor(64 v)) nearest; a pixel within 1/64 texel of a texel edge or outside [0, 1) not predicted) and every texel map as a sha256 in predictions/; scored by the frozen score/score.py (a texel map right at <= 1 % of its predicted pixels wrong, wrong above 10 %); at the fold the scorer re-ran byte-identical on the kept files and every kept file decompresses to the raw sha256 the laptop logged (fold/reproduce.sh); jobs as E971's with --kpoke-render 1:bg:9 to 14 (word 10 at eight values, the others at 1.0 and 0xffffffff), and `--poke cmd:24=V` (the command's bgobj_words[1], which the kernel copies into the object's word 1: it reads back) at 0x30000, 0x30001 and 0x30004; every 0xffffffff row last; the five changed images read post hoc by fold/posthoc.py (texel distributions; not frozen)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-k1:out/20261113-083450/s3/", "render-closing-r9-k1:fold/", "vectors-closing-r9-k1-pixels"]
terms = ["CR_ISP_BGOBJVALS", "hw_render_details.pds_bgnd"]
+++
**What ran.** Q066 asks what the rest of a render's background object is. In a copy the format
word after the coordinates changes nothing over eight values and 0xffffffff breaks the copy (E069,
E209). Stage s3 poked the layered object's words 9 to 14 and the format word, and the command's
attribute-row word, as exploration (frozen: no change, with two named rivals).

**Frozen verdict (as printed).** `s3: H-FMT0 (explore): words 9-14 and bgobj_words[1] at 0, 1 or 4
rows change nothing is not supported: 16 held, 5 FAILED, 0 cannot tell of 21`; `explore H-17: 1
held` (word 10 at 0xffffffff, texel (0, 0) everywhere); `explore H-NOTEX: 0 held, 1 FAILED` (zero
rows).

**Results [HW].** The 16 unchanged rows give the identity texels at 3034 of 3034. Post hoc
(fold/posthoc.py): word 12 = 0xffffffff gives tx = x and ty = 0 at every pixel; word 14 =
0xffffffff tx = 0 and ty = y; word 11 = 0xffffffff tx = 0 everywhere and ty at 35 values; word 10 =
0xffffffff texel (0, 0) at every pixel; word 1 at 0 rows (it reads back 0x30000) a texel at every
pixel, its own at 74, the offsets from it -47 to 46 columns (within 8 at 2651) and -7 to 12 rows
(within 4 at 2958). Every poked word reads back.

**What it shows.** [HW] The format word behaves as a copy's (E069, E209): seven values change
nothing and 0xffffffff collapses the sample to texel (0, 0). Words 9 and 13 change nothing at the
values run; words 11, 12 and 14 change nothing at 1.0 but at 0xffffffff (a NaN) each removes one
coordinate's variation, so they are read [infer: as factors or terms of the iteration, which a
finite value other than 1.0 would show]. One attribute row is enough for the texel (four change
nothing); with none the shader still gets a texel, not its own [infer: another pixel's attribute].

**What it does not show.** What words 11 to 14 hold (only 1.0 and 0xffffffff ran), word 13's and
word 9's role, why zero rows mis-assign texels, the PDS words 0 and 2.
