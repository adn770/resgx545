+++
id = "C0711"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/pbestate.xml:337"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/pbestate.xml#L337"
quote = "<field name=\"address_low\" start=\"0\" end=\"31\" shift=\"2\" type=\"address\">"
terms = ["EMIT3.ADDRESS"]
+++

Line 337 of `pbestate.xml` in Mesa's Rogue csbgen names `address_low`. It backs the glossary field
`EMIT3.ADDRESS`: surface address >> 2 (the surface base; the PBE adds the tile offset).
