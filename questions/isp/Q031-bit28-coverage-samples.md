+++
id = "Q031"
question = "with ISP word 0 bit 28 set, is a pixel covered by any of eight samples placed by 0x04c8 and 0x0520, or by the four samples of 0x0520 plus the pixel centre?"
unit = "isp"
phase = 10
evidence = ["E214", "E215"]
terms = ["CR_ISP_SAMPLE_POS", "CR_ISP_MULTISAMPLECTL", "programmable sample positions", "ISP0"]
+++

With bit 28 of ISP word 0 set, 55 values of 0x0520 give six distinct images of the single-sampled
triangle, and each is reproduced pixel for pixel by a pixel covered when any of four samples
placed by 0x0520's bytes, the pixel centre or the pixel's top-left corner is inside (E214). The
default 0x04c8 word, 0x88, places one sample at the centre and three at the corner, so that rule
is also the union of eight samples, four from 0x04c8 and four from 0x0520. A second rule, the
four samples plus the centre counted inside on every edge, fits the same 55 images. E214
keeps 0x04c8 at its default, so it cannot tell these apart.

E215 varies 0x04c8 with 0x0520 at 0x0c0c0c0c: 1122, 1134 and 1098 pixels for 0x04c8 at 0x88,
0xffffffff and 0. The eight-sample union predicts all three, and a model in which 0x04c8 does not
enter predicts 1122 for all three. That favours the eight samples, but these cases are in the
data as a hash and a count only, not fitted pixel for pixel, and come from one session run twice.
Under 4x multisampling bit 28 hangs the job, so the rule is seen only single-sampled.

To settle it: the run needs sample offsets that separate the two rules. The 36 on-edge pixels have
their centre on the long edge x + y = 76, inside being x + y < 76, so a sample at (a, b) / 16 from
the pixel's top-left corner is inside exactly when a + b < 16 (a + b = 16 lies on the long edge,
which counts as outside, E214). A sample near the corner, such as (2, 2), or 0x0520 at 0, which
puts its four samples at the corner, is inside: with either, both rules keep the 36. With bit 28
set and every pixel read back, run 0x04c8 and 0x0520 both at values whose eight samples all have
a + b > 16, for example both at 0xcccccccc (12, 12) and both at 0xeeeeeeee (14, 14), with no
sample at the centre or on the inner side of the long edge. The eight-sample rule predicts losing
the 36 on-edge pixels; the centre rule keeps them through the centre. As a control, run the same
0x04c8 values with 0x0520 at 0, where both rules keep the 36. Fit both rules to every image, and
run each case twice.
