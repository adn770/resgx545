+++
id = "E766"
claim = "debugfs xfer_ro (E021's 64 x 32 fill aimed at a read-only alias of a kernel buffer) on the current kernel writes nothing and faults at CR_BIF_INT_STAT 0x80020 and CR_BIF_FAULT 0x32200001 as in E021, and reads CR_EVENT_STATUS 0x20000000 and CR_EVENT_STATUS2 0x440 at 2.8 s and 3.8 s, clear after the debugfs reset: the transfer's write fault raises no status bit of its own and reads 0x440, not the EDM write fault's idle 0x400 (the frozen HE, not HE-edm; 1 run, held out); post hoc from the timeline rows (not frozen), bit 6 sets 124.1 us after the fault word"
unit = "transfer"
method = "S3 stage s3-xfer, attempt 20261110-003455 (paths relative to closing/s3/, to become render-closing-s3), 2026-11-10 00:35 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, regtimeline as in s3-e1-ctl (278817 samples over 0.51 s, ending before the reset); debugfs reset, regs (snap 0), `cat` of debugfs xfer_ro in the background (no hold: the kernel's own EDM transfer path has no watchdog), regs 2.8 s and 3.8 s after the launch, the debugfs reset, regs (snap 3), health triangles; the gate open (E444 controls passed); predictions/s3-e1.tsv frozen 2026-11-09 23:11 (int_stat 0x80020 and 0 written for both; HE status2 0x440, HE-edm 0x400, HF an extra bit); verdict by the frozen score/score_s3.py s3-xfer (re-run on the kept files: e1-xfer-ro HE)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s3:out/20261110-003455/s3-xfer/"]
terms = ["CR_BIF_INT_STAT", "CR_BIF_INT_STAT.FAULT_REQ", "CR_BIF_INT_STAT.FAULT_TYPE", "CR_BIF_FAULT", "CR_EVENT_STATUS2", "CR_EVENT_STATUS2.TRIG_3D"]
+++
**Frozen verdict.** `e1-xfer-ro: HE: status 0x20000000 status2 0x440 int_stat 0x80020 bif_fault
0x32200001 bif_ctrl 0x0; stable True; cleared by the reset True; at the fault (t 304.368 ms): rose
status 0x0 status2 0x40`; `SUMMARY: s3-xfer: e1-xfer-ro HE`.

**Results [HW].** The debugfs file's own report, as in E021: `fill whole 64x32: command matches the
12 TQ_CMD words`, `no SW_EVENT after 500 ms`, status F 0 (1 expected), the context count 1, wrong
dwords 0x800 (the sentinel kept), `dwords written through the read-only alias: 0`, `BIF_INT_STAT
0x80020 BIF_FAULT 0x32200001 bif_faults 0`, `kernel buffer protected; reload and boot to recover`;
rc 0. No BIF fault line in the kernel log (no watchdog on this path; bif_faults 0). Snaps 1 and 2
equal; the reset line `SGX reset: BIF_FAULT 0x0 EVENT_STATUS 0x20000000/0x440`; snap 3
`0x20000000 0x400 0x80000 0x0`; health triangles diff 0 (the debugfs reset, a halt and a boot in
place, was enough; E021's phase-4 kernel used a stop, reload and boot).

**Post hoc, the timeline rows (not frozen).** 278817 samples to 808 ms: 304.368 ms 0x80020 /
0x32200001 with status2 0x400; 304.492 ms status2 0x440 (124.1 us later); nothing else to the end
of the sampling. The frozen scorer's `rose status2 0x40` collects the bits that rise while the
fault word is up and does not say when.

**What it shows.** [HW] E021's fault repeats on this kernel (word, page 0x32200, directory list 1,
nothing written), and the transfer's write to a read-only page (type 0, requestor bit 5) reads
`CR_EVENT_STATUS2` 0x440 with no bit of its own, while the EDM's write to a read-only page (E444,
0x80400) leaves status2 at 0x400. [infer, post hoc] Bit 6 sets about 124 us after the fault word,
as after the 3D's fetch faults (E764, E765), and follows the pipeline the faulting requestor
serves (a transfer is a 3D-side pass), not the fault type.

**Not shown.** The transfer's fault of type 1 (0x90020, E024) held; the requestor behind bit 5
beyond "a transfer's write" (one kind of transfer job).
