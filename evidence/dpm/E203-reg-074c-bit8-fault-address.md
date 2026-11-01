+++
id = "E203"
claim = "With bit 8 of ta:167 (the word loaded into CR_DPM_REG_074C) set, the job faults at the same BIF address, 0x20006011, whatever the other bits (0x1100, 0x10100, 0x100100, 0x1000100, 0x10000100, 0x80000100 and 0x101: seven of the eight values), and at 0x20006013 once, with bit 8 alone, which was also the first case of the run, so value and run order are not separated"
unit = "dpm"
method = "the script of probes/dpm/reg-074c.toml (fault_addresses): eight values of ta:167 through the kernel's per-render poke in the 64x64 triangle job, the kernel log read after each, on the laptop with the linux fork and the debug option on, one run"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["dpm-reg-074c"]
terms = ["CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c"]
+++

**What runs.** The values are 0x100, 0x1100, 0x10100, 0x100100, 0x1000100, 0x10000100, 0x80000100
and 0x101. Each is set on ta:167 for one render of the triangle job and the new kernel log lines are
kept.

**Results.** All eight jobs fail with "job faulted, context lost" and the kernel recovers each time
(a reset, then one live context loaded again). Each log has one BIF fault, status 0x90004:

| ta:167 | fault address |
|---|---|
| 0x100 | 0x20006013 |
| 0x1100, 0x10100, 0x100100, 0x1000100, 0x10000100, 0x80000100, 0x101 | 0x20006011 |

The page is 0x20006000 in all eight; the low bits differ in one case, 0x100, which is the first
case of the script; every later case gives 0x20006011. The page directory shown by
the kernel differs between the cases, as each job has a fresh context.

**Reading [infer].** The faulting address does not move with the seven other bits tried (0, 12, 16,
20, 24, 28 and 31), which rules out an address field in those bits only; bit 8 makes the DPM use
something at a place fixed in the context's address space, near 0x20006000, that was not set up. Why
the low bits are 0x13 once and 0x11 otherwise is not known: bit 8 alone and the first case of the
run are the same case here.

**Not shown.** What lies at 0x20006000: the table does not map a buffer there, so the access type
and the structure are not seen. The other bits of the address are one page of the context's address
space; whether that page follows the end of the TA data buffers is not read from this log. Values
with bit 8 clear were not run here (E054, E056 hold them). The bits 1 to 7, 9 to 11 and the others
not listed were not tried with bit 8. A run in another order (0x100 not first) would tell whether
the 0x13 comes from the value or from the first job after the script starts. One run.
