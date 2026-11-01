+++
id = "E230"
claim = "With ISP word 2 at stencil compare never, no single bit of atst8's control word among bits 1, 4-12 and 16-31 makes the punch-through pass obey the stencil: all 29 cases drew the copy at z 0 on 1062 pixels and the copy at z 1/16 on 36, in both runs"
unit = "isp"
method = "the probe isp-punch-through-atst8-ctl-stencil of probes/isp/punch-through.toml, 29 cases, fenced (the 64x64 baseline triangle drawn clean before and after), on the laptop with the linux fork and the debug option on, run twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["ISP0", "FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "FEEDBACK_CTL.DEPTH_ALWAYS"]
+++

**What runs.** The punch-through scene of E226 (five copies of the triangle at depths from 0 to
4/16, depth test less, a pixel program that writes the copy's depth to o0) with ISP0 at
0x08400300 and ISP word 2 at 255, which the table's question reads as stencil compare never. The
pixel program loads a control word into r2 and ends in `atst8 ... fb`. The 29 control words are
0xe001 (the word E218 finds to draw), 0xe001 with bit 1 set (0xe003), with each of bits 4 to 12
set (nine words, 0xe011 to 0xf001), with each of bits 16 to 31 set (sixteen words), and two
further copies of 0xe001 that stand for bits 13 to 15, which 0xe001 already has set. Bits 0 to 3
are not varied here: bit 0 is set in every word and bits 3:2 are the ones E218 links to the
depth-always result.

**Results.** All 29 cases gave the same image in the first run and in the follow-up run: 2998
pixels of the background (0xff203040), 1062 pixels of 0x00000000 and 36 pixels of 0x3d800000.
That is the image of the same scene without stencil (E226). The baseline triangle drawn before
and after the probe was clean in both runs (0 of 4096 pixels differ).

**Not shown.** That the stencil is not turned on by the control word is shown for single-bit
additions to 0xe001 with the stencil compare at never, and for no multi-bit word. A stencil kill
is told from a removed object only by a second pass that sets the compare to always, which this
table does not run. What does enable the stencil in a punch-through pass, if anything, is not
shown, and so neither is what `atst8`'s `twosided` and `optdwd` select.
