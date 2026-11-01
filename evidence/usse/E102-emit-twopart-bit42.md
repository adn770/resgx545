+++
id = "E102"
claim = "Bit 42 of the vertex emits (.twopart) is needed on emitvcbvtx and not on emitmtevtx: without it on emitvcbvtx alone the job hangs, without it on emitmtevtx alone the triangle is exact (1062 pixels), and without it on both the job completes with no triangle drawn"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/emits.toml, the four usse-emits-emit probes (the triangle's vertex shader, vtx_emit.s, .twopart on each of its two emits or not), one probe a case, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-emits"]
terms = []
+++

**What runs.** The triangle's vertex shader emits each vertex twice: `emitvcbvtx.end` ends
phase 0 and `emitmtevtx.end.freep` ends phase 1. The probe names are `emit-<vcb>-<mte>`; each
emit carries `.twopart` (bit 42) or not.

**Results.**

| `emitvcbvtx` | `emitmtevtx` | result |
|--------------|--------------|--------|
| `.twopart` | `.twopart` (as drawn) | 1062 pixels of `0xff00ff00` |
| none | `.twopart` | the job hung (`context lost (Connection timed out)`) |
| `.twopart` | none | 1062 pixels of `0xff00ff00` |
| none | none | the job completed; 4096 pixels of background, no triangle |

Baseline triangles before and after every probe, the hang included, were exact.

**What it shows.** The bit acts on the VCB emit. One reading fits all four rows **[infer]**: the
bit says the vertex's output comes in more than one emit, the VCB part first. Without it on
the VCB emit the vertex is complete at that emit, and a later MTE emit that still claims a
two-part vertex waits for a part that never comes (the hang); with neither flagged, each emit
stands alone and no vertex reaches the MTE in a form it draws. The MTE emit, the last part,
draws the same with or without the bit. The reading is an inference; the table is the
measurement. The state task's emits carry the same bit (E106).

**Not shown.** One run per case.
