+++
id = "E378"
claim = "With idiv's four-bit repeat count and bank 6's write to neither index register in the simulator, it matches 271 of the 340 scalar vectors of the 11.13 runs and stops on 69, none differing; over all the vectors 24,711 scalar vectors match (24,440 before), 1,112 are fitted, 755 stop and none differs"
unit = "usse"
method = "offline: vectors.py convert on the 11.13 runs (destination bank 6, idiv enc[47], encoding gaps end, hazards, MOE state, g19) into vectors/semantics/usse/; cargo test --release -p sgx-sim --test vectors over those alone and over the whole data repository, and the coverage report (doc/isa/sim-coverage.json); one run each"
tiers = ["HW"]
date = "2026-11-03"
data = ["vectors-usse-semantics"]
terms = []
+++

**Results.** Of the 340 scalar vectors of the 11.13 runs, 271 match: the hazard cases, the
bank 6 writes to temporaries, the idiv counts whose iterations read no earlier destination,
the MOE state across jobs. 69 stop: a read of pa or sa the program did not write (34, the
moved-attribute probes), g19 and g18, whose values the simulator does not model (14), an idiv
iteration reading an earlier one's pending result (9), and words no form decodes (12). None
differs from the hardware.

**Not shown.** The pixel vectors of these runs (g19 and globals images, the leftover o0) are not
run: their values come from per-instance registers and earlier jobs.
