+++
id = "E412"
claim = "CR_REG_0148 (render details dword 9) at 0 and at 1 gives the same image, the same stored pages and a time within the spread in a render with depth and stencil stored, in 4x multisampled renders in modes 1 and 2, in a 1024x768 render and in a 1024x768 render that overflows the parameter buffer at 0x24 and 0x30 pages (the same wrong-pixel count each), three runs each"
unit = "render"
method = "probes/render/reg-0148-jobs.toml (reg-0148-jobs.sh: 24 jobs) and probes/render/reg-0148-partial.toml (reg-0148-partial.sh: 18 jobs) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: rd:9 poked to 0 and 1 through the kernel poke in the depth-and-stencil store setup of probes/zls/control-bits.sh, in CR_ISP_MSAA modes 1 and 2 with the sample words of E210 and the TE bits, in the 1024x768 triangle, and in the 1024x768 triangle with render_pb_pages 0x422, 0x24 and 0x30"
tiers = ["HW"]
date = "2026-11-07"
data = ["render-reg-0148-jobs", "render-reg-0148-partial"]
terms = ["CR_REG_0148"]
+++

**What was seen.** Depth and stencil stored: both values gave the control's image (hash
0x99385a04ee01c585) and the same stored pages (a stencil page and four depth pages), times 18.9 to
25.7 ms against 20.7 to 24.7 ms. Mode 1: 786 pixels wrong with both values (the tool's reference
does not model it), mode 2: 807, the same hash each time, times 7.5 to 9.2 ms. The 1024x768
triangle: exact with both, 861 to 866 ms. The overflowing scene: with 0x422 pages (no overflow)
exact with both values; with 0x24 pages the job fails with "scene overflowed the parameter buffer"
and 2225 pixels wrong, with 0x30 pages 154574 wrong, the same hash for 0 and 1 in all three runs
each.

**What it shows.** Bit 0 of the word the firmware loads into CR_REG_0148 changes none of these jobs
(and E302's five copies, a fill and a copy), all of which write o0 only: the plain value 0 and the
value 1 give the same pixels and times in depth, multisampled, large and partial renders. With a
shader that writes o1 to o3 as well bit 0 is not inert: E406 finds that with it set o1 no longer
lands on other pixels (with the other settings of E406).

**What it does not show.** A copy with filtering (not run: the transfer tool has no filtered copy);
other bits of the word (E302 covers them on a triangle); what the register is for.
