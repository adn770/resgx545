+++
id = "C0710"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/pbestate.xml:412"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/pbestate.xml#L412"
quote = "<field name=\"linestride\" start=\"34\" end=\"49\" type=\"uint\">"
terms = ["EMIT2.LINE_STRIDE"]
+++

Line 412 of `pbestate.xml` in Mesa's Rogue csbgen names `linestride`. It backs the glossary field
`EMIT2.LINE_STRIDE`: surface line stride, in pairs of pixels less one: the row pitch in pixels / 2 -
1, in RGB565 and ARGB8888 alike.
