+++
id = "Q284"
question = "what does a TEXTYPE 2 cube sample read at an exact texel boundary when |ma| is not a power of two (E923: 14 of 207 such pixels one texel low, the rest up), at a tie between the two largest coordinates, under bilinear filtering across a face edge, and with faces other than 16 x 16"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E726", "E567", "E844", "E923"]
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
