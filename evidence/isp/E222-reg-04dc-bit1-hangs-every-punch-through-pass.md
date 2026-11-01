+++
id = "E222"
claim = "In the punch-through scene that draws (pcoeff and the source-34 iteration, 1062 pixels of the nearest copy and 36 of the next), 0x04dc at 0, 1 and 4 give the same image and 2 and 7 hang every case, atst8 with fb or nfb, depthf and nop.end alike, in two runs; whether bit 1 is the up-front depth test of other GPUs is not shown"
unit = "isp"
method = "probes isp-punch-through-pt2-punch, -pt2-punch-04dc-1, -04dc-2, -04dc-4, -04dc-7, -pt2-depthf-04dc-0 and -04dc-2 of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: five copies of the 64x64 triangle in the punch-through pass (render block word 1 = 0x08400200), 0x04dc (rd:21) poked per probe, every pixel read back, the visibility counter 0x0498 sampled; two runs (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["CR_ISP_REG_04DC", "ISP0.PASS_TYPE", "FEEDBACK_CTL.ENABLE", "CR_ISP_VISIBILITY_COUNT0"]
+++

**What runs.** The working punch-through scene of E083: five copies at depths 0 to 4/16, the pt
phase running pcoeff on the source-34 iteration and ending in atst8 (control word 0xe001) with fb,
with nfb, or in nop.end; the colour written is the copy's depth. The same scene with a depthf
ending instead of atst8 (two operand orders, and an atst8 control) is the depthf probe. 0x04dc is
left alone (value 0), or poked to 1, 2, 4 or 7.

**Results.** With 0x04dc at 0 the fb case draws 1062 pixels of the nearest copy (depth 0) and 36
of the next (1/16), 2998 background; the nfb and nop.end cases draw nothing. At 1 and at 4 the
three cases give exactly these images. At 2 and at 7 all three cases hang ("job hung, context
lost (Connection timed out)"), 3 of 3 for each value. In the depthf scene, 0x04dc at 0 gives the
atst8 control's image and the depthf image of the operand order that works; at 2 all three hang.
The result is the same in the second run, case for case. The register 0x0498 (visibility counter 0)
read 0x44a (1098) after the fb case at 1, at 4 and in the depthf scene at 0, and 0x43e in the base
probe; at 2 and 7 it had reached 0x70 in the first case when the job hung, in both runs. The
counter's differences between probes are not interpreted here (the counters count in some boots
only).

**What it shows.** Bit 1 of 0x04dc hangs the pass in every ending tried, including nop.end and
including the endings that discard every pixel; bits 0 and 2 alone change no pixel. That fits a
test the pass waits on whatever its shader does. The reading as the up-front depth test of other
GPUs' punch-through passes is ours and not tested, because a hang gives no depth result.

**Not shown.** Values 3, 5 and 6 were not run in this scene (E213 has 3 hanging in another one, and
E068 has 3, 6, 7 hanging in a third). What a pass that completes with bit 1 set would look like is
not seen: none did. What the 0x70 pixels counted before the hang are is not shown. Two runs.
