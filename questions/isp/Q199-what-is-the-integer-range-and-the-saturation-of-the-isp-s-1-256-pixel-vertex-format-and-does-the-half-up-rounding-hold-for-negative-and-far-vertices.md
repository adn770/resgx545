+++
id = "Q199"
question = "what is the integer range and the behaviour at the limits (saturation, wrap, removal) of the ISP's 1/256-pixel vertex format (E607: window coordinates are rounded half up to 1/256 pixel), and does the rounding hold for negative and far-off-screen vertices"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E606", "E607"]
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
