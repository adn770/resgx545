+++
id = "E615"
claim = "The address rule of E465 held to the 18 stored-depth dump pairs of E489 by a rule function written for the pipeline simulator (sgx-pipe zls::store_dword, in-tile order y0 x0 y1 x1 y2 x2 y3 x3 x4, 512 * (ty * (G + 1) + tx)), replayed as 18 unit vectors: of 3415552 dwords stored 3279132 are at the rule's address (3225000 for pixels of the target, which the replay counts fitted, and 54132 for pixels past it, refused as Q122), 7780 are background depth (1124 at pixels past the target, refused as Q122, and 6656 in whole tiles of the two 4096 x 4096 jobs, refused as Q107) and 128640 are zero in both ramps (the same two jobs, refused as Q107), none is at another address (0 mismatches), the slots touched equal the rule's in 18 of 18 and 1098340 pixels walk to their own ramp values at their rule address in the four cases whose tiles do not overlap; every count equals recompute.txt's line of the case"
unit = "zls"
method = "offline, no laptop, no new run: tools/usse-asm/unit_vectors.py writes one zls-store vector for each of the 18 cases of zls/store-layout-dumps (the two ramp dumps by path and the sha256 of the gz, the counts of the dataset's recompute.txt as the expected values), and cargo test --release -p sgx-pipe replays them with the crate's own gunzip, ramp decoding (z = 0.25 + 0.5 (p + 0.5) / (3 size), within 0.05 of a pixel's centre) and rule, written in Rust and not from recompute_e465.py; the replay's verdict for every vector is fitted, not matched, because E465 states the rule as fitted on the 1024 x 768 runs and the small targets (doc/specs/vectors.md section 5)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["zls-store-layout-dumps", "unit-vectors-12-0"]
terms = ["CR_ISP_ZLSCTL"]
+++

**What ran.** The 36 dumps of E489 (an x-ramp and a y-ramp depth buffer for each of 18 cases, 13
target sizes, G 0 to 511) are read by `sgx-pipe`: each dword that left the 0xdeadbeef fill is placed
in a pixel by the two ramps and compared with the rule's address. The vector carries the counts the
dataset's recompute script printed; the replay counts its own items and the vector is a mismatch
if any differs.

**Results.** 18 of 18 vectors replay with no mismatch; the totals are the ones of E489: 3415552
dwords stored, 3279132 at the rule's address (3225000 for pixels of the target and 54132 for pixels
past it: x >= W or y >= H in the edge tiles of 1000 x 600, 1536 x 1010, 2000 x 2000, 258 x 130 and
34 x 18, Q122), 7780 background (1124 at pixels past the target of 34 x 18, Q122, and 6656 whole
tiles of the two 4096 x 4096 jobs, 3584 and 3072, that follow the zero tiles of the overflowed job,
Q107), 128640 zero (48000 at G = 0 and 80640 at G = 1 for 4096 x 4096, Q107), 0 at another address.
The replay counts 3225000 items fitted and refuses 55256 as Q122 and 135296 as Q107. The
pixel-to-address walk holds for 1098340 pixels (1024 x 768 with G = 33, 640 x 480 with G = 511,
64 x 64 with G = 1, 34 x 18 with G = 3).

**What it shows.** [HW] E465's rule holds to the stored data. A second implementation (Rust, with
its own decompression and decoding) agrees with the dataset's recompute; that is a statement about
the code, not a measurement. It is the unit function the simulator will use; its status in the
simulator is fitted, as E465 states.

**What it does not show.** The overflow store and tile order (Q107), pixels outside the target
(Q122), the formats other than 0 to 2 (Q120) and the stencil's in-tile order (Q121); a rule for
a tile larger than 32 x 16.
