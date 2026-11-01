+++
id = "E345"
claim = "The secondary pixel program an MTE state block names is a lone doutu (no constants), one or two doutd of 10 to 18 constant dwords then a doutu, or in GLES1 a doutu then three or four douta, with DOUTU1 0 or 0x4; the primary is a doutu followed by one douti per iterated set and one doutt per texture fetch, each fetch after the douti of its coordinates, with DOUTU1 0x4 when it iterates nothing, 0x01000004 when it iterates without fetching (0x01000006 in three branching shaders), 0x02000004 in most textured programs and 0x03000004 in every textured GLES1 program but GL_REPLACE's and in five GLES2 ones (texture times colour, two textures, a half-float luminance texture); the special object's programs are a lone doutu and a doutu, douti and doutt with 0x02000004"
unit = "pds"
method = "the thirteen 3D capture tables of 11.11 (the closed GLES1 and GLES2 stacks under the harness on the laptop): the secondary and primary programs of every MTE state block's pds_sec and pds_pri and of the TA command's special object words, decoded by state3d.py's walker (mte.sec, mte.pri, spec.sec, spec.pri) into their dout writes"
tiers = ["CAP"]
date = "2026-11-03"
data = [
    "render-state-variations", "render-register-gaps", "render-draws-frames-pb",
    "isp-registers", "isp-line-width", "texture-textures", "texture-samplers",
    "texture-formats", "texture-streams", "usse-inputs", "usse-gles1-programs",
    "usse-shaders", "ta-target-sizes",
]
terms = [
    "PDS_PRIMARY.USE_KICK", "PDS_SECONDARY.USE_KICK", "DOUTU1.WAIT_ITER", "DOUTU1.WAIT_FETCH",
    "DOUTU1.BIT2", "PORT.DOUTU", "PDS_SIZE.BITS24_18",
]
+++

**What runs.** 1232 MTE state blocks with pixel programs and 1263 special objects over
thirteen tables; each program's movs are decoded to the port they
write and the data words they read.

**Results.**

| program | dout writes, in order | DOUTU1 | programs |
|---|---|---|---|
| MTE primary | doutu | 0x4 | 393 |
| | doutu, douti (one to eight) | 0x01000004 | 722 |
| | the same | 0x01000006 | 3 |
| | doutu, douti, doutt (one to four pairs, a douti more) | 0x02000004 | 93 |
| | the same | 0x03000004 | 21 |
| MTE secondary | doutu | 0x0 (744), 0x4 (3) | 747 |
| | doutd (one or two), doutu | 0x4 (415), 0x0 (59) | 474 |
| | doutu, three or four douta (GLES1) | 0x0 | 11 |
| special object primary | doutu, douti, doutt | 0x02000004 | 1263 |
| special object secondary | doutu | 0x0 | 1263 |

- The doutu comes first in every primary and in every secondary but the constant-loading GLES2
  ones, where the doutd comes first. The doutd copies the program's constants (the triangle's
  colour as half floats among them), and their count, in rows of four, is the size word's bits
  24:18 (E343).
- A doutt always follows the douti that iterates its coordinates; the float RGBA texture's four
  fetches are four douti and doutt pairs (E342).
- 0x03000004 appears in every textured GLES1 program but GL_REPLACE's (the combine modes, the
  texture environments, two textures, fog and lighting with a texture) and in GLES2's
  fs_tex_modulate, fs_tex_two, tex2, tex2_mip and fmt_lf16; 0x02000004 in every other textured
  program (the YUV streams and the float RGBA texture included). The douti and doutt counts do
  not tell the two apart: one pair gives either.
- 0x01000006 is fs_loop_uniform's, fs_nested_if's and uni_loop_ui's, the only primaries with
  bit 1.
- The doutd secondaries with DOUTU1 0 are in the shader corpus, the cube maps and tex2; the
  others carry 0x4.

**What it shows.**

- The closed driver sets `DOUTU1.WAIT_FETCH` (bit 25) on every primary with a doutt and on no
  other, and `DOUTU1.WAIT_ITER` (bit 24) on every primary that iterates without fetching [CAP].
  With a fetch, bit 24 is added where the program uses something besides the coordinates'
  texel: the vertex colour (GLES1's environments, fs_tex_modulate) or a second texture; the
  half-float luminance texture also carries it, so the rule is not settled (Q093) [infer].
- `DOUTU1.BIT2` is set on every primary, the special object's included, and on 415 of the 474
  constant-loading secondaries; bit 1 is set only in three shaders with loops or branches;
  neither is tied to a program shape beyond that [CAP].
- The secondary program is where the closed driver loads per-draw constants: by DMA from the
  PDS data in GLES2, by douta writes in GLES1 [CAP].
