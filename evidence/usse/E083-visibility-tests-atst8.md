+++
id = "E083"
claim = "atst8 is an alpha test of src0's top byte against src2's top byte by the function in src2 bits 15:13 (0 never, 1 less, 2 equal, 3 lequal, 4 greater, 5 notequal, 6 gequal, 7 always), writing src0 and setting the predicate on a pass and leaving both on a fail, in all 687 fill cases; in a fill the fb, nfb, optdwd and twosided modes, src1 and the other src2 bits change nothing, and depthf and pcoeff change nothing; in a punch-through pass a pixel is kept by atst8 only with fb and a control word of 0xe001 or 0xffffffff in src1; ptoff is not measured"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/alpha-test.toml, fills whose pixel program runs atst8 (or pcoeff, depthf) on preset registers and stores r10, the predicate's marks and the registers; and the pt2 probes of probes/isp/punch-through.toml, a 64x64 render of five triangle copies in a punch-through pass; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-alpha-test", "isp-punch-through", "isp-punch-through-followup"]
terms = ["FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "FEEDBACK_CTL.DEPTH_ALWAYS", "DOUTI0.ATTR_SOURCE", "PIXEL_EVENT.PT_OFF"]
+++

**What runs.** In the fill the program is `atst8 r10, p0, r1, r2, r3, <mode>` after a setup
that sets p0, then two marks, 0x11111111 stored in r11 if p0 is set and 0x22222222 in r12 if
it is clear; r10 starts at a sentinel (0xa0a1a2a3). Cases: a grid of the three sources (585),
every function at an alpha just below, at and above a reference of 0x80 (24), the byte
positions of the reference and the alpha (12), src2 with one bit cleared from all ones (32),
the modes and src1 (16), `fb` and `optdwd` on nine src0 values each.

**Results.** In all 687 atst8 cases a pass is `alpha FUNC reference`, with alpha = src0 bits
31:24, reference = src2 bits 31:24 and FUNC = src2 bits 15:13: on a pass r10 holds src0 and
p0 is set; on a fail r10 keeps its sentinel and p0 is clear. The other bits of src2 change
nothing (the 32 cases with one bit cleared change only when bit 13 does, because it changes
the function), the low bits of src0 and the contents of r2 do not matter, and `fb`, `nfb`,
`optdwd` and `twosided, nfb` give the same result as each other in the fill. pcoeff r1, r2,
r3 and depthf r1, r2, r3 with nfb, fb or optdwd leave r10, p0 and the registers as a nop
does: all six cases are identical.

In the punch-through pass (isp/punch-through, pt2 probes) the triangle copies are drawn
with an atst8 `always` and `fb`, and then the image holds 1062 pixels of 0x00000000 and 36
of 0x3d800000; with `nfb` or `nop.end` nothing is drawn. With `fb` and a control word in src1
only 0xe001 draws that image, and 0xffffffff draws 1074 pixels of 0x3e800000 and 24 of
0x3e000000; 0x0, 0x1, 0x2, 0x3, 0xf, 0xe000, 0xe002, 0x80000001 and 0x100 draw nothing.
The label "greater 0x00" fails the first copy only (1098 pixels drawn), "less 0x3e" fails the
last three copies (the 1062 + 36 image) and "never" fails all five (nothing drawn).

**Not shown.** The follow-up run repeats the images above except for the pcoeff-only probe and the
unset-r4 case, which differ from run to run. Nothing here uses ptoff, so whether it ends the
punch-through phase is not tested. pcoeff's and depthf's effect in a punch-through pass is not shown
here either.