+++
id = "E290"
claim = "CR_ISP_REG_04DC bit 1 neither hangs nor changes an opaque or a translucent pass of five overlapping copies with depth less and writes: the nearest copy keeps its 1062 pixels and the visibility counter counts 0x44a with the bit clear and set, in two runs"
unit = "isp"
method = "probes/isp/reg-04dc-depth.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle at clip z c/16 (each pixel carrying its copy's z), ISP word 0 0x00400200 (pass type 0) or 0x02400200 (pass type 1), ISP word 1 0x10f8 (visibility test into counter 0), render-details word 21 (it loads 0x04dc, a kernel poke) at 0 and 2; every pixel read back, the visibility counters through regtimeline; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-reg-04dc-depth"]
terms = ["CR_ISP_REG_04DC", "hw_render_details.isp_reg_04dc"]
+++

**What runs.** Two probes, `isp-reg-04dc-depth-r1` and `-r2`, four cases each: opaque and
translucent copies with 0x04dc at 0 and with bit 1 set.

**Results.** Every case of both runs: 1062 pixels of copy 0, 36 of copy 1, 2998 of the background;
counter 0 reads 0x44a after each. No job hung.

**What it shows.** Bit 1, which hangs every punch-through pass (E213, E222), does nothing visible
in passes 0 and 1 with depth less: neither the kept copy nor the count of passing pixels moves.
With a depth test that the shader does not change, a test moved ahead of the shader keeps the same
pixels, so the runs cannot tell whether bit 1 moves it [infer]; they show that it is the
punch-through pass alone that bit 1 stops (Q072).
