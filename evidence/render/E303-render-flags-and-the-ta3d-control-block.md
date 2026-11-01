+++
id = "E303"
claim = "Read after a job's context is cleaned up, the TA/3D control block keeps the RT data in dword 20 (the first DPM slot's owner) when the render flags had bit 2 or bit 3, and in dword 25 too with bit 3, and neither without them; with render flag bit 10 clear the render draws its image but the context's RT data set cleanup never completes, as after a scene of two kicks; dword 24 reads the TA client CCB's base plus 0x2c0 per render less one, dword 32 the context's PB descriptor, the one the cleanup names (the only one tried; that it is the cleanup's is the RE dataflow's reading), and dword 49 one more per context; two runs"
unit = "render"
method = "probes/render/frag-flags.toml on the laptop, linux fork with the debug option on: its script frag-flags.sh runs sgxfive-test tri with the render flags (TA command dword 7, kernel value 0x400) flipped by 0x4, 0x8, 0xc or 0x400 through the kernel poke ta:7, two renders on one context with the first flipped by 0xc, a scene of two kicks (the first geometry only), and one to four renders; after each it prints the EDM's TA/3D control block (debugfs buf09) and the last context cleanup's trace (debugfs render_cleanup); twice over; read with ta_words.py states"
tiers = ["HW", "RE", "infer"]
date = "2026-11-02"
data = ["render-frag-flags"]
terms = [
    "FRAG_FLAGS.BIT2", "FRAG_FLAGS.NO_DEALLOCATE", "FRAG_FLAGS.BIT10",
    "ta3d_ctl.dpm_slot0_rt_data_dev_vaddr", "ta3d_ctl.hw_rt_data_ta", "ta3d_ctl.cmd_ta_dev_vaddr",
    "ta3d_ctl.cleanup_pb_desc", "ta3d_ctl.render_context_count", "hw_rt_data_set.executed_count",
]
+++

**What runs.** Each case is one `sgxfive-test tri` process: a new render context, its renders,
then the context's cleanup when the process closes it. The control block is read after that,
with no context left. The kernel's addresses are the same in every case: the RT data set at
0x32411300 (its RT data at 0x32411318), the context at 0x32411000, the PB descriptor at
0x32411380, the TA client CCB at 0x32400000.

**Results.** Both runs agree in every case.

| case | dword 20 | dword 25 | cleanup |
|---|---|---|---|
| render flags 0x400 (the kernel's) | 0 | 0 | completes |
| 0x404 | 0x32411318 | 0 | completes |
| 0x408 | 0x32411318 | 0x32411318 | completes |
| 0x40c | 0x32411318 | 0x32411318 | completes |
| 0x000 (bit 10 clear) | | | fails (the kernel times out and resets the GPU) |
| two renders, the first 0x40c | 0 | 0 | completes |
| two kicks, the first geometry only | | | fails, as with bit 10 clear |

Every job draws the control's image (1062 triangle pixels). After the cleanups that complete,
dword 24 reads 0x32400000 after one render, 0x324002c0 after two, 0x32400580 after three and
0x32400840 after four; dword 32 reads 0x32411380, the PB descriptor the cleanup trace names;
dwords 41 and 42 read the render count. Dword 49 grows by one from case to case (5, 6, 7, 8 in
the second run), whatever the case's renders, and restarts at 1 after the resets.

**What it shows.**

- Either bit of the render flags' mask 0xc keeps the slot's owner, dword 20, after the render
  (the completion's test, 3d.md §5.4); `NO_DEALLOCATE` also keeps dword 25, which the TA finish
  clears for a last kick without it (§4.5). A later render with the bits clear clears dword 20
  again. The context's cleanup clears neither word.
- Without bit 10 the RT data set cleanup does not complete [HW]. That the cleanup waits for the
  count bit 10 adds at the render's completion is a reading: the completion adds it (E164) [RE],
  and E304's outcomes fit a cleanup that waits for the count to equal the host's [infer]; no
  case read the count.
- Dword 24 is the address of the last TA command, the CCB's read address of a 0x2c0-byte command
  [infer: four render counts]; dword 32 holds the PB descriptor the cleanup names, and the
  context's, since every case uses the one descriptor 0x32411380 [HW]: that it is the cleanup's
  rests on the EDM's dataflow, which writes it from the cleanup command's data (E013) [RE], and a
  cleanup of a context whose PB another shares would tell the two apart (Q029); dword 49 counts
  render contexts, one per context whatever its renders, since the firmware's boot [infer: it is not
  shown whether the first kick or the cleanup adds it].
