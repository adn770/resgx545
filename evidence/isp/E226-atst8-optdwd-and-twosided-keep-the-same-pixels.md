+++
id = "E226"
claim = "In the working punch-through scene atst8 ending in fb, optdwd, twosided with fb and twosided with optdwd all keep the same pixels (1062 of depth 0, 36 of 1/16, 2998 background, one identical image), in two runs; nfb keeps none (E217); what optdwd adds over fb, and what twosided does on front faces, is not shown"
unit = "isp"
method = "probe isp-punch-through-atst8-modes-feedback of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle at depths 0 to 4/16 in the punch-through pass (render block word 1 = 0x08400200), pcoeff on the source-34 iteration, src1 0xe001 and src2 0xee00, four endings of the pt phase, every pixel read back, the probe fenced by a baseline render before and after; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "FEEDBACK_CTL.DEPTH_ALWAYS", "ISP0.PASS_TYPE"]
+++

**What runs.** The working scene of E217 with the pt phase ending in one of four instructions:
atst8 with the feedback mode fb (the control), atst8 with optdwd, atst8 with the twosided flag and
fb, and atst8 with the twosided flag and optdwd. The colour written is the copy's depth.

**Results.** All four cases give the same image, the same pixel for pixel: 1062 pixels of depth 0,
36 of depth 1/16 and 2998 background. Both runs agree, and the baseline renders before and after
are clean.

**What it shows.** In this scene the third feedback mode (optdwd) keeps the pixels that fb keeps,
and adding the twosided flag changes no pixel. The control word 0xe001 was the one that keeps a
pixel with fb (E218); optdwd was run with that word only.

**Not shown.** What optdwd adds over fb (an optional depth write, perhaps) does not show with the
depth taken from the iteration of this scene and with depth writes on. The twosided flag was run
on front-facing triangles here; E227 has the mirrored scene. Other control words under optdwd were
not run. Two runs.
