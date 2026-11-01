+++
id = "E660"
claim = "A model of the ISP written for the pipeline simulator (sgx-pipe isp, iter, objects, pixel: the exact integer centre test on vertices rounded half up to 1/256 pixel with left and top edges owning ties, the plane through the rounded vertices at the pixel centre) reproduces the colour image of 2752 of 2752 E606 and E607 depth jobs it is asked about, 0 of 14368768 + 11149312 + 6586368 pixels wrong, of which 1566 jobs are the ones the rule was found on (E606's 692 fit cases, E607's 874 fine cases) and 1186 held out (E606's 814 held-out cases and 30 repeat cases, E607's 342 fine2 cases of 422); the 1.0 stored where nothing is covered exactly, the stored depth of every covered pixel of a plane of gradient below 0.03 within E606's stated 3 units of 2^-23 (330844 + 106639 + 201663 pixels, 0 outside; the largest error is 1.9, so the data do not pin the 3 from below), and the iterated clip z of 700 triangles within E606's stated 4 units where its range per root area is below 0.05 (132050 pixels, 0 outside); it refuses what E606 and E607 did not measure, naming the open question: the 80 tiny-edge cases on 256 x 256 targets (Q240), the covered pixels of a plane of gradient 0.03 or more (80665 + 60412 + 26292 pixels, Q200) and the iterated clip x (Q200: its error in the record's own table reaches 23 units, E661). Run through the whole pipeline (the vertex tasks on sgx-sim, the MTE, the TA, the ISP, the pixel programs on sgx-sim, the end-of-tile task and the PBE) from the words the library's builder puts in its five pages, the first triangle reproduces the recorded image hash at the three target sizes E606 ran (64 x 64, 128 x 128, 256 x 128: 3 of 3, with E023's 1062 triangle and 3034 background pixels at 64 x 64; the rule alone gives the hash at all 16 sizes, E662, and the pipeline refuses the 13 outside E606's three) and 92 of 92 built scenes of the 202 sampled (192 E606 depth jobs, every eighth, and 10 E607 fine2 tiny-edge jobs) whose depth the model decides (the image hash and, for the 59 that store a depth by a plane of gradient below 0.03, the depth within 3 units, counted per scene as fitted with depth near; 33 more store only the background); every one of these rests on a fitted rule, so none is reported matched. It refuses 97 of the 202 sampled depth jobs (a depth compare against a plane of gradient 0.03 or more, Q200: the refusal drops the whole image, coverage included, so the replayed sample is skewed to planes of gradient below 0.03 although the coverage of those 97 is not in doubt), 10 (a 256 x 256 target, Q240) and 3 (a triangle with no area: the TA has no record for its winding mark, Q230), and of the 16 first-triangle sizes 2 by the TA (four macrotiles in a row, Q139, Q100, Q086) and 11 by the target size (Q240). It decodes the ISP words only as far as their records go (the unit tests check the model against itself there, see below): a vertex depth outside [0, 1] under a depth compare or write (the clamp of E287, one run), the ISP word 1 gate pairs E232 and E235 did not measure and a pass type 1, 2, 4, 5 or 6 with a pixel shader other than the library's colour write (E065's) refuse under Q241. Of the 2464 triangle-host vectors of the data repository 2281 were rebuilt as scenes (183 not: a kernel poke 159, a job that wrote no pixel 24) and replayed against the image each recorded; this census is a development set (its 71 first-run mismatches were removed by rules and refusals after they showed, so 0 mismatch is a figure after the fixes, not a test on unseen scenes) with 733 content duplicates among the 2281 (1548 distinct: 1508 refused, 39 reproduced, 1 predicted hang): 47 reproduce (fitted; the 39 distinct are the library's triangle with other programs, evidence of plumbing, not of coverage or depth), 1 predicted hang (E102: the record that defined the rule, a reproduction, not a prediction), 0 mismatch, 2233 refused by question, 97.9 percent of the census, 1231 of them at Q094 before the ISP is reached (Q094 1231, Q206 373, Q142 377, Q052 47, Q050 35, Q202 33, Q240 30, Q230 21, Q162 20, Q047 14, Q042 12, Q069 15, Q066 4, Q163 with Q047 4, Q241 4, Q076 with Q003 3, Q199 2, Q070 2, Q139 with Q100 and Q086 2, Q159 with Q160 2, Q163 2), so the census says almost nothing of the ISP itself"
unit = "isp"
method = "offline, no new run: sgx-pipe (crates/sgx-pipe isp.rs, iter.rs, objects.rs, pixel.rs, arith.rs, render.rs, vtx.rs) against the recorded material of the dataset isp-arith-1138 (cases.tsv, cases-fine.tsv, cases-fine2.tsv, the D jobs' output and depth dumps, the I jobs' images: tests/isp_arith.rs, examples/arith_stats.rs), the target-sizes, client-jobs and parameter-buffer runs' image hashes (tests/isp_scenes.rs, the fixture first-triangle.scene.json), the scene vectors of scene-vectors-12-3 (tools/usse-asm/isp_scenes.py first-triangle and arith, the words rebuilt by sgxfive-test --mock probe --tri --emit-scene with the --tri-v and --tri-z options of E606) and the triangle-host vectors of vectors/ (isp_scenes.py inventory, examples/inventory_stats.rs, nothing declared refused, so the census counts every refusal); the scenes' words are rebuilt, not captured, and the pixel program of every probe is the file its vector names; the unit model was written from E606, E607, E465 and E065 before it was run on the images, the three checks of E606 (coverage cell, plane, tolerance) are recomputed independently here from the recorded dumps; the two data tests were seen failing against a mutated tie rule and a floor instead of a half-up rounding, the tolerance sum of two planes at its boundary (5 and 6 units of 3 + 3 refuse, 7 decides) and E606's 3 and 4 are pinned by unit tests, the scene tests against the pixel side switched off; the census mismatches that the first run showed (71, all in vectors whose shader or vertex emits depend on the quad or the emit flags, or whose recorded outcome was a hang) were investigated one by one and became rules or refusals only where a record states them (E104, E111, E113 helper instances; E112 the branch leader; E102 the vertex emits) or by a refusal naming Q052, Q050 and Q230; the replay's tolerance verdicts are near, the coverage rule is the record's fit and reports fitted; the merged tree (the 12.1 and 12.2 folds under the 12.3 commits) was rerun after the review's fixes, the census included"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-arith-1138", "render-target-sizes", "render-client-jobs", "dpm-parameter-buffer", "scene-vectors-12-3"]
terms = ["ISP0.PASS_TYPE", "ISP0.DCMP_MODE", "ISP0.DWRITE_DISABLE", "ISP0.TAGWRITE_DISABLE", "CR_ISP_CTL", "CR_ISP_ZLSCTL"]
+++

**What ran.** The ISP model is five functions of sgx-pipe: `Tri::covers` (the pixel centre against
the three edges in integers of 1/256 pixel, the winding normalised, a centre on an edge owned by a
left or top edge), `Tri::depth_at` (the plane through the vertices, exact), `isp::resolve_tile` (the
objects of a tile in list order, the compare of ISP word 0 against the stored depth, the writes of
bits 20 and 21), `iter::at_centre` (the plane through an attribute) and `pixel::image` (the pixel
programs of the winning object and of the background object per pixel on sgx-sim, the pixel-event
program, the end-of-tile task and the PBE). The objects, the region headers and the control streams
are read back from what the TA model wrote (E650), not from the scene.

**Results.** [HW] *The images.* Every image of E606's 1536 depth jobs (14368768 pixels, the number
the record gives), of E607's 874 fine and 342 of 422 held-out jobs (the 80 tiny-edge jobs are on 256
x 256 targets, outside the sizes run: refused) is reproduced pixel for pixel by the integer test on
the vertices rounded half up to 1/256 pixel (the fine sets' vertices are in 1/4096 and 1/65536
pixel): 0 wrong pixels in 14368768 + 11149312 + 6586368. The 2752 are not 2752 independent
confirmations: the rule was found on E606's 692 fit cases and E607's 874 fine cases (the half-up
rounding on the fine ones), 1566 jobs; the held-out ones are E606's 814 and 30 repeats and E607's
342 fine2 jobs, 1186. The depth stored where nothing is covered is 1.0 to the bit in every job. The
depth of the covered pixels of a plane of gradient |dz/dx| + |dz/dy| below 0.03 (the gradient of
E606's table, per pixel: 330075 pixels of the fit and held-out jobs and 769 of the repeats, the
record's 330075 recomputed) is within 3 units of 2^-23 in all 330844 + 106639 + 201663 pixels; the
largest error is E606's own 1.9, so the data do not pin the 3 from below (2 would pass; the 3 is
the record's stated tolerance). [HW] *The iteration.* pa0 of the 700 iteration jobs is within 4
units of the plane through the clip z where its range per root area is below 0.05 (132050 pixels in
116 triangles, the record's table), 0 outside; the pixels of the poorer triangles (19090) are not
compared. The clip x has no tolerance to check against (E661). [HW] *The pipeline.* The scenes are
the library's pages rebuilt offline. At 64 x 64 the chain gives E023's 1062 and 3034, and the image
hash 0x99385a04ee01c585 of E148's first render; 128 x 128 and 256 x 128 give their recorded hashes
too. The model admits these three targets only: E606 ran no other (E662 shows the rule alone gives
the hash of the library's triangle at 13 more sizes, which is one triangle and not a record of the
rule there). A scene whose image is expected and whose pixel side refuses is a refusal, not a
mismatch; a recorded hang is the whole job's. The command's pixel-side words are the library's
(E278's multisample word, the ISP control word's bits other than 5:0, the background depth, the
pixel-event program and its data) or the scene is refused by question. The per-scene result keeps
the depth tolerance visible: a fitted image whose depth is only within 3 units is counted apart
(`Fitted (depth near)`, 59 scenes) in the test's output, so the combined verdict (fitted either
way) does not hide it. [HW] *The census.* The 2281 rebuilt triangle-host vectors are of 717 files;
41 of them carry a saved parameter buffer, which this replay does not read (E650 does); every one
has the recorded image of its run. 733 of the 2281
are content duplicates of another scene (the same words and expectation; files under `followup/`
repeat vectors listed elsewhere), so there are 1548 distinct scenes: 1508 refused, 39 reproduced
and 1 predicted hang. The 47 that reproduce (39 distinct) are the library's triangle with other
pixel or vertex programs: they add evidence that the plumbing (the vertex tasks, the TA, the pixel
programs, the PBE) agrees with the hardware, not of coverage or depth. The refusals by question are
97.9 percent of the census (2233 of 2281) and mostly upstream of the ISP: 1231 at a vertex task
word the library does not write (Q094, which holds every five-copy depth scene, every
punch-through and every translucent one, the iterated depth-test vectors among them), so those
units have no whole-pipeline evidence in 12.3; the rest the end-of-tile or pixel-event programs a
probe replaced (Q206), CR_TE_AA bits 30 and 31 (Q142), a command word the library never changes
(Q202 33). What the pixel side adds: 47 vectors whose pixel shader writes without .skipinv over a
quad the triangle covers in part (Q052: E104, E111 and E113 say the helper instances' o0 lands in
some runs only), 35 with a branch or a vertex program the model does not run (Q050: E112 says the
branch is taken as one instance of the quad), 30 with a target outside E606's three (Q240) and 4 at
the ISP words (Q241: a pass type with another shader, bits 15 to 18). Of the 202 sampled depth jobs,
97 refuse at Q200 and so lose their coverage check although the image is certain (the triangle is
far from the 1.0 background, 145 to 366 units by any bound seen): the refusal is conservative, and
the replayed sample is skewed to planes of gradient below 0.03. The one predicted hang is the E102
probe itself (a rule generalised from that single vertex program, so a reproduction of the record
that defined it; the neighbouring case, neither emit with .twopart, refuses at Q230).

**Against the first run.** The first census of the pixel side gave 71 mismatches in 2240 scenes: 40
were pixel shaders whose writes lack .skipinv (E104, E111, E113), 26 recorded hangs and faults that
the comparer judged by the job's outcome without the pixel side's refusal (it now judges a recorded
hang or fault by it), 3 a branch by quad position (E112) and 2 the vertex emits of E102 (without
.twopart on emitvcbvtx the job hangs or draws nothing); each became a refusal or a rule that a
record states, and none a fit. The counts in the claim are of the rebuilt scenes after that, 2281 of
them (the 41 that carry a saved parameter buffer were added by a later fix of the scene builder,
which first excluded every job with a dump option). The census is therefore a development set: the
rules and refusals were chosen after the mismatches showed, so the 0 mismatch is a post-fix figure
and not a test on unseen scenes.

**What it does not show.** Any image the model refuses; the depth of a plane of gradient 0.03 or
more (E606: up to 145 units); the clip x; multisampling, lines, points and perspective (Q202); a
target other than 64 x 64, 128 x 128 and 256 x 128 (Q240; E662 is one triangle); negative
coordinates with a sub-grid fraction (Q199); the stencil, the translucent and punch-through
passes, the iterated attributes in a scene (the TA model writes position-only objects: Q094); the
pixel shader of a quad (the model runs one instance per pixel); that the rounded vertices are the
ISP's rather than the TA's (the TA model refuses a coordinate off the grid: Q230); the depth clamp
beyond E287's one run (a vertex depth outside [0, 1] refuses, Q241). [infer] The decode of the ISP
words rests on the records as follows and no replay exercises it: the six `isp/depth-test`
vectors and the 169 punch-through vectors of the census are all refused at Q094, so the unit tests
of the compares 0, 1, 4 and 7, the write bits, the tag write and the gate check the model against
itself. The ISP words decode as 3d.md 11.1 says for those compares, the write bits and pass types
3 and 7 removing the object (E065, E282); the gate of ISP word 1 bits 31:26 against CR_ISP_CTL
bits 5:0 only for the pairs E232 (the library's gate 0 at 0 to 8, 16, 32, 63) and E235 (gate 0 and
63 at 1 and 63) measured, read as "removed when the gate is below the threshold"; the compares 2,
3, 5 and 6, bits 15 to 18, a visibility test, the polygon offset, a pass other than 0 for several
triangles, a pass type 1, 2, 4, 5 or 6 with a shader other than the library's colour write (E065's)
and a stencil word refuse (Q241, Q073, Q032, Q071; the state block of a stencil job is refused by
the MTE model first, Q069).
