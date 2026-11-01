+++
id = "E099"
claim = "setm #0 to #15 masks nothing a fill or a single-sample triangle shows: in a fill every one of the 2048 pixels writes the marker in all 23 cases, with or without .skipinv on the mov and with a second mov, and the triangle's pixel shader after setm #0, #1 or #15 keeps exactly the 1062 covered pixels, as without setm"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/instance-masking.toml, probes usse-instance-masking-setm (client fill, 64x32, every pixel and a scratch page read back) and usse-instance-masking-setm-tri (the 64x64 triangle's pixel shader replaced, every pixel read back), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-instance-masking"]
terms = []
+++

**What runs.** The fill probe presets r20 and r21 to known values, runs `setm #k` (k = 0 to 15) and
then `mov r20, #0x0A0A0A0A`, and stores the registers to scratch while r20 is also the pixel (o0).
The 23 cases are: no `setm`; `setm #0` to `#15`; `setm #0`, `#5` and `#15` before a `mov.skipinv`;
and `setm #1`, `#2` and `#3` before two movs (the first writes r21). The triangle probe replaces the
first triangle's pixel shader with `mov.skipinv.end o0, #0xFF00FF00`, with no `setm` or with `setm
#0`, `#1` or `#15` in front. The fill is a client fill of the kind E022 runs, and the triangle is
the 64x64 one of the render probes.

**Results.** Every fill case reports `o0 0x0a0a0a0a (2048 of 2048)`: the marker lands on all pixels
whatever `setm` precedes it, with `.skipinv` or without. In the 20 single-mov cases the scratch
readback is dword for dword the control's; in the three two-mov cases r21 also holds its marker
(0x0b0b0b0b) in the one dword that differs from the control. In the triangle probe all four images
are identical (one hash): 1062 pixels of 0xff00ff00 and 3034 of the background 0xff203040. The 1062
are the triangle's covered pixels (they equal the image of `.skipinv`-only writes in E104). The
baseline triangle before and after each probe was exact. No visibility counter counted in these
runs.

**Not shown.** One run per probe. Nothing here covers a multisampled render (E103) or the instance
masks of a divergent branch (E112); what `setm` sets is not shown by any of them.
