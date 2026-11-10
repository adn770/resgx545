+++
id = "E764"
claim = "Held with debugfs hold_recovery and read 2.8 s and 3.8 s after the launch, E444's two faults reproduce word for word (1 run each): the TA's read of an unmapped stream page CR_EVENT_STATUS 0x20000000, CR_EVENT_STATUS2 0x480, CR_BIF_INT_STAT 0x90008, CR_BIF_FAULT 0x3e000001, the background program's fetch 0x20000000, 0x440, 0xd0400, 0x0001f061, each stable between the two reads and clear after the debugfs reset (the frozen verdict, a control passing); and, read post hoc from the timeline rows (not frozen), sampled about every 4.3 us from the launch, the fault word and address appear first with CR_EVENT_STATUS2 still 0x400, and bit 7 (TA read) or bit 6 (background fetch) sets 121.2 and 121.1 us later, no other bit rising up to the reset"
unit = "edm"
method = "S3 stage s3-e1-ctl, attempt 20261110-003209 (paths relative to closing/s3/, to become render-closing-s3), 2026-11-10 00:32 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...), ~/regtimeline (sha256 079f6359..., read-only polling of 0x0118, 0x012c, 0x0c00 to 0x0c08); per job: debugfs reset, regs (snap 0), hold_recovery Y read back, the job in the background under regtimeline (tri --fault --wait-ms 20000; tri --pixels --poke cmd:23^=0x08000000 --wait-ms 20000), regs 2.8 s after the launch (snap 1) and 1 s later (snap 2), the debugfs reset with the hold still Y, hold_recovery N read back, regs (snap 3), health triangles; predictions/s3-e1.tsv frozen 2026-11-09 23:11; verdict by the frozen score/score_s3.py s3-e1-ctl (re-run on the kept files: method ok); the timeline rows read post hoc"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s3:out/20261110-003209/s3-e1-ctl/"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_STATUS2", "CR_EVENT_STATUS2.TRIG_TA", "CR_EVENT_STATUS2.TRIG_3D", "CR_BIF_INT_STAT", "CR_BIF_FAULT", "CR_EVENT_STATUS.MADD_CACHE_INVAL_COMPLETE", "CR_EVENT_STATUS.SW_EVENT"]
+++
**Frozen verdict.** `e1-ta-read: PASS`, `e1-bg-fetch: PASS`, `SUMMARY: s3-e1-ctl: method ok: both
controls reproduce E444's held readings`: class fault, the kernel's hold message (`job N hung,
recovery held`), snap 0 clear, snap 1 equal to E444's four words, no extra bit, snap 3 clear. This
opened the gates of s3-e1 and s3-xfer.

**Results [HW].** Snaps 1 and 2 as in the claim (frozen scorer); snap 3 `0x20000000 0x400
0x80000 0x0` in both; both tools rc 1 (`job faulted, context lost`). Timelines (1031659 and
about as many samples over
4.45 s; times from the launch):

| job | fault row | STATUS2 bit set | delay | rows before the fault |
|---|---|---|---|---|
| e1-ta-read | 323.378 ms, 0x90008 / 0x3e000001, status2 0x400 | 323.499 ms, 0x480 | 121.2 us | none |
| e1-bg-fetch | 319.240 ms, 0xd0400 / 0x0001f061, status2 0x400 | 319.361 ms, 0x440 | 121.1 us | 319.134 ms status 0x24000000; 319.197 ms 0xa0004000; 319.209 ms 0x20000000 |

`CR_BIF_CTRL` read 0 throughout the hold. The kernel log of each job holds `BIF fault 0x90008 at
0x3e000001 (PD ...) stalls job 8881, recovering` and `BIF fault 0xd0400 at 0x1f061 ... job 8883`,
then `job N hung, recovery held`.

**Post hoc, from the timeline rows (not frozen, nothing was predicted about the lag).** The delays
in the table are read from the rows of the kept `.txt.gz` after the scoring; the frozen scorer's
`rose` bits are the bits that rise at any time while the fault word is up, so they do not say the
bit rose with the fault.

**What it shows.** [HW] E444's held readings repeat on S1's tool and the current kernel (frozen
verdict). [infer, post hoc, 1 run each, sampling interval about 4.3 us] The status2 bit that
follows each fault is not raised with it but about 121 us after it, the same delay
for the TA's bit 7 and the 3D's bit 6. In the background-fetch job the TA's end shows before the
fault: bit 26 (`MADD_CACHE_INVAL_COMPLETE`), then the EDM's SW_EVENT with bit 31 (the enabled
event), cleared by the kernel's handler 12 us later, and the fault 31 us after that [infer: the
3D pass started after the TA's event and faulted on its first fetch].

**Not shown.** What sets bits 7 and 6 121 us after the fault (hardware or the firmware's reaction);
whether the delay is fixed (one run each).

**Post hoc, on the S3 preflight (a pre-run document of the dataset, not a landed record).** Its
section 8 item 9 said the watchdog prints no BIF fault line under a hold; the kernel printed one for
each held render fault of S3 (3 of 3: here two, E765 the third). The scorer read the page from
snap 1, so no score depends on it. No landed record states the claim (checked in evidence/ and
questions/).
