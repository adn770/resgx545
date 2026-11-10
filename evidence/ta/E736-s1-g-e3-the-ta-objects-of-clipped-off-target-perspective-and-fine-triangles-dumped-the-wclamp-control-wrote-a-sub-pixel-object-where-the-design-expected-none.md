+++
id = "E736"
claim = "In 35 dumped 64x64 renders of the TA's object for clipped, perspective, off-target and 1/1024-pixel triangles, the frozen scorer says cannot tell because one control failed: with the state block's WCLAMP word (blk:14) at 1e-3 and w = 1e-5 at every vertex, which E194 saw as a background image and the design read as no object, the TA wrote an object of 4 vertices, a square of 0.96 pixel centred on (32, 32) that covers no pixel centre, with every 1/w word 0x4479ffff (1/1e-3 toward zero); the other five controls reproduced E651's object or E650's no-object; read after the run, per group as the proposal's decision says (the frozen scorer voids all groups when one control fails): triangles wholly beyond z = w or -w leave no object, cut and w-clipped triangles are stored as clipped polygons of 3 to 5 vertices, a viewport offset of 8 or 64 pixels keeps the object and 128, 512 and 1000 leave none, 1/1024-pixel vertices are packed rounded to 1/256, w = 2 and 0.5 store x / w exactly, and with the clamp one ulp above w = 1e-3 the stored 1/w is the clamp's reciprocal"
unit = "ta"
method = "S1 stage g-e3 (35 jobs, 31 conditions; paths relative to render/closing-s1/ of the dataset: probe --tri vtxuse or pixel at 64x64 with --dump-render, the landed mte vertex programs vtx_w.s, vtx_zab.s and vtx_wclip.s with their inputs, --blk 6 (viewport x offset) and --blk 14 (WCLAMP), --tri-v with --tri-unit 8 or 10), a debugfs reset before each, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); tables, programs, predictions and scorer frozen before the stage; scored by the frozen score/score_s1.py g-e3 (out/score-g-e3.txt, the landed pbdump decoder); the per-group reading, the 1/w words and the WCLAMP reading by analysis/scripts/geo_e3_objects.py, written after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/g-e3/"]
terms = ["PB_OBJ.RHW", "WCLAMP", "VIEWPORT.X_OFFSET"]
+++
**What ran.** Seven groups, each led by a control: a w scan (w = 1 control; 2 twice, 0.5, 1e-3,
1e-5), z clipping (flat at 0.99 control; flat at 1.01 and -1.01; sloped cuts at +w and -w, twice
each), w clipping of the second vertex (w = 1 control; 0.1, 0, -0.05, -0.5), viewport x offsets
(1000 control; 8, 64, 128 twice, 512), a 1/1024-pixel grid (1/256 control; three triangles), the
WCLAMP boundary (control: w = 1e-5 under a clamp of 1e-3, E194; clamp equal to w = 1e-3, one ulp
above, one below), and three guard-band scales without predictions.

**Frozen verdict.** cannot tell: controls failed or void: ['e3k-ctl'] (out/score-g-e3.txt).

**The failed control [HW].** e3k-ctl's object is present: 4 vertices at (32.48, 32.48), (31.52,
32.48), (32.48, 31.52), (31.52, 31.52), 1/w 0x4479ffff at all four, depth 0.5. No pixel centre lies
inside it, which is E194's background image. The design had turned E194's image into "no object";
the premise is false at the object level. The other five controls passed: w = 1, flat 0.99 and the
unclipped w-clip job equal E651's object, the offset of 1000 writes no object, the 1/256 triangle
packs as E651.

**Read per group after the run [HW for the dumps, the reading post hoc].** The proposal makes
each group's control gate that group only; the frozen scorer gates the whole stage on any control.
Read per group:
- z clipping: no object for the flat triangles at 1.01 and -1.01 (2 of 2). The cut at +w gives 4
  vertices (2 of 2), the cut at -w gives 3 vertices that are not the original three ((56, 20), (32,
  44), (32, 14); 2 of 2): both are clipped polygons. The frozen scorer counts vertices, so it calls
  the second "HC-orig".
- w clipping: 4, 4, 4 and 5 vertices for w = 0.1, 0, -0.05 and -0.5: clipped polygons.
- viewport offset: an object at 8 and 64, none at 128 (2 of 2), 512 and 1000: as HO-region.
- fine grid: the packed 24-bit values are the 1/1024 coordinates rounded to 1/256 (HF-round); one
  triangle fits both rules, two only rounding.
- w scan: x and y are stored divided by w exactly at w = 2 (2 of 2) and 0.5. At w = 1e-3 and 1e-5
  the triangle is clipped to the guard band (four corners at -16 and 80) and the four 1/w words are
  not all equal (0x4479ffff twice and 0x4479fffd twice; 0x47c35000 three times and 0x47c34fff
  once): every stored vertex is made by the clip, so the frozen per-vertex 1/w rule had no original
  vertex to test.
- WCLAMP [infer]: with the clamp one ulp above w all four 1/w words are 0x4479fffd, the reciprocal
  of the clamp; with the clamp equal to w or one ulp below they are those of w. With the control's
  sub-pixel square, this reads as "w below the clamp is replaced by the clamp", not as removal.
- guard-band scale: 8x gives 5 vertices (two at (80, 80)), 64x and 1024x the 4-vertex square.

None of this is held out: the frozen verdict is cannot tell. A frozen run that confirms needs the
per-group gate in the scorer, the cut scored by vertex identity, 1/w scored on triangles that stay
inside the guard band, and the WCLAMP control predicted from the replace reading.

**Not shown.** The guard band's exact width, the clip's interpolation of 1/w at the made vertices,
and where between 64 and 128 pixels the object disappears.

**Correction 2026-11-10:** Two statements above are refined by S1b's g-e3 (E754). The note that the
w scan's every stored vertex was made by the clip, so that the frozen per-vertex 1/w rule had no
original vertex to test, is answered inside the guard band: with x and y scaled by w (stored x and y
equal the original triangle's) the 1/w word was the float32 reciprocal truncated toward zero at w =
3, 7, 0.003 and 3e-5 (4 of 4, frozen held out, round-to-nearest refuted 4 of 8 checks, the w = 1
control passing). And the WCLAMP reading that the clamp replaces a smaller w by its own value holds
for position and 1/w in 4 of 5 clamp jobs at w = 1e-5 (x and y shrunk by w over the clamp, 1/w =
1/clamp) but is not one rule: the 1/w word was the truncated reciprocal at a clamp of 3e-5, the
rounded one at 3e-4, and the clamp of 1e-3 wrote no object here where this record's control wrote a
0.96 pixel square, so every frozen clamp model was refuted at least once.

**Correction 2026-11-10:** A post hoc reading of this record's viewport-offset cells (e3o-x8, x64, x128
and the others), made before the round 2 runs on data measured before the reading; it is a fit, not
a test. [infer] The viewport's word 6 is an absolute x offset (default 32.0): the window x of a
vertex is X + 32 x_clip, so e3o-x64 put the triangle at x 40 to 88 (straddling the target's edge at
64, with streams in target column 1 only) and e3o-x128 at 104 to 152, which is inside macrotile 0's
128-wide region grid and yet wrote no object. A rule "the object is written when the triangle
overlaps a macrotile of the grid" is therefore refuted on these cells, and a rule of E542's tile
test applied to the target's regions only (low side closed, high side open) fits all five cells;
the offset of the object's disappearance lies for its minimum x in (64, 104]. The "as HO-region"
above stands for the cells, with this reading of what the cells show. Q230's off-target clause
refers to this note; the boundary has not been run.
