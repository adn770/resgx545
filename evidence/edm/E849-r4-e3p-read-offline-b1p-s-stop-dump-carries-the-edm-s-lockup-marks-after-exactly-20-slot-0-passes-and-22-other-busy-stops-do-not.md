+++
id = "E849"
claim = "Read offline after the hypothesis (post hoc, no frozen prediction; round 5 plan closing5/events, step F0): E836's b1p stop dump, taken at the stop's signature before the host's clears, holds HostCtl dword 3 (host_ctl.ukernel_detected_lockups) = 1 and dword 8 (host_ctl.interrupt_flags) = 1, dword 9 0, dword 14 0, sw_events 1 and TA3DCtl dwords 56 to 58 = 0, 0 (ta3d_ctl.kick_clear_3d), 0xaac267c2, where the dumps of the same job at the arm read 0 throughout; its page counts exactly 20 slot 0 passes after the fill's kick entry (10 ticks logged in the ring, then 10 counted with the ring full), 2 x host_ctl.hw_recovery_sample_rate (dword 5 = 10), against 0 in E823's b1 and 302 and 289 in the two fills that completed; of the 23 published dumps past the boot with CR_CLKGATESTATUS 0x000ccfa0, b1p's alone has dword 3 or dword 8 set (the other 22 read 0, 0 and dwords 56 to 58 = 0): [infer] the stop is the EDM's own lockup routine of E353, its second sample of a 3D progress word equal to the first"
unit = "edm"
method = "offline, no laptop session: three read-only scripts of the round 5 plan (closing5/events/exp-events-r5.md section 2, O1 to O3), written after the hypothesis was formed from b1p's dump and run on 2026-11-12, published with their outputs in closing5/events/offline/ (dataset cited-scratch); ticks_after.py reads a kept job record's page (the slot 0 ring of 16 rungs at dword 256, the slot 3 ring at dword 512, the ring-full counters dwords 16 to 19 that asm/ring_skip3p.s counts only with the window open, the pass counter dword 20) of r4-events e3p b1p.json, stop-b1p-own_res.json, b0.json and of r3k-events e3b b1.json and b0.json (E823); stop_dumps.py and hwr_scan.py walk every text dump of the data repository (22 top-level directories, firmware/ left out, 569 files, 6797 dumps) for HostCtl dwords 3, 8, 9, 12, 14, sw_events, CR_CLKGATESTATUS and TA3DCtl dwords 56 to 58; the fold changed one line of stop_dumps.py (it printed the path relative to its root, dropping the unit; it now prints the path as walked) and ran all three from the data worktree with relative paths, so the outputs name files of resgx545-data; the rows and counts equal the plan's run; each script re-run from its published copy gave byte-identical output; the job dumps at the arm read by hand in b1p.dmesg; no prediction was frozen before any of these reads, E823's b1 included, so every row here is post hoc, an offline check and not a held-out row"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["edm-closing-r4-events:out/a1/e3p/", "edm-closing-r3k-events:out/e3b/", "cited-scratch:cited/closing5/events/offline/"]
terms = [
    "Event Data Master (EDM)", "host_ctl.ukernel_detected_lockups", "host_ctl.interrupt_flags",
    "host_ctl.hw_recovery_sample_rate", "ta3d_ctl.kick_clear_3d", "CR_CLKGATESTATUS",
    "CR_EVENT_STATUS.SW_EVENT",
]
+++
**Why.** E836's b1p (slot 3's first end-of-render pass skipped and ended by our task with the phase
end) was followed by 10 ticks and then a stop with E537's busy signature; when and why were open
(Q295: "the stop's time is an estimate", "something of the skipped handler is needed later"). E353
names, from our dataflow of the firmware, one routine (`0x1c4`-`0x599`) that counts a lockup in
`host_ctl.ukernel_detected_lockups`, sets `host_ctl.interrupt_flags` bit 0 and writes `SW_EVENT`,
and in the same routine a counter at TA3DCtl `+0xe4` (`ta3d_ctl.kick_clear_3d`, dword 57) tested
against `host_ctl.hw_recovery_sample_rate`, and a word at `+0xe8` (dword 58) whose equality leads
to the call (`edm_dataflow.md`). Round 4 never read those words in its dumps. The round 5 plan
read them after forming the hypothesis; this fold publishes the scripts and records what they
print. No frozen prediction preceded any read.

**Results [HW, post hoc].**

b1p's stop dump (`stop-b1p-status.txt`, taken at the signature, before the host's writes of
`CR_EVENT_HOST_CLEAR` of E837):

| word | at the arm (b1p.dmesg) | at the stop |
|---|---|---|
| HostCtl dword 3 (`ukernel_detected_lockups`) | 0 | **1** |
| HostCtl dword 5 (`hw_recovery_sample_rate`) | 10 | 10 |
| HostCtl dword 8 (`interrupt_flags`) | 0 | **1** |
| HostCtl dword 9 (`interrupt_clear_flags`) | 0 | 0 |
| HostCtl dword 12 (`edm_ticks`) | 3 | 1051 |
| HostCtl dword 14 (`assert_fail`) | 0 | 0 |
| `sw_events` (the kernel's count) | 0 | **1** |
| TA3DCtl dwords 56, 57, 58 | 0, 0, 0 | 0, 0, **0xaac267c2** |

The slot 0 passes after the fill's kick entry (`ticks_after.out`):

| job | ticks before the kick | ticks after it, ring | dword 16 (ring full) | passes after the kick |
|---|---|---|---|---|
| r4 b1p (`b1p.json`, `stop-b1p-own_res.json`: the same page) | 5 | 10 | 10 | **20** |
| r4 b0 (control, the fill completed) | 5 | 10 | 292 | 302 (alive) |
| E823 b1 (the pass ended `idf, wdf, nop.end`) | 5 | 0 | 0 | **0** |
| E823 b0 | 5 | 10 | 279 | 289 (alive) |

In b1p the gaps after the kick entry are 7623 `CR_TIMER` units, then 24990, 25000 seven times and
25005: the tenth logged tick came about 9.3 ms after the kick; with ten more on the 25000-unit
grid the twentieth came about 19.3 ms after it. The ring-full counters of slots 1 to 3 read 0 and
the slot 3 ring holds its one entry (37 µs after the kick entry), so no slot 3 pass followed the
skipped one: between it and the stop our task logged 20 slot 0 passes.

The scan (`stop_dumps.out`, `hwr_scan.data.out`): 6797 dumps, 95 of a firmware past its boot
(dword 12 above 20), 26 of those not idle (`CR_CLKGATESTATUS` not 0x20), 23 of them 0x000ccfa0.
b1p's is the only one of the 23 with dword 3 or dword 8 set; the other 22 (the stop dumps of
r3-events b, r3k-events e3b (E823), f and t, r3x-events d and e, r4-q152 fr, the in-window reads of
r3k-events k0h and r3x-events h, the session fixtures of E537, E813 and E817, firmware-tasks
p1130-b2-variants and transfer isolation; some are copies of one stop) read dword 3 = 0, dword 8 =
0 and TA3DCtl dwords 56 to 58 = 0; `sw_events` reads 0 in 21 of them and 4 in transfer
isolation's output, a run of several jobs. Of the 47 idle dumps past the boot none has dword 3 or
dword 8 set. Over all 6797 dumps the only other non-zero TA3DCtl dwords 56 to 58 are r1-events d1
(E771) and its first try, two dumps with the same words: 0x720b23e4, 0, 0x3c8c9a29 with dword 3 = 0.

**What it shows.** The tick stop after a skipped slot 3 end-of-render pass ended with the phase end
carries the EDM's lockup marks, and the other stops with this signature do not: E836's stop is a
second kind of stop, not E537's. [infer, from E353 and the dataflow] After a 3D kick the closed
tick routine counts its passes in `ta3d_ctl.kick_clear_3d`; at `hw_recovery_sample_rate` (10) it
samples a progress word into dword 58 and restarts the count. The first sample (pass 10) differs
from the saved 0 and is kept (0xaac267c2); the second (pass 20) is equal, so the routine counts a
lockup, sets `interrupt_flags` bit 0 (the recovery request) and writes `SW_EVENT` (the kernel
counted it in `sw_events` and does nothing with it: our kernel reads no dword 8), and the tick
stops. The count matches 2 x the sample rate exactly. The closed end-of-render handler, skipped,
is what would have ended that check for the held render. E823's b1 (0 passes, no marks) stopped
for the other reason, at the pass's own end without the phase end. r1-events d1's words fit jobs
that ran longer than 10 passes with progress between samples [infer].

**What it does not show.** One job, read after the hypothesis: b1p is the fit, not a held-out
test (replicates are the round 5 plan's h1). Whether the count is in passes or in time: at the
stock `timer_clock` 20 passes and about 20 ms are the same (the plan's h2). Which state the
skipped handler would have cleared, what the sampled word is, and why the EDM stops instead of
continuing after the request (the DDK's host answers a recovery request with a reset; ours does
not answer it). Whether a host clear of `CR_EVENT_STATUS` bit 18 before the 20th pass changes
anything. The idle and busy dumps read here were not taken for this purpose: a stop that kept no
dump is not in the scan.
