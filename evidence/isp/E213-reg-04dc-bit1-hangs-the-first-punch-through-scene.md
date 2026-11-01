+++
id = "E213"
claim = "With 0x04dc at 2 and at 3, every case of the first punch-through scene (a one-phase shader waiting for a fetchless iteration; four endings, nop.end among them) hangs the job, in two runs; at 0 the same four cases draw nothing, so whether bit 1 moves the depth test cannot be seen in this scene"
unit = "isp"
method = "probes isp-punch-through-pt-punch, -pt-punch-04dc-2 and -pt-punch-04dc-3 of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle in the punch-through pass (render block word 1 = 0x08400200), pixel shader with a pt phase ending in four different endings, the primary PDS program waiting for one iteration without a fetch; 0x04dc (rd:21) poked to 2 or 3; every pixel read back; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["CR_ISP_REG_04DC", "ISP0.PASS_TYPE", "DOUTU1.WAIT_ITER", "DOUTI0.LAST_ITER"]
+++

**What runs.** The scene of E082: five copies of the triangle at depths 0 to 4/16, depth test less,
punch-through pass, the colour written being the copy's depth. The pt phase ends in one of four
ways: atst8 with the always function and fb, atst8 with a less function and fb, atst8 always
with nfb, and nop.end. With 0x04dc untouched the four cases are one probe; with
0x04dc poked to 2 and to 3 they are one probe each. Each probe is fenced by a baseline render
before and after it; the fence is clean in both runs.

**Results.** With 0x04dc at 0 (the base probe) none of the four cases draws a pixel, in both runs
(each case: 4096 background pixels). With 0x04dc at 2 and at 3 all four cases hang: "job hung,
context lost (Connection timed out)", 8 of 8 per run, nop.end included, in the first run and in
the follow-up run. The baseline renders before and after each probe are clean.

**What it shows.** In this scene bit 1 of 0x04dc hangs the job whatever the shader's ending, so a
nop.end shader hangs too. The scene draws nothing when 0x04dc is 0, so the hang cannot be compared
with a drawn image, and what bit 1 would change for a pass that draws is not seen here. E222 has
the scene that draws.

**Not shown.** Values of 0x04dc other than 0, 2 and 3 were not run in this scene (E068 has
2, 3, 6 and 7 hanging and 0, 1, 4 and 5 not, in another punch-through scene). Why the pass draws
nothing at 0 is not shown. The hang's cause is not shown.
