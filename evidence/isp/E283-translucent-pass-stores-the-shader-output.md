+++
id = "E283"
claim = "In a translucent pass the stored pixel is exactly the shader's o0: a shader that writes a constant without reading o0 stores the constant, one that passes o0 on stores the background unchanged, and one that ORs 0xff into o0 stores the background with its low byte set; in the one ISP and PBE state run, nothing after the shader blends [infer: no blend-related word was varied]"
unit = "isp"
method = "probes/isp/translucent-blend.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with ISP word 0 0x03d00200 (pass type 1) or 0x01d00200 (opaque), over the background 0xff203040, its pixel shader writing 0xff00ff00, o0 itself, or o0 | 0xff; every pixel read back; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["isp-translucent-blend"]
terms = ["ISP0.PASS_TYPE"]
+++

**What runs.** One probe, run twice (`isp-translucent-blend-r1`, `-r2`): six cases, three pixel
shaders in a translucent pass (ISP word 0 bits 27:25 at 1) and the same three in the opaque pass.
The shaders end in `mov o0, #0xFF00FF00`, `mov o0, o0` and `or o0, o0, #0x000000FF`.

**Results.** Both runs:

| shader | translucent pass | opaque pass |
|---|---|---|
| constant | 1062 pixels of 0xff00ff00 | 1062 pixels of 0xff00ff00 |
| o0 | 4096 pixels of the background 0xff203040 | 517 and 426 pixels of 0xff00ff00, the rest background |
| o0 \| 0xff | 1062 pixels of 0xff2030ff | 594 and 636 of 0xff2030ff, 468 and 426 of 0xff00ffff |

**What it shows.** In the translucent pass o0 starts as the pixel's colour in the tile (E077), and
what the pass stores is the shader's o0 and nothing else: the constant replaces the background
whatever it was, and o0 passed on leaves it. So blending is the shader combining its colour with o0.
In the one ISP and PBE state run, with no blend-related word varied, no unit after the shader blends
[infer], which answers Q073's blending question. In the opaque pass o0 starts as a leftover: some
pixels hold the colour an earlier case's shader wrote (0xff00ff00), and the counts differ between
runs.
