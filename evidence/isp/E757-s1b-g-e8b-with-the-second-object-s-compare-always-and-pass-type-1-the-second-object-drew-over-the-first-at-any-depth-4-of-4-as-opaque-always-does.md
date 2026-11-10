+++
id = "E757"
claim = "Over two overlapping objects (green first at depth 0.5, red second at 0.25 or 0.75) a second object with the depth compare ALWAYS (ISP word 0 bits 24:22 = 7) and pass type 1 (word 0x03c00200) drew over the first although it was the farther (0.75) in 2 of 2 runs (red 1098 pixels, green 0), and a first object with compare always and pass type 1 under a nearer opaque second (0.25) left the second's colour in 2 of 2 runs (red 1098, green 0); the opaque always control (0x01c00200, second, farther) gave the same image (red 1098), as did both-opaque-less with the second nearer (red 1098) while the second farther lost (green 1062, red 36); the frozen verdict: controls pass; held out: list order and pass type changes nothing (S1 post hoc) consistent with 4 of 4, depth order and pass order refuted in 2 of 4 each; no hypothesis separates list order from pass type changes nothing here"
unit = "isp"
method = "S1b stage g-e8b of the question-closing pass (7 jobs; paths relative to render/closing-s1b/ of the dataset: probe --tri pixel --vertices 6 --obj2 3 --obj2-pixel pix-red.bin over the green program, block word 1 = 0x00400200 (less) on both objects for the controls t-opq-near and t-opq-far with object 2's word 10 = 0.25 or 0.75, 0x01c00200 (opaque always) on the second for o-2-alw-far (0.75), 0x03c00200 (pass type 1, always) on the second for t-2-alw-far (0.75, two runs) and on the first for t-1-alw-far (second less at 0.25, two runs)), a debugfs reset before each job, run 1794266092-21153 on 2026-11-10 00:14 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71, built on the laptop from main with the --index-width and --move changes), regtimeline unchanged; tables, predictions, scorer and runner frozen before the first job of the session (FROZEN.sha256, PREDICTIONS.sha256, TABLES.md; verified before the stage and before scoring) and the verdict printed by the frozen score/score_s1.py g-e8b (out/score-g-e8b.txt, reproduced by running it again on the kept files)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/g-e8b/"]
terms = ["CR_ISP_ZLSCTL", "ISP0.PASS_TYPE"]
+++
**What ran.** E739's two-object table (g-e8b of S1) could not separate depth order (HD) from
translucent-after-opaque (HP): they predicted the same winner in all six jobs, and the translucent
images equalled the opaque ones. S1b made them differ by giving the pass-type-1 object the compare
ALWAYS and putting it where the hypotheses disagree: second and farther (HD: green, the rest red) or
first with an opaque second nearer (HP: green, the rest red). Frozen hypotheses: HL (list order: the
second object wins), HD (depth order), HP (translucent pass after the opaque), HN (pass type changes
nothing, E739's post-hoc reading, so a pass-type-1 job predicts as its opaque twin). Controls: both
opaque, second nearer (red) and farther (green), and the opaque always control o-2-alw-far (red:
an opaque second object with compare always draws although farther).

**Frozen verdict.** controls pass; held out: consistent HL-list-order (4),
HN-pass-type-changes-nothing (S1 post hoc) (4), refuted HD-depth-order (2 of 4), HP-pass-order
(2 of 4); repeat only: consistent none, refuted none (out/score-g-e8b.txt). The four held-out
entries are t-2-alw-far and t-1-alw-far and their replicates; no row of the table was a repeat.

**Results [HW].** The image is 64 x 64, 4096 pixels of which 2998 are the background 0xff203040.
t-opq-near: red 1098; t-opq-far: green 1062, red 36 (S1's two controls: E739's counts); o-2-alw-far:
red 1098, green 0. t-2-alw-far and its replicate: red 1098, green 0. t-1-alw-far and its replicate:
red 1098, green 0. Every job rc 0, class ok, no fault line; the scratch line `scratch at
0x3e00e000 (64 KiB)` in all seven.

**Read from the table [infer].** With the compare always, the second object drew over the first
at depth 0.75 against 0.5 whether it carried pass type 1 or not: the translucent job is the opaque
always job, pixel for pixel in the colour count (red 1098 in both). So pass type 1 changed nothing
in this one pair, and where the second object wins by its compare the depth order of the two does
not decide, which refutes HD for these jobs; HP (the translucent object waits for the opaque one)
is refuted by t-1, where the first object is translucent and the opaque second still won. HL and HN
made the same prediction in all four held-out jobs (HN predicted its opaque twin, which is list
order), so the table does not separate them: "the second object's compare decides, pass type 1 does
nothing" is what survives, and "list order" is true only with the compare always (the opaque far
control with compare less lost, as in E739).

**Caveats.** The winner is the colour with more pixels (score_e8b); it is not a per-pixel model.
The red and the green come from the two pixel programs of the probe, so the image says which
object's shader ran last at a pixel and not what a blend would give; the shader writes opaque colour
(0xffff0000, 0xff00ff00), so a translucent blend is not observed. The first object has pass type
1 in t-1 and the second object in t-2, one position each; compare 7 is the only compare tried with
pass type 1, the translucent object with another compare was not run. The table has one geometry
(the overlap of 1098 pixels) and two depth orders.

**Not shown.** What o0 holds at the start of an opaque pass (Q073's open question: this table
reads colours written by the shader, not the value a shader finds); a translucent shader that
writes alpha; pass types other than 1; two triangles per object; a compare other than always with
pass type 1; the translucent blend.
