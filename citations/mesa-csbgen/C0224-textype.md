+++
id = "C0224"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/texstate.xml:310"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/texstate.xml#L310"
quote = "<enum name=\"TEXTYPE\">"
terms = ["TEXTYPE"]
+++

Line 310 of `texstate.xml` in Mesa's Rogue csbgen names `TEXTYPE`. It backs the glossary enum value
`TEXTYPE`: texture type enum (Rogue: 1D, 2D, 3D, CUBE, STRIDE...): on SGX545 0 a power-of-two 2D
texture, 3 a non-power-of-two one and the YUV streams, 6 strided (also depth textures).
