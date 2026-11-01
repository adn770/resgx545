+++
id = "E227"
claim = "In E226's scene atst8 in fb, optdwd, twosided fb and twosided optdwd keep the same pixels with ISP word 0 bit 20 set, on the scene mirrored in y to back faces, and with both (12 cases, 1062 pixels of depth 0 and 36 of 1/16 each, the mirrored images being exact y-mirrors of the front one), in two runs; with later copies winning when the depth test is always (E218), a depth-write-off bit that the feedback obeyed would be expected to change the image, and it did not"
unit = "isp"
method = "probes isp-punch-through-atst8-dwoff, -atst8-back and -atst8-back-dwoff of probes/isp/punch-through.toml on the laptop, linux fork with the debug option on: E226's scene with ISP word 0 bit 20 set (render block word 1 = 0x08500200), with the viewport word blk:9 at 0xc2000000 (-32.0 in y, no culling) so that the triangles are back-facing, and with both, the four endings of E226 each, every pixel read back, each probe fenced by a baseline render before and after; two runs (the second is the follow-up run)"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "FEEDBACK_CTL.DEPTH_ALWAYS", "ISP0.PASS_TYPE"]
+++

**What runs.** Three probes of four cases each (fb, optdwd, twosided with fb, twosided with
optdwd), all on E226's scene: ISP word 0 with bit 20 set, the scene mirrored in y by the viewport
word, and both. Bit 20 is set in the depth-always scenes of E068 that are described there as
written without depth write; its role is read from that table and not tested alone here.

**Results.** All 12 cases, in each run, give 1062 pixels of depth 0, 36 of depth 1/16 and 2998
background. With bit 20 set the images are identical to E226's, pixel for pixel. In the two
mirrored probes the images are identical across the cases and each is E226's image with its rows
in reverse order (row y of the front image is row 63 - y). The baseline renders before and after
every probe are clean, and the follow-up run agrees case for case.

**What it shows.** Neither optdwd nor twosided changes which copies are kept, on front or on back
faces, and the bit 20 does not either. [infer] If the depth written by the feedback obeyed bit 20
as other passes' depth writes seem to, the nearest copy could not hold the pixels against the
later, farther ones: the scene with depth always shows that the last copy wins when nothing is
kept in the depth (E218, bit 2 or bit 3 of the control word), and here the nearest wins. So in a
punch-through pass the depth the feedback writes does not look as if it follows bit 20, with fb or
with optdwd. That reading assumes bit 20 is the depth-write-off bit.

**Not shown.** That bit 20 turns depth writes off in this hardware is not tested alone in this
table (E068 carries it in scenes that also change the depth function). The stencil words of the
state block and a two-sided stencil were not part of these probes; the twosided flag changes
nothing seen with no stencil. What optdwd adds over fb is not seen (E226). Two runs.
