+++
id = "C0357"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/cr.xml:932"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/cr.xml#L932"
quote = "<struct name=\"ISP_BGOBJVALS\" length=\"1\">"
terms = ["CR_ISP_BGOBJVALS"]
+++

Line 932 of `cr.xml` in Mesa's Rogue csbgen names `ROGUE_CR_ISP_BGOBJVALS`. It backs the glossary
register `CR_ISP_BGOBJVALS`: background object values (Rogue: bit 9 background tag enable, bit 8
mask, 7:0 stencil); the 3D kick and the transfer path load it from their commands.
