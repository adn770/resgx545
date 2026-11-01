+++
id = "E376"
claim = "On the triangle's vertex program, incp 1, 2 or 3 on emitvcbvtx or on emitmtevtx draws the triangle as with 0 (1062 pixels, two runs each), and .cut on emitmtevtx hangs the job (two of two)"
unit = "usse"
method = "on the laptop, linux fork b5a86838ae59 with the debug option on: probes/usse/emit-flags.toml (vtx_emit_incp.s: use_vtx.s with the two emits' modifiers and incp fields from the case; host tri, slot vtxuse, 64x64, every pixel read back), eight cases, two runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["usse-emit-flags"]
terms = []
+++

**Results.** The control (`.twopart` on both emits, incp 0) and the six incp cases give the same
image: 1062 pixels of 0xff00ff00 on 3034 of 0xff203040. `emitmtevtx.end.twopart.cut.freep`
hangs the job in both runs; the kernel recovered.

**Not shown.** What incp counts (a job with one vertex task shows no partition count), `.cut`
on a program that emits more than one primitive, `.tasks`/`.taske` (emitpds only).
