+++
id = "C0349"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/texstate.xml:28"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/texstate.xml#L28"
quote = "<enum name=\"ADDRMODE\">"
terms = ["ADDRMODE"]
+++

Line 28 of `texstate.xml` in Mesa's Rogue csbgen names `ADDRMODE`. It backs the glossary enum value
`ADDRMODE`: (Rogue) texture address modes REPEAT, FLIP, CLAMP_TO_EDGE...; on SGX545 the T0 wrap
fields: 0 repeat, 1 mirror, 2 clamp, 3 mirror once (T0.ADDRMODE_U, T0.ADDRMODE_V).
