+++
id = "E129"
claim = "With the render's pixel-event info word at 0, the douta writes of the replaced pixel-event program reach sa0 to sa15 of the plain USSE task it starts, all sixteen words in order; the data does not vary the info word, so the gate that bits 5:0 would make is not tested"
unit = "pds"
method = "probe pds-pixel-event-readback of probes/pds/pixel-event.toml (pixev_dump.s with the plain task task_dump.s) on the laptop, linux fork with the debug option on: 32x16 triangle job of one tile, one run of the single case in each of two runs (the second is the follow-up run); the triangle host sets the pixel-event info word to 0 when it replaces the pixel-event program (userspace/libsgxfive/src/tri_probe.c)"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-pixel-event", "pds-pixel-event-followup"]
terms = ["PIXEL_EVENT.END_OF_TILE"]
+++

**What runs.** The triangle job's pixel-event program is replaced by one that, on the end-of-tile
event, passes sixteen marker dwords (0x7e570000 to 0x7e57000f) on with sixteen `douta` writes,
attribute k getting marker k, and then starts a plain USSE task with the DOUTU1 word 0 (no PBE
write) before the end-of-tile task. The plain task stores `sa0` to `sa15` to the first sixteen
dwords of the scratch buffer. The target is one tile of 32x16, so the event runs once. The
render command's pixel-event info word, which the host sets to 0 in this configuration, is not
varied: this table has one case.

**Results.** The scratch buffer holds the sixteen markers in order, 0x7e570000 at the first
dword to 0x7e57000f at the sixteenth. The target read back holds 322 background pixels, 126
triangle pixels, 4 pixels of 0x7e570000, 4 of 0x7e570001 and 56 others.

**Second run.** The follow-up run reads the same: the sixteen markers in order, and the same
pixel summary.

**Not shown.** The info word was at 0 in this run and in no other, so nothing here says what
changes with a bit of 5:0 set, whether `douta` then reaches the task's `sa` registers, or what the
task reads there instead. Where the 8 marker pixels and the 56 others come from is not examined:
the pixels were summarised, not read back one by one, and the other pixel-event probes
(E130) use a different end-of-tile program. One case, once in each run.
