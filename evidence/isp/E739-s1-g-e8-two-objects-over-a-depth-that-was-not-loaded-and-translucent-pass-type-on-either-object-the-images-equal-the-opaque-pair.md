+++
id = "E739"
claim = "Two objects over a depth buffer filled with 0.25 under the ZLS control word 0x0017100e did not test a loaded depth: that word has bit 1 and not bit 14, which E664 needs both of for the load, and the one-object control drew its whole triangle under the compare less (4284 green pixels, the tool's own check exact), so the frozen verdict is cannot tell; read after the run, the drawn mask of all 8 jobs is the frozen model's with the depth starting at 1.0 (0 pixels differ), and both objects of a two-render scene are drawn in the closing render's colour; separately, ISP pass type 1 (bits 27:25 of ISP word 0) on the second, the first or neither of two overlapping objects gives pixel-identical images to the opaque pair at both depth orders (6 of 6 jobs, controls passed), and the frozen verdict is that depth order and pass order both fit and list order does not"
unit = "isp"
method = "S1 stages (paths relative to render/closing-s1/ of the dataset) g-e8 (8 jobs: tri --width 128 --height 128 -n 1 or -n 2 --geometry 1 --move 2:32,16 or 2:-16,24 --tri-z 0.2,0.5,0.8 --depth --depth-ctl 0x0017100e --depth-fill 0x3e800000 --depth-dump --dump-render --keep-going --poke blk:1=0x00400200 (less) or 0x00000200 (never) --pixels) and g-e8b (6 jobs: probe --tri pixel --vertices 6 --obj2 3 --obj2-pixel pix-red.bin, block word 1 = 0x00400200 or 0x02400200 per object, object 2's word 10 = 0.25 or 0.75), a debugfs reset before each job, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage; scored by the frozen score/score_s1.py (out/score-g-e8.txt, out/score-g-e8b.txt); the depth histogram, the model with the depth at 1.0 and the image hashes by analysis/scripts/geo_e8_depth.py and geo_e8_union.py, written after the run; a first g-e8 run stopped at its second job (a control without the runner's expected-diff knob) and repeats the two controls with identical images (out/g-e8.run1-stopped)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/g-e8/", "render-closing-s1:out/g-e8b/"]
terms = ["CR_ISP_ZLSCTL", "ISP0.PASS_TYPE"]
+++
**What ran.** E8a wanted the first dumps of two objects over a loaded depth for the simulator's
ISP (frozen model: list order, compare less or never against 0.25). The one-object jobs were the
controls (E664 and E665's patterns). E8b put two overlapping objects (green first, red second) at
depth 0.5 and 0.25 or 0.75, with pass type 1 on the second, the first or neither, under three
hypotheses: list order (HL), depth order (HD), translucent after opaque (HP).

**Frozen verdicts.** g-e8: cannot tell: one-object controls void or not equal to the model
(o1-less-ctl 4224 pixels differ). g-e8b: controls pass; HD-depth-order and HP-pass-order are
consistent with all six jobs.

**Why g-e8's control failed: the design [HW for the image and the dump].** The control word
0x0017100e sets bit 1 and not bit 14. With less, the one-object job drew all 4284 pixels of its
triangle (the frozen model expected only those nearer than 0.25); the stored depth dump (32768
dwords) holds the fill 0.25 in 23552 dwords, 1.0 in 6348 and 2868 dwords of 836 other values; the
dump alone does not say which dwords belong to which pixel. This is E664's "without bits 1 and 14
the pass starts from the clear value 1.0".

**Post hoc [infer].** With the frozen model's code and the start depth 1.0, the drawn and undrawn
pixels match all 8 jobs (0 differ, the two-object jobs included). In the two-object jobs every drawn
pixel is red and the background is the closing render's: the tool writes each render's pixel
programs into the same page of the context (render.c memsets and refills it per render; the colour
alternates by render index), so the geometry-only kick's object is shaded by the closing render's
program. List order cannot be read from colour with this tool; a load needs bit 14.

**g-e8b [HW].** Near: red 1098, green 0; far: green 1062, red 36, in all three variants. The images
of the translucent jobs are byte-identical to the opaque controls'. HL (the second object wins at
any depth) is refuted by the far jobs. HD and HP predicted the same winner in every job, so the
table could not separate them, and "pass type 1 changes nothing here", which no hypothesis stated,
fits as well (post hoc).

**Not shown.** Any loaded-depth behaviour with two objects; the translucent pass's order or blend.
