+++
id = "Q114"
question = "does a texture word other than TEXTYPE name a 3D (volume) texture (no TEXTYPE value does, E567, E726), and if one does, how are its slices laid out and how do the third coordinate and the filter combine them?"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E342", "E567", "E726", "E923", "E930", "E894", "E910", "E911", "E940", "E941", "E942", "E958"]
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
(type 2 is the cube, E726), as are the slice layout, the third coordinate's mode and filter and a
volume's mip chain.

Narrowed in round 12 (decision R12-7 a): no TEXTYPE value names a volume [infer]. Of the eight E567
ran, only type 2 follows smp3d's third coordinate, and type 2 is the cube (E726; its face rule held
out, E923, E930); the others are 2D layouts: 0 and 7 twiddled, 6 strided, 1 and 3 rasters (E910,
E940), 4 blocks of 32 x 32 (E941, E958) and 5 one bit a texel (E894, E911, E942), and on types 0, 3
and 6 the third coordinate changes nothing (E567). What stays open is whether another word (T0 to
T3, Q078's unexplained bits) names a volume; the slice layout, the third coordinate's mode and
filter and a volume's mip chain are moot until one does. The question retires on a word sweep that
finds none, or is answered by one that finds it.
