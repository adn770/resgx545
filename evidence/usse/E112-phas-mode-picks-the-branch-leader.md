+++
id = "E112"
claim = "phas's instance mode decides which instance a divergent quad's predicated branch follows: under parallel the quad's first covered instance (24 pixels, the right columns of the 12 quads whose left column is uncovered, branch as instance 1 does), under perinstance instance 0 even when it covers no pixel (all 1062 pixels branch as instance 0); .skipinv skips the uncovered instances under both modes"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/phases.toml, probes usse-phases-phasbr-tri-parallel, -tri-perinstance, -tri-parallel-odd, -tri-perinstance-odd (phase 1 of the triangle's pixel shader, pix_phas_br.s), usse-phases-phasbr-fill-parallel and -fill-perinstance (the same branch in a fill), and usse-phases-phasbr-out-{parallel,perinstance}-mov and -mov-skipinv (phase 1 writes o0 with a plain mov or a mov.skipinv only), the first phas none, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-phases"]
terms = []
+++

**What runs.** Phase 1 sets p0 from the pixel's x parity within its quad (even x, or odd x in the
"odd" probes), runs a predicated `br` over three `or`s, and writes o0 = 4 when the instance
branches and 7 when it falls through. A quad whose instances all agree is unambiguous. In a
quad whose instances disagree the branch is taken as one instance, and the value written
shows which. The triangle's 42 partly covered quads come in three shapes (E104): 18 cover only
the top-left instance 0, 12 cover the bottom row (instances 2 and 3) and 12 the right column
(instances 1 and 3).

**Results.**

| where | first phas | p0 set on | pixels |
|-------|------------|-----------|--------|
| fill | end, parallel | even x | all 2048: 4 |
| fill | end, perinstance | even x | all 2048: 4 |
| triangle | none, parallel | even x | 1038: 4; 24: 7 |
| triangle | none, perinstance | even x | all 1062: 4 |
| triangle | none, parallel | odd x | 1038: 7; 24: 4 |
| triangle | none, perinstance | odd x | all 1062: 7 |

The 24 pixels that differ under parallel are the right-column pixels of the 12 quads whose
left column the triangle does not cover: in those quads instance 0 (top left) covers no pixel
and instance 1 is the first covered. The 30 other partly covered quads have a covered
instance 0, or a covered bottom row whose first instance (2, bottom left) has instance 0's x
parity, and they follow the same value as instance 0.

Writes in phase 1 under none: with `mov.skipinv` only, 1062 pixels (the covered ones) in both
modes; with a plain `mov` 1132 pixels under parallel and 1128 under perinstance, that is 70 and
66 uncovered pixels of covered quads landing (E111).

**What it shows.** The mode picks the instance a divergent quad follows: the first covered one
under parallel, instance 0 whatever its coverage under perinstance. In a fill every instance is
covered, so both give instance 0. `.skipinv` skips the uncovered instances under both modes.

**Not shown.** Neither mode makes instances branch apart. One run per probe.
