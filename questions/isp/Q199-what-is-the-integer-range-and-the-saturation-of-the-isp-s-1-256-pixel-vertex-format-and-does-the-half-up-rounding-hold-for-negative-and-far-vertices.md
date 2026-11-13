+++
id = "Q199"
question = "does E607's half-up rounding to 1/256 pixel hold for negative vertices and for the vertices the guard-band clip makes, and what of the vertex format's range does a vertex inside the guard of a large target (4096 x 4096) reach (E1024: past the guard a far vertex is clipped, not saturated, wrapped or removed, up to 2^30 pixels)"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E606", "E607", "E683", "E684", "E979", "E1024"]
terms = []
+++
E606 and E607 put vertices between -9% and +124% of targets up to 256 pixels wide and fitted a
rounding to 1/256 pixel half up (floor(256 x + 0.5), x >= 0 only) at 0 mismatching pixels over
874 + 1536 cases. Nothing was run with vertices outside that range, at negative coordinates with a
tie or a sub-grid fraction (the 9 main cases with a negative coordinate are on the grid), or beyond
a few hundred pixels, so the width of the fixed-point format (a 24.8 integer range of 2^23
pixels? a narrower one?), the clamp or wrap past it, and the MTE's window conversion before it are
all open. A model must refuse such vertices until this is settled.

To settle it: the E607 sweep (steps of 1/4096 across a tie) at vertices placed at -1, -64, -2048
and +2048, +8192, +65536 pixels from a sample (a long edge, 1 and 2 of its vertices off screen),
on a 64 x 64 and a 4096 x 4096 target, tool unit 4096 to 1/256; plus a vertex exactly on a tie
(n + 0.5 in 1/256 units) at a negative coordinate; and the ISP's use of the 1/256 vertex in the
plane equations at the far vertex (a depth that depends on a vertex 5000 pixels away).

Narrowed in 11.39 (E684, E683). For one vertex on the 1/256 grid at +-2^k pixels up to k = 21 from a
64 x 64 or a 512 x 512 target the ISP draws the exact coverage except for 16 pixels in 14 of 208
cases, all within 6e-4 pixel of an edge line: no clamp of the vertex range to 2^20 pixels or less
and no wrap into 2^21 pixels or less (E684). What would settle the rest is not answered: a 4096
target, a far vertex on a tie and one with a sub-grid fraction, two or three far vertices, and the
saturation at 2^22 pixels or more (Q261). Negative vertices with a sub-grid fraction are not
rounded half up (E683, Q260).

Narrowed 2026-11-13 (E979). One vertex at +2^22 to +2^24 or -2^22 to -2^25 pixels, or two at +-2^23
or +-2^24, on a 64 x 64 target: the coverage is exact outside E684's 1e-3 pixel band in 10 of 10
rows, and a clamp or a two's-complement wrap of a 24.8 word is refuted wherever it would differ; no
fault. Open: past +2^24 and -2^25 (the tool's reach), sub-grid fractions and ties at far vertices, a
4096 target.

Narrowed 2026-11-13 (round 13, r13-isp stage far, E1024, held out; the question line is reworded,
the question is not retired). It read "what is the integer range and the behaviour at the limits
(saturation, wrap, removal) of the ISP's 1/256-pixel vertex format (E607: window coordinates are
rounded half up to 1/256 pixel), and does the rounding hold for negative and far-off-screen
vertices". A far vertex at +-2^26, 2^28 and 2^30 pixels in x and
y on 64 x 64 drew `job: ok` with no fault, the image of the far edges clipped to the guard q261
read (E1023: x <= 80, y in [-16, 80]); saturation or wrap of a 24.8 word and removal failed 6 of 6.
So the format's limits are never met by a far vertex: it reaches the format only as a clip vertex
inside the guard [infer], and its own sub-grid fraction or tie cannot show. Open: negative
vertices with a sub-grid fraction (E683, Q260), the clip vertices' rounding beyond the rows read,
a 4096 target (the guard there is Q261's), past 2^30 pixels.
