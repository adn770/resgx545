+++
id = "E294"
claim = "After 11.7 the simulator matches 23,597 of the 25,245 scalar USSE vectors of the earlier probe rounds (6,028 before), 143 of the 161 pixel vectors (135 before), and stops on 582 (19,217 before) and 18; 1,066 more agree with firh's fixed-bank families, which were fitted to them, and count as fitted, not as matches; none differs. The 15,262 near matches are 209 within a measured bound and 15,053 with a value taken as any value. atst8, pcoeff, depthf, setfc, moest and setm gain semantics; with the 11.7 runs' 1,038 vectors, 24,440 scalar vectors match, 1,112 are fitted, 686 stop and none differs"
unit = "usse"
method = "offline: cargo test --release -p sgx-sim (crates/sgx-sim/tests/vectors.rs) and cargo run --release -p sgx-sim --example coverage (doc/isa/sim-coverage.json) over the data repository, once with the vectors of the earlier rounds only and once with the 11.7 runs' vectors (vectors/knowledge/usse/) as well; one run each"
tiers = ["HW"]
date = "2026-11-02"
data = [
    "vectors-usse", "vectors-usse-followup", "vectors-usse-jobs", "vectors-usse-knowledge",
    "usse-alpha-test", "usse-moe", "usse-moe-followup", "usse-instance-masking",
]
terms = []
+++

**What changed in the simulator.**

- firh reads the job's coefficients (E292), and the latch bytes a task did not write are any
  value; centres below #-4 and positions past the line follow E292.
- atst8 as E083 gives it: alpha (src0 bits 31:24) against the reference (src2 bits 31:24) by the
  function in src2 bits 15:13; a pass writes src0 and sets the predicate, a fail leaves the
  destination and clears it; `!pN` and `.c10` stop.
- pcoeff and depthf (E083; depthf's twosided, which E083 did not run, stops), setfc (E097,
  E109), moest (E087's moest-state and moest-dest, selectors 0 to 15, E097, E109) and setm
  (E099) leave every register and predicate as a nop does: what they set is not visible in a
  fill.
- A vector that agrees only with firh's fixed banks 1 and 2 is fitted, not matched
  (`Outcome::Fitted`): their tap families come from the same vectors (E292). The coverage
  counts it with the stops, under its own reason, and its totals give "fitted".
- A bit outside every field that the hardware reads stops the run: idiv's enc[47] (E295),
  setfc's and imo's enc[51] and depthf's enc[44], which hang the job (E296).

**Results on the earlier rounds' vectors** (vectors/usse, vectors/followup/usse and the other
units' probe vectors, as E147 counted them):

| | before (E147) | after |
|---|---|---|
| scalar match | 6,028 | 23,597 |
| of them within a measured bound | 209 | 209 |
| of them with a value taken as any value | 0 | 15,053 |
| scalar fitted (firh's banks 1 and 2, in-sample) | 0 | 1,066 |
| scalar unsupported | 19,217 | 582 |
| pixel match / unsupported | 135 / 26 | 143 / 18 |
| PDS match / unsupported | 1,144 / 91 | 1,144 / 91 |
| mismatches | 0 | 0 |

The forms without semantics fall from 14 to 8 (the register forms of smoa, smr, smlsi and smbo,
imo, wop and both phas forms); the forms with vectors but no match from 10 to 3 (ba and both
bexception forms, which hang or branch out of a fill). The largest remaining stops: the firh
latch read through (285), smoa taking an operand below r0 (64 + 16), per-instance g registers
(36), registers past the temporaries (26 + 8), smlsi with non-zero limits (20), texture formats
no decoder fixes (20), eld's index bits (12).

**With the 11.7 runs.** The encoding-bit, filter and gap tables add 1,038 USSE vectors, 993 of them
compared (vectors/knowledge/usse/): 24,440 scalar vectors match, 1,112 are fitted (the 46 of
usse-filter-bank2 among them), 686 stop, none differs. Before
idiv's enc[47] stopped the run, its flipped vector was the one mismatch the simulator gave (it ran
the plain idiv); that is how the read bit shows.

**Not shown.** That the stopped vectors agree. The any-value matches check one byte of four.
