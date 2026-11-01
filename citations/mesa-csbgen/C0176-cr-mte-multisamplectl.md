+++
id = "C0176"
source = "mesa-csbgen"
locator = "src/imagination/csbgen/rogue/cr.xml:707"
link = "https://gitlab.freedesktop.org/mesa/mesa/-/blob/ab2374a4a18ba0ae4c11d499ac35607dd7bbb571/src/imagination/csbgen/rogue/cr.xml#L707"
quote = "<struct name=\"PPP_MULTISAMPLECTL\" length=\"2\">"
terms = ["CR_MTE_MULTISAMPLECTL"]
+++

Line 707 of `cr.xml` in Mesa's Rogue csbgen names `ROGUE_CR_PPP_MULTISAMPLECTL`. It backs the
glossary register `CR_MTE_MULTISAMPLECTL`: the sample positions on the TA side: the TA command word
that loads it carries CR_ISP_MULTISAMPLECTL's value in every capture, 0x88 with one sample,
0xeaa26e26 with 4x multisampling [infer].
