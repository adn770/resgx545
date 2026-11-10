+++
id = "E762"
claim = "S3's control a4 (tri --tri-full at 320 x 400, CR_TE_AA 0x20000000, mode 2 with E507's sample words, in a render context made for 544 x 400) completed and stored the triangle colour in all but 28 of 128000 pixels, the first wrong one at (304, 128) holding the clear colour 0xff203040; E727's region model, unchanged and run after the session, predicts exactly 28 background pixels with the first at (304, 128) (7 in each of the 32 x 16 tiles (9, 8), (7, 13), (5, 18), (3, 23), at their top-left corners), with the TA's own per-tile primitive masks as well as with the model's; the frozen prediction (diff 0) did not use the model, so the control's failure is a design error of S3, not a hardware fault, a layout effect or a scorer error [infer, post hoc]"
unit = "isp"
method = "S3 stage s3-a-safe of the question-closing pass, attempt 20261110-003114 (paths relative to closing/s3/ of the scratch area, to become render-closing-s3), 2026-11-10 00:31 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1 (sha256 d776afbcb9f26a3fccc8dc6be5fa513f8843a0b2185e78c66d2c4737ade0714e): tri --tri-full --keep-going --wait-ms 20000 --width 320 --height 400 --max-width 544 --max-height 400 --poke cmd:1=0x20000000 --poke cmd:10=0xeaa26e26 --poke cmd:13=0x80000002 --poke cmd:16=0xeaa26e26 --dump-render; predictions/s3-a.tsv frozen 2026-11-09 23:11 (PREDICTIONS.sha256 verified); frozen score/score_s3.py s3-a-safe re-run on the kept files (a4 control: FAIL: class fail rc 1; diff 28 of 128000). Post hoc, not frozen: analysis/a4_model.py and analysis/a4_model_dumpmasks.py import resgx545-data texture/p1141/recompute/msaa_model.py (E727's model) read-only and decode the kept param and TA data dumps (region headers, control-stream masks, the object's vertices)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s3:out/20261110-003114/s3-a-safe/"]
terms = ["CR_TE_AA", "CR_ISP_MSAA", "CSTREAM.PRIM_TILES", "REGION_HDR.POS"]
+++
**What ran.** a4 was S3's first job and the control of pixel A (the TA-array question, answered by
E788): a 4x-free setting (TE 0x20,
bit 29 alone, one region-header array) at the size of the decisive job a5, frozen to complete with
`diff: 0 of 128000`, the echo `targets up to 544x400`, a TA data dump of 0xa000 bytes and one array.
It carried no `expectdiff`, so a wrong image stops the stage (runner exit 4).

**Results [HW].** rc 1, `job: ok`, `diff: 28 of 128000 pixels, first (304, 128) 0xff203040 expected
0xff00ff00`, `127972 triangle, 28 background, 0 other; wrong 28 inside, 0 outside, 0 at edges`,
the echo `render context for targets up to 544x400`, dumps of 4603904 and 40960 (0xa000) bytes, no
kernel-log line of the job (dmesg slice empty), snap 0 clear, health triangles before and after
diff 0. The stage stopped there (a1, a2, a3 did not run), and the gate of s3-a-fault stayed closed
in the later attempts (a5, a6 did not run).

**Frozen verdict.** a4 control FAIL (diff 28); s3-a-safe "cannot tell"; the TA-array question
(answered by E788)
"cannot tell (a control failed: a4 False, a6 False)" (a6 never ran).

**Post hoc, read after the run [infer, not held out, not frozen].**
E727's model (2026-11-09, scored 17 of 17 on held-out
images) says that in mode 2 a stored 32 x 16 tile takes each pixel from a sample of the source
region at half resolution, the left half of the tile through the region's left 16 x 16 tile mask
and the right half through the right one. With `--tri-full` the TA clips the triangle to a quad of
(0, 0) to (400, 500) (the four vertices decoded from the object: fields 0x100000, 0x119000,
0x11f400, z 0.5) split along (400, 0) to (0, 500). In the four tiles where that diagonal leaves the
right tile's mask with the lower primitive only while the right half's samples (source x 8 to 15
of the region) lie on the upper primitive, 7 pixels per tile are drawn by no listed primitive. The
model gives 28, first (304, 128), and 0 at TE 0xe0 at this size; with the masks read from the dump
instead of the model's overlap test the same 28 (the two mask sets are equal in 250 of 250
regions). The tool prints only the count and the first pixel, so the other 27 positions are the
model's, not a measurement. The same model gives 30 background pixels for `--tri-full` at 256 x
160 and TE 0x20, and 0 at 64 x 64 and 320 x 128.

**What it shows [infer, post hoc].** The image a4 stored is the one the landed region model
predicts (count and first
pixel); the 544 x 400 maximum plays no part in it (the model and the masks know only the target).
The frozen "diff 0" took E728's 64 x 64 TE 0x20 control (diff 0) as the rule, which the model
also gives at 64 x 64, and missed that at 320 x 400 the full-target quad's diagonal crosses tiles
where the region model leaves pixels empty. The control failed as designed; its failure says
nothing about 4x layouts.

**Not shown.** The other 27 pixel positions (the image was not kept); a 320 x 400 TE 0x20 job in a
context made for 320 x 400 (the maximum's effect is read from the model, not compared); anything
about f.
