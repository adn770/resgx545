+++
id = "E049"
claim = "In the fill, the copy and the triangle alike, flipping bit 1 or bit 2 of the pixel-partition word of the kernel-built command, or setting it to 0xffffffff, hangs the job; the other 30 single-bit flips and the value 0 change nothing"
unit = "render"
method = "kernel-poke sweeps of probes/transfer/kernel-words.toml (fill-kernel, copy-kernel: word 101 of the transfer command) and probes/render/kernel-words.toml (tri-kernel: word 79 of the render details), on the laptop, linux fork with the debug option on; the triangle sweep ran twice (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["transfer-kernel-words", "render-kernel-words", "render-kernel-words-followup"]
terms = ["transfer_cmd.num_pixel_partitions", "hw_render_details.num_pixel_partitions"]
+++

**What runs.** The kernel builds the firmware command of every job itself, and its debugfs (`kpoke`)
can change a word of it, armed before the job, in the command the kernel builds for the next job.
Three sweeps each give the word that holds the pixel-partition count (`tq:101` in the 64x32 fill and
in the copy, `rd:79` in the 64x64 triangle) 34 values: each of its 32 bits flipped on its own, the
value 0 and the value 0xffffffff, one case, one fresh context each, after an unpoked baseline. The
kernel poke applied in all 34 cases of every sweep.

**Results.** In all three jobs the same three cases fail and the rest match the baseline image
(fill hash 0xb60c6095080bd325, copy hash 0x9b1c0be484ac0d25, triangle hash 0x99385a04ee01c585):

| job | word | `^=0x2` | `^=0x4` | `=0xffffffff` | other 31 values |
|---|---|---|---|---|---|
| fill | `tq:101` | hang | hang | hang | baseline image |
| copy | `tq:101` | hang | hang | hang | baseline image |
| triangle | `rd:79` | hang | hang | hang | baseline image |

A hang here is a job that never completes: the tool times out and the context is lost. The 31
unchanged values include the value 0 and every bit from 3 up, bits 26:22 among them. The triangle
sweep ran a second time, in a follow-up run, and `rd:79` gave the same three hangs and the same
baseline images for the rest; the fill and the copy ran once.

**Not shown.** Which value the job writes to the word is not tested, nor what a value other than
those tried (a count) would do; the sweep only separates the bits that hang the job from those
that do not. The visibility counters stayed at 0 in all runs.
