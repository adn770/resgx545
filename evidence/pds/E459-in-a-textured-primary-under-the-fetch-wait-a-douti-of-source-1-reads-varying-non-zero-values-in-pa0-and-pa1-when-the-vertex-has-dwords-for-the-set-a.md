+++
id = "E459"
claim = "In a textured primary under the fetch wait, a douti of source 1 reads varying non-zero values in pa0 and pa1 when the vertex has dwords for the set (a set of two or three dwords, the colour dwords then a set, and with the colour select word's vertex size matching 6, 7 or 8 coordinate dwords); with the select word left at size 8 over a vertex of 10 or 11 dwords and the default coordinate-size word pa0 and pa1 read 0 in every triangle pixel (16 of 16 jobs, 856 pixels), and a coordinate-size word of 2 or 0x12 on 6 coordinate dwords or 3 on 7 faults every job (24 of 24 with the vertex size matching, 36 of 36 with it left at 8)"
unit = "pds"
method = "probes/pds/iter-coords-arrive.toml, iter-coords-colour.toml and iter-coords-sized.toml on the laptop (direct cable): textured primary pds_tex_col.s (a douti of source 1 or 2 with two or three components, the fetch, a doutt) with DOUTU1 0x02000004 on vertex shaders vtx_coords.s, vtx_coords3.s, vtx_color2.s, vtx_color3.s and vtx_color4.s (coordinate dwords after the position and after the colour in o4-o7), state words 13 and 16 as listed, pa0 to pa2 read in separate probes, every pixel of the 64x64 triangle compared by its value; 60, 60 and 72 jobs, one run of each case"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["pds-iter-coords-arrive", "pds-iter-coords-colour", "pds-iter-coords-sized"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTI0.LAST_ITER", "OUTSEL.VTX_SIZE", "COORDSIZE.SET_LAYOUT"]
+++

**What runs.** E454's coordinate registers read 0 in every pixel. Its vertices held the position
and the colour only (`--vtx-coords 4`, state word 13 = 0x83800: vertex size 8, the colour select),
so a coordinate set after the colour had no vertex dwords. Three tables put dwords there. All use
the textured primary `pds_tex_col.s` (one douti, the fetch's douti 0x46012201 and a doutt on the
16x16 scratch texture) with DOUTU1 = 0x02000004 (the fetch wait, bit 25), the 64x64 triangle (1062
pixels), and read pa0, pa1 and pa2 in separate probes (the register the shader writes out as the
colour); each probe has four cases: the douti `0x20400800` (source 1, two components), `0x20401000`
(source 2, two components), `0x20800800` (source 1, three) and `0x20801000` (source 2, three).

- `pds/iter-coords-arrive` (5 layouts, 60 jobs): a, one 2-dword set (`--vtx-coords 2`,
  `vtx_coords.s`, as E436); b, the colour in o4-o7 and a 2-dword set in o8, o9 (`--vtx-coords 6`,
  `vtx_color2.s`) with word 13 = 0x83800; c, the same vertex with the default state words; d, one
  3-dword set (`--vtx-coords 3`, o6 = 0.25); e, `--vtx-coords 7` (o8-o10) with word 13 = 0x83800.
- `pds/iter-coords-colour` (5 layouts, 60 jobs): word 13 = 0x83800 kept with longer vertices and
  coordinate-size words (word 16) of 2, 0x12, 3 on vertices of 6 and 7 coordinate dwords, and 5 and
  2 on 8.
- `pds/iter-coords-sized` (6 layouts, 72 jobs): word 13 made to the vertex's size (0xa3800,
  0xb3800, 0xc3800 for 6, 7, 8 coordinate dwords, the vertex size field being bits 19:16) with the
  default word 16 (0x15, 0x1d, 0x2d), and word 16 = 2 on 6, 3 on 7 and 5 on 8.

**Results**, pa0 (X: varying non-zero values over the 1062 pixels, for example 0xbeb80000 on 44
pixels; Z: 0x00000000 in every triangle pixel; the cases are source 1 with two components, source 2
with two, source 1 with three, source 2 with three; pa1 reads alike except for source 2 in sized k,
below; pa2 the texel or the third component):

| table, layout | what the vertex has | word 13, word 16 | cases (pa0) |
|---|---|---|---|
| arrive a | one 2-dword set | default | X Z X Z |
| arrive d | one 3-dword set | default | X Z X Z |
| arrive c | colour dwords, 2-dword set | default | X X X X |
| arrive b | colour, 2-dword set | 0x83800, default | Z Z Z Z (856 triangle pixels) |
| arrive e | colour, 3-dword set | 0x83800, default | Z Z Z Z (856 triangle pixels) |
| sized f | colour, 2-dword set | 0xa3800, 0x15 | X Z X Z |
| sized h | colour, 3-dword set | 0xb3800, 0x1d | X Z X Z |
| sized j | colour, 4-dword set | 0xc3800, 0x2d | X Z X Z |
| sized k | colour, 4-dword set | 0xc3800, 5 | X Z X Z |
| sized g | colour, 2-dword set | 0xa3800, 2 | all faulted |
| sized i | colour, 3-dword set | 0xb3800, 3 | all faulted |

In `iter-coords-colour` 36 of 36 jobs on vertices of 6 and 7 coordinate dwords faulted (word 13 =
0x83800 kept, word 16 = 2, 0x12 or 3), and the 24 jobs on 8 coordinate dwords (word 16 = 5 or 2)
drew no triangle pixel (the image was all background, 0 triangle pixels in 24 of 24). In
`iter-coords-sized` the 24 faulted jobs are those of layouts g and i (BIF fault status `0x92000` in
12, `0xd2000` in 12); the other 48 jobs rendered. `iter-coords-arrive` had no fault. kernel.log is
authoritative for the fault lines (36 in colour, 25 in sized, 24 of them "stalls job N,
recovering"); no recovery failed in any of the three.

**What it shows.**

- A coordinate set arrives in pa0 and pa1 when the vertex carries dwords for it: varying, non-zero
  values in arrive a and d, whose vertices have no colour dwords, under the fetch wait [HW]. In
  arrive c and sized f, h, j and k the values are the same x and y, which the colour's o4, o5 and
  the set's o8, o9 both hold, so which dwords source 1 reads is not separated there [infer]. The
  third component of a 3-component douti reads 0.25 (0x3e800000) in all 1062 pixels where
  the vertex wrote 0.25, as the model of 3d.md section 9.4 says [HW].
- E454's zeros are the vertex without the dwords: with the select word at size 8 and a vertex of 10
  or 11 dwords (arrive b and e) the same douti reads 0 in all triangle pixels and the triangle has
  856 pixels, and with the size field made to the vertex (sized f and h) the coordinates arrive
  [HW]. That E454's vertices (colour only, size 8) lacked the dwords the douti read is the reading
  these fit [infer].
- Source 2 reads 0 in pa0 in sized f, h, j and k and in pa1 in f, h and j; in sized k pa1 it reads
  1.0 (0x3f800000) in all 1062 triangle pixels of cases 1 and 3 [HW]. Which vertex dword that 1.0
  comes from is not shown. In arrive c source 2 gives the same histogram as source 1 (0xbeb80000
  x44, 0xbec80000 x43, 0xbea80000 x43 in all four cases, pa0 and pa1) [HW]; whether it reads a
  second set there is not shown, since the colour's o4, o5 and the set's o8, o9 hold the same x and
  y.
- A coordinate-size word of 2 or 0x12 on 6 coordinate dwords, or 3 on 7, faulted every job: 24 of
  24 with the vertex size field matching (sized g and i) and 36 of 36 with it left at 8 (colour f,
  g and h) [HW]. With the size field left at 8 and the default word 16 nothing faulted (arrive b
  and e: 24 jobs rendered, the set reading 0), so the size mismatch alone does not fault [HW].
  Word 16 = 5 or 2 on 8 coordinate dwords with the size left at 8 did not fault and drew no
  triangle pixel (24 of 24) [HW].

**What it does not show.** Which vertex dwords source 1 and 2 read where the colour's o4, o5 and
the set's o8, o9 hold the same values (arrive c, sized f, h, j, k; the layouts' first and second
sets both begin with x), what the 1.0 of sized k pa1 is, and the same layouts without the fetch
wait.

**Provenance.** linux fork commit 6ee9501832af with the debug option on, module srcversion
14D099861204842EA496D85 (read by the campaign with modinfo from the installed module file and named
in each env.toml; the run script compared it with the loaded module's /sys/module value before the
run, outside the data, and neither is printed in the dataset), sgxfive-test sha256
2c2949e4e6bf9b6120a63014770f0bdc1dabb4e9249046c792dd08fb88fe1b8d (built from this phase's overlay
source as it stood at the run, named in each env.toml), the laptop over the direct cable. Three
builds of the tool ran in this phase (this one predates the rename of --depth-clear to --depth-base
and the registers at the words snapshots; the probe subcommand is the same in all three); the
sha256 of each dataset's build is in its env.toml.
