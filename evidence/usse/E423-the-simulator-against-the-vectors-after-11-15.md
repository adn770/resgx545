+++
id = "E423"
claim = "The simulator is unchanged by 11.15 and still matches every vector it models: over all the vectors 24711 scalar vectors match, 1112 are fitted, 755 stop and none differs, 143 pixel vectors match with 18 stopping and none differing, and the PDS vectors match, as after 11.14 (E400)"
unit = "usse"
method = "offline: cargo test --release -p sgx-sim --test vectors over the whole data repository (RESGX545_DATA), and cargo test -p sgx-sim -p pds-isa (182 tests, 0 failed), on the tree built after the 11.15 overlay; no run of 11.15 was converted to vectors; one run each"
tiers = ["HW"]
date = "2026-11-07"
data = []
terms = []
+++

**Results.** The probe vectors: 24711 pass, 1112 fitted, 755 unsupported, 0 fail; the pixel vectors:
143 pass, 18 unsupported, 0 fail; the PDS vectors pass; every skip row matches a vector and the
coverage report is fresh. These are the numbers of E378 and E400.

**Why nothing was converted.** What 11.15 measured is not scalar semantics the simulator models:
registers and values in the TA, ISP and ZLS control words, a hang that alternates, which tile
columns a render writes, and a pixel task's output room. The output room (E406) is a measured
behaviour of the pixel task, and the simulator has no pixel task to put it in; adding the setting
would have no vector that checks more than E406's counts, so it is left to phase 12.

**Not shown.** Any behaviour of the pixel pipeline the simulator would need to place o1 to o3.
