+++
id = "E415"
claim = "Under CR_ISP_MSAA modes 1 and 2 a 10-pixel triangle placed in each of the nine 16x16 tiles of a 64x64 target is drawn only in the first and third tile columns with the TE anti-aliasing bits clear and only in the middle column with them set (nine of nine cases each, three triangle phases and three rows), each drawn tile with the TE bits clear landing 4 pixels right of its place (x) and at its place (mode 1) or 4 pixels below (mode 2); with them set the middle triangle is wider and lies left of its tile"
unit = "isp"
method = "probes/isp/msaa-tiles.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: the right triangle of the layout probes (legs 10 pixels, edges at tile origin 4, 20, 36 in x and y plus k/16 with k = 0, 6, 12), CR_ISP_MSAA mode 1 and 2 (cmd:13 0x80000001, 0x80000002) with the sample words of E210 and the TE anti-aliasing bits (cmd:1) clear and 0xe0000000, 4 probes of 27 cases, every pixel read, the green pixels counted and boxed"
tiers = ["HW"]
date = "2026-11-07"
data = ["isp-msaa-tiles"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MSAA.ENABLE", "CR_ISP_MULTISAMPLECTL", "CR_TE_AA"]
+++

**What was seen.** Triangles whose edges sit at x0 = 4, 20 and 36 and y0 = 4, 20 and 36 (a tile of
16 pixels each), with k = 0, 6, 12:

| probe | x0 = 4 | x0 = 20 | x0 = 36 |
|-------|--------|---------|---------|
| mode 1, TE bits clear | 9 of 9 drawn, 54 or 64 pixels, x 8 to 15 | 0 of 9 | 9 of 9, x 40 to 47 |
| mode 2, TE bits clear | 9 of 9, 42 to 64 pixels, x 8 to 15 | 0 of 9 | 9 of 9, x 40 to 47 |
| mode 1, TE bits set | 0 of 9 | 9 of 9, 90 or 100 pixels, x 8 to 27 | 0 of 9 |
| mode 2, TE bits set | 0 of 9 | 9 of 9, 72 pixels, x 8 to 20 | 0 of 9 |

The rows do not matter: y0 = 4, 20 and 36 are drawn alike. The boxes of the drawn triangles are at
x0 + 4 in x for the first and third columns, at y0 (mode 1: y 4 to 13, 20 to 29, 36 to 45) or y0 + 4
(mode 2: y 8 to 15, 24 to 31, 40 to 47). With the TE bits set the drawn middle column triangle is
wider (x 8 to 27 in mode 1, 8 to 20 in mode 2) and lies left of its tile, at y0 in mode 1 and 4
above y0 in mode 2 (y 0 to 11, 16 to 27, 32 to 43).

**What it shows.** The multisampled tiles past the first land at a constant displacement of their
place, not at a growing one; the tile column that is processed alternates (the first and third with
the TE bits clear, the middle with them set), so the TE bits choose which tile columns a render
writes in modes 1 and 2 [infer: the macrotile row sequence]. One run of each table.

**What it does not show.** Which pixels the unwritten columns hold (they read as the background of
the tool, not the sentinel); the layout fit (isp_words.py layout) per tile.
