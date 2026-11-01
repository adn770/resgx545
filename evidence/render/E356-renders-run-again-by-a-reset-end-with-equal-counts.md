+++
id = "E356"
claim = "Render jobs queued on other contexts while a fault is held run again after the reset that ends the hold and end with the RT data set's executed count equal to the kernel's pending count: 0 and 0 for a render without render flag bit 10, then 1, 2 and 3 for a three-kick scene whose first kick ran again; every cleanup completes and each round resets once; two rounds, and the same jobs without a hold as control"
unit = "render"
method = "probes/render/replay-pending.toml on the laptop, linux fork b5a86838ae59 (commit 30: a reset sets the pending count to what the jobs it runs again add, sgx_render_executed) with the debug option on: with debugfs hold_recovery set a render faulting on its unmapped stream page; 3 s in three tri processes on their own contexts 1 s apart (one render with TA command word 7 bit 10 cleared by kernel poke, one render, a scene of three kicks, the first two geometry only), each with --words (render_words and buf09 after each render) and a 30 s wait; 2 s later debugfs reset with the hold set; twice, the render without bit 10 started last in the first round and the scene last in the second, since render_words shows the newest context; read with render_words.py report and log"
tiers = ["HW", "DDK"]
date = "2026-11-03"
data = ["render-replay-pending"]
terms = [
    "hw_rt_data_set.executed_count", "hw_rt_data_set.pending_count_dev_vaddr", "FRAG_FLAGS.BIT10",
]
+++

**Results** (pending, executed after each job, for the context each snapshot shows):

| round | case read (the newest context) | after job 1 | 2 | 3 |
|---|---|---|---|---|
| replay-a | render without bit 10 (run again) | 0, 0 | | |
| replay-b | three-kick scene (kick 1 run again) | 1, 1 | 2, 2 | 3, 3 |
| control | the same three, no hold | 0, 0; 1, 1; 1, 1 / 2, 2 / 3, 3 | | |

- In each round the held render fails with -EIO, the kernel log shows one stop, reset and boot,
  the kernel poke is applied at the submit while held, and the three queued jobs complete after
  the reset with the images of the control (the scene's closing render the same 2026 triangle
  pixels as without a hold). No render-context cleanup fails.

**What it shows.**

- A render run again by a reset adds what it adds the first time: none for a render without render
  flag bit 10, one for a geometry kick, and the kernel's count follows the per-kick rule, so the
  cleanup completes [HW: two rounds] [DDK: linux fork, commit 30]. render_uapi §13's follow-up on
  the replayed count is settled; the case of several unfinished jobs on one context is not run
  (the tool waits for each job).
