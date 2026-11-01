+++
id = "E364"
claim = "In the closed driver's 114 captured primary pixel programs with a texture fetch, DOUTU1 bit 24 is set exactly when one of their douti iterates an attribute into the primary attribute registers (DOUTI0 source field 16:11 below 36: the vertex colour 32 or a coordinate set 1 to 3), 21 of 21, and every USSE program those 21 start reads that iterated register; in the 93 without it every douti has source 36, which writes no attribute register, and their programs read only fetched texels"
unit = "pds"
method = "the thirteen 3D capture tables of 11.11 (the closed GLES1 and GLES2 stacks under the harness on the laptop), unpacked with cap3d.py: each MTE state block's primary pixel program decoded by state3d.py's walker into its dout writes (DOUTU1, each douti's source, component and coordinate fields, the doutt count), the USSE program each doutu starts disassembled with our usse-dis and only the primary attribute registers it reads and writes listed, and where its first wdf lies; counts and register numbers only"
tiers = ["CAP", "infer"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = ["DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH"]
+++

**Results.**

| group | state blocks | USSE programs | douti sources | attribute registers read | an iterated one read |
|---|---|---|---|---|---|
| bit 24 set (DOUTU1 0x03000004) | 21 | 17 | 32 in 18, 1 in 2, 3 in 1 | pa0-pa1 (16), pa0-pa2 (5) | 21 of 21 |
| bit 24 clear (0x02000004) | 93 | 9 | 36 in all | pa0 (89), pa0-pa1 (3), pa0-pa3 (1) | 0 of 93 |

- The set group is GLES1's combine modes, `tex_add`, `tex_blend`, `tex_decal`, the lit and fogged
  textured programs and the two-texture modes, and GLES2's `tex2`, `tex2_mip`, `fs_tex_modulate`,
  `fs_tex_two` and `fmt_lf16`; the clear group the GL_REPLACE program and the GLES2 programs that
  only return the texel (`fs_tex2d`, `fs_texcube`, `fs_tex_dependent` and the texture tables').
- In the set group every program reads its iterated register in its first or second instruction,
  the colour programs together with the texel; in the clear group every register read is a
  texel. The douti's component field is 0 in the clear group and 1 to 3 in the set group, and every
  set-group douti has bit 29 or 30. The douti and doutt counts do not separate the groups (one
  each in 89 clear and 17 set blocks).
- Every primary resolved to its USSE program.

**What it shows.**

- The closed driver asks the primary to wait for its iterations (bit 24) exactly when it iterates
  something besides the fetch coordinates into the attribute registers, which the program then
  reads [CAP]. Which register holds the texel and that source 36 writes nothing are readings
  (E132's order, the glossary's row) [infer]; whether the bit is needed, rather than chosen, was
  tried on the hardware in 11.16: it is not needed under the fetch wait (E436).
