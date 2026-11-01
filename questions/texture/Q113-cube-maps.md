+++
id = "Q113"
question = "how does the sampler address the six faces of a cube map: which TEXTYPE and word layout name one, how are the faces laid out in memory, and how are they picked from the coordinates?"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E342", "E345", "E364"]
terms = ["TEXTYPE", "TEXFORMAT"]
+++

TEXTYPE 0 is a power-of-two 2D texture, 3 a non-power-of-two one and the YUV streams, and 6 a
strided one (the glossary row, from E342 and E035). The closed driver's shader corpus samples cube
maps (`fs_texcube`, E345, E364), but its cube-map runs give no doutt with data-segment operands, so
the texture words are not read (E342). No record shows a cube map sampled by a run of ours.

Open: the TEXTYPE value or words that make a cube map, the faces' order and distance in memory, the
face select (as a function of the three coordinates a smp instruction takes), and the filtering at a
face's edge.

To settle it: a texture chain of six faces whose texels are the scratch buffer's own dwords (the
tool of E441), sampled by a USSE program that feeds known three-component coordinates to smp, with
the T0 to T3 words varied.
