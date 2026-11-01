+++
id = "E082"
claim = "With the iteration marked done (U1 bit 24, iteration source set) the colour phase after a pt phase does not get the pt phase's writes or the iterated attributes: in the punch-through scene (render block word 1 = 0x08400200) none of the 4 + 3 cases writes a pixel in either of two runs, and in the depth-always scene (0x01d00200) they write 118 to 407 pixels of the colour 0xff00ff00, never the 0x12345678 the pt phase wrote, the count differing from run to run"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/isp/punch-through.toml, probes pt-control, pt-punch, pt-always, pt-pa0-punch and pt-pa0-always, a 64x64 render of five depth-ordered triangle copies whose two-phase pixel shader (pix_pt.s) has a pt phase ending in the case's atst8 or nop.end and then writes the colour from pa0; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["ISP0.PASS_TYPE", "DOUTU1.WAIT_ITER", "DOUTI0.LAST_ITER", "CR_ISP_REG_04DC"]
+++

**What runs.** The pixel program PDS fetches with the iteration marked done (U1 bit 24). Five copies
of a triangle at depths 0 to 4/16 are drawn. The control is the one-phase shader `mov o0, pa0` with
the same primary.

**Results.**

- Control (pt-control): 1074 pixels of 0x3e800000 (the iterated value 0.25, the last copy's
  area) and 24 of 0x3e000000 (0.125) in both runs, 2998 background (0xff203040): the
  iteration works. The case with the old primary's words and no fetch hangs the job (the
  context is lost with a timeout), in both runs.
- Punch-through scene (pt-punch, pt-pa0-punch): none of the cases writes a pixel in either
  run: atst8 "always" with `fb`, "less 0x3e" with `fb`, "always" with `nfb`, `nop.end`; and,
  with the result written to pa0, atst8 always with `fb` and `nfb`, and pa0 = 0x12345678 with
  `nop.end`. The image stays 0xff203040.
- Depth-always scene (pt-always, pt-pa0-always): every case writes pixels, all of one
  colour, 0xff00ff00. Counts of those pixels, run 1 and run 2: always/fb 324 and 383, less/fb
  288 and 288, always/nfb 203 and 288, nop.end 118 and 288; into pa0: always/fb 407 and 383,
  always/nfb 288 and 288, pa0 = 0x12345678 with nop.end 288 and 288. No pixel holds
  0x12345678 or an iterated value.

So the colour phase after the pt phase gets neither the iteration's values nor what the pt
phase wrote to pa0: it runs as a task of its own, on fewer pixels (118 to 407 of the
1062 to 1074 covered), and what it writes is the colour 0xff00ff00 that E077 also finds as the
leftover in the opaque pass.

**Not shown.** Where 0xff00ff00 comes from, why the count of pixels varies between the two
runs, and what a second PDS program or the ISP's feedback path through 0x04dc would give that
colour task. The 0x04dc variants pt-punch-04dc-2 and -3 hang in both runs, and
pt2-punch-04dc-2 and -7
hang in the first run; pt2-punch-04dc-1 and -4 draw their triangle.
