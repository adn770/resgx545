+++
id = "E399"
claim = "The colour-space words set 0 holds survive the driver's GPU reset (debugfs reset) and a 5 s idle: a YUYV copy that does not load set 0 gives, after the reset and after the idle, the same image as one that loads it, every pixel, two runs"
unit = "texture"
method = "probes/texture/copy-followup.toml (csc_after_reset) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x32 YUYV copy (T1 bit 28) with set 0 loaded as BT.601, without the load, then debugfs reset, without the load, loading again, 5 s, without the load; two runs; every pixel read back"
tiers = ["HW"]
date = "2026-11-03"
data = ["texture-copy-followup"]
terms = ["transfer_cmd.load_yuv_csc"]
+++
**Results.** All ten copies gave one image (first pixel 0xff280100).
