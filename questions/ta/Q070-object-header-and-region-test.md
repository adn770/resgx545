+++
id = "Q070"
question = "what are the TA object's three header words made from, do its set masks mean half precision, one component, has z and has w, and does the fitted region test hold beyond the triangles it was fitted to?"
unit = "ta"
phase = 11
evidence = ["E176", "E177", "E180", "E181", "E185"]
terms = ["PB_OBJ.PDS_WORDS", "PB_OBJ.SET_MASKS", "CSTREAM.PRIM_TILES", "REGION_HDR.POS"]
+++

The object starts with three header words, read as the pixel program's words (E176), and its four
set masks follow the half-precision and coordinate-size settings (E176, E181). A bounding-box and
edge test reproduces all 472 regions of 26 shifted triangles (E180); the region headers place each
32x16 region (E177).

What is open (3d.md §10.1 and §10.2): the header words' origin, the set masks' meaning, whether
the region test holds for other triangles, and that the ISP walks the headers [infer].

To settle it: on the laptop, the header words read over the PDS program's words varied one at a
time; the set masks over every half-precision and coordinate-size setting; the region test checked
on a fresh set of random triangles, lines and points (pbdump), not the fitted ones.
