+++
id = "E307"
claim = "The region test fitted to 26 shifts of one triangle (E180: a bounding box half-open between a region's two 16x16 tiles, then each edge against the tiles' corners) predicts exactly the regions and the PRIM_TILES form of 24 fresh random triangles on 128x128, among them triangles reaching past the target's edges: 265 regions predicted, 265 streamed, none missing, none extra, none of another form; the triangles test the generic overlap, not the fitted boundary rules: no vertex or edge of theirs lands on a tile boundary, so a plain overlap test, closed or open, gives the same tiles in all 768 regions, and only the forms 0x80, 0x90 and 0x98 occur; one run"
unit = "ta"
method = "probes/ta/object-words.toml on the laptop, linux fork with the debug option on: its probe ta-object-words-random draws 24 triangles (seed 1108, vertices in 1/16 pixel from -16 to 144 pixels, at least 24 square pixels each) through the vertex shader vtx_affine.s, which maps the library triangle onto each by an affine map (isp_words.py affine_params), on a 128x128 target, the render memory dumped after each; the regions compared by ta_words.py regions (region_tiles.py's test)"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["ta-object-words"]
terms = ["CSTREAM.PRIM_TILES", "REGION_HDR.POS", "control stream"]
+++

**What runs.** Fresh triangles, not the shifts the test was fitted on: random sizes, shapes and
orientations, 20 of them with a vertex outside the target.

**Results.** For every triangle the regions with a stream are exactly the regions the test predicts,
and each stream's first primitive word carries a `CSTREAM.PRIM_TILES` form of the predicted tile
pair (0x80 or 0x8a the left tile only, 0x98 or 0x8c the right only, 0x90 both): 265 regions over the
24 triangles, from 3 to 20 a triangle. The forms seen are 0x80 (61 regions), 0x90 (154) and 0x98
(50); 0x8a and 0x8c never occur. A plain separating-axis overlap of the triangle and each 16x16
tile, with every edge closed or every edge open, gives the fitted test's tile pair in all 768
regions of the 24 triangles (test_ta_words.py).

**What it shows.** The 24 triangles confirm the test as a generic overlap of the triangle and the
tiles, also where a triangle leaves the target [infer: 24 triangles, one size]. They do not test
what the fit decided beyond it, the bounding box half-open between a region's two tiles and the
closed corners: no vertex or edge of theirs lands on a tile boundary, and the wide-mask forms 0x8a
and 0x8c do not occur. Those rules rest on the 26 fitted shifts alone (E180). Lines and points are
not tested here.
