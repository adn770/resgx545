+++
id = "E168"
claim = "With render-context flag bit 5 set, the render-context cleanup unloads the context's own PB from the TA and 3D loaded-PB slots; with it clear the slots keep the PB until the PB cleanup; and with the flag set a context whose PB is not loaded leaves the slots alone"
unit = "edm"
method = "probes/edm/context-flags.toml (script context-flags.sh) on the laptop, linux fork with the debug option on: render contexts made with the flag clear and set through debugfs render_ctx_flags, each rendering the first triangle once (64x64, compared with the reference); the loaded-PB slots (TA3DCtl dwords 46 and 47) read before the cleanup and after each of its three steps RT, RC and PB (debugfs render_cleanup); flag clear and set twice each, then flag set on four contexts destroyed while a long-running context (1500 renders) has loaded its own PB since their render; one run"
tiers = ["HW"]
date = "2026-11-02"
data = ["edm-context-flags"]
terms = ["CONTEXT_FLAGS.OWN_PB", "CLEANUP.RENDER_CONTEXT", "CLEANUP.PB", "ta3d_ctl.hw_pb_desc_ta", "ta3d_ctl.hw_pb_desc_3d"]
+++

**What runs.** `render_ctx_flags` holds bits that render contexts created from then on get in
their flags word. `render_cleanup` shows the last render-context cleanup: the context, its PB
descriptor, its flags word, and TA3DCtl dwords 46 and 47 (the PB loaded for the TA and for the
3D) before the cleanup and after `RT`, `RC` and `PB`. The three steps run back to back in the
kernel, so the slots are only seen after each step. E167 is the reading of the firmware.

**Results.** The slot values are the PB descriptor address (own) or 0.

| flag | slots before | after RT | after RC | after PB |
|------|--------------|----------|----------|----------|
| `0x00`, own PB loaded | own | own | own | 0 |
| `0x20`, own PB loaded | own | own | 0 | 0 |
| `0x20`, another context's PB loaded | other | other | other | other |

- The first two rows came out the same in both repeats (flag clear twice, flag set twice); every
  triangle matched the reference (0 of 4096 pixels differ).
- Third row: all four contexts destroyed beside the long-running one (own PB `0x32423380`, the
  other's `0x32411380`) left both slots at the other's PB through all steps; their renders
  were exact.
- The long-running context's own cleanup afterwards (flag `0x20`, its PB loaded) gave the second
  row: own, own, 0, 0. All 1500 of its renders were exact.
- The flags word the cleanup read was `0x20` or `0`.

So bit 5 makes the render-context step unload the context's PB from both slots, only if that PB
is the one loaded; without it the slots clear at the PB step. This agrees with E167.

**Not shown.** Two contexts sharing one PB were not tried (the kernel gives each render context a
PB of its own), so the case E167 describes as the reason for the bit is not shown. A context
destroyed with the flag clear while another context's PB is loaded was not run. One run; only
bit 5 was set among the flag bits. What else the flag changes is not shown beyond exact renders.
