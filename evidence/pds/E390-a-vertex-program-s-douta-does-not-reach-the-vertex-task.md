+++
id = "E390"
claim = "A douta from the triangle's vertex PDS program does not reach the vertex task's sa registers: with each of twelve special reads passed by douta to sa[4 + ir0], the vertex shader stored sa4-sa6 = 0.75, -0.375, 1.0 (vertex data) and sa0-sa3 = 0x32400000, 0x00400000, 0, 0x7e570000 in 34 of 36 jobs, whatever the read, as the earlier vertex-programs douta probe's single run did; two jobs (one mov32 ir0.1, one mov64 mr01 high) stored other values (0x2, 0x73, 0x1000, 0x32411200, 1); so the specials of a vertex program were not read this way"
unit = "pds"
method = "probes/pds/vertex-specials.toml on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: vtx_specials.s (vtx_douta.s with the case's read of ir0, ir1, tim, ir1.0, ir1.1, ir0.1, mr01, mr23 low and high, tstz and tstn of ir1 into ds0[50], passed by douta to sa[4 + ir0]) as the vertex PDS program, vtx_dump_sa.s storing x, y, z, w and sa0-sa7 per vertex slot; twelve reads, three runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["pds-vertex-specials"]
terms = []
+++

**Results.** See the claim. The control read (`or ds0[50], ir1, ds1[2]`) is vtx_douta.s's own line
(the table labels it "the control of E127"); its markers 0x7e57000n never appeared in sa4-sa6.

**Not shown.** Where a vertex program's `douta` lands, and the specials themselves (Q060).
