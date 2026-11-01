+++
id = "Q088"
question = "which of CR_ISP_ZLSCTL bits 1, 13 and 14, which the closed driver adds when a render loads a kept depth and stencil buffer, loads depth and which stencil, and what reads the render details' unpatched ZLS word the driver writes between frames?"
unit = "zls"
kind = "hw"
value = "high"
phase = 11
evidence = ["E335", "E336", "E337", "E411"]
terms = ["CR_ISP_ZLSCTL", "hw_render_details.isp_zlsctl"]
+++

This narrows Q071, which asked what the ISP word 2 and ZLS control values of a depth-buffered
render are: E335-E337 give the closed driver's values, and what is left is below.

The closed driver's first render of a window surface stores depth and stencil with
`CR_ISP_ZLSCTL` `0x0017100c`; every later render, cleared or not, has `0x0017700e`, bits 1, 13 and
14 added, and `ExternalZBufferMode=2` gives `0x0017300e` (1 and 13, not 14) from the context's
setup (E335, E337). Every window render has both ZLS render flags, so no capture parts depth from
stencil. Between frames the driver also writes `0x0011700a` into the render details' own word,
which the next render's 3D patch overrides (E336); no captured kick shows what reads it (a
partial render's reload is a candidate).

To settle it: on the laptop, a two-render job of our own stack with a depth and stencil buffer
(as `probes/zls` runs do) whose second render takes `0x0017100c` with each of bits 1, 13 and 14
added alone and in pairs, reading back the depth test's outcome against the first render's depth
and a stencil test against its stencil; and a scene that runs out of parameter memory, with the
render details' word poked to a marked value, to see whether the partial render's reload takes it.

Narrowed in 11.15 (E411, two runs each): bits 13 and 14 act only with bit 1 set. In a store
arrangement 0x17300e (bits 1 and 13 added to 0x17100c) stores the depth and no stencil, 0x17500e
(bits 1 and 14) the stencil and a depth page of 0x5eadbeef (the loaded sentinel read as a depth),
0x17700e the 0x5eadbeef depth and no stencil; without bit 1 the control's stores. In a load
arrangement (depth 0.25f loaded, the triangle at z 0.5, depth test less) the load-only 0x11700a
leaves 936 pixels wrong, 0x17300e 512 and 0x17500e and 0x17700e 1382, the control and the words
without bit 1 none. So bit 1 turns the load on, bit 13 concerns the stencil and bit 14 the depth
[infer]. Still open: the stencil load itself, and what reads the unpatched word the driver writes
between frames (the partial render's reload was not run). Status: narrowed, not answered.
