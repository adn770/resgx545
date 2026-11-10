+++
id = "E767"
claim = "Sampled every 4.3 us through the debugfs reset of three held render faults (S3's e1-ta-read, e1-bg-fetch, e1-tex), CR_BIF_INT_STAT drops to the idle 0x80000 and CR_BIF_FAULT to 0 in one row while CR_EVENT_STATUS and CR_EVENT_STATUS2 keep their held values (0x20000000 and 0x480 or 0x440), and the two status registers read 0 only 11.3, 8.2 and 6.8 ms later; by the kernel's reset code the first change is the halt (the firmware's deinit script and the soft reset of every block) and the second the host clears that follow the CLEAR_FAULT write of CR_BIF_CTRL, so the fault already reads clear before CR_BIF_CTRL's clear bit is written [infer, post hoc, outside the frozen window]"
unit = "bif"
method = "S3 regtimeline rows of the three held render faults (attempts 20261110-003209 and 20261110-003406, paths relative to closing/s3/, to become render-closing-s3; the job's .txt.gz keeps the `tl` rows of 0x0118, 0x012c, 0x0c00, 0x0c04, 0x0c08 from the launch to the end), the rows at or after HOLD_READ + HOLD_GAP = 3.8 s, which the frozen scorer leaves out as the reset's; the order of the kernel's register writes read in the linux fork (drivers/gpu/drm/gma500/sgxfive: sgxfive_reset, sgxfive_halt, sgxfive_clear_faults; sgx_seq.c sgx_seq_boot) at 71e5791d8f957; the kernel's `SGX reset:` line of each reset. Post hoc: nothing here was predicted"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s3:out/20261110-003209/s3-e1-ctl/", "render-closing-s3:out/20261110-003406/s3-e1/"]
terms = ["CR_BIF_INT_STAT", "CR_BIF_FAULT", "CR_BIF_CTRL", "CR_BIF_CTRL.CLEAR_FAULT", "CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_SOFT_RESET"]
+++
**Frozen verdict.** None: the frozen scorer reads no row at or after the reset and predicted
nothing here; every finding of this record is post hoc.

**Results [HW], read post hoc.** Rows after the reset was written (time from the launch; status2,
status, CR_BIF_CTRL, CR_BIF_INT_STAT, CR_BIF_FAULT):

| job | fault reads clear | status registers 0 | later rows |
|---|---|---|---|
| e1-ta-read | 4536.883 ms: 0x480 0x20000000 0 0x80000 0 | 4548.224 ms | 4553.154 CR_BIF_CTRL 0x8 (one row); 4553.164 0x400; 4554.193 0x20000000; 4673.886 status 0x24000000 for 8 us |
| e1-bg-fetch | 4523.570 ms: 0x440 0x20000000 0 0x80000 0 | 4531.767 ms | 4536.718 CR_BIF_CTRL 0x8 (one row); 4536.732 0x400; 4537.759 0x20000000; 4650.842 0x24000000 for 6 us |
| e1-tex | 4539.303 ms: 0x440 0x20000000 0 0x80000 0 | 4546.094 ms | 4550.841 0x400; 4551.924 0x20000000 |

Each reset's kernel line reads `SGX reset: BIF_FAULT 0x0 EVENT_STATUS 0x20000000/0x480` (or
`/0x440`), and snap 3 after it `0x20000000 0x400 0x80000 0x0`.

**Read with the kernel's code [infer].** sgxfive_reset reads CR_BIF_INT_STAT and CR_BIF_FAULT for
the devcoredump, halts (deinit script, then `CR_SOFT_RESET` 0x3f), then sgxfive_clear_faults reads
the status, prints the line above, writes `CR_BIF_CTRL` 0x10 (CLEAR_FAULT) and 0, and host-clears
both status registers with the values it read; the boot later writes CR_BIF_CTRL 0x8 (INVALDC) and
0, which is the one-row 0x8 seen in two of three. The first change of the timeline matches the
halt (the status registers are untouched by it, as the printed line says) and the second matches
the host clears, which come right after the CLEAR_FAULT write; the 0x10 pulse itself was not
sampled. So in 3 of 3 the latched fault reads clear from the halt on, 6.8 to 11.3 ms before the
clear bit is written: what the preflight's scan of 1101 published resets inferred from
`BIF_FAULT 0x0` (the halt leaves the fault reading zero), now with CR_BIF_INT_STAT too and with
the time between.

**Not shown.** Whether the halt clears the latch or only makes the BIF's registers read zero while
the block is held in reset (a register of a block in reset may read zero whatever it holds); which
of the deinit script's writes and the soft reset does it; whether CLEAR_FAULT alone, without the
halt, clears it (Q003's E2, a kernel change). bit 26 of `CR_EVENT_STATUS` after the boot is the
boot's own event, not the fault's.
