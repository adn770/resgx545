+++
id = "E313"
claim = "With CR_DPM_REG_074C bit 8 set the 64x64 job faults at the context's address 0x20006010 or 0x20006012 whether CR_DPM_STATE_BASE1 holds 0x20006000 or 0x20042000, so the address does not come from that register; on a context for up to 4096x4096, whose TA data covers 0x20006000, the same word renders the triangle exactly, with no fault and nothing written to the TA data's DPM pages"
unit = "dpm"
method = "probes/dpm/state-base.toml on the laptop, linux fork with the debug option on: its script state-base.sh runs a partial render on a 1024x768 context (0x30 pages), the 64x64 triangle with TA command word 167 = 0x100 (kernel poke ta:167), a partial render on a 4096x4096 context (0x100 pages), the poked 64x64 job again, then the poked and the unpoked 64x64 triangle as probe --tri on a context for up to 4096x4096 with its render memory dumped; registers 0x062c, 0x0634, 0x0674 and 0x0720 (debugfs regs) before each job; the faults from the table's kernel log; one run, two intended faults"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["dpm-state-base"]
terms = ["CR_DPM_REG_074C", "cmd_ta.dpm_reg_074c", "CR_DPM_STATE_BASE1", "CR_DPM_STATE_BASE0"]
+++

**Results.**

| case | 0x0674 before | job | fault |
|---|---|---|---|
| 1024x768 partial render (0x30 pages) | 0x20006000 | overflow | - |
| 64x64, ta:167 = 0x100 | 0x20006000 | faulted, recovered | 0x20006010 |
| 4096x4096 partial render (0x100 pages) | 0x20006000 | overflow, 0x0674 then 0x20042000 | - |
| 64x64, ta:167 = 0x100 | 0x20042000 | faulted, recovered | 0x20006012 |
| 64x64 on a 4096x4096 context, 0x100 | 0x20042000 | ok, 1062 triangle pixels | none |
| the same, no poke | 0x20042000 | ok | none |

Both faults are BIF status 0x90004 on page 0x20006000 of the job's context, like E203's eight.
The TA data of a 64x64 context ends at 0x20006000 (E310's layout); a 4096x4096 context's covers
it (its tail pointers, 0x20000000-0x2003ffff). In the job that renders with the bit set the
TA data's DPM control, OTPM and state pages stay zero, as without it.

**Reading [infer].** Bit 8 makes the DPM read or write near offset 0x6010 of the context's
TA-data space, at a place fixed by something other than `CR_DPM_STATE_BASE1` (which changes at
partial renders, E312) and not by the other bits (E203); with that place mapped the job is
unchanged. So it enables a DPM structure at a fixed offset of the TA data, which no client sets
up. Whether the offset follows `CR_DPM_CONTROL_BASE`, `CR_DPM_STATE_BASE0` or the TA data's base
is not separated: all three are at fixed distances from it in a 64x64 context.

**Not shown.** What the DPM writes there (the tail-pointer page under it was not dumped before
and after); a context whose TA data puts its control or state page elsewhere relative to 0x6000.
