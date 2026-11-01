+++
id = "E618"
claim = "The window rule of E503 (tile (tx, ty) of a multisampled render holds the source pixels x = 32 tx + 16 b31 + a div sx, y = 16 ty + 8 b30 + b div sy, (sx, sy) = (1, 1), (2, 1), (2, 2) for the modes 0 to 2, b30 counting in mode 2 only) held to the 96 position dumps of the 48 runs of isp/msaa-ident by a rule function written for the pipeline simulator (sgx-pipe isp::msaa_source): of 786 tiles every one equals the rule on every decodable pixel (0 mismatches), 773 are decodable in all 512 pixels (matched) and 13 hold background pixels (refused as Q141), replayed as 48 unit vectors"
unit = "isp"
method = "offline, no laptop, no new run: tools/usse-asm/unit_vectors.py writes one isp-tile vector for each run of isp/msaa-ident (the x and y position dumps by path and the sha256 of the gz, the counts of the dataset's an_ident_rule.txt as the expected values), and cargo test --release -p sgx-pipe replays them with the Rust rule and a parser of the dumps' rows (a position decodes as x + 0.375 and y + 0.125 within 1e-4, the offsets of the 11.26 reading); mode 0 with CR_TE_AA bits 31 or 30 set and mode 3 are refused (Q141, Q138), as E503 states them untested; the verdict is fitted for every vector, because E503 states the rule as read post hoc from the 64 x 64 runs"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["isp-msaa-ident", "unit-vectors-12-0"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++

**What ran.** For each of the 48 runs (11 fit, 29 held out, 8 repeat) the stored pixels decodable in
both dumps are compared with the rule's source pixel, per 32 x 16 tile.

**Results.** 48 of 48 vectors replay with no mismatch: 786 tiles, 786 equal to the rule, 773
decodable in 512 of 512 pixels and 13 tiles refused (the 455 background pixels of E502, Q141).
[HW] The numbers are E503's.

**What it shows.** E503's window rule is implemented in the simulator's ISP as a unit function and
reproduces the stored positions of every run, with the post hoc status the record gives it.

**What it does not show.** The window for CR_TE_AA values without bit 29, mode 3, the sample
positions inside a pixel, the pixels of the 13 background tiles (Q141), and whether four windows of
a tile come from four renders of one frame (Q138).
