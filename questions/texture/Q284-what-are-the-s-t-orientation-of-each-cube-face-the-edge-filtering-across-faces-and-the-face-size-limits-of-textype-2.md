+++
id = "Q284"
question = "what are the (s, t) orientation of each cube face, the edge filtering across faces and the face size limits of TEXTYPE 2"
unit = "texture"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E726", "E567", "E844"]
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
