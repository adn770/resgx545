+++
id = "E398"
claim = "The copy draws its source only with the background tag's layer count (transfer word 0 bits 30:25) at 1, as the library builds it: at 0, 2, 3, 31 and 63 every pixel is one colour (0xff6648dc over the every-value source), two runs; a 128x64 copy was rejected by the kernel (Invalid argument) and wrote no pixel, with or without word 7 bit 1 (CR_ISP_MSAA mode 2), so mode 2 on it was not measured"
unit = "transfer"
method = "probes/texture/copy-followup.toml (tag_layers) on the laptop over the cable, linux fork b5a86838ae59 with the debug option on: the 64x32 copy of the every-value source with word 0 bits 30:25 changed by xor from 1; a 128x64 copy with and without word 7 bit 1; two runs"
tiers = ["HW"]
date = "2026-11-03"
data = ["texture-copy-followup"]
terms = ["transfer_cmd.isp_background_tag"]
+++
**Results.** Layers 1: the source, every pixel; 0, 2, 3, 31, 63: 0xff6648dc at all 2048 pixels.

The 128x64 copy, baseline and with word 7 bit 1, was rejected before it ran ("job: rejected (Invalid
argument)") in both runs; the target kept its 0xdeadbeef fill.
