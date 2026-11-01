+++
id = "E455"
claim = "On a new transfer context, poking word 0 of its HW context to 0x2 makes a fill complete without writing (2 of 2 runs), 0x10 or 0x12 or a priority word of 1 or 2 hang the job (12 of 12 jobs, the driver recovered each), a priority word of 3 faults it (2 of 2), and the controls complete (4 of 4)"
unit = "transfer"
method = "probes/transfer/ctx-flags.toml (ctx-flags.sh) on the laptop (direct cable), sgxfive-test dummy and fill with --kpoke-job 1:th:W=V (kernel poke th:W=V, linux fork commit 40, applied at the job's submission), 12 cases of two runs, the GPU reset before each, the kernel log and the exit status of each run kept; sgxfive-test 6f8f2bf8, linux fork ea5482bc59a6 with the debug option on, module srcversion 9A7BCDC4FC2A2166A409EEA (loaded and installed equal, both printed by the run)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["transfer-ctx-flags"]
terms = ["hw_transfer_context.fw_com_ctx_flags", "hw_transfer_context.priority"]
+++

**What runs.** The transfer context's HW context holds the flags in word 0 and the priority in word
1 (Q004). The linux fork's kernel poke `th:W=V` (commit 40) writes a word of it when the next
transfer job is submitted, a dummy too, and sgxfive-test's `dummy` and `fill` take `--kpoke-job
1:th:W=V` to write the poke just before the job. Each case ran on a new context after a GPU reset,
twice (24 runs). A job that did not complete is reported as hung or faulted: the dummy after 4 s of
waiting, the fill given up by the driver's hang detector after 1.018 to 1.039 s (kernel.log "job N
hung, recovering"), before the tool's 5 s wait ends.

**Results** (the same in both runs of each case).

| word poked | dummy job | fill of 64x64 (destination otherwise the sentinel) |
|---|---|---|
| none (control) | completes | completes, 4096 of 4096 dwords written |
| word 0 = 0x2 | completes | completes in 3.2 to 3.3 ms, 0 of 4096 dwords written |
| word 0 = 0x10 | hung | hung |
| word 0 = 0x12 | hung | not run |
| word 1 = 1 | hung | hung |
| word 1 = 2 | hung | not run |
| word 1 = 3 | faulted | not run |
| word 0 = 0x10, then a second dummy job whose poke sets word 0 = 0 | both jobs complete | not run |

Counts: 12 jobs hung (dummy: 0x10, 0x12, priority 1, priority 2, two runs each, 8; fill: 0x10 and
priority 1, two runs each, 4); the driver logged "hung, recovering" 12 times (kernel.log) and no
recovery failed; the 2 priority-3 jobs faulted with a BIF fault (INT_STAT `0xd0400`, BIF_FAULT
`0xf`: list 15, the EDM's own directory, page 0); 22 pokes were logged as applied. The controls (2
dummy jobs, 2 fills) completed (a fill in 0.36 to 0.38 ms), and the health fill and triangle at the
end of the run were exact. A hung fill was given up after 1.018 to 1.039 s (4 jobs, by the driver's
hang detector); the fill with flags 0x2 took 3.2 and 3.3 ms.

**What it shows.**

- Flag bit 1 makes a fill take the path of a dummy: the job completes and writes nothing (2 of 2)
  [HW]. That the firmware clears the bit afterwards is not shown (the tool cannot read the word
  back).
- A job on a context whose flag bit 4 is set never completes (6 of 6 jobs, the fill included) [HW].
  That the pick routine skips the context (E015) is the reading that fits; a job left in the queue
  and a job the firmware lost are not told apart by this run [infer].
- A priority of 1 or 2 hangs the job (6 of 6) and 3 faults it (2 of 2) [HW]; that priorities above
  0 reach queue slots the firmware does not set up, or ones another queue uses, is [infer] from the
  dataflow (secondary attributes 13 + priority and 14 + priority, E015).
- The chain whose second job cleared word 0 completed (2 of 2). The second poke is applied when
  that job is submitted, right after the first job's, so the flags may have been cleared before the
  firmware picked the first job; the chain does not show that a cleared bit 4 releases a job the
  firmware had skipped.

**What it does not show.** Whether bit 4 is a suspend that a CONTEXTSUSPEND command sets and
clears, whether anything but the host sets bit 1, what the priorities above 3 do, the words after
the job (they are not read back), and the effect of the flags on a context with several jobs
queued.

**Sources of the counts.** kernel.log is authoritative for the facts only the log holds (the 12
"hung, recovering" lines, the 22 "kpoke applied" lines, the BIF faults, no "recovery failed"):
the script's dmesg filter lost lines from output.txt, which holds only 6 of the 22 "kpoke applied"
lines and none of the 12 "hung, recovering" lines.

**Provenance.** linux fork commit ea5482bc59a6 with the debug option on, module srcversion
9A7BCDC4FC2A2166A409EEA (the loaded module, read from /sys/module, equal to the installed file's
modinfo; both printed by the run), sgxfive-test sha256
6f8f2bf8295d302f50594b02b92989a72a127adc36b0a8cf245cbd14c53da4f5 (built from this phase's overlay
source, named in each env.toml), the laptop over the direct cable.
Revised after these runs: the series was rebuilt on tip 6ee9501832af, which clears armed pokes on
load and reset (commit 40), moves the submission's poke calls into one function,
sgxfive_submit_xfer_pokes() (40), makes alias_skip refuse bits 16-31 with -EINVAL (42) and rewords
comments and commit messages (40 to 42); the module of these runs is the one built from
ea5482bc59a6. The paths this run used did not change [infer]: git diff ea5482bc59a6 6ee9501832af
leaves the th poke's arming, its application at the job's submission (the same two calls, in the
same order) and the transfer path as they were, and ctx-flags.sh resets the GPU before each case and
arms its pokes after, so the clear on reset had none to drop (22 pokes armed, 22 logged as applied).
