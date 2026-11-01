+++
id = "E120"
claim = "No bit of the render details' isp_sample_pos (word 19), reg_0800 (word 22), isp_line_sample_pos (word 26) or frag_flags (word 53), nor of the render command's word 10, runs a 4x triangle's sample-rate pixel shader per sample; 22 bits of isp_multisamplectl (render details word 20, the same register as command word 16, with identical images bit for bit) move the samples and the coverage by a few samples (1240 to 1256 covered samples in 320 to 328 pixels against the control's 1248), the rest change nothing"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/sample-rate.toml, probes usse-sample-rate-rdrate-rd19, -rd20, -rd22, -rd26, -rd53 (one bit of the render details word flipped by the kernel's poke) and -cmd10, -cmd16 (one bit of the render command's word flipped), the 4x triangle of E115 at the sample rate, 224 cases, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-sample-rate"]
terms = ["hw_render_details.isp_multisamplectl", "hw_render_details.isp_sample_pos"]
+++

**What runs.** The 4x triangle of E117's control (1248 samples drawn, one value in every 2x2
block), with one bit flipped per case in each of seven words, 32 cases a word. The pixel shader
writes o0 from its g-bank place, so two different instance values in a block would show a
per-sample run.

**Results.** All 224 cases complete. Render details word 19, 22, 26 and 53 and command word 10:
all 160 cases give the control's image. Render details word 20 and command word 16: 10 bits
give the control's image; the other 22 (bits 1 to 3, 5 to 7, 9 to 11, 14 to 16, 18, 19, 21 to
23, 26 to 28, 30 and 31) each change it, with 1240 to 1256 covered samples (one case, bit 27,
has 1248 again but another image) in 320 to 328 pixels. The word 20 and word 16 sweeps give the
same image in every one of the 32 cases. In every image each block of drawn samples holds one
value. Baselines before and after every probe were exact; no visibility counter counted.

**What it shows.** isp_multisamplectl holds sample positions: the changed images fit positions
moved across the triangle's edges. None of the words reachable by the kernel's pokes or the
command turns per-sample shading on. With E115 and E117 that leaves render details words not
swept, registers the kernel does not expose, or a core without the mode.

**Not shown.** That the changed images are position shifts is a reading of coverage counts
**[infer]**; the positions themselves were not read. One run per case.
