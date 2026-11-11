+++
id = "Q113"
question = "how does the sampler address the six faces of a cube map: which TEXTYPE and word layout name one, how are the faces laid out in memory, and how are they picked from the coordinates?"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E342", "E345", "E364", "E567", "E725", "E726"]
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

Narrowed in 11.32 (E567). smp3d at third coordinates from -0.5 to 4 read the smp2d image on
twiddled and stride textures (8 of 8 jobs and 3 sweeps), and TEXTYPE 7 read the twiddled image; no
cube reading was identified. TEXTYPE 2 gives three different images under smp2d, smp3d at 0.5 and
smp3d at 1.5, the only type of eight on which the third coordinate acts: a candidate, with no cube
face read yet (Q178 carries the observations). The six cube directions of the plan were not run.

Run in 11.39 (E725, E726): types 3 and 1 read a raster of w dwords per row (8 jobs held out,
8 x 8 to 32 x 32); E567's "fixed 16" was the 16 x 16 case. Type 4 reads 32 dwords per row at 8,
16 and 32 wide [fitted, Q283]. TEXTYPE 2 with smp3d is a cube: six faces of 256 dwords (a 16 x 16
face), face = +x, -x, +y, -y, +z, -z along the dominant axis (exploratory: the plan predicted only
faces 1, 3, 5 for the negative axes; the mapping and the dominant-axis rule are post hoc [infer],
checked on cu-w02). Open: the faces' (s, t), the edges, other sizes (Q284); type 5 not run.

Note 2026-11-11 (round 4, decision R4-3; not retired). E725 and E726 answer the main clause (TEXTYPE
2 with smp3d is the cube, six faces of 256 dwords, face order +x, -x, +y, -y, +z, -z), but the face
mapping and the dominant-axis rule are post hoc [infer] (E726; the plan predicted only faces 1, 3
and 5), so the question waits for a 2-job held-out cube row before it is retired as answered. The
faces' (s, t) and the edges are Q284's.
