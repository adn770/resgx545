+++
id = "E229"
claim = "In the 64x64 punch-through scene turned to back faces with ISP word 0 bit 11 set and a second pair of state words added, the stencil words (front never and back always, or front always and back never) change nothing in atst8's fb and optdwd modes or in their twosided forms: all 8 cases drew the copy at z 0 on 1062 pixels and the copy at z 1/16 on 36, in both runs"
unit = "isp"
method = "the probes isp-punch-through-atst8-ts-back and isp-punch-through-atst8-ts-back-swap of probes/isp/punch-through.toml, 4 cases each, fenced (the 64x64 baseline triangle drawn clean before and after), on the laptop with the linux fork and the debug option on, run twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-punch-through", "isp-punch-through-followup"]
terms = ["ISP0", "ISP1", "FEEDBACK_CTL.ENABLE"]
+++

**What runs.** The scene is the punch-through scene of E226: five copies of the triangle at
depths from 0 to 4/16 (15 vertices), depth test less, ISP0 pass type 4, and a pixel program that
ends in `atst8` with the control word 0xe001 and writes the copy's depth to o0, so that the image
says which copy a pixel belongs to. The table asks for back faces with a state-block word 12 of
0xc2000000, sets ISP0 to 0x08400b00 (bit 11 is the bit E228 finds to select two-sided
stencil) and adds two state-block words (presence bits 3 and 5,
0x08400300 and 0x0e0000ff). ISP word 2 is 255 in `atst8-ts-back`, whose question reads it as
the front's stencil compare never and the added 0x0e0000ff as the back's always; in
`atst8-ts-back-swap` the two values change places (front 0x0e0000ff, back 255). Each probe has
four cases, the ending of the program: `atst8 ... fb`, `... optdwd`, `... twosided, fb` and
`... twosided, optdwd`.

**Results.** All 8 cases gave the same image in the first run and in the follow-up run: 2998
pixels of the background (0xff203040), 1062 pixels of 0x00000000 (the copy at z 0) and 36 pixels
of 0x3d800000 (the copy at z 1/16). That is the image of the front-facing scene without
stencil (E226). The baseline triangle drawn before and after each probe was clean in both runs
(0 of 4096 pixels differ). The ISP visibility counter sampled in these jobs counts differently
from boot to boot (0x420 pixels in the first run's first case, 0x413 in the follow-up run's) and
is not used here.

**Not shown.** That the stencil does not decide which punch-through pixels survive is shown for
these two orderings of never and always only. Whether `twosided` picks a face's stencil handling
in the feedback is not shown: the cases do not read the stencil back, and a later opaque draw
with a stencil compare, after a punch-through pass whose stencil operations write, would. The
table does not check that the triangles are taken as back faces beyond the state word it sets;
E228 does so for opaque triangles.
