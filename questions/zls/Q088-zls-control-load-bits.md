+++
id = "Q088"
question = "what reads the render details' unpatched ZLS control word that the closed driver writes between frames (0x0011700a), now that bit 14 is known to load the depth and bit 13 the stencil?"
unit = "zls"
kind = "fw"
phase = 11
evidence = ["E335", "E336", "E337", "E411", "E467", "E665", "E997", "E989", "E1014"]
terms = ["CR_ISP_ZLSCTL", "hw_render_details.isp_zlsctl"]
+++

The hardware part of this question is answered (E467): with bit 1 the load is on, bit 14 loads the
depth and bit 13 the stencil, each from the address the store writes, the loaded depth takes part
in the depth test and its sign bit is cleared. E411 had found that bits 13 and 14 act only with bit
1 and that the loaded sentinel 0xdeadbeef came back as 0x5eadbeef; E467 shows which bit loads what,
with a stencil buffer of its own.

The closed driver's first render of a window surface stores depth and stencil with `CR_ISP_ZLSCTL`
`0x0017100c`; every later render, cleared or not, has `0x0017700e`, bits 1, 13 and 14 added, and
`ExternalZBufferMode=2` gives `0x0017300e` (1 and 13, not 14) from the context's setup (E335,
E337). Every window render has both ZLS render flags, so no capture parts depth from stencil.
Between frames the driver also writes `0x0011700a` into the render details' own word, which the
next render's 3D patch overrides (E336); no captured kick shows what reads it (a partial render's
reload is a candidate).

What is open is the closed firmware's or driver's behaviour, parked as kind fw: what reads the
unpatched word. Whether the final render's reload loads the depth at all is the hardware question
of Q038, not this one. To settle it: a scene that runs out of parameter memory with the render
details' word poked to a marked value, to see whether the partial render's reload takes it (the
same job answers the reload half of Q038; the tile pitch and the stores of E465 make the marked
word readable now).

Round 12 cites, context for the word's bits: E665 (the ZLS control fields decoded), E997 and E989
(bits E411 flipped singly, flipped together), E1014 (the stencil test under E989's control reads 0).
