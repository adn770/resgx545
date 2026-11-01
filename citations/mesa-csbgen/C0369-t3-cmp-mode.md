+++
id = "C0369"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/texstate.xml:492"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/texstate.xml#L492"
quote = "<field name=\"cmp_mode\" start=\"59\" end=\"61\" type=\"CMP_MODE\">"
terms = ["T3.CMP_MODE"]
+++

Line 492 of `texstate.xml` in Mesa's Rogue csbgen names `cmp_mode`. It backs the glossary bit field
`T3.CMP_MODE`: the comparison of smp.pcf/.pcff16 against the reference: 0 never, 1 less, 2 equal, 3
less or equal, 4 greater, 5 greater or equal, 6 not equal, 7 always.
