+++
id = "E318"
claim = "Saved before the kernel recovers (recovery held), the job hung in its pixel task holds its object in the parameter buffer and the TA data a finished TA leaves (byte for byte the one-kick triangle's of E288), in both held runs; saved after the recovery, the same job holds the same object but an all-zero TA data; the job with VDM state word 1 bits 15:13 = 0 holds neither, held: the TA wrote nothing before it stopped; while either is held GETMISCINFO is not answered; one run of each, the pixel control held twice"
unit = "vdm"
method = "probes/render/hold-hang.toml on the laptop, linux fork 66dc1fda6ae8 with the debug option on: its script hold-hang.sh runs the staged vdm/state1 jobs vdm-state1-hang-pixel (held, not held, held) and vdm-state1-vdm-state-15-13-0 (held) as sgxfive-test probe --tri with --dump-render; with debugfs hold_recovery set the tool's wait (5 s) ends first and it dumps the render memory before the context is closed and the GPU reset; 2 s in, the state (registers, kreg, status, GETMISCINFO timed); each dump summarised and kept as gzip in base64; debugfs reset after each held job"
tiers = ["HW"]
date = "2026-11-03"
data = ["render-hold-hang", "render-kick-objects"]
terms = ["VDM_STATE1.BITS15_13", "Parameter Buffer (PB)", "control stream", "CR_EVENT_STATUS2",
         "misc_info"]
+++

**Results.**

| job | recovery | parameter slot | TA data |
|---|---|---|---|
| hung in its pixel task | held | object at 0x1000, 1147 non-zero dwords | 71 non-zero dwords |
| the same | not held | the same object, 1147 | all zero |
| the same, again | held | as the first held run, byte for byte | as the first held run |
| VDM state word 1 bits 15:13 = 0 | held | the page table only (1066) | all zero |

The held TA data is byte for byte the TA data of E288's one-kick triangle scene (its region
headers and control stream pages from TA data offset 0x4000). The parameter slot after the
recovery differs from the held one in two page-table entries (slot offsets 0x423008 and
0x42300c), the head of the free list. While each job is held, GETMISCINFO times out (649 to 660
ms from the shell) and `CR_EVENT_STATUS2` reads 0x440 for the pixel-task hangs, 0x480 for the VDM
hang (0x400 when idle); `CR_BIF_INT_STAT` shows no fault. The held pixel jobs' waits end with "Timer
expired"; the unheld one fails with the job timeout's error.

After each debugfs reset, which blames no job, the held job runs again (render_uapi.md §10). The
held pixel jobs (82 and 84) then fault, bus status 0x90008 at 0x3e000001 in their own page
directories, and the fault watchdog's recovery resets the GPU and fails their contexts; the
kernel log then has a failed render-context cleanup for each, which resets the GPU once more.
The VDM case's job 85 is recovered by the job timeout 0.17 s after the debugfs reset, and the
log ends 0.13 s later with no cleanup line for it. Why the two cleanups fail is not shown
(Q029). The cleanup traces the script reads after each reset were read before the context was
freed and show an earlier cleanup (`ret 0` for the first held job, the second's -110 for the
VDM case), so they say nothing of these cleanups. Later jobs run exactly.

**What it shows.**

- A job hung in its pixel task has finished its TA: its object, region headers and control
  streams are all in place before the recovery [HW].
- The recovery zeroes the TA data and keeps the parameter buffer's pages (the PB is rewritten
  only in its free list's head) [HW]: a dump after recovery shows the object without its control
  streams, which is what E186's runs saw in part.
- The VDM state word 1 bits 15:13 = 0 job writes no object and no control stream before it
  stops, read before any recovery [HW]: the TA stops before writing, which E186 could not tell
  from a dump taken after the recovery.
- E186's run whose pixel-task control kept no object is not reproduced: the object is present in
  all three runs here.
- A held job runs again after a debugfs reset and is recovered once more before its context is
  lost [HW]: two resets per held job where one would do, a kernel follow-up (render_uapi.md
  §13).
