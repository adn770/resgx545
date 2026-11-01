+++
id = "E355"
claim = "While a faulting render's recovery is held, another render context's cleanup that the stopped EDM does not answer fails (ret -110) and logs its warning, but no reset follows: the EDM still answers no GETMISCINFO, the bus fault stays in the status registers and seven kernel memory releases wait on the deferred list; the debugfs reset that ends the hold resets once, fails the held render with -EIO, empties the deferred list, and the faulted context's own cleanup then completes; one run"
unit = "render"
method = "probes/render/held-reset.toml (its cleanup case) on the laptop, linux fork b5a86838ae59 with the debug option on: with debugfs hold_recovery set, a 128x128 triangle on its own context writes its every pixel (--pixels) into a pipe read only 4 s later, so the tool waits with its render done and its context alive; 1 s in a render faulting on its unmapped stream page (30 s wait) is held; once the pipe is read the triangle's tool destroys its context; 2 s later the driver's lines, the state (status, GETMISCINFO) and the cleanup trace (debugfs render_cleanup); debugfs reset with the hold set; the lines, the state and the cleanup trace again"
tiers = ["HW", "DDK"]
date = "2026-11-03"
data = ["render-held-reset"]
terms = ["misc_info", "hw_rt_data_set.executed_count"]
+++

**Results.**

- The triangle renders exactly (4284 triangle and 12100 background pixels). The faulting render
  is held 0.1 s after its kick (the fault line and the hold's warning).
- 3.3 s into the hold the triangle's context is destroyed: the kernel logs "render context cleanup
  failed, resetting" and the cleanup trace reads ret -110, with the TA's PB descriptor before the
  cleanup at the faulting context's (0x32423380). No stop, reset or boot line follows. 2 s later
  hold_recovery reads Y, the status file counts 7 deferred releases, `CR_EVENT_STATUS2` reads
  0x480 and GETMISCINFO times out (649 ms from the shell).
- The reset (275 ms) is the only one in the case: stopped, reset, boot, EDM up. The held render's
  tool reports -EIO. Afterwards the deferred count is 0, GETMISCINFO is answered in 170 µs, the
  last cleanup trace is the faulted context's (0x32423000, flags 0x1) with ret 0, and a fill and
  the triangle run exactly.

**What it shows.**

- The reset a failed cleanup asks for is not done while a recovery is held: the hold stays and
  the context's memory waits for the reset that ends it, which resets for both [HW: one run]
  [DDK: linux fork, commit 31].
- A held render's context cleanup completes after a reset that blamed it; E317's and E318's
  cleanups failed after blame-free resets that ran the held job again [HW: one run] [infer].
- The held job's own context cannot be cleaned up during the hold at all: its unfinished job keeps
  a reference to the context, so its cleanup runs after the reset
  [DDK: linux fork, sgxfive_ctx_release].
