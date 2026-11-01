+++
id = "C0218"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/texstate.xml:517"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/texstate.xml#L517"
quote = "<field name=\"mipfilter\" start=\"40\" end=\"40\" type=\"bool\">"
terms = ["T0.MIPFILTER"]
+++

Line 517 of `texstate.xml` in Mesa's Rogue csbgen names `mipfilter`. It backs the glossary field
`T0.MIPFILTER`: filter between mipmap levels: 0 the nearest level (a half rounds up), 1 a linear
blend of the two levels.
