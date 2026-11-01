+++
id = "E057"
claim = "Bit 0 of the render details' ZLS control word (rd:11, CR_ISP_ZLSCTL), and the value 0xffffffff, let the triangle job complete with no pixel written; the other 31 single-bit flips change nothing; the outcome is the same image as the render flags' bit 4 (E050), and both fresh runs agree"
unit = "zls"
method = "kernel-poke sweep of probes/render/kernel-words.toml (tri-kernel, word rd:11, 34 values) on the laptop, linux fork with the debug option on: the 64x64 triangle job, run twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-kernel-words", "render-kernel-words-followup"]
terms = ["hw_render_details.isp_zlsctl", "CR_ISP_ZLSCTL", "FRAG_FLAGS.SET_ZLSCTL_BIT0"]
+++

**What runs.** `kpoke` changes the ZLS control word of the kernel-built render details of the
triangle job after the job is submitted: each of its 32 bits flipped alone, the value 0, and
0xffffffff, a fresh context each. The kernel poke applied in all 34 cases. The unpoked job draws
1062 triangle pixels and 3034 background (hash 0x99385a04ee01c585).

**Results.** The flip of bit 0 (`^=0x1`) and the value 0xffffffff complete with `job: ok` and
write nothing: all 4096 pixels keep the sentinel (0xdeadbeef), hash 0xe4364b426cdce325. That is
the same hash as the render flags word with bit 1 or bit 4 flipped (E050). The other 31 cases,
the value 0 among them, give the baseline image. The follow-up run of the sweep gave the same
results.

**Not shown.** The sweep says that bit 0 of this word stops the render from writing pixels. It
does not show why two routes reach the same outcome, and the word is set to useful values
(not only its bit 0) in E058.
