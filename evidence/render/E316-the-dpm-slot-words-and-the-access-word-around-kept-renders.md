+++
id = "E316"
claim = "Read while the context lives, a render with render flag bit 2 leaves the TA/3D control block's dword 20 (the first DPM slot's RT data) set and dword 25 clear, one with bit 3 or both leaves both set; a later render on the context with the bits clear clears both; a new context at the same addresses starts with them set and its first render draws the control's image and clears them; the access word render details word 52 points at stays 0 in every case; with debugfs rtds_keep set the kernel leaves the RT data set's words as the previous job left them (an out-of-memory count poked to 5 stays 5) and nothing else of the set's words changes, the kept dwords cleared by the second render as without it; one run"
unit = "render"
method = "probes/render/slot-words.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script slot-words.sh runs sgxfive-test tri --words (debugfs render_words and buf09 before the first render and after each) with the render flags (TA command dword 7, kernel value 0x400) flipped by 0x4, 0x8 and 0xc (kernel poke ta:7), two renders the first flipped by 0xc, a render on a new context after a plain render and after a 0xc render with the registers 0x0600-0x0750 read after it (--regs), then with debugfs rtds_keep off and on a scene of two kicks, two renders the first flipped by 0xc and two renders with the set's word 3 poked to 5 at the first (rtds:3); read with render_words.py report"
tiers = ["HW"]
date = "2026-11-03"
data = ["render-slot-words"]
terms = [
    "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "ta3d_ctl.dpm_slot0_rt_data_dev_vaddr",
    "ta3d_ctl.hw_rt_data_ta", "hw_render_details.access_dev_vaddr",
    "hw_rt_data_set.num_out_of_mem_signals", "CR_DPM_PAGE_STATUS", "ta3d_ctl.kick_clear_3d",
    "ta3d_ctl.render_context_count",
]
+++

**What runs.** Every context has the same addresses: the RT data at 0x32411318, render details
word 52 pointing at the kernel's access word at 0x32411208.

**Results.** TA/3D control block dwords 20, 21 and 25 after each job.

| case | after render 1 | after render 2 |
|---|---|---|
| render flags 0x404 | 20 = 0x32411318, 21 = 0, 25 = 0 | |
| 0x408 | 20 = 25 = 0x32411318 | |
| 0x40c | 20 = 25 = 0x32411318 | |
| two renders, the first 0x40c | 20 = 25 = 0x32411318 | all 0 |
| a new context after a 0x40c render | all 0 (20 and 25 = 0x32411318 before it) | |
| a new context after a plain render | all 0 | |

Every render draws the control's image (1062 triangle pixels) and every cleanup completes. The
access word reads 0 before and after every job. Of the registers 0x0600-0x0750 read after the
new contexts' renders only `CR_DPM_PAGE_STATUS` (0x0724) differs: 0x8 after the 0x40c
predecessor, 0x6 after the plain one.

With rtds_keep off and on, the scene of two kicks and the two renders (the first 0x40c) give the
same counts, the same control block words and the same image. Poked to 5 at the first render,
the set's out-of-memory count reads 5 after it in both runs; after the second it reads 0 with
rtds_keep off, the kernel's rewrite, and 5 with it on. Both jobs complete either way. Of the
control block's other words, dword 57 (`kick_clear_3d`) reads 1 once, after the first of the two
renders whose out-of-memory count is poked to 5 with rtds_keep on, and 0 in every other snapshot
of the table, the same case with rtds_keep off included; what set it is not shown. Dword 49
(`render_context_count`) rises by one at each context's first kick, from 6 before the first
case, and goes from 0xe to 0 at the first kick of the scene of two kicks with rtds_keep off, then
on to 5; the table's kernel log holds no reset.

**What it shows.**

- Bit 2 keeps the first slot's owner, bit 3 the TA's RT data as well, now read while the context
  lives, not only after its cleanup (E303) [HW].
- A kept slot owner does not stop a later render: a render with the bits clear on the same
  context clears both dwords, and a new context whose RT data has the kept address renders
  exactly and clears them [HW]. What happens with a new context at another address is not shown:
  every context of the tool lands at the same addresses.
- The kernel's rewrite of the RT data set before each job is not what clears the kept words:
  with it off the second render clears them as before [HW]. The out-of-memory count the kernel
  zeroes is not read by any of these jobs.
- The access word is not written by these renders [HW].
