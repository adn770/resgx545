+++
id = "Q114"
question = "how does the sampler read a 3D (volume) texture: which TEXTYPE or words name one, how are its slices laid out, and how do the third coordinate and the filter combine the slices?"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E342", "E567"]
terms = ["TEXTYPE", "TEXFORMAT"]
+++

The core is built with volume textures (SGX_FEATURE_VOLUME_TEXTURES, doc/specs/hw_spec.md section 2,
from the driver headers). No record shows a texture word or a run for one: the TEXTYPE values seen
are 0, 3 and 6 (the glossary row, E342), and E342's tables list no volume texture.

Open: whether and how a volume texture is named, the slice layout and the twiddling over three axes,
the third coordinate's address mode and filter, and the mip chain of a volume.

To settle it: a volume texture uploaded from the host (a stack of the 2D textures of E035) sampled
by a USSE program with a three-component coordinate set, over the T0 to T3 words and TEXTYPE values
not yet used (Q078 lists the unexplained bits), the result compared with the 2D slices.

Narrowed in 11.32 (E567). The TEXTYPE values 0 to 7 were run at 16x16 (and 6 at 64x32): 7 reads as
twiddled, 1 and 3 as one image, 4 and 5 as one image each, and 2 changes with smp3d's third
coordinate; no volume slice read was identified. Whether type 2 is a volume or a cube is open
(Q178), as are the slice layout, the third coordinate's mode and filter and a volume's mip chain.
