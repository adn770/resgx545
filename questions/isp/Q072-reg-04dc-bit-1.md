+++
id = "Q072"
question = "is bit 1 of CR_ISP_REG_04DC an up-front depth test, given that it hangs every punch-through pass tried?"
unit = "isp"
phase = 11
evidence = ["E068", "E073", "E213", "E222"]
terms = ["CR_ISP_REG_04DC"]
+++

No value of the render-constant ISP registers changes a copy, a fill, a textured triangle (E068) or
42 overlapping triangles (E073). CR_ISP_REG_04DC bit 1 hangs every punch-through case tried, while
0, 1 and 4 give the pass's own image (E213, E222).

What is open (3d.md §11.9): whether bit 1 moves the depth test ahead of the shader, since a hang
gives no depth.

To settle it: on the laptop, bit 1 set on opaque and translucent scenes with depth less and a shader
whose output would differ before and after the test, the visibility counters read; a punch-through
scene without feedback.
