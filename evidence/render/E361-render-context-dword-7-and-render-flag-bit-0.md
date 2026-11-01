+++
id = "E361"
claim = "Render context dword 7 set to 0xdeadbeef or to the background object's address at the first kick changes nothing in a render, a scene of three kicks, a 1024x768 render that overflows its parameter buffer or the context's cleanup, and the word keeps the value through later kicks; render flag bit 0 hangs a render after its TA: held, the 3D has taken its render details, the PB descriptor holds the TA's two pages, the executed count is 0 against the kernel's pending 1, the RT data state reads 0x20; two runs and one"
unit = "render"
method = "probes/render/word-pokes.toml on the laptop, linux fork b5a86838ae59 with the debug option on: sgxfive-test tri with kernel pokes at the first kick (--kpoke-render 1:ctx:7=V; 1:ta:7^=0x1 for render flag bit 0), --words and --dump-render, against unpoked controls of the same shape, twice; the cleanup trace and the driver's lines per case; render flag bit 0 with debugfs hold_recovery set, render_words and the TA/3D control block read 2.5 s in, then debugfs reset with the hold set"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["render-word-pokes"]
terms = [
    "hw_render_context.param_obj_dev_vaddr", "ta3d_ctl.hw_render_details_3d", "hw_rt_data.state",
    "hw_rt_data_set.executed_count", "ta3d_ctl.frame_num_3d",
]
+++

**Results.**

- *Dword 7.* Every poked case draws the control's image (the 64x64 triangle exactly; the 1024x768
  render the same 154574 pixels wrong as its control, both failing with -ENOSPC), its cleanup
  completes (ret 0) and no fault is logged. The 64 bytes at the scratch primitive block (slot +
  0x463000, where the kernel points the word) read the same after every job, poked or not.
  render_words reads the poked value after the job, after the scene's third kick too.
- *Render flag bit 0.* The job hangs (the timeout detector, 1.0 s after the poke is applied) and
  is held. 2.5 s in: frag_flags 0x401; the context's pending render list holds the render details
  and submitted_commands is 1; the PB descriptor has allocated 2 pages; the TA/3D control block's
  `hw_render_details_3d` (dword 29) holds the render's details and both frame numbers read 1; the
  RT data set's executed count is 0, the kernel's pending count 1, the RT data state 0x20. The
  reset fails the job with -ETIMEDOUT; `CR_EVENT_STATUS` reads 0x20000800 at the reset.

**What it shows.**

- No path run here uses dword 7's value: the word and the object it points at are unchanged
  [HW: two runs] (Q049).
- Render flag bit 0 hangs the render in its 3D, after the TA has finished and the 3D has taken it,
  not at its cleanup [HW: one run]; its executed count is not added, as for a render that does not
  complete (Q065).
