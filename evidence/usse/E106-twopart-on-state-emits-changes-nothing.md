+++
id = "E106"
claim = ".twopart (bit 42) on the state task's emitvcbst or emitmtest, alone or on both, changes nothing: the triangle is drawn exactly (1062 pixels) in all four cases"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/emits.toml, the four usse-emits-stemit probes (the triangle host's state slot, state_emit.s, .twopart on neither emit, either one or both), one probe a case, one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-emits"]
terms = []
+++

**What runs.** The state task of the triangle run is replaced by `state_emit.s`, whose two emits
are `emitvcbst` and `emitmtest`. The probe names are `stemit-<vcb>-<mte>`: each emit carries
`.twopart` (bit 42, as on the vertex emits, E102) or not.

**Results.** All four cases complete and draw the triangle: 1062 pixels of `0xff00ff00` and 3034
of background. Neither emit flagged, `.twopart` on `emitvcbst`, on `emitmtest` and on both
give the same image. Baselines before and after every probe were exact.

**What it shows.** On the state emits the bit has no effect a single triangle shows, while on
the vertex emits it is needed on the VCB emit (E102). What it changes for a state block, if
anything (a state task split over several emits, say), is not shown.

**Not shown.** One run per case, one triangle.
