+++
id = "C0223"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/texstate.xml:153"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/texstate.xml#L153"
quote = "<enum name=\"FORMAT\">"
terms = ["TEXFORMAT"]
+++

Line 153 of `texstate.xml` in Mesa's Rogue csbgen names `FORMAT`. It backs the glossary enum value
`TEXFORMAT`: texel format enum: on SGX545 2 RGBA4444, 4 RGBA5551, 5 RGB565, 12 BGRA8888 (ARGB8888 in
memory), 13 RGBA8888, 17 RGBA half-float, 18 float32 (RGBA, luminance, depth), 23 PVRTC 2 bpp, 24
PVRTC 4 bpp, 27 ETC1, 28 YUYV, 29 UYVY; with T0.TEXFORMAT_ALT 25 A8, 26 L8, 27 LA88, 30 luminance
half-float (Rogue values differ).
