+++
id = "E285"
claim = "CR_ISP_REG_04E8 at the job's 0x100, at 0, 1 and 0x101 changes no outcome of the stencil test against the background stencil (equal 0 draws, equal 1 does not) and no pixel or visibility count of 42 overlapping copies, depth always or less, in two runs; it is not the background-object values"
unit = "isp"
method = "probes/isp/reg-04e8.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with ISP word 2 compare equal and ISP word 0 reference 0 or 1, and 42 copies of the triangle (copy c at clip z c/16, each pixel carrying its copy's z) with ISP word 0 0x01d00200 (depth always) or 0x00400200 (depth less) and ISP word 1 0x10f8 (visibility test into counter 0), render-details word 51 (it loads 0x04e8, a kernel poke) at four values; every pixel read back, the visibility counters through regtimeline; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-reg-04e8"]
terms = ["CR_ISP_REG_04E8", "hw_render_details.isp_reg_04e8", "CR_ISP_BGOBJVALS"]
+++

**What runs.** `isp-reg-04e8-stencil` and `-r2`: compare equal against the background stencil
(the job's `CR_ISP_BGOBJVALS`, which acts as 0) with the reference at 0 and 1, and 0x04e8 at
0x100, 0, 1 and 0x101. `isp-reg-04e8-many` and `-r2`: 42 copies, depth always and depth less,
0x04e8 at the same four values.

**Results.** Equal 0 draws the triangle's 1062 pixels and equal 1 draws none, at every value of
0x04e8, in both runs. The 42 copies give, at every value: depth always, 1062 pixels of copy 16,
24 of copy 2, 24 of copy 13, 12 of copy 7 and 11 of copy 8; depth less, 1062 of copy 0, 36 of
copy 1 and 35 of copy 9. The visibility counter 0 reads 0x4782 after the depth-always cases and
0x46d after the depth-less ones, whatever 0x04e8 holds; both runs alike. Copies 17 to 41, at
clip z above 1, leave no pixel.

**What it shows.** 0x04e8's two bits hold neither the background stencil nor its enable, which
reproduces the notebook record that refuted the background-object reading, and do not change a
scene of 42 objects per tile. What the register does is not shown; a resource limit or threshold
left at its default would need a load past it [infer].
