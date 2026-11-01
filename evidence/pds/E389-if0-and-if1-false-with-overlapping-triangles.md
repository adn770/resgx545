+++
id = "E389"
claim = "In the primary pixel program neither if0 nor if1 tests true on any pixel of a 64x64 render with the triangle drawn twice or five times over itself: every pixel of both flag cases equals the source-1 control (x + 0.5 where a flag held would be the source-0 control's), three runs each"
unit = "pds"
method = "probes/pds/input-flags-overlap.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: pds_iter_if.s as the triangle's primary pixel program (the douti source 0 under the flag, source 1 otherwise), pix_pa0.s, vtx_coords.s, the triangle and one or four copies of it at the same place (vertices 6 and 15); controls source 1 and source 0; three runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-input-flags-overlap"]
terms = []
+++
**Results.** In all 24 jobs the source-1 control, if0 and if1 gave the same image (the iterated
coordinate, 0xbeb80000-0xbec80000 on 1098 pixels) and the source-0 control the pixel positions
(0x419c0000-0x41ac0000): no pixel took the source-0 value under a flag.
