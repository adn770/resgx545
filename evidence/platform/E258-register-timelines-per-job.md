+++
id = "E258"
claim = "Around the fill, the copy, the triangle, two renders in one context, two render contexts, a partial render and the triangle at seven sizes, 137 of the 206 registers sampled never change; a fill moves 23, a copy 13, a triangle 31 to 51, a partial render 57, and `contexts -n 2` only 2 (it renders nothing); the USSE slot registers 0x0aa4, 0x0aa8, 0x0b80 and 0x0b84 hold 0xaaaaaaaa when idle and other 2-bit-per-slot patterns while tasks run"
unit = "platform"
method = "probes/platform/register-timelines.toml on the laptop, linux fork with the debug option on: regtimeline samples 206 registers (every glossary register and the 13 with no row, less the four that move on their own and those the kernel's register file never reads) from 50 ms before each job to its end, printing each change: the debugfs fills and copies, the 64x64 triangle, two renders in one context, two render contexts and the 1024x768 triangle in a 0x30-page parameter buffer, twice each, then the triangle at 96x64, 256x256, 512x512, 1024x768, 1366x768, 2048x2048 and 4096x4096; one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-timelines"]
terms = [
    "CR_USE0_DM_SLOT", "CR_USE1_DM_SLOT", "CR_DMS_CTRL", "CR_CLKGATESTATUS", "CR_BIF_BANK0",
    "CR_EVENT_STATUS",
]
+++

**What runs.** regtimeline samples the registers in a loop, one pass of the 206 every 0.07 to 0.11
ms, and prints a line at each change; a register that changes and changes back between two passes is
missed, which matters for the fills and copies (about 0.1 ms each). Every job of the table completes
as it does without sampling: the fills and copies read correct, the triangles `diff: 0`, the partial
render the overflow and the image E202 reports at 0x30 pages.

**Registers that move.** Counted over each job, the registers whose value changed at least once:

| job | changed (run 1, run 2) |
|---|---|
| debugfs fills | 23, 23 |
| debugfs copies | 13, 13 |
| 64x64 triangle | 31, 51 |
| two renders in one context | 17, 14 |
| `contexts -n 2` | 2, 2 |
| 1024x768 triangle, 0x30 pages | 57, 57 |
| triangle at 96x64 to 4096x4096 | 34 to 45 |

The triangle's first run changed fewer because the jobs before it had left the same tiling values.
137 registers never change in any job: the identity, clock and init-script registers, the HWPerf
counters, most of the ISP's per-render words (the jobs load the same values), the TPU and USSE
coefficient words, the TA store registers and the DPM bases the contexts share. `contexts -n 2`
moves only `CR_CLKGATESTATUS` and `CR_USE0_DM_SLOT`: it creates and destroys render contexts without
a render.

**USSE slots.** `CR_USE0_DM_SLOT` and `CR_USE1_DM_SLOT` (0x0aa4, 0x0aa8) and 0x0b80 and 0x0b84 read
0xaaaaaaaa idle: sixteen 2-bit fields of value 2. While tasks run fields read 1 as well, and in
0x0aa4 also 3, in mixes such as 0x95555aa5 and 0x996aaa56 that change from pass to pass: a per-slot
state of each USSE pipe [infer]. 0x0b80 and 0x0b84 move only in the larger jobs.

**Not shown.** What each 2-bit slot value means; the registers' values inside the fills and copies,
which are shorter than a few passes.
