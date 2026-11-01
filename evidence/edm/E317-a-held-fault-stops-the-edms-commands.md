+++
id = "E317"
claim = "With recovery held after a render faults reading its unmapped stream page, the EDM does not answer GETMISCINFO (the kernel's 500 ms wait ends the query, about 0.65 s from the shell), a fill on another context does not run, CR_BIF_INT_STAT reads 0x90008 and CR_BIF_FAULT 0x3e00000a the whole time, CR_EVENT_STATUS2 0x480, the interrupt counters do not move, the EDM tick count in CR_USE0_SERV_EVENT stays still between two reads 19 s apart, and the render memory holds no object and an all-zero TA data; the TA kick had taken the DPM slot and loaded the PB; a debugfs reset (halt, firmware buffers rebuilt, boot in place) recovers, the kernel log showing three more resets within 0.91 s: the fault watchdog's recovery of the faulted job, a failed render-context cleanup and the fault of a job left queued; one run"
unit = "edm"
method = "probes/render/hold-fault.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script hold-fault.sh sets debugfs hold_recovery, runs sgxfive-test tri --fault (the stream page unmapped) with a 20 s wait in the background, reads 2 s in the kernel log, every register (debugfs regs), kreg, status, GETMISCINFO (debugfs miscinfo, timed), the context's words and its render memory (debugfs render_param and render_tadata); then a fill on another context and the state again; then clears hold_recovery and writes debugfs reset; the tool's lines, words, cleanup trace and the state after the reset; the table's kernel log"
tiers = ["HW", "DDK", "infer"]
date = "2026-11-03"
data = ["render-hold-fault"]
terms = [
    "CR_BIF_INT_STAT", "CR_BIF_FAULT", "CR_EVENT_STATUS2", "misc_info",
    "ta3d_ctl.dpm_slot0_rt_data_dev_vaddr", "ta3d_ctl.hw_pb_desc_ta", "CR_USE0_SERV_EVENT",
]
+++

**Results.**

- *Before.* GETMISCINFO is answered in 1025 µs; `CR_BIF_INT_STAT` reads 0x00080000,
  `CR_BIF_FAULT` 0, `CR_EVENT_STATUS2` 0x400; the status file counts 58 SGX events and 0 bus
  faults.
- *Held.* The kernel logs the fault (status 0x90008 at 0x3e00000a, the job's page directory)
  about every 0.12 s and the job timeout about every second, with one "recovery held" line: the
  detectors keep logging while the recovery is held (205 lines), where the switch's description
  says they report once (a kernel follow-up, render_uapi.md §13). 2 s in: `CR_BIF_INT_STAT`
  0x00090008, `CR_BIF_FAULT` 0x3e00000a, `CR_EVENT_STATUS2` 0x480; the event and bus-fault counts
  unchanged (58, 0); GETMISCINFO times out (-ETIMEDOUT; 665 ms of the shell's time, the kernel
  waiting 500 ms [DDK: linux fork, sgxfive_debug.c]). The control block has dword 20 and 25 = the
  RT data (0x32411318) and dword 46 = the context's PB descriptor, all 0 before the job; dwords
  24, 26 and 27 hold the TA command, render details and context, the values the previous context
  had left there (at the same addresses), so they do not tell whether this kick wrote them. The
  render memory: the parameter slot holds only the page table (1066 non-zero dwords from slot
  offset 0x423000), the TA data is all zero.
- *A fill on another context*, submitted while held: its wait fails after 5 s ("Timer expired")
  and its target keeps the tool's sentinel; afterwards the status file shows 3 deferred kernel
  commands, GETMISCINFO again times out (667 ms from the shell), and the registers are unchanged:
  `CR_USE0_SERV_EVENT` reads 0x0001010e at both reads, where the EDM tick advances it about once
  a millisecond (E009).
- *Reset.* With hold_recovery cleared, debugfs reset takes 373 ms from the shell. The kernel
  log shows four resets within 0.91 s. The first two (1454.598 and 1454.746) are the debugfs
  reset and the fault watchdog's recovery of job 76, whose "recovering" line (1454.581) is the
  first after the hold is cleared; the log does not tell which ran first. A debugfs reset blames
  no job, so every unfinished job runs again after it [DDK: linux fork, sgxfive_reset_write]:
  if it ran first, job 76 ran again and faulted again before the watchdog's reset failed its
  context. Then a bus fault 0x90080 at 0x3e000001 in another page directory (job 77, the fill
  the tool had given up on, run after a boot; logged at 1454.954) and a failed render-context
  cleanup of the faulted context (1455.368) reset the GPU once each (1455.370, 1455.509).
  Afterwards GETMISCINFO is answered in 178 µs, the registers read as before the fault, and the
  fill and the triangle run exactly.

**What it shows.**

- A fault the kernel does not recover stops the EDM, not only the faulted job: neither a kernel
  command (GETMISCINFO) nor another context's job is served while it is held, and its tick no
  longer advances its service-event count [HW]. That the EDM's task is stalled on the faulted
  bus, rather than looping without serving, is the reading the still count gives [infer].
- The bus interface keeps the fault in its status and address registers until the reset, and
  raises no interrupt the kernel counts: the bus-fault and event counters do not move [HW].
- The TA kick had passed its PB load and DPM slot steps before the fault (3d.md §4.3, §4.4),
  and wrote nothing to the parameter buffer or the TA data [HW].
- A job a client stops waiting for stays queued in the kernel and runs after the next boot,
  where its own memory may be gone [HW: one case].
- A reset written while a recovery is held is not given the held job as its suspect, so the
  held job may run again before a detector blames it, and the reset count after a hold depends
  on the order [DDK: linux fork]; recovering with the held suspect is a kernel follow-up
  (render_uapi.md §13).
