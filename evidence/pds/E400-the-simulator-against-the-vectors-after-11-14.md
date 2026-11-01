+++
id = "E400"
claim = "With mov128's bit 15 (lastpair) writing the ds0 pair the last mov32 or movs read from a data row, after the instructions E379 measured, the simulator matches 116 of the 169 vectors of the 11.14 PDS fill runs and stops on 52 (25 on the leading (p0) movs mr words of the fetch-pc probe, whose p0 it does not know, 27 on a movs to mr, an open port in a fill), one skipped (a store fault in one run of three), none differing; over all the vectors 1305 PDS vectors match and 98 stop, where the coverage report before 11.14 had 1144 and 91 over the vectors then: the 116 new ones and the 45 mov128 bit 15 stops of E261's runs, now matching, and the USSE and pixel counts are unchanged (24711 matching, 1112 fitted, 755 stopping; 143 pixel vectors), none differing"
unit = "pds"
method = "offline: vectors.py convert on the 11.14 runs pds-mov128-bit15, pds-fetch-pc-pad and pds-store-totals into vectors/semantics/pds/; cargo test --release -p sgx-sim --test vectors over those alone and over the whole data repository, and the coverage report written again (doc/isa/sim-coverage.json); one run each"
tiers = ["HW"]
date = "2026-11-03"
data = ["vectors-pds-semantics"]
terms = []
+++

**Results.** Of the 169 vectors: the mov128 companions and second markers (75 of 78; the other 3
write mr) and the `movs douta` cases of the mr probe match; the fetch-pc vectors match where no
leading word runs (the five with none); the store-total vectors match, the one-run fault skipped.
The stops: the leading `(p0) movs mr` words (25) and every `movs mr` (27).

The simulator names or keeps the pair only after the instructions E379 measured (a `mov32` from
`ds0[2]` or `ds0[9]` and a `movs` from the pairs 2 and 6 name it; a `mov32` from `ds1[9]`, a `not`
of `ds0[48-55]` or `ds1[48-55]`, a `movs` from the pair 50 and a `mov64` from `mr01` keep it) and
stops after any other, a plain `mov128` and `movsa` included. The counts above are those of the
run after this narrowing (116 and 52 over the 169 vectors, 1305 and 98 over all): no vector
reached an instruction it left open.

**Not shown.** A `movs mr` in the simulator: the port's effect is open (pds_isa 7.1), so the pair it
names for bit 15 runs only on the hardware.
