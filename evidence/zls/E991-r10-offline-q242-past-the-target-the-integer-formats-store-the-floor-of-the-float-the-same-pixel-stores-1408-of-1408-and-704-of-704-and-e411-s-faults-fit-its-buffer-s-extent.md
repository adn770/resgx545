+++
id = "E991"
claim = "Round 10 offline (Q242; no run): past the target of r9-x's z242-c (80 x 40, G 2, a tile area of 96 x 48, E977 scored only its 3200 in-target pixels), stored format 1 is min(floor(z0 * 2^24), 0xffffff) and format 2 floor(z0 * 2^16) in E490's layout, z0 the format-0 float the same pixel stores there (E831's band, 105 distinct values from 0.403 to 1.0): H-EXT 1408 of 1408 dwords (format 1) and 704 of 704 (format 2), frozen by hash (q242_edge_rule.json, ae732269...) before the past-target dwords were read, against H-FILL (the fill left) 0 and 0 and H-ROUND (round(z0 * 0xffffff)) 832 and 683 [HW data, held out in dwords, not in jobs: the session's fit rows]; E465's address rule recomputed for E411's 64 x 64 target (depth at scratch page 12, stencil at page 4, a 16-page buffer) gives the stored pages of E411's table for G 0, 1, 3, 5, 9 and 17 up to the first page past the buffer each faulting row reaches (G 5: depth 12 and 15, stencil 4, then 18; G 9 and 17: depth 12, stencil 4, then 17 and 21), and E977 ran G 7 and 9 with a buffer sized to the extent without a fault, so the extent past the buffer, not the pitch field, faults the job [infer]; one misfit: at G 3 the rule puts tile rows 2 and 3 at pages 16 and 18 and E411 saw no fault"
unit = "zls"
method = "Offline, no run (round 10, decision R10-1 a, package O10-2; ranking closing10/rank/rank-round10.md finding 2). Data: r9-x (render/closing-r9-x, dataset render-closing-r9-x) attempt out/20261113-081821, stage zls, the kept depth dumps z242-c-f0, z242-c-f1 and z242-c-f2 (.depth.1.bin.gz; 80 x 40, CR_ISP_ZLSCTL formats 0, 1 and 2 at G 2; module B60AB0B4, tool t4, as E977 gives them), read through the session's own gen/zls.py (tiles, in_tile_pixel, in_tile_index16). The ranking's closing10/rank/q242_edge.py (standard library; checks q242_edge_rule.json against q242_edge_rule.sha256 before it reads a dump) takes, for every pixel of the 3 x 3 tiles with x >= 80 or y >= 40, the format-0 dword at the pixel's address (E465) as z0 and compares the format 1 dword at the same address and the format 2 dword of its row pair (E490) with each rival. E411's pages: closing10/rank/q242_e411_pages.py (standard library, no data) prints the pages each store writes per G from E465's rule (depth 512 dwords a tile at 512 (ty (G + 1) + tx), stencil 128, E467) for E411's arrangement, compared with E411's table by eye (no fit). This record re-ran both scripts with the repository's .venv (python -B) and got q242_edge.out and q242_e411_pages.out byte-identical to the ranking's."
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/zls/", "cited-scratch:closing10/rank/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What was done.** E977 held the floor rule of the integer formats over the 3200 pixels inside an 80
x 40 target with edge tiles; the tiles of that target cover 96 x 48, and E831's band stores past the
target in the float format. Q242 asked what the integer formats store there. The ranking froze three
rivals by hash, then read the dwords past the target of the three kept dumps of the same job in
formats 0, 1 and 2. Q242 also asked why E411's scratch jobs with G past 3 faulted; the ranking
recomputed E411's stored pages from E465's address rule.

**Results [HW].** Past the target 1408 pixels (and 704 row pairs) were stored, no fill left; the
format-0 floats there take 105 values from 0.403 to 1.0. Format 1: H-EXT 1408 of 1408, H-FILL 0,
H-ROUND 832. Format 2: H-EXT 704 of 704, H-FILL 0, H-ROUND 683.

**E411's pages [infer].** For G 0 and 1 the rule's pages are E411's (12 to 14, 12 to 15, stencil 4).
For the faulting rows the stores in tile order reach a page past 15 at tile row 2 (G 5: page 18) or
1 (G 9: page 17; G 17: page 21), and the pages E411 saw stored are exactly those before it (G 5:
depth 12 and 15, stencil 4 with 512 dwords; G 9 and 17: depth 12, stencil 4 with 256). E977's G 7
and 9 jobs, with a buffer sized to the extent, did not fault. At G 3 the rule puts tile rows 2 and 3
at pages 16 and 18, past the buffer, and E411's job stored pages 12 and 14 and did not fault, so
what lies past page 15 (whether page 16 or 18 was mapped and 17 not) is not known.

**What it shows.** [HW] Past the target, the integer formats store the floor rule of the float the
same pixel stores in format 0, the band's depth and the background 1.0 alike, at 80 x 40 and G 2.
[infer] E411's faults are the store reaching an unmapped page past its 16-page buffer, not the pitch
field.

**What it does not show.** Other sizes with edge tiles in an integer format (odd widths or heights,
whose band is rule A in the float format, E885, E903: sgx-pipe refuses them, Q242), a 16-bit store
whose last row pair straddles the target's last row at an odd height, which pixel a dword shared by
overlapping tiles holds (Q242), and why G 3's pages 16 and 18 did not fault (Q242).
