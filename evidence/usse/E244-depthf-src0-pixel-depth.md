+++
id = "E244"
claim = "At the end of a punch-through pixel phase, depthf's src0 replaces the pixel's depth in the depth test, in ISP0 pass type 4 as in pass type 5: with 1.0 nothing is drawn, with 0, 0.5 or the copy's own depth the copy at z 0 keeps 1062 pixels and the copy at z 1/16 keeps 36, and with 0.5 - z the last copies win (1074 and 24 pixels); the same in both runs"
unit = "usse"
method = "the probes isp-punch-through-pt-depthf-p4, -p5, -rev-p4 and -rev-p5 of probes/isp/punch-through.toml (pix_pt5.s and pix_pt7.s, 10 cases), on the laptop with the linux fork and the debug option on, each probe fenced (the 64x64 baseline triangle compared with its clean image before and after), run twice (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["ISP0.PASS_TYPE", "FEEDBACK_CTL.ENABLE"]
+++

**What runs.** The punch-through scene of E226: five copies of the triangle at depths from 0 to
4/16, depth test less against the background object's depth 1.0, depth written, a pixel program
whose punch-through phase loads r1 = 0xee00 and r2 = 0xe001, hands the iterated depth to the ISP
with `pcoeff`, and ends in `depthf.end r4, r2, r1, fb`; the colour phase writes the copy's depth
to o0. ISP0 is 0x08400200 (pass type 4, probes -p4) or 0x0a400200 (pass type 5, probes -p5). r4
holds, per case: 1.0, 0, 0.5, or the copy's own depth (pa0); in the -rev probes `fmad` makes it
0.5 - z (z the copy's depth, pa0 * -1.0 + 0.5).

**Results.** Pass type 4 and pass type 5 gave the same classes in each case, and the follow-up
run gave the same as the first.

| depthf src0 | image (of 4096 pixels) |
|-------------|------------------------|
| 1.0 | background only (4096 of 0xff203040): nothing drawn |
| 0 | 2998 background, 1062 of 0x00000000 (the copy at z 0), 36 of 0x3d800000 (z 1/16) |
| 0.5 | the same |
| the copy's depth | the same |
| 0.5 - z | 2998 background, 1074 of 0x3e800000 (z 4/16), 24 of 0x3e000000 (z 2/16) |

With a constant src0 all copies have the same depth, so the copy drawn first keeps the pixels
(the same 1062 and 36 pixels as the iterated depth gives, E083) **[infer]**; with 0.5 - z the
order reverses and the last copy wins. The baseline triangle before and after every probe was
clean (0 of 4096 pixels) in both runs.

**What it shows.** depthf's src0 stands in for the pixel's depth in the test, both against the
background (1.0 is not less than 1.0) and between copies, in pass type 4 as in pass type 5. With
`atst8` the iterated depth that `pcoeff` hands the ISP is the one tested (E083). That the depth
written is src0 as well is read from the order of the copies and not from a depth read back
**[infer]**.

**Not shown.** Other values of the control word in src1 (0xe001 only), other pass types, and a
depth read back from the buffer after the pass. The visibility counters sampled in the jobs are
not used.
