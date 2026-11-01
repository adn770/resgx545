+++
id = "Q031"
question = "why does ISP word 0 bit 28 hang a multisampled render, when single-sampled it widens coverage to the union of eight samples?"
unit = "isp"
phase = 10
evidence = ["E214", "E215", "E278"]
terms = ["CR_ISP_SAMPLE_POS", "CR_ISP_MULTISAMPLECTL", "programmable sample positions", "ISP0"]
+++

Which samples bit 28 uses is answered (E278): a single-sampled pixel is covered when any of the
eight samples of `CR_ISP_MULTISAMPLECTL` and `CR_ISP_SAMPLE_POS` is inside, under the top-left rule;
the eight-sample reading predicts all 56 images of 28 settings, each run twice, pixel for pixel, and
the reading with the pixel centre in place of 0x04c8's samples fails in 10 of the 28 settings (20 of
the 56 images). Each byte of both words is x in bits 3:0 and y in bits 7:4.

What is open: under 4x multisampling bit 28 hangs the job (E215), so whether 0x0520's samples add
to a multisampled pixel's coverage, and why the combination hangs, are not shown. Of the top-left
rule only the long edge's exclusion is seen, on a triangle with no horizontal edge, and a centre
sample under that rule added to the eight is not excluded.

To settle it: bit 28 under modes 1 and 2 with 0x0520 at 0 and at 0x04c8's value, one case a probe so
that a hang stops one case, the kernel log kept; and the right triangle of the layout probes
(isp_words.py affine_target) for a horizontal edge under the single-sampled rule; both words at 0,
which parts the eight from the eight and the centre.
