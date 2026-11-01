+++
id = "C0301"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/cr.xml:643"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/cr.xml#L643"
quote = "<struct name=\"TE_PSG\" length=\"1\">"
terms = ["CR_TE_PSG"]
+++

Line 643 of `cr.xml` in Mesa's Rogue csbgen names `ROGUE_CR_TE_PSG`. It backs the glossary register
`CR_TE_PSG`: tiling-engine control word: bit 22 set on the kick that ends the scene (with the word
at 0 the job faults), bit 21 makes the TA mark every target region header (REGION_HDR.FLAGS bit 29),
bit 25 with a depth/stencil buffer (Rogue analogue).
