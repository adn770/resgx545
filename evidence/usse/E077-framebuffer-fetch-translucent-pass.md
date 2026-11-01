+++
id = "E077"
claim = "In a translucent pass (render block word 1 = 0x03d00200, pass type 1) a pixel shader's o0 holds the pixel's current colour when it starts, for all 1062 pixels of the triangle; in the opaque pass it holds either the same background colour (714 and 800 pixels in two cases) or a leftover colour from elsewhere (348 and 262 pixels), different pixels in different cases"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/output-registers.toml, probes fbf-opaque and fbf-translucent, a 64x64 triangle whose pixel shader (pix_op.s) runs one instruction on o0, the same three cases in both passes, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-output-registers"]
terms = ["ISP0.PASS_TYPE"]
+++

**What runs.** A 64x64 triangle (1062 covered pixels, 3034 background) with a pixel shader of one
instruction. The cases are `mov o0, o0`, `o0 = o0 ^ 0x00ffffff` and a control that writes the
constant 0xa. The background is 0xff203040. The translucent probe differs only in setting the render
block word 1 to 0x03d00200, which makes the pass type 1; the opaque probe leaves it at its default.

**Results.** In the translucent pass:

- `mov o0, o0` leaves the whole image at 0xff203040: the triangle's pixels read back the background.
- The xor case turns the 1062 covered pixels to 0xffdfcfbf, the background xor 0x00ffffff, and
  leaves the 3034 others.
- The control writes 0x0000000a on exactly the 1062 covered pixels.

Opaque pass, the same shaders:

- `mov o0, o0`: 3748 pixels read 0xff203040 and 348 read 0xff00ff00.
- The xor case: 800 covered pixels read 0xffdfcfbf (o0 was the background) and 262 read 0xffff00ff
  (o0 was 0xff00ff00).
- The control again writes 0x0000000a on exactly 1062 pixels.

So at the start of the shader o0 holds the background colour of the pixel in the translucent pass
for every covered pixel, as the image the pass blends over. In the opaque pass it holds the
background for most covered pixels (714 or 800) and 0xff00ff00 for the rest (348 or 262). The two
opaque cases split the covered pixels differently (348 against 262 leftovers), so which pixels see
the leftover is not fixed from case to case.

**Not shown.** One run each. Where 0xff00ff00 comes from (a colour an earlier task wrote, or a tile
initial value) is not told by this data, nor why the opaque pass shows the background on most
pixels.
