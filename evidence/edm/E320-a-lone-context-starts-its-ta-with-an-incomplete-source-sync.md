+++
id = "E320"
claim = "On a lone render context the EDM starts a TA command whose one source sync is incomplete (read and write pending values 0x5a5a5a5a against a word that reads 0): the geometry kick completes, the render details take the sync (words 90 to 94), the closing render draws the control's image and the cleanup completes; the same kick with its transfer-queue sync set (word 25 = 0x5a5a5a5a, word 26 that word) never starts and the EDM faults reading page 0 through its own directory list, 15 (bus status 0xd0400), the read of the sync's second pointer, word 28, left 0; one run"
unit = "edm"
method = "probes/edm/ta-syncs.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script ta-syncs.sh runs sgxfive-test tri --words for a scene of two kicks (the first geometry only) on one render context, unpoked; then with the first kick's TA command poked (kernel poke ta:N): the source sync count (word 33) 1 and its four words (34 to 37) 0x5a5a5a5a and the address of a zero word of the context's kernel page (0x32411280, from the control's context words); then its transfer-queue sync (words 25 and 26) the same; then unpoked again; the kernel log"
tiers = ["HW", "RE", "infer"]
date = "2026-11-03"
data = ["edm-ta-syncs"]
terms = ["cmd_ta.shared", "hw_render_details.num_src_syncs", "hw_render_context.submitted_commands",
         "CR_BIF_INT_STAT", "CR_BIF_FAULT"]
+++

**Results.**

| case | kick 1 | kick 2 | cleanup |
|---|---|---|---|
| control | ok | ok, the control's image | completes |
| source sync incomplete | ok | ok, the control's image | completes |
| transfer-queue sync incomplete | fails: bus fault, context lost | not run | completes |
| control after | ok | ok | completes |

In the source-sync case render details words 90 to 94 read 1, 0x5a5a5a5a, 0x32411280,
0x5a5a5a5a, 0x32411280 after kick 1 (the kick's copy of the source syncs, 3d.md §4.4 step 7)
and 0 after kick 2, whose command has none; both counts reach 2. In the transfer-queue case the
context's `submitted_commands` reads 1 after the failed kick, the command never taken, and the
kernel logs a bus fault with status 0xd0400 and `CR_BIF_FAULT` 0xf, then resets: a read of page 0
through directory list 15, the EDM's own, for which the kernel names no client directory (PD 0).
The kernel recovers at once (hold_recovery is not set), and no registers are read.

**What it shows.**

- With no other context queued, the TA pick does not hold a command back for an incomplete
  source sync [HW], as E161 read the pick to skip that check when the TA queue holds no other
  context [RE]. The other half, that the check holds a command back when another context is
  queued, is not run: it needs two contexts with commands queued at once.
- The transfer-queue sync is read whatever the queue: with its first pointer set, the pick goes on
  to the pointer in word 28, here 0, and the EDM faults reading it [HW], which fits E161's reading
  that both pointers are compared when the first is set [infer]. As a control it shows that the
  poked words reach the pick.
- The fault's status sets bit 10, as the control block write of E319 does: both are the EDM's
  own accesses [infer], this one through its own directory list.
