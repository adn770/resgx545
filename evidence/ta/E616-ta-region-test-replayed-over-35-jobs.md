+++
id = "E616"
claim = "The region test of E542 (a 16 x 16 tile lists a primitive iff the bounding box has max x and max y at or beyond the tile's low sides and min x and min y below its high sides, and no edge line has all four tile corners strictly outside it) held to the 35 jobs of ta-tri-boundary and ta-tri-corner by a rule function written for the pipeline simulator (sgx-pipe ta::tile_lists): 14656 (primitive, tile) pairs (12242 checked per primitive, 2414 by presence only), 0 mismatches, replayed as 35 unit vectors whose listed tiles are those of each job's first control stream per region, as E542 counts them"
unit = "ta"
method = "offline, no laptop, no new run: tools/usse-asm/unit_vectors.py writes one te-region vector for each completed job of the ta-tri-region dataset (27 ta-tri-boundary and 8 ta-tri-corner), with the pixel vertices of the dataset's recompute script (geometry of its geometry(): the NDC constants and the c / 16 pixel shift of copy c, which E542 states as an assumption of the recompute and not read from the packed vertices) and the tiles of the first stream of each region (forms 0x80, 0x90 and 0x98 as `any`, 0x88, 0x8a and 0x8c as the primitive masks), and cargo test --release -p sgx-pipe replays them with the Rust rule; the verdict is fitted for every vector, because E542 states the rule as fitted post hoc to E180's 472 regions and then declared as a prediction"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["ta-tri-region", "unit-vectors-12-0"]
terms = ["CSTREAM.PRIM_TILES", "REGION_HDR.POS"]
+++

**What ran.** For each of the 35 jobs every 16 x 16 tile of the target is tested for every primitive
by the Rust function and compared with the tile's recorded listing: a tile with no stream lists
nothing, a tile of the forms that name no primitive lists "any" (the rule must list at least one),
a tile of a mask form lists exactly the masked primitives.

**Results.** 35 of 35 vectors replay with no mismatch over 14656 pairs (13632 + 1024), as E542
counts them. [HW]

**What it shows.** The rule of E542 is implemented outside the analysis script and gives its
listing for every tile of every job, the 27 of the pairs the landed fit of E180 got wrong included.
The rule is a unit function of the simulator's TA, fitted as E542 states.

**What it does not show.** The check of "any" tiles is weaker than a mask: for the form 0x90 (and
the forms 0x80 and 0x98 of objects of more than 8 primitives) only that some primitive is listed is
tested, 2414 of the 14656 pairs; the forms 0x80 and 0x98 of up to 8 primitives are checked per
primitive against bits 7:0 of the primitive word; the geometry is the recompute's
assumption; objects of more than 8 primitives, lines (E543) and points (E544), the region's own
boundary (through the tiles only) and the object writer (Q070).
