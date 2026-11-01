+++
id = "E315"
claim = "The RT data set's cleanup completes only when its executed count equals the word the set's word 0 points at: one render whose pending count is poked to 2 or to 0 (executed 1) fails its cleanup, and with the count at 2 but word 0 pointed at the executed count itself it completes; render details word 54 moved by 0x8 puts the count in the set's word 3, so one render leaves executed 0 against pending 1 and a scene of two kicks executed 1 against pending 2, and both cleanups fail; one run each"
unit = "render"
method = "probes/render/pending-kw.toml and probes/render/pending-rd54.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: their scripts run sgxfive-test tri --words (debugfs render_words and buf09 before the first render and after each) with kernel pokes of the kernel's pending count (kw:1, after the kernel's own write) and of the RT data set's word 0 (rtds:0), applied at the kick, and with render details word 54 flipped by 0x8 (rd:54) on one render and on a scene's geometry kick; controls before and after; the cleanup trace (debugfs render_cleanup) and the kernel log; read with render_words.py report"
tiers = ["HW"]
date = "2026-11-03"
data = ["render-pending-kw", "render-pending-rd54"]
terms = [
    "hw_rt_data_set.executed_count", "hw_rt_data_set.pending_count_dev_vaddr",
    "hw_rt_data_set.num_out_of_mem_signals", "hw_render_details.count_rt_data_set",
    "ta3d_ctl.render_context_count",
]
+++

**What runs.** The RT data set is at 0x32411300; its word 0 holds 0x3241120c, the kernel's
pending count. Each poked case is one render (or a scene of two kicks) on a new context.

**Results.** Pending and executed counts after the last job, and the set's word 3.

| case | pending | executed | word 3 | cleanup |
|---|---|---|---|---|
| control | 1 | 1 | 0 | completes |
| pending poked to 2 | 2 | 1 | 0 | fails (-110) |
| pending poked to 0 | 0 | 1 | 0 | fails (-110) |
| pending 2, word 0 = 0x32411304 (the executed count) | 2 | 1 | 0 | completes |
| one render, rd:54 ^ 0x8 | 1 | 0 | 1 | fails (-110) |
| two kicks, rd:54 ^ 0x8 on kick 1 | 2 | 1 | 1, then 0 after kick 2 | fails (-110) |
| control after | 1 | 1 | 0 | completes |

Every job completes and draws the control's image. Each failed cleanup makes the kernel reset
the GPU (kernel log: "render context cleanup failed, resetting"); the case after it runs
normally. The kernel zeroes the set's word 3 before each job, so the geometry kick's count there
is gone after the closing render. After each of those resets the control block's dword 49
(`render_context_count`) reads 0, and the next context's first kick makes it 1.

**What it shows.**

- The cleanup compares the executed count with the word the set's word 0 points at, and waits
  for them to be equal: a pending count one above or one below fails it, and the same counts
  pass once word 0 points at the executed count itself, which is then compared with itself
  [HW]. Word 0 is a pointer the firmware reads, not padding.
- Render details word 54 is the set the firmware counts in, and the count lands one word after
  the address it holds: moved by 0x8, the count of a render and of a geometry kick appear in
  word 3 [HW]. This restates E304's reading with the counts read: under the kernel that counts
  each kick, the two-kick scene whose geometry count is moved away now fails, as one render's
  does.
