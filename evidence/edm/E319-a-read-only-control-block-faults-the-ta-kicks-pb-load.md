+++
id = "E319"
claim = "With the TA/3D control block mapped read-only in the render client's VM (debugfs alias_ta3d_ro) the first kick faults on the block's page, CR_BIF_INT_STAT 0x80400 and CR_BIF_FAULT 0x32004005, before the PB load writes dword 46 and before the DPM slot is taken (dwords 46, 20 and 25 stay 0), after the render-context count (dword 49) has moved; the job stalls, GETMISCINFO is not answered while recovery is held, and the job fails with a fault once recovered; one run"
unit = "edm"
method = "probes/render/ta3d-ro.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script ta3d-ro.sh sets debugfs alias_ta3d_ro and hold_recovery, runs sgxfive-test tri --words with a 20 s wait in the background, reads 2 s in the kernel log, every register (debugfs regs), kreg, status, GETMISCINFO (timed) and the context's words and control block; then clears hold_recovery, writes debugfs reset, clears alias_ta3d_ro and runs an unpoked render"
tiers = ["HW", "infer"]
date = "2026-11-03"
data = ["render-ta3d-ro"]
terms = ["ta3d_ctl", "ta3d_ctl.hw_pb_desc_ta", "ta3d_ctl.render_context_count",
         "ta3d_ctl.dpm_slot0_rt_data_dev_vaddr", "CR_BIF_INT_STAT", "CR_BIF_FAULT"]
+++

**What runs.** The control block is at 0x32004000 (its own dword 0). The kernel maps every
firmware buffer into a render VM at its own address, read-only except this block (render_uapi.md
§5.3); the switch maps the block read-only too.

**Results.** The kernel logs a bus fault, status 0x80400 at 0x32004005 in the job's page
directory, and holds the recovery. 2 s in: `CR_BIF_INT_STAT` 0x00080400, `CR_BIF_FAULT`
0x32004005, `CR_EVENT_STATUS2` 0x400; GETMISCINFO times out (666 ms from the shell). The control
block:

| dword | before the job | held | unpoked render, after |
|---|---|---|---|
| 20, 25 (DPM slot, TA RT data) | 0, 0 | 0, 0 | 0, 0 |
| 24, 26, 27 (command, details, context) | as left | 0x32400000, 0x32411400, 0x32411000 | same |
| 46, 47 (PB loaded for the TA, the 3D) | 0, 0 | 0, 0 | 0x32411380, 0x32411380 |
| 49 (render contexts) | 4 | 5 | 1 |

The previous context had the same addresses, so dwords 24 to 27 cannot tell this kick's writes
from that context's. After the reset the job fails ("job faulted, context lost"), its replay
faulting again; with the switch cleared an unpoked render draws the control's image.

**What it shows.**

- The first write the TA kick makes to the control block through the client's page directory
  faults [HW]: dword 46, which the PB load writes, stays 0, and the DPM slot step after it never
  runs (§4.3, §4.4). That the faulting write is dword 46's is a reading [infer]: the fault
  address gives the page only, and dword 46 is the first write the dataflow places in that
  window (E200).
- Dword 49 grows by one before that point: the render-context count moves at the kick, not at
  the cleanup [HW], which E303 left open. The tables of E314 and E316 show the same at every
  context's first kick, and the count going from 0xe to 0 there with no reset [HW].
- A render client's VM cannot do without a writable mapping of the block while the EDM loads
  parameter buffers through the client's directory [HW]. Whether a per-VM copy would do is not
  tried.
- The bus status bit of this fault is bit 10 where the stream read of E317 sets bit 3: the bit
  follows the requester [infer: two faults].
