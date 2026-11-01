+++
id = "Q201"
question = "why does the position source (E437, E502: x + 0.375, y + 0.125 in mode 0 and every multisampling mode tried) differ from the point at which coordinate-set attributes are evaluated (the pixel centre, E606, for the one iteration setup used), and does an attribute iterated with the position's source read the same way"
unit = "isp"
kind = "hw"
value = "low"
phase = 11
evidence = ["E606", "E437", "E502"]
terms = []
+++
In 700 triangles E606 fits pa0 (the vertices' clip z) and pa1 (their clip x) of source 1 (two
components, E437's program) to the plane at the pixel centre (none of the other 255 points of the
1/16 grid fits better; (0.375, 0.125) is the 96, 32 cell and does not). E437 and E502: source 0
reads x + 0.375 and y + 0.125 under every mode. A simulator needs both as separate rules; the
reason matters for 4x, where E502 saw the same offsets under every sample mode.

To settle it: iterate a coordinate set carrying the vertices' own window x and y (vtx coords equal
to the position) and a source 0 position in the same program, on a triangle at several places, and
compare their difference per pixel; repeat under mode 2 and the closed driver's 4x words.
