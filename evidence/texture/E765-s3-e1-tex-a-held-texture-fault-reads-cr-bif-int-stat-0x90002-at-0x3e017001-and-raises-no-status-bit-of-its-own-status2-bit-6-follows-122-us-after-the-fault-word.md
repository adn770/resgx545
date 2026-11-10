+++
id = "E765"
claim = "Held with debugfs hold_recovery, S1's texture job that reads past the probe's 64 KiB scratch (s1d-tw64x64-l2e2, E722's ad-tw64x64-L2e2 at the 16-page scratch of E743) faults at CR_BIF_INT_STAT 0x90002 and CR_BIF_FAULT 0x3e017001 (page 0x3e017, as in S1) and reads CR_EVENT_STATUS 0x20000000 and CR_EVENT_STATUS2 0x440 at 2.8 s and 3.8 s, clear after the debugfs reset, the frozen HE (no status bit of its own; 1 run, held out); post hoc from the timeline rows (not frozen), sampled every 4.3 us the fault word appears with status2 0x400 and bit 6 sets 122.5 us later, as for E444's background fetch"
unit = "texture"
method = "S3 stage s3-e1, attempt 20261110-003406 (paths relative to closing/s3/, to become render-closing-s3), 2026-11-10 00:34 on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...), regtimeline as in s3-e1-ctl; probe --temps 32 --coords --pixels bins/s1d-tw64x64-l2e2__0.bin (sha256 7540ac80..., byte-identical to S1's frozen copy), the probe's `scratch at 0x3e003000 (64 KiB)` line the knob proof; held as the controls (snap 0, hold Y read back, snaps 2.8 s and 3.8 s after the launch, the debugfs reset with the hold Y, hold N read back, snap 3); the gate (both E444 controls passed in attempt 20261110-003209) open; predictions/s3-e1.tsv frozen 2026-11-09 23:11 (HE: status 0x20000000, status2 0x440, no extra bit; HF: an extra bit; int_stat 0x90002 and page 0x3e017 for both); verdict by the frozen score/score_s3.py s3-e1 (re-run on the kept files: e1-tex HE)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s3:out/20261110-003406/s3-e1/"]
terms = ["CR_BIF_INT_STAT", "CR_BIF_INT_STAT.FAULT_REQ", "CR_BIF_FAULT", "CR_BIF_FAULT.CID", "CR_EVENT_STATUS2", "CR_EVENT_STATUS2.TRIG_3D"]
+++
**Frozen verdict.** `e1-tex: HE: status 0x20000000 status2 0x440 int_stat 0x90002 bif_fault
0x3e017001 bif_ctrl 0x0; stable True; cleared by the reset True; at the fault (t 306.371 ms): rose
status 0x0 status2 0x40`; `SUMMARY: s3-e1: e1-tex HE`. Every frozen row of e1-tex holds: outcome
fault, the 64 KiB line, the word, the page, status, status2 and no extra bit.

**Results [HW].** Snap 0 `0x20000000 0x400 0x80000 0x0`; snaps 1 and 2 as in the claim; snap 3
`0x20000000 0x400 0x80000 0x0`. The probe: rc 3, `failed: job faulted, context lost`, `scratch
unchanged`. Kernel log: `BIF fault 0x90002 at 0x3e017001 (PD 0x288e3000) stalls job 8889,
recovering`, `job 8889 hung, recovery held`, and at the reset `SGX reset: BIF_FAULT 0x0
EVENT_STATUS 0x20000000/0x440`. `CR_BIF_CTRL` 0 throughout the hold. Health triangles after the
job diff 0.

**Post hoc, the timeline rows (not frozen).** 1032896 samples over 4.45 s: 306.371 ms the fault
word and address with status2 0x400; 306.494 ms status2 0x440 (122.5 us later); no other change
until the reset at 4.54 s. The frozen scorer's `rose status2 0x40` collects the bits that rise
while the fault word is up and does not say when; the delay was read after the scoring.

**What it shows.** [HW] The texture fetch's fault is requestor bit 1 of type 1 at the page 16 KiB
past the scratch's end (0x3e003000 + 0x10000 = 0x3e013000; fault 0x3e017000) in directory list 1,
the same as unheld in S1, and it raises no status bit of its own (frozen HE). [infer, post hoc]
The 3D side's bit 6 follows it with the delay the controls show (121 to 122 us, E764). [infer] The
status the kernel prints at the reset of every published 0x90002 fault (0x440, 50 of 50, the
preflight's scan of the published logs) is the same reading after the halt; here it is also the
reading during the hold.

**Not shown.** Whether bit 1 names the texture unit alone (0xd0002, the type-5 form, appears in
the published logs of texture/sampler-bits at low addresses: consistent, not a test); an event
raised and cleared between two samples (4.3 us).
