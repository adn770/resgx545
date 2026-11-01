+++
id = "E314"
claim = "Read while the context lives, the RT data set's executed count (word 1) and the kernel's pending count rise together by one at every kick, the geometry kicks included, and are equal after every job of scenes of one to four kicks; a render without render flag bit 10 adds to neither, so its cleanup completes; every cleanup of the table completes and no case resets the GPU, where one-count-per-scene cleanups of two kicks had failed; one run"
unit = "render"
method = "probes/render/pending-counts.toml on the laptop, linux fork 66dc1fda6ae8 (the pending count raised once per kick, debug option on): its script pending-counts.sh runs sgxfive-test tri --words (debugfs render_words and buf09 saved before the first render and after each) for one render, scenes of two and three kicks (the first geometry only), two renders, two scenes of two kicks, a render with render flag bit 10 cleared (kernel poke ta:7^=0x400) and a scene of two kicks whose closing render has it cleared; the cleanup trace (debugfs render_cleanup) after each; read with render_words.py report"
tiers = ["HW", "DDK"]
date = "2026-11-03"
data = ["render-pending-counts"]
terms = [
    "hw_rt_data_set.executed_count", "hw_render_details.count_rt_data_set", "FRAG_FLAGS.BIT10",
    "hw_rt_data.state", "hw_render_context.pending_renders_head",
    "ta3d_ctl.dpm_slot0_rt_data_dev_vaddr", "ta3d_ctl.hw_rt_data_ta",
    "ta3d_ctl.render_context_count",
]
+++

**What runs.** The kernel keeps the pending count in its context page (`kw:1`, at 0x3241120c,
the address the RT data set's word 0 holds) and raises it at each kick by what the kick adds to
the executed count: one for a kick that is not the scene's last, one for a last kick whose
render has render flag bit 10, else none [DDK: linux fork, sgx_render_executed]. The context is
at 0x32411000, the RT data set at 0x32411300 (its RT data at 0x32411318), the render details at
0x32411400, in every case.

**Results.** Pending and executed counts, read after each job.

| case | after job 1 | 2 | 3 | 4 | cleanup |
|---|---|---|---|---|---|
| one render | 1, 1 | | | | completes |
| two kicks | 1, 1 | 2, 2 | | | completes |
| three kicks | 1, 1 | 2, 2 | 3, 3 | | completes |
| two renders | 1, 1 | 2, 2 | | | completes |
| two scenes of two kicks | 1, 1 | 2, 2 | 3, 3 | 4, 4 | completes |
| one render, bit 10 cleared | 0, 0 | | | | completes |
| two kicks, the render's bit 10 cleared | 1, 1 | 1, 1 | | | completes |
| one render, after | 1, 1 | | | | completes |

Every render draws the control's image (1062 triangle pixels), the closing render of a scene
included. Before the first render both counts are 0. Between the kicks of an open scene the
context's pending render list (context words 8 and 9) holds the render details, RT data `state`
(set word 19) has bit 4 clear, where it is set before the scene and after its render, and the
TA/3D control block's dwords 20 and 25 hold the RT data; the closing render empties the list,
sets bit 4 again and clears both dwords. No case writes the access word (`kw:0`). The table's
kernel log holds no reset. The control block's dword 49 (`render_context_count`) rises by one at
each context's first kick (7 before the first case) and not at its later kicks, and goes from
0xe to 0 at the first kick of the last case, never reading 0xf.

**What it shows.**

- Every kick of a scene adds one to the executed count when it finishes, as the firmware's TA
  finish and render completion were read to do (E156, E164) [HW]: the count follows the jobs one
  by one, and after the closing render it equals the number of kicks.
- A render without bit 10 adds nothing: the count does not move [HW]. Its cleanup completes
  because the kernel did not raise the pending count either.
- With the pending count raised by the same rule, every cleanup completes, where scenes of two
  kicks failed theirs when the kernel raised it once per scene (E303, E304) [HW].
- The render-context count of the control block moves at a context's first kick and wraps after
  0xe without a reset [HW]: a count or index modulo 15, not a plain count since the boot
  [infer]; E316's table shows the same wrap.
