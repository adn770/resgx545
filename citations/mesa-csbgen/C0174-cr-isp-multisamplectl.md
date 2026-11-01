+++
id = "C0174"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/cr.xml:945"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/cr.xml#L945"
quote = "<struct name=\"ISP_AA\" length=\"1\">"
terms = ["CR_ISP_MULTISAMPLECTL"]
+++

Line 945 of `cr.xml` in Mesa's Rogue csbgen names `ROGUE_CR_ISP_AA`. It backs the glossary register
`CR_ISP_MULTISAMPLECTL`: the pixel's sample positions, a byte per sample (x in bits 3:0, y in bits
7:4, sixteenths of a pixel): 0x88 one sample at the centre, 0xeaa26e26 four in a rotated grid with
4x multisampling (Rogue analogue: PPP_MULTISAMPLECTL).
