+++
id = "E789"
claim = "R2-pixel stage r2-a-fault, job a6-320x400-max320 (a 4x job, mode 2, CR_TE_AA 0xe0000000, 320x400 in a render context made for 320x400, held with hold_recovery so that the registers are read before the kernel's reset; the control of the stage's sufficiency job a5, E788): the job faulted (rc 1, class fault) and the held registers read CR_BIF_INT_STAT 0x00090004 and CR_BIF_FAULT 0x20008061 (the faulting page 0x20008, the address the frozen model gave for a TA write past the layout), CR_EVENT_STATUS 0x20000000 and CR_EVENT_STATUS2 0x480; the frozen E1 row for the TA write (the TA's write of the region headers, E763) was HE, the fault raises no status bit of its own (extra bits: none; HF, some, refuted): STATUS2 0x480 is the 0x400 of the idle register plus bit 7, the bit a TA job that faults sets (E317, E764), as for the TA's read fault"
unit = "bif"
method = "R2-pixel stage r2-a-fault, row a6-320x400-max320 (the last job of the stage, risk class risky, held: hold_recovery Y written and restored to N and read back) of the question-closing pass, round 2 (decisions R2-7 to R2-9 and R2-17), dataset render-closing-r2-pixel (attempt 20261110-105258), on the laptop (host cedar), 2026-11-10 at 10:54:55 laptop time (09:54 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); tri --tri-full --keep-going --wait-ms 20000 --width 320 --height 400 --max-width 320 --max-height 400 with --poke cmd:1=0xe0000000, cmd:10=0xeaa26e26, cmd:13=0x80000002 and cmd:16=0xeaa26e26 and --dump-render; the registers read from the debugfs by the runner in the snapshots of the held job (BIF_INT_STAT at 0x0c04, BIF_FAULT at 0x0c08, EVENT_STATUS 0x012c, EVENT_STATUS2 0x0118; the snapshots are not a timeline, so the delay of the bit after the fault word is not read here); the frozen rows int_stat, fault_page, status, status2 and extra_bits for the TA write (HE against HF) and the knob proof the tool's echo `targets up to 320x400`; scored by the frozen score/score_r2.py r2-a-fault (out/20261110-105258/score-r2-a-fault.txt: a6 control PASS, `E1 TA write row (a6-320x400-max320): HE`); the stage's final health triangle passed (stage log: health ok)"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r2-pixel:out/20261110-105258/r2-a-fault/"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT", "CR_EVENT_STATUS2"]
+++
**What ran.** Q003 asks whether a bus-interface fault of another unit sets another status bit. S3
answered it for a held texture fetch fault (E765) and a transfer's write fault (E766); the 3D's
own stores and a held TA-write fault were not run. The 4x render of this session (E788's a6, the
control of the sufficiency job) is a held TA-side write fault at a known page, and its registers
are the row for the TA write.

**Frozen verdict.** `E1 TA write row (a6-320x400-max320): HE` with the control `a6-320x400-max320
control: PASS`, i.e. status 0x20000000, STATUS2 0x480 and no other bit, as predicted; HF (some
other bit) was the alternative.

**Results [HW].** Held snapshot: `CR_BIF_INT_STAT` 0x00090004 (bits 19, 16 and 2), `CR_BIF_FAULT`
0x20008061, `CR_EVENT_STATUS` 0x20000000, `CR_EVENT_STATUS2` 0x00000480.

**What it shows and does not.** The TA's write of the region headers past the layout faults with
the BIF word 0x90004 (bit 2, the same word as E507's 4x faults) and raises no status bit
beyond the 0x480 a TA fault leaves (E317); with E765 and E766 the faults of the texture unit, the
transfer unit and the TA's write each leave no bit of their own. What the register's bit 7 does
after a TA fault in time (E764 read 121 us) was not sampled here. Not answered: the 3D's own
stores, the ZLS, the type-1 transfer fault, and the requestor of each bit (Q003).
