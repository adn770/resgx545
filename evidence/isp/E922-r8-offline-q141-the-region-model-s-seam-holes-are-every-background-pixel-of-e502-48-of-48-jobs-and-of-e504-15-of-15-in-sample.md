+++
id = "E922"
claim = "Round 8 offline (Q141; no run, in sample): the landed region model (resgx545-data texture/p1141/recompute/msaa_model.py, sha256 1c0e8205..., E727's freeze, unchanged) with its two-halves rule gives the background pixels of E502's identity jobs as a set, exactly, in 48 of 48 jobs (the 8 with 9 to 192 holes, the 40 with none; with the halves rule off, 40 of 48 and 0 of the 8), and of E504's tri-full images in the 15 of 21 jobs outside E829's empty case (the 136 at (32, 32) of mode 0 at 0xe0000000 among them); each hole is a staircase at a tile's top-left cut by the diagonal of the TA's clipped quad, where a stored half takes only its half-region's list and that list lacks the second triangle [infer]; the seam was set on E502, so this is a fit, and the out-of-sample evidence is E727 and E762 alone"
unit = "isp"
method = "Offline, no run (round 8, decisions R8-1 a and R8-3 a; ranking closing8/rank/rank-round8.md finding 2 and R8-1). The ranking's closing8/rank/q141_model.py imports msaa_model.py read-only by path and compares, for each of the 48 jobs of resgx545-data isp/msaa-ident (E502), the pixels holding the clear colour 0xff203040 in the kept x dump with the target pixels the model's predict() stores nothing in, for tri_full(W, H) (k = 1.25) with halves on and off; closing8/rank/q141_e504.py does the same on the 21 kept tri-full images of isp/msaa-te-dumps (E504), with the bit-29 gate on and off; closing8/rank/q141_pat.py prints each hole's shape (run with the arguments A-m1-te60-64x64 C-m1-tee0-128x64 C-m1-te00-96x80 C-m2-te00-96x80). The model file was checked by sha256 (1c0e8205...) and is unchanged since E727's freeze. Not held out: tri_full's seam k = 1.25 was chosen on these 48 jobs when the model was written (texture/p1141/out/msaa_rescore.txt, 2026-11-09: exact 48 of 48 at 1.25, 20 to 29 at 1.20 to 1.30), and E504's 136 pixels were known (Q141's own text) before the model existed, though no scorer had read E504's images with it; the shape was read after the hypothesis. Standard library only; the three scripts re-run in this fold from their published copies (cited/closing8/rank/) with the repository's .venv: output byte-identical to the kept .out files. The R8-1 prediction table for r8-geo was generated in this fold from the same model, unchanged (closing8/offline/r8-1/q141_r8pred.py, its outputs and q141_r8pred.sha256)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["isp-msaa-ident", "isp-msaa-te-dumps", "texture-isp-msaa-verification-1141", "cited-scratch:closing8/rank/", "cited-scratch:closing8/offline/r8-1/"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++
**What was done.** Q141 asked why a few pixels stay background when `tri --tri-full` covers a
multisampled target: 455 pixels in 13 tiles of 8 of E502's 48 identity jobs, and 136 pixels at (32,
32) in E504's mode 0 job at `CR_TE_AA` 0xe0000000. E727's region model (written from E503's window
rule for 11.39, frozen there, scored 17 of 17 held out on other triangles) draws a stored 32 x 16
tile from the last region walked in it, its left half through the left half-region's primitive list
and its right half through the right one's. The tool's `--tri-full` triangle, (0, 0), (3W, 0), (0,
3H), reaches the 3D as the quad (0, 0) to (1.25 W, 1.25 H) split along (1.25 W, 0) to (0, 1.25 H)
(E762 decoded it from the object), which is the model's `tri_full(W, H)`. The ranking scored the
model on every kept image of E502 and E504; this fold re-ran the scripts from their published copies
(byte-identical) and checked the model's hash.

**Results [HW, in sample].** E502 (isp/msaa-ident, 48 jobs): with the halves rule the model's empty
pixels equal the hardware's background pixels as a set in 48 of 48 jobs: A-m1-te60-64x64 64,
B-m1-te60-128x128 192, C-m1-tee0-128x64 108, C-m1-te00-96x80 and C-m1-te20-96x80 9 each,
C-m1-tee0-96x80 39, C-m2-te00-96x80 and C-m2-te20-96x80 17 each, and none in the other 40. With
`halves=False` (both halves take the union of the two lists) it gives 0 holes in 7 of the 8 and 3 of
39 in the eighth: 40 of 48, 0 of the 8. E504 (isp/msaa-te-dumps, 21 jobs): equal in 15 of 21, the 12
jobs with bit 29 set (0 holes in 11, the 136 at (32, 32) in te-m0-e0-64x64) and the 3 at TE 0; the 6
jobs with bit 29 clear and bit 30 or 31 set store no triangle at all (3969 of 4096 pixels wrong),
E829's zero dword, which the model does not take. The shape (`q141_pat.out`): every hole is a
staircase in one tile, at its top-left, its rows 15, 13, 11, ... pixels wide in mode 1 at 0x60, 15,
11, 7, 3 at 0xe0, 5, 3, 1 at TE 0x00 (rows doubled in mode 2), along the quad's diagonal; never a
whole tile or region.

**What it shows.** [HW, in sample] Every background pixel of the 63 kept tri-full images of E502 and
E504 that store a triangle at all is a pixel the landed model leaves empty, and no other is, with
the seam fixed by the tool's geometry (E762's decode) and k = 1.25 chosen on E502. [infer] Q141's
three readings are thereby narrowed to one: not "a region left without any primitive" (the holes are
part of a tile, the rest of the tile is drawn) and not a clip (the clip gives the quad, whose two
triangles together cover the target), but the region model's own halves: the half tile takes only
its half-region's list, which lacks the seam's second triangle where a stored half's samples lie
past the diagonal. Out of sample the same model holds in E727 (17 of 17, other triangles) and E762
(320 x 400 at 0x20000000: the 28 holes and the first, post hoc).

**What it does not show.** Nothing here is held out: the seam was set on E502 and E504's pixels were
known. The hole sets at sizes, modes and slopes never run are R8-1's frozen predictions
(`closing8/offline/r8-1/q141_r8pred.tsv`, 24 jobs: 14 held out with holes, 2 zero-hole twins, 6
single triangles inside the clip quad, 2 controls; H-REGION is the model, H-UNION its halves-off
rival, which predicts holes too in 9 of the 14 and the same set in 2 of them, mode 0 at 0xa0000000,
where the holes come from the window and not the halves), for session r8-geo; Q141 retires on that
row (R8-3 a). The rank's single triangles reaching past 1.25 W or 1.25 H were moved inside the quad
in the table: the TA clips them into two triangles in an order no record decodes, which would put a
seam where the model has none. Why the hardware lists a primitive per half-region and not per tile
is not shown.
