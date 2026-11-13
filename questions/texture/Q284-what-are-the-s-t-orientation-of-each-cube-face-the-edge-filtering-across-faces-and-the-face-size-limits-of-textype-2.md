+++
id = "Q284"
question = "what does a TEXTYPE 2 cube sample read at an exact texel boundary when |ma| is not a power of two (E923, E931, E956: up or down by the boundary's place, a pattern that moves at |ma| 1.25), at a tie of the two largest coordinates when the third is large (E956: the higher axis's face on every sweep, the lower on 7 of 599 kept tie pixels), and which texel the out-of-face tap of a bilinear sample reads at a face edge (E956: the adjacent one on one edge of two)"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E726", "E567", "E844", "E923", "E930", "E931", "E951", "E955", "E956"]
terms = ["TEXTYPE"]
+++
E726: the six faces are six consecutive 256-dword blocks in the order +x, -x, +y, -y, +z, -z for a
16 x 16 face, and each axis direction reads one face (2048 of 2048). The face-local index is not
decoded (12 to 252, 144 to 169 distinct values a job); the boundary between two faces (|w| = |u|)
was not tested; one size only. To settle it: freeze a (s, t) rule from the six face jobs (decode
the local index per pixel against the coordinates), predict a different set of directions (off-
axis, with the three coordinates all different in magnitude), a w sweep through the boundary at
1/16 steps, bilinear at a face edge, and 8 x 8 and 32 x 32 faces.

Status: open. Split from the cube-map question, since answered by E844 (the TEXTYPE, the face
order and the face select are known).

Note 2026-11-11 (round 4, E844). The face select is held out: two off-axis programs read the face
of the coordinate of largest magnitude and its sign on 2048 of 2048 pixels each (all six faces
between them, no pixel within 0.0078 of a tie), so the question this one narrowed is answered and
retired; the faces' (s, t), the edges and ties between equal magnitudes stay here. E844's kept
pixel values (the dword index read) are inputs for a (s, t) fit, with the six axis jobs of E726.

Narrowed 2026-11-13 (round 8 offline, decisions R8-1 a and R8-4 a; E923). The faces' (s, t) is
answered: the public cube-map table (our u, v, w as x, y, z), texel floor((q + 1) / 2 * 16) and the
Morton index with t in bit 0, fitted on E726's eight jobs, frozen by hash and held out offline on
E844's two off-axis jobs at 4090 of 4096 pixels; sgx-pipe's `cube::point_index` models it. Every
miss is an exact texel boundary with |ma| not a power of two (one texel low; at a power of two the
upper texel every time), and no rounding of the reciprocal and product tried fits all 58 such
pairs. What stays: that tie rule, a tie between the two largest magnitudes (never run), bilinear
filtering across a face edge, and faces of 8 x 8 and 32 x 32, which session r8-geo's R8-2 rows
test ((b) the sizes, (c) the ties, (d) the edge); the question retires when they are decided.

Narrowed 2026-11-13 (round 8, session r8-geo, decision R8-4 a; E930, E931). On hardware rows never
used for a fit, E923's (s, t) rule held out on four new off-axis 16 x 16 programs (all six faces)
and, as the same rule with N = 8, on three programs at 8 x 8 faces (faces 64 dwords apart). At 32
x 32 faces sit 1024 dwords apart but the local index is not the 5-bit Morton: post hoc, the fifth
bits of s and t sit in the other order (4831 of 4831 pixels, fitted). Readings: a face tie |w| =
|u| went to w's face for both signs of u (64 of 64); exact texel boundaries at |ma| 1.75, 1.625 and
1.875 go up or down by the boundary in one pattern, at 0.90625 always up (post hoc pattern);
bilinear at a face edge read a G byte of another face in the one decided job (H-SEAM held, H-CLAMP
failed; the other job cannot tell). Not retired: what stays is the 32 x 32 index held out, the
face-tie rule for other axis pairs, the texel-tie rule, and which neighbour texels an edge's taps
take.

Note 2026-11-13 (round 9 offline, decision S-2 a, E951; the question line is unchanged). E930's
post hoc 32 x 32 index is E561's twiddle law of a 32-bit texture at every (s, t): tiles of 16 x 16,
the tiles in raster order with s first (bit 8 = s4, bit 9 = t4), a law recorded before E930 ran
but not frozen for it. sgx-pipe's `cube::point_index` takes 32 x 32 faces with that index and
replays E930's three jobs with every predicted pixel matched. The 32 x 32 clause narrows to a
held-out row on new directions; 64 x 64 faces part E561's law (s4, s5 in bits 8 and 9, t4, t5
in 10 and 11) from a pairwise order (s4, t4, s5, t5) at half the texels: the round 9 seeds' stage
cube2 runs both, with the face ties of the other axis pairs and the edges.

Narrowed 2026-11-13 (round 9, session r9-geo, decision R9-3 a; E955, E956; the question line is
rewritten to what stays). The face sizes are answered: faces of 32 x 32 and 64 x 64 read E561's
twiddle law (16 x 16 tiles in raster order with s first), held out on three new directions each,
against E923's plain Morton and, at 64, a pairwise order of the bits above 7 (0 of 3); 4 x 4 faces
sit 16 dwords apart with a 2-bit Morton (2 of 2, against 64 apart); sgx-pipe's
`cube::point_index` models faces of 4 to 64. A face tie goes to the higher axis (z over y over x)
on four held-out sweeps of x = y and y = z with the tied coordinates of opposite signs (128 of 128
tie pixels; the lower axis and the positive one refuted), but post hoc 7 of the 599 tie pixels of
every kept cube job read the lower axis's face, all with the third coordinate 0.62 to 0.93 of |ma|:
no rule, and sgx-pipe still refuses ties. Texel ties at |ma| 1.5 follow E931's table, at 1.25 two
boundaries go the other way. At a face edge the out-of-face tap reads the neighbour face near the
adjacent texel (the wrapped local texel refuted 0 of 2), exactly on -y/+x and not on +z/+x. What
stays is in the question line.
