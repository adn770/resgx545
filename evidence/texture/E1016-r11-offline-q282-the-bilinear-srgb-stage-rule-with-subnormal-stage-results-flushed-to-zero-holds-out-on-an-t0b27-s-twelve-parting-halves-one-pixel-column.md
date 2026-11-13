+++
id = "E1016"
claim = "Round 11 offline (Q282; no run): E982's bilinear sRGB stage rule R10-BF11 with every stage result below 2^-14 flushed to +0 (FTZ-OUT, E1004's post hoc form), frozen by hash before any held-out pixel was read (closing11/plan/c2-texture/rule_b.py, sha256 84bd4264...), holds out on p1132 tx-lod's an-t0b27 (E564's 64 x 64 twiddled bilinear sRGB job, in neither E982's nor E1004's fit): 2048 of 2048 pixels, and 12 of 12 on the halves where it parts from the unflushed rule (pixel column x = 4, rows 0 to 11, channel 0, two corner quads), where R10-BF11 is right on 0 of the 12 (2036 pixels) and the input-only flush (FTZ-IN: x-stage results flushed entering the y stage, the final result not) on 11 (2047 pixels), missing (4, 4), whose y-stage result 5.7e-5 the hardware stores as 0 [HW, held out offline; thin: one column of one job, 12 correlated halves, the final-result flush on one half]; E723's g-bl-st-a and -b and the reruns srgb2-ctl, srgb-ctl and srgb-eq reach no subnormal stage (2048 of 2048 under every form: no test); an-t0b27's footprint (LOD and layout) is texmodel.py's [infer]"
unit = "texture"
method = "Offline, no run (round 11, decision R11-6 a of closing11/plan/rank-round11.md, finding 5; the planner's check closing11/plan/c2-texture/, part B). Data: p1132 tx-lod's kept an-t0b27 (texture/p1132/tx-lod/an-t0b27.txt.gz, footprint from texture/p1141/support/texmodel.py and specs.json), E723's kept g-bl-st-a and g-bl-st-b (texture/p1141/out-hw/p1141tex-dumps/tex-d-t0b27/), r10-tex's srgb2-ctl (render-closing-r10-tex out/20261113-102730/srgb2/) and r9-x's srgb-ctl and srgb-eq (render-closing-r9-x out/20261113-081821/srgb/). rule_b.py (standard library) declares R10-BF11 (copied from render/closing-r10-tex/gen/q282.py), FTZ-OUT (the fold's out/fold/post_srgb_ftz.py mode out), FTZ-IN (operands flushed, results not) and FTZ-INOUT; FREEZE.log gives its hash at 2026-11-13T11:08:08Z and everything read before it (records, generators, the fit rows of E1004's fold, no held-out pixel dump); score_b.py scores every pixel and counts the halves where a stage result is subnormal (SUB) and where the forms part (PART); detail_b.py prints the 12 parting halves, next_row_b.py the weights that would part FTZ-OUT from FTZ-IN in a later row. This fold re-ran score_b.py, detail_b.py and next_row_b.py with python -I and got byte-identical outputs, then modelled FTZ-OUT in sgx-sim (tex.rs srgb_stage)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["texture-p1132-tx-lod", "texture-isp-msaa-verification-1141", "render-closing-r10-tex:out/20261113-102730/srgb2/", "render-closing-r9-x:out/20261113-081821/srgb/", "cited-scratch:closing11/plan/c2-texture/"]
terms = ["T0.BIT27"]
+++
**What was done.** E1004 ran E982's stage rule R10-BF11 on hardware: it held on four of five new
rows and missed srgb2-sub only where a stage's result is a subnormal half; post hoc, the rule with
every stage result below 2^-14 flushed to +0 fitted all of r10-tex's and r9-x's rows, not held out.
The round 11 planner looked for a kept bilinear sRGB job (T0 bit 27 with bilinear filters) that
neither E982 nor E1004 had fitted and that reaches a subnormal stage. Of the kept ones (E723's
g-bl-st-a and -b, their reruns srgb2-ctl and srgb-ctl, r9-x's equal-corner srgb-eq, and p1132
tx-lod's an-t0b27; ab-t43, s64x32-t0b27 and ind-t0b27 are point sampled) only an-t0b27 does. The
rule and its rivals were frozen by hash before any held-out pixel was read.

**Results [HW, held out offline].** Pixels exact (score_b.out):

| job | R10-BF11 | FTZ-OUT | FTZ-IN | FTZ-INOUT | halves SUB / PART |
|---|---|---|---|---|---|
| g-bl-st-a, g-bl-st-b, srgb2-ctl, srgb-ctl, srgb-eq | 2048 | 2048 | 2048 | 2048 | 0 / 0 |
| an-t0b27 | 2036 | 2048 | 2047 | 2048 | 12 / 12 |

The 12 parting halves of an-t0b27 (detail_b.out) are pixel column x = 4, rows 0 to 11, channel 0,
corner bytes (21, 23, 0, 2) at rows 0 to 3 and (0, 2, 1, 3) at rows 4 to 11, kx 4, ky 4 to 60 in
steps of 8. The x stage of bytes 0 and 2 at kx 4 gives 3.797e-5, below 2^-14: unflushed R10-BF11
is above the hardware on all 12 (by 0x0a to 0x3ba half bits), FTZ-OUT equals it on all 12. At
(4, 4) the y stage's own result, 5.686e-5, is subnormal too: the hardware stores 0, FTZ-OUT 0,
FTZ-IN (which does not flush a final result) 0x0166. A decoded sRGB byte is never subnormal (byte
1 decodes to 3.04e-4), so the only operands a flush of inputs can touch are the x stage's results
entering the y stage; FTZ-IN differs from FTZ-OUT only where the y stage's result is subnormal.

**What it shows.** [HW, held out offline] Each lerp stage of a bilinear sRGB sample gives +0 where
E982's rule gives a subnormal half, on the x stage (12 halves) and on the y stage (one half), as
E1004's post hoc form says; the rest of the rule stays exact on the job (4084 of 4084 other
halves). The sample is thin: one pixel column of one job, two corner quads, one weight kx, so the
12 halves are not 12 independent tests, and the final-result flush rests on (4, 4) alone with
E1004's fit rows.

**What it does not show.** Where the threshold lies (the kept data put it between 5.7e-5, flushed,
and 6.4e-5, kept); a row of its own for the y stage's flush (next_row_b.out: corners 0, 1, 0, 1
at ky 0 with kx 11 to 14 parts FTZ-OUT from FTZ-IN, and 0, 0, 1, 1 at kx 0 the y stage alone);
negative values, other channels than the two halves, other filters. an-t0b27's footprint is the
11.32 model's (texmodel.py), and its 2048 of 2048 under FTZ-OUT supports that model too [infer].
