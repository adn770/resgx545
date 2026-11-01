+++
id = "Q073"
question = "is blending only a shader that combines its colour with o0 in a translucent pass, or does a unit after the shader blend as well?"
unit = "isp"
phase = 11
evidence = ["E077"]
terms = ["ISP0.PASS_TYPE"]
+++

In a translucent pass a pixel shader's o0 holds the pixel's current colour when it starts, at every
pixel of the triangle; in the opaque pass it holds a leftover (E077).

What is open (3d.md §11.11): that blending is a shader combining its colour with o0 is a reading
[infer].

To settle it: on the laptop, a translucent pass whose shader writes a constant without reading o0,
against one that adds o0, over a coloured target; any image other than the constant in the first
shows a blend outside the shader.
