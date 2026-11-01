+++
id = "C0295"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/cr.xml:823"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/cr.xml#L823"
quote = "<struct name=\"PPP_SCREEN\" length=\"1\">"
terms = ["CR_PPP_SCREEN", "cmd_ta.ppp_screen"]
+++

Line 823 of `cr.xml` in Mesa's Rogue csbgen names `ROGUE_CR_PPP_SCREEN`. It backs the glossary
register `CR_PPP_SCREEN`: screen size in pixels: width - 1 (15:0), height - 1 (31:16) (Rogue
analogue); the square targets measured do not tell which half is the width [infer]; and the glossary
field `cmd_ta.ppp_screen`: screen size in pixels minus one (x 15:0, y 31:16); the EDM copies it into
CR_PPP_SCREEN.
